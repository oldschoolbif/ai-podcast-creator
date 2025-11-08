"""
Face Generator Module
Generates AI faces optimized for lip-sync using Stable Diffusion
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.gpu_utils import get_gpu_manager


class FaceGenerator:
    """Generate AI faces optimized for lip-sync."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize face generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_dir = Path(config["storage"]["cache_dir"]) / "faces"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get GPU manager
        self.gpu_manager = get_gpu_manager()
        self.device = self.gpu_manager.get_device()
        self.use_gpu = self.gpu_manager.gpu_available

    def generate(
        self,
        prompt: Optional[str] = None,
        description: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate an AI face optimized for lip-sync.

        Args:
            prompt: Custom prompt for face generation
            description: Natural language description (e.g., "professional male presenter")
            output_path: Optional output file path

        Returns:
            Path to generated face image
        """
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            from PIL import Image

            print("[FACE] Generating AI face optimized for lip-sync...")

            # Use lightweight model for faster generation
            # "runwayml/stable-diffusion-v1-5" is smaller and faster than SDXL
            model_id = "runwayml/stable-diffusion-v1-5"
            
            # Build optimized prompt for lip-sync-friendly face
            if description:
                # Convert natural description to prompt
                base_prompt = self._description_to_prompt(description)
            elif prompt:
                base_prompt = prompt
            else:
                base_prompt = "professional male presenter, headshot"
            
            # Add lip-sync optimization keywords
            optimized_prompt = (
                f"{base_prompt}, "
                "front-facing portrait, "
                "neutral expression, "
                "clean lighting, "
                "studio lighting, "
                "high quality, "
                "detailed face, "
                "symmetrical features, "
                "professional headshot, "
                "512x512, "
                "8k uhd"
            )
            
            negative_prompt = (
                "blurry, "
                "low quality, "
                "distorted, "
                "asymmetric, "
                "side profile, "
                "extreme expression, "
                "facial hair covering mouth, "
                "shadows on face, "
                "bad lighting, "
                "artifacts"
            )

            print(f"  Prompt: {optimized_prompt[:80]}...")
            print(f"  Model: {model_id}")
            print(f"  Device: {self.device}")

            # Load pipeline
            if self.use_gpu:
                print("  Loading model on GPU...")
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16 if self.gpu_manager.get_performance_config().get("use_fp16", False) else torch.float32,
                    device_map="auto" if self.use_gpu else None,
                )
                pipe = pipe.to(self.device)
            else:
                print("  Loading model on CPU (this will be slow)...")
                pipe = StableDiffusionPipeline.from_pretrained(model_id)

            # Generate image
            print("  Generating face (this may take 30-60 seconds)...")
            with torch.no_grad():
                image = pipe(
                    prompt=optimized_prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=30,  # Balance between quality and speed
                    guidance_scale=7.5,
                    width=512,
                    height=512,
                ).images[0]

            # Save image
            if output_path is None:
                output_path = self.output_dir / "generated_face.png"
            else:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)

            image.save(output_path, quality=95)
            print(f"  ✓ Face generated: {output_path}")
            print(f"     Size: {image.size[0]}x{image.size[1]}")

            return output_path

        except ImportError:
            print("  ⚠ diffusers not available - install with: pip install diffusers transformers")
            raise
        except Exception as e:
            print(f"  ❌ Face generation failed: {e}")
            raise

    def _description_to_prompt(self, description: str) -> str:
        """Convert natural language description to Stable Diffusion prompt."""
        description_lower = description.lower()
        
        # Gender detection
        if any(word in description_lower for word in ["male", "man", "guy", "gentleman"]):
            gender = "male"
        elif any(word in description_lower for word in ["female", "woman", "lady"]):
            gender = "female"
        else:
            gender = "person"  # Neutral
        
        # Age detection
        if any(word in description_lower for word in ["young", "teen", "teenager"]):
            age = "young"
        elif any(word in description_lower for word in ["old", "elderly", "senior"]):
            age = "mature"
        else:
            age = "professional"
        
        # Style detection
        if any(word in description_lower for word in ["professional", "business", "corporate"]):
            style = "professional business portrait"
        elif any(word in description_lower for word in ["casual", "friendly", "relaxed"]):
            style = "friendly casual portrait"
        else:
            style = "professional portrait"
        
        return f"{age} {gender}, {style}"

