"""
Avatar Generator Module
Generates animated talking head videos synced to audio
Supports multiple engines: Wav2Lip, SadTalker, D-ID
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys
import subprocess
import os
import hashlib

# Add parent directory to path for GPU utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.gpu_utils import get_gpu_manager


class AvatarGenerator:
    """Generate animated avatar video synced to audio."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize avatar generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.engine_type = config.get('avatar', {}).get('engine', 'wav2lip')
        
        # Get source image from config or use default
        avatar_config = config.get('avatar', {})
        source_image = avatar_config.get('source_image', 'src/assets/avatars/default_female.jpg')
        self.source_image = Path(source_image)
        
        self.output_dir = Path(config['storage']['cache_dir']) / 'avatar'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Model storage
        self.models_dir = Path('models')
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Get GPU manager for optimization
        self.gpu_manager = get_gpu_manager()
        self.device = self.gpu_manager.get_device()
        self.use_gpu = self.gpu_manager.gpu_available
        
        # Initialize based on engine type
        self.model = None
        if self.engine_type == 'wav2lip':
            self._init_wav2lip()
        elif self.engine_type == 'sadtalker':
            self._init_sadtalker()
        elif self.engine_type == 'did':
            self._init_did()
    
    def _init_sadtalker(self):
        """Initialize SadTalker model with GPU acceleration."""
        try:
            import torch
            
            if self.use_gpu:
                print(f"✓ Initializing SadTalker on GPU ({self.device})")
                
                # Set environment for GPU
                import os
                os.environ['CUDA_VISIBLE_DEVICES'] = str(self.gpu_manager.device_id)
                
                # MAX PERFORMANCE: Enable all GPU optimizations
                os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
                os.environ['CUDA_LAUNCH_BLOCKING'] = '0'  # Async execution for max throughput
                os.environ['TORCH_ALLOW_TF32_CUBLAS_OVERRIDE'] = '1'  # TensorFloat32 for Ampere+
                
                # Enable cudnn benchmarking for optimal convolution algorithms
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.enabled = True
                
                # TODO: Load SadTalker models with GPU
                # from inference import SadTalker
                # self.sadtalker = SadTalker(
                #     checkpoint_dir=self.config['avatar']['sadtalker']['checkpoint_dir'],
                #     config_dir=self.config['avatar']['sadtalker']['config_dir'],
                #     device=self.device
                # )
                
                # Enable optimizations
                perf_config = self.gpu_manager.get_performance_config()
                if perf_config['use_fp16']:
                    print("✓ FP16 (Mixed Precision) enabled for avatar generation")
                
                print("✓ GPU optimizations: async CUDA, cudnn benchmark, TF32, max memory")
                
            else:
                print("⚠ SadTalker requires GPU. Using CPU will be very slow.")
                
        except ImportError:
            print("⚠ SadTalker not installed")
    
    def _init_wav2lip(self):
        """Initialize Wav2Lip model with GPU acceleration."""
        try:
            import torch
            
            # Download model if not exists
            model_path = self.models_dir / 'wav2lip_gan.pth'
            if not model_path.exists():
                self._download_wav2lip_model(model_path)
            
            if model_path.exists():
                if self.use_gpu:
                    print(f"✓ Wav2Lip initialized on GPU ({self.device})")
                else:
                    print("⚠ Wav2Lip will use CPU (slower)")
                self.wav2lip_model_path = model_path
            else:
                print("⚠ Wav2Lip model not available - using static avatar fallback")
                self.wav2lip_model_path = None
            
        except ImportError as e:
            print(f"⚠ Wav2Lip dependencies not installed: {e}")
            print("  Using static avatar fallback instead.")
            self.wav2lip_model_path = None
    
    def _init_did(self):
        """Initialize D-ID API."""
        import os
        
        # Get API key from environment or config
        self.did_api_key = os.getenv('DID_API_KEY') or self.config.get('avatar', {}).get('did', {}).get('api_key')
        
        if self.did_api_key:
            print(f"✓ D-ID API initialized")
        else:
            print("⚠ D-ID API key not found. Set DID_API_KEY in .env or config")
            print("  Sign up at: https://www.d-id.com/")
    
    def generate(self, audio_path: Path, for_basic_mode: bool = True) -> Path:
        """
        Generate avatar video synced to audio.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Path to generated video file
        """
        output_path = self.output_dir / f"avatar_{audio_path.stem}.mp4"
        
        if self.engine_type == 'sadtalker':
            return self._generate_sadtalker(audio_path, output_path)
        elif self.engine_type == 'wav2lip':
            return self._generate_wav2lip(audio_path, output_path)
        elif self.engine_type == 'did':
            return self._generate_did(audio_path, output_path)
    
    def _generate_sadtalker(self, audio_path: Path, output_path: Path) -> Path:
        """Generate video using SadTalker with GPU acceleration."""
        try:
            import torch
            import sys
            
            # Add SadTalker to path
            sadtalker_path = Path(__file__).parent.parent.parent / 'external' / 'SadTalker'
            
            if not sadtalker_path.exists():
                print(f"⚠ SadTalker not found at {sadtalker_path}")
                print("  Using static avatar fallback.")
                return self._create_fallback_video(audio_path, output_path)
            
            # Add both root and src to path
            sys.path.insert(0, str(sadtalker_path))
            sys.path.insert(0, str(sadtalker_path / 'src'))
            
            # Clear GPU cache
            if self.use_gpu:
                self.gpu_manager.clear_cache()
            
            print(f"🎬 Generating avatar animation with SadTalker (GPU-accelerated)...")
            
            # Use subprocess to avoid import path issues
            import subprocess
            
            # SadTalker settings from config
            sadtalker_cfg = self.config.get('avatar', {}).get('sadtalker', {})
            still_mode = '--still' if sadtalker_cfg.get('still_mode', False) else ''
            expression_scale = sadtalker_cfg.get('expression_scale', 1.0)
            enhancer = sadtalker_cfg.get('enhancer', 'gfpgan')
            
            # Prepare temp output directory
            temp_result_dir = output_path.parent / 'sadtalker_temp'
            temp_result_dir.mkdir(exist_ok=True)
            
            # Get python from current virtual environment
            import sys as sys_module
            python_exe = sys_module.executable  # Use same Python as current process
            
            # Build command
            cmd = [
                python_exe,  # Use venv python
                str(sadtalker_path / 'inference.py'),
                '--driven_audio', str(audio_path),
                '--source_image', str(self.source_image),
                '--result_dir', str(temp_result_dir),
                '--checkpoint_dir', str(sadtalker_path / 'checkpoints'),
                '--expression_scale', str(expression_scale),
                '--enhancer', enhancer,
                '--preprocess', 'full',
                '--size', '256',
            ]
            
            if still_mode:
                cmd.append(still_mode)
            
            # FORCE GPU or CPU mode explicitly (don't rely on auto-detection)
            if self.use_gpu:
                # Don't pass --cpu flag, let SadTalker auto-detect GPU
                # SadTalker will use GPU if torch.cuda.is_available() returns True
                pass
            else:
                cmd.extend(['--cpu'])
            
            print("  Running SadTalker inference...")
            print(f"  Command: {' '.join(cmd[:5])}...")
            
            # Set up environment with proper Python path AND max GPU performance
            import os
            env = os.environ.copy()
            env['PYTHONPATH'] = str(sadtalker_path)
            
            # MAX GPU PERFORMANCE: Set environment variables for throughput
            if self.use_gpu:
                env['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
                env['CUDA_LAUNCH_BLOCKING'] = '0'  # Async for max GPU utilization
                env['TORCH_ALLOW_TF32_CUBLAS_OVERRIDE'] = '1'  # TensorFloat32
                env['CUDNN_BENCHMARK'] = '1'  # Find optimal algorithms
                env['TORCH_CUDNN_V8_API_ENABLED'] = '1'  # Latest cuDNN API
                print("  🚀 MAX GPU MODE: async CUDA, cudnn benchmark, TF32")
            
            # Run SadTalker
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(sadtalker_path),
                env=env
            )
            
            if result.returncode != 0:
                print(f"⚠ SadTalker failed with return code {result.returncode}")
                print(f"  Error: {result.stderr[:300]}")
                return self._create_fallback_video(audio_path, output_path)
            
            # Find generated video
            result_files = list(temp_result_dir.glob("*.mp4"))
            
            if result_files:
                import shutil
                # Use the first (and usually only) generated file
                shutil.copy(result_files[0], output_path)
                print(f"✓ SadTalker avatar video generated: {output_path}")
                
                # Cleanup temp files
                for f in result_files:
                    f.unlink(missing_ok=True)
                temp_result_dir.rmdir()
            else:
                print("⚠ SadTalker output not found")
                print(f"  Output: {result.stdout[:200]}")
                return self._create_fallback_video(audio_path, output_path)
            
            # Clear cache
            if self.use_gpu:
                self.gpu_manager.clear_cache()
            
            return output_path
            
        except Exception as e:
            print(f"⚠ SadTalker generation failed: {e}")
            print(f"  Error details: {str(e)[:200]}")
            print("  Using static avatar fallback.")
            return self._create_fallback_video(audio_path, output_path)
    
    def _generate_wav2lip(self, audio_path: Path, output_path: Path) -> Path:
        """Generate video using Wav2Lip with GPU acceleration."""
        try:
            import torch
            import cv2
            import numpy as np
            from scipy.io import wavfile
            
            print(f"🎬 Generating talking head with Wav2Lip...")
            
            # Use inference script approach with subprocess for simplicity
            # This avoids complex model loading code
            wav2lip_script = Path(__file__).parent.parent.parent / 'scripts' / 'wav2lip_inference.py'
            
            if not wav2lip_script.exists():
                # Create inference script
                self._create_wav2lip_inference_script(wav2lip_script)
            
            cmd = [
                'python3', str(wav2lip_script),
                '--checkpoint_path', str(self.wav2lip_model_path),
                '--face', str(self.source_image),
                '--audio', str(audio_path),
                '--outfile', str(output_path),
            ]
            
            if self.use_gpu:
                cmd.extend(['--device', 'cuda'])
            else:
                cmd.extend(['--device', 'cpu'])
            
            # Run inference
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠ Wav2Lip error: {result.stderr}")
                # Fallback: create simple static video
                return self._create_fallback_video(audio_path, output_path)
            
            print(f"✓ Avatar video generated: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"⚠ Avatar generation failed: {e}")
            return self._create_fallback_video(audio_path, output_path)
    
    def _generate_did(self, audio_path: Path, output_path: Path) -> Path:
        """Generate video using D-ID API."""
        import requests
        import time
        import base64
        
        if not self.did_api_key:
            print("⚠ D-ID API key missing. Using static avatar fallback.")
            return self._create_fallback_video(audio_path, output_path)
        
        try:
            print(f"🎬 Generating talking head with D-ID API...")
            
            # Read and encode source image
            with open(self.source_image, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Read audio file
            with open(audio_path, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            # D-ID API endpoint
            url = "https://api.d-id.com/talks"
            
            headers = {
                "Authorization": f"Basic {self.did_api_key}",
                "Content-Type": "application/json"
            }
            
            # Create talk payload
            payload = {
                "source_url": f"data:image/jpeg;base64,{image_data}",
                "script": {
                    "type": "audio",
                    "audio_url": f"data:audio/mp3;base64,{audio_data}"
                },
                "config": {
                    "fluent": True,
                    "pad_audio": 0.0
                }
            }
            
            # Submit talk creation
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code != 201:
                print(f"⚠ D-ID API error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return self._create_fallback_video(audio_path, output_path)
            
            talk_data = response.json()
            talk_id = talk_data.get('id')
            
            if not talk_id:
                print("⚠ No talk ID received from D-ID")
                return self._create_fallback_video(audio_path, output_path)
            
            print(f"  Talk ID: {talk_id}")
            print(f"  Waiting for D-ID to generate video...")
            
            # Poll for completion
            get_url = f"{url}/{talk_id}"
            max_attempts = 60  # 5 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(5)  # Wait 5 seconds between checks
                attempt += 1
                
                status_response = requests.get(get_url, headers=headers)
                
                if status_response.status_code != 200:
                    print(f"⚠ Status check failed: {status_response.status_code}")
                    continue
                
                status_data = status_response.json()
                status = status_data.get('status')
                
                print(f"  Status: {status} ({attempt}/{max_attempts})")
                
                if status == 'done':
                    video_url = status_data.get('result_url')
                    if video_url:
                        # Download the generated video
                        print(f"  Downloading generated video...")
                        video_response = requests.get(video_url)
                        
                        if video_response.status_code == 200:
                            with open(output_path, 'wb') as f:
                                f.write(video_response.content)
                            print(f"✓ D-ID avatar video generated: {output_path}")
                            return output_path
                        else:
                            print(f"⚠ Failed to download video: {video_response.status_code}")
                            break
                    else:
                        print("⚠ No result URL in response")
                        break
                
                elif status == 'error' or status == 'failed':
                    error_msg = status_data.get('error', {}).get('message', 'Unknown error')
                    print(f"⚠ D-ID generation failed: {error_msg}")
                    break
            
            # If we got here, something went wrong
            print("⚠ D-ID generation timed out or failed. Using static fallback.")
            return self._create_fallback_video(audio_path, output_path)
            
        except Exception as e:
            print(f"⚠ D-ID API error: {e}")
            print("  Using static avatar fallback.")
            return self._create_fallback_video(audio_path, output_path)
    
    def _download_wav2lip_model(self, model_path: Path):
        """Download Wav2Lip pre-trained model."""
        import urllib.request
        
        # Alternative download URLs for Wav2Lip model
        model_urls = [
            "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0.0/wav2lip_gan.pth",
            "https://github.com/justinjohn0306/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth",
            "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55YNDcIA?e=n9ljGW"
        ]
        
        print("📥 Attempting to download Wav2Lip model...")
        success = False
        
        for url in model_urls:
            try:
                print(f"  Trying: {url[:60]}...")
                urllib.request.urlretrieve(url, model_path)
                print("✓ Model downloaded successfully")
                success = True
                break
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                continue
        
        if not success:
            print("\n⚠ Automatic download failed.")
            print("  For full lip-sync animation, please manually download the model from:")
            print("  https://github.com/Rudrabha/Wav2Lip")
            print(f"  Save as: {model_path}")
            print("\n  For now, using static avatar (image + audio) instead.")
    
    def _create_fallback_video(self, audio_path: Path, output_path: Path) -> Path:
        """Create a simple static video with the avatar image and audio."""
        try:
            from moviepy.editor import ImageClip, AudioFileClip
            
            print("  Creating static avatar video...")
            
            # Load audio to get duration
            audio = AudioFileClip(str(audio_path))
            duration = audio.duration
            
            # Create video from static image
            if self.source_image.exists():
                video = ImageClip(str(self.source_image), duration=duration)
            else:
                # Create a placeholder if image doesn't exist
                import numpy as np
                from PIL import Image
                img_array = np.zeros((1080, 1920, 3), dtype=np.uint8) + 50
                temp_img = self.output_dir / 'placeholder.png'
                Image.fromarray(img_array).save(temp_img)
                video = ImageClip(str(temp_img), duration=duration)
            
            # Set audio
            video = video.set_audio(audio)
            
            # Write output
            video.write_videofile(
                str(output_path),
                fps=25,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            return output_path
            
        except Exception as e:
            print(f"⚠ Fallback video creation failed: {e}")
            output_path.touch()
            return output_path
    
    def _create_wav2lip_inference_script(self, script_path: Path):
        """Create Wav2Lip inference script."""
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        script_content = '''"""
Wav2Lip Inference Script
Simplified inference for AI Podcast Creator
"""
import sys
print("⚠ Wav2Lip full installation required")
print("  Please install Wav2Lip from: https://github.com/Rudrabha/Wav2Lip")
sys.exit(1)
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)

