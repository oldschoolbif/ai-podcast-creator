"""
Music Generator Module
Generates background music from text descriptions
"""

from typing import Dict, Any, List
from pathlib import Path
import hashlib
import sys

# Add parent directory to path for GPU utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.gpu_utils import get_gpu_manager


class MusicGenerator:
    """Generate background music using AI models."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize music generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.engine_type = config['music']['engine']
        self.cache_dir = Path(config['storage']['cache_dir']) / 'music'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Get GPU manager for optimization
        self.gpu_manager = get_gpu_manager()
        self.device = self.gpu_manager.get_device()
        self.use_gpu = self.gpu_manager.gpu_available
        
        if self.engine_type == 'musicgen':
            self._init_musicgen()
        elif self.engine_type == 'mubert':
            self._init_mubert()
        elif self.engine_type == 'library':
            self._init_library()
    
    def _init_musicgen(self):
        """Initialize MusicGen model with GPU acceleration."""
        try:
            from audiocraft.models import MusicGen
            import torch
            
            model_name = self.config['music']['musicgen']['model']
            
            if self.use_gpu:
                print(f"✓ Initializing MusicGen on GPU ({self.device})")
                self.model = MusicGen.get_pretrained(model_name, device=self.device)
                
                # Enable performance optimizations
                perf_config = self.gpu_manager.get_performance_config()
                
                # Enable torch.compile for PyTorch 2.0+
                if hasattr(torch, 'compile') and torch.__version__ >= '2.0':
                    try:
                        self.model.lm = torch.compile(self.model.lm, mode='reduce-overhead')
                        print("✓ torch.compile enabled for MusicGen")
                    except:
                        pass
                
                # Use mixed precision if supported
                if perf_config['use_fp16']:
                    try:
                        self.model.lm.half()
                        print("✓ FP16 mixed precision enabled for music generation")
                    except:
                        pass
            else:
                print("⚠ Initializing MusicGen on CPU (very slow)")
                self.model = MusicGen.get_pretrained(model_name, device='cpu')
                
        except ImportError:
            print("⚠ AudioCraft not installed. Run: pip install audiocraft")
            self.model = None
    
    def _init_mubert(self):
        """Initialize Mubert API."""
        # TODO: Initialize Mubert API client
        pass
    
    def _init_library(self):
        """Initialize music library."""
        # TODO: Load pre-existing music library
        pass
    
    def generate(self, music_input) -> Path:
        """
        Generate background music based on description or cues.
        
        Args:
            music_input: Either a string description or list of music cues
            
        Returns:
            Path to generated music file (or None if no music)
        """
        if not music_input:
            return None
        
        # Handle both string descriptions and music cue lists
        if isinstance(music_input, str):
            primary_cue = music_input
        elif isinstance(music_input, list) and len(music_input) > 0:
            # Extract first cue description
            if isinstance(music_input[0], dict):
                primary_cue = music_input[0].get('description', 'calm background music')
            else:
                primary_cue = str(music_input[0])
        else:
            return None
        
        cache_key = self._get_cache_key(primary_cue)
        cached_path = self.cache_dir / f"{cache_key}.wav"
        
        if cached_path.exists():
            return cached_path
        
        if self.engine_type == 'musicgen':
            return self._generate_musicgen(primary_cue, cached_path)
        elif self.engine_type == 'mubert':
            return self._generate_mubert(primary_cue, cached_path)
        elif self.engine_type == 'library':
            return self._select_from_library(primary_cue, cached_path)
    
    def _generate_musicgen(self, description: str, output_path: Path) -> Path:
        """Generate music using MusicGen with GPU acceleration."""
        if self.model is None:
            print("⚠ MusicGen not available, skipping music generation")
            return None
        
        try:
            import torch
            import torchaudio
            
            # Clear GPU cache
            if self.use_gpu:
                self.gpu_manager.clear_cache()
            
            # Get generation parameters
            duration = self.config['music']['musicgen'].get('duration', 10)
            temperature = self.config['music']['musicgen'].get('temperature', 1.0)
            top_k = self.config['music']['musicgen'].get('top_k', 250)
            top_p = self.config['music']['musicgen'].get('top_p', 0.0)
            
            # Set generation parameters for performance
            self.model.set_generation_params(
                duration=duration,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                use_sampling=True,
                cfg_coef=3.0,  # Classifier-free guidance
            )
            
            print(f"🎵 Generating music: {description[:50]}...")
            
            # Generate with GPU acceleration
            with torch.inference_mode():
                if self.use_gpu:
                    with torch.cuda.amp.autocast(enabled=True):  # Automatic mixed precision
                        wav = self.model.generate([description])
                else:
                    wav = self.model.generate([description])
            
            # Save audio
            torchaudio.save(
                str(output_path),
                wav[0].cpu(),
                sample_rate=self.model.sample_rate
            )
            
            # Clear cache
            if self.use_gpu:
                self.gpu_manager.clear_cache()
            
            print(f"✓ Music generated: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"⚠ Music generation failed: {e}")
            return None
    
    def _generate_mubert(self, description: str, output_path: Path) -> Path:
        """Generate music using Mubert API."""
        # TODO: Implement Mubert API call
        output_path.touch()
        return output_path
    
    def _select_from_library(self, description: str, output_path: Path) -> Path:
        """Select music from pre-existing library."""
        # TODO: Implement library selection based on description
        output_path.touch()
        return output_path
    
    def _get_cache_key(self, description: str) -> str:
        """Generate cache key for music description."""
        content = f"{description}_{self.engine_type}"
        return hashlib.md5(content.encode()).hexdigest()

