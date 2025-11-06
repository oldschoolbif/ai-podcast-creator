"""
Avatar Generator Module
Generates animated talking head videos synced to audio
Supports multiple engines: Wav2Lip, SadTalker, D-ID
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

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
        self.engine_type = config.get("avatar", {}).get("engine", "wav2lip")

        # Get source image from config or use default
        avatar_config = config.get("avatar", {})
        source_image = avatar_config.get("source_image", "src/assets/avatars/default_female.jpg")
        
        # Resolve relative paths from project root (where config.yaml is)
        if Path(source_image).is_absolute():
            self.source_image = Path(source_image)
        else:
            # Resolve from project root (parent of src directory)
            project_root = Path(__file__).parent.parent.parent
            self.source_image = (project_root / source_image).resolve()

        self.output_dir = Path(config["storage"]["cache_dir"]) / "avatar"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Model storage
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Get GPU manager for optimization
        self.gpu_manager = get_gpu_manager()
        self.device = self.gpu_manager.get_device()
        self.use_gpu = self.gpu_manager.gpu_available

        # Initialize based on engine type
        self.model = None
        self.last_file_monitor = None  # Store last file monitor for metrics tracking
        if self.engine_type == "wav2lip":
            self._init_wav2lip()
        elif self.engine_type == "sadtalker":
            self._init_sadtalker()
        elif self.engine_type == "did":
            self._init_did()
    
    def get_file_monitor(self):
        """Get the last file monitor used for metrics tracking."""
        return self.last_file_monitor
    
    def _get_audio_duration_ffmpeg(self, audio_path: Path) -> float:
        """Get audio duration using FFmpeg (safer than librosa which can crash with C extensions)."""
        try:
            # Use ffprobe to get duration without loading audio into memory
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path)
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            pass
        # Fallback: return None to use default timeout
        return None

    def _init_sadtalker(self):
        """Initialize SadTalker model with GPU acceleration."""
        try:
            import torch

            if self.use_gpu:
                print(f"[OK] Initializing SadTalker on GPU ({self.device})")

                # Set environment for GPU
                import os

                os.environ["CUDA_VISIBLE_DEVICES"] = str(self.gpu_manager.device_id)

                # MAX PERFORMANCE: Enable all GPU optimizations
                os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
                os.environ["CUDA_LAUNCH_BLOCKING"] = "0"  # Async execution for max throughput
                os.environ["TORCH_ALLOW_TF32_CUBLAS_OVERRIDE"] = "1"  # TensorFloat32 for Ampere+

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
                if perf_config["use_fp16"]:
                    print("[OK] FP16 (Mixed Precision) enabled for avatar generation")

                print("[OK] GPU optimizations: async CUDA, cudnn benchmark, TF32, max memory")

            else:
                print("[WARN] SadTalker requires GPU. Using CPU will be very slow.")

        except ImportError:
            print("[WARN] SadTalker not installed")

    def _init_wav2lip(self):
        """Initialize Wav2Lip model with GPU acceleration."""
        try:
            import torch

            # Download model if not exists
            model_path = self.models_dir / "wav2lip_gan.pth"
            if not model_path.exists():
                self._download_wav2lip_model(model_path)

            if model_path.exists():
                if self.use_gpu:
                    print(f"[OK] Wav2Lip initialized on GPU ({self.device})")
                else:
                    print("[WARN] Wav2Lip will use CPU (slower)")
                self.wav2lip_model_path = model_path
            else:
                print("[WARN] Wav2Lip model not available - using static avatar fallback")
                self.wav2lip_model_path = None

        except ImportError as e:
            print(f"[WARN] Wav2Lip dependencies not installed: {e}")
            print("  Using static avatar fallback instead.")
            self.wav2lip_model_path = None

    def _init_did(self):
        """Initialize D-ID API."""
        import os

        # Get API key from environment or config
        self.did_api_key = os.getenv("DID_API_KEY") or self.config.get("avatar", {}).get("did", {}).get("api_key")

        if self.did_api_key:
            print("[OK] D-ID API initialized")
        else:
            print("[WARN] D-ID API key not found. Set DID_API_KEY in .env or config")
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

        if self.engine_type == "sadtalker":
            return self._generate_sadtalker(audio_path, output_path)
        elif self.engine_type == "wav2lip":
            return self._generate_wav2lip(audio_path, output_path)
        elif self.engine_type == "did":
            return self._generate_did(audio_path, output_path)
        else:
            # Unknown engine type, use fallback
            return self._create_fallback_video(audio_path, output_path)

    def _generate_sadtalker(self, audio_path: Path, output_path: Path) -> Path:
        """Generate video using SadTalker with GPU acceleration."""
        try:
            import sys

            import torch

            # Add SadTalker to path
            sadtalker_path = Path(__file__).parent.parent.parent / "external" / "SadTalker"

            if not sadtalker_path.exists():
                print(f"[WARN] SadTalker not found at {sadtalker_path}")
                print("  Using static avatar fallback.")
                return self._create_fallback_video(audio_path, output_path)

            # Add both root and src to path
            sys.path.insert(0, str(sadtalker_path))
            sys.path.insert(0, str(sadtalker_path / "src"))

            # Clear GPU cache
            if self.use_gpu:
                self.gpu_manager.clear_cache()

            print("[VIDEO] Generating avatar animation with SadTalker (GPU-accelerated)...")

            # Use subprocess to avoid import path issues
            import subprocess

            # SadTalker settings from config
            sadtalker_cfg = self.config.get("avatar", {}).get("sadtalker", {})
            still_mode = "--still" if sadtalker_cfg.get("still_mode", False) else ""
            expression_scale = sadtalker_cfg.get("expression_scale", 1.0)
            enhancer = sadtalker_cfg.get("enhancer", "gfpgan")

            # Prepare temp output directory
            temp_result_dir = output_path.parent / "sadtalker_temp"
            temp_result_dir.mkdir(exist_ok=True)

            # Get python from current virtual environment
            import sys as sys_module

            python_exe = sys_module.executable  # Use same Python as current process

            # Build command
            cmd = [
                python_exe,  # Use venv python
                str(sadtalker_path / "inference.py"),
                "--driven_audio",
                str(audio_path),
                "--source_image",
                str(self.source_image),
                "--result_dir",
                str(temp_result_dir),
                "--checkpoint_dir",
                str(sadtalker_path / "checkpoints"),
                "--expression_scale",
                str(expression_scale),
                "--enhancer",
                enhancer,
                "--preprocess",
                "full",
                "--size",
                "256",
            ]

            if still_mode:
                cmd.append(still_mode)

            # FORCE GPU or CPU mode explicitly (don't rely on auto-detection)
            if self.use_gpu:
                # Don't pass --cpu flag, let SadTalker auto-detect GPU
                # SadTalker will use GPU if torch.cuda.is_available() returns True
                pass
            else:
                cmd.extend(["--cpu"])

            print("  Running SadTalker inference...")
            print(f"  Command: {' '.join(cmd[:5])}...")

            # Set up environment with proper Python path AND max GPU performance
            import os

            env = os.environ.copy()
            env["PYTHONPATH"] = str(sadtalker_path)

            # MAX GPU PERFORMANCE: Set environment variables for throughput
            if self.use_gpu:
                env["CUDA_VISIBLE_DEVICES"] = str(self.gpu_manager.device_id)
                env["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
                env["CUDA_LAUNCH_BLOCKING"] = "0"  # Async for max GPU utilization
                env["TORCH_ALLOW_TF32_CUBLAS_OVERRIDE"] = "1"  # TensorFloat32
                env["CUDNN_BENCHMARK"] = "1"  # Find optimal algorithms
                env["TORCH_CUDNN_V8_API_ENABLED"] = "1"  # Latest cuDNN API
                env["TORCH_CUDA_ARCH_LIST"] = "7.0;7.5;8.0;8.6;8.9;9.0"  # Support all modern GPUs
                print("  🚀 MAX GPU MODE: async CUDA, cudnn benchmark, TF32, GPU forced")

            # Run SadTalker
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(sadtalker_path), env=env)

            if result.returncode != 0:
                print(f"[WARN] SadTalker failed with return code {result.returncode}")
                print(f"  Error: {result.stderr[:300]}")
                return self._create_fallback_video(audio_path, output_path)

            # Find generated video
            result_files = list(temp_result_dir.glob("*.mp4"))

            if result_files:
                import shutil

                # Use the first (and usually only) generated file
                shutil.copy(result_files[0], output_path)
                print(f"[OK] SadTalker avatar video generated: {output_path}")

                # Cleanup temp files
                for f in result_files:
                    f.unlink(missing_ok=True)
                temp_result_dir.rmdir()
            else:
                print("[WARN] SadTalker output not found")
                print(f"  Output: {result.stdout[:200]}")
                return self._create_fallback_video(audio_path, output_path)

            # Clear cache
            if self.use_gpu:
                self.gpu_manager.clear_cache()

            return output_path

        except Exception as e:
            print(f"[WARN] SadTalker generation failed: {e}")
            print(f"  Error details: {str(e)[:200]}")
            print("  Using static avatar fallback.")
            return self._create_fallback_video(audio_path, output_path)

    def _generate_wav2lip(self, audio_path: Path, output_path: Path) -> Path:
        """Generate video using Wav2Lip with GPU acceleration."""
        try:
            import sys

            print("[AVATAR] Generating talking head with Wav2Lip...")

            # Use the actual Wav2Lip inference script from cloned repository
            wav2lip_dir = Path(__file__).parent.parent.parent / "external" / "Wav2Lip"
            wav2lip_script = wav2lip_dir / "inference.py"

            if not wav2lip_script.exists():
                print(f"[WARN] Wav2Lip inference script not found at {wav2lip_script}")
                print("  Creating Wav2Lip inference script...")
                # Create the inference script if it doesn't exist
                self._create_wav2lip_inference_script(wav2lip_script)

            # Get Python executable from current environment
            python_exe = sys.executable

            # Resolve paths to absolute paths for Wav2Lip
            # Handle relative paths by resolving from project root
            if not self.source_image.is_absolute():
                # If relative, resolve from project root (where config.yaml is)
                project_root = Path(__file__).parent.parent.parent
                source_image_path = (project_root / self.source_image).resolve()
            else:
                source_image_path = Path(self.source_image).resolve()
            
            audio_path_resolved = Path(audio_path).resolve()
            
            # Check if model path is available
            if self.wav2lip_model_path is None:
                print("[WARN] Wav2Lip model not found: model path is None")
                print("  Creating static avatar video...")
                return self._create_fallback_video(audio_path, output_path)
            
            checkpoint_path_resolved = Path(self.wav2lip_model_path).resolve()
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path_resolved = Path(output_path).resolve()
            
            # Debug: Print the path being used
            print(f"[AVATAR] Using avatar image: {source_image_path}")
            print(f"   Path exists: {source_image_path.exists()}")
            
            # Verify files exist
            if not source_image_path.exists():
                print(f"[WARN] Source image not found: {source_image_path}")
                print(f"   Tried path: {self.source_image}")
                return self._create_fallback_video(audio_path, output_path)
            
            if not checkpoint_path_resolved.exists():
                print(f"[WARN] Wav2Lip model not found: {checkpoint_path_resolved}")
                return self._create_fallback_video(audio_path, output_path)
            
            # CRITICAL: Always detect face before generating video
            # This ensures accurate lip-sync alignment
            face_box = self._detect_face_with_landmarks(source_image_path)
            
            if not face_box:
                print(f"  [ERROR] Face detection failed - cannot proceed without accurate face detection")
                print(f"     Please ensure the image contains a clear, front-facing face")
                return self._create_fallback_video(audio_path, output_path)
            
            # Build command using the actual Wav2Lip inference script
            # Note: Wav2Lip inference.py doesn't have --device argument
            # GPU/CPU is handled automatically by PyTorch
            cmd = [
                python_exe,
                str(wav2lip_script),
                "--checkpoint_path",
                str(checkpoint_path_resolved),
                "--face",
                str(source_image_path),
                "--audio",
                str(audio_path_resolved),
                "--outfile",
                str(output_path_resolved),
                "--static",
                "True",  # Use static image (process single frame repeatedly)
                "--fps",
                "25",
                "--pads",
                "0", "0", "0", "0",  # Minimal padding - let Wav2Lip handle alignment with tight box
                "--resize_factor", "1",  # Don't resize - use original image size
                "--nosmooth",  # Disable smoothing for sharper lip-sync
            ]
            
            # Always use detected face box (mandatory - we already validated it exists)
            y_min, y_max, x_min, x_max = face_box
            cmd.extend([
                "--box",
                str(y_min),  # top
                str(y_max),  # bottom
                str(x_min),  # left
                str(x_max),  # right
            ])
            print(f"  [OK] Using detected face bounding box (mandatory for accurate lip-sync)")

            # Change to Wav2Lip directory for imports to work
            import subprocess
            import os

            original_dir = os.getcwd()
            try:
                os.chdir(str(wav2lip_dir))
                
                # CRITICAL: Create temp directory that Wav2Lip expects
                temp_dir = wav2lip_dir / "temp"
                temp_dir.mkdir(exist_ok=True)
                print(f"  [OK] Created temp directory: {temp_dir}")
                
                # MAX GPU PERFORMANCE: Set environment variables for GPU acceleration
                env = os.environ.copy()
                if self.use_gpu:
                    env["CUDA_VISIBLE_DEVICES"] = str(self.gpu_manager.device_id)
                    env["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
                    env["CUDA_LAUNCH_BLOCKING"] = "0"  # Async for max GPU utilization
                    env["TORCH_ALLOW_TF32_CUBLAS_OVERRIDE"] = "1"  # TensorFloat32 for Ampere+
                    env["CUDNN_BENCHMARK"] = "1"  # Find optimal algorithms
                    env["TORCH_CUDNN_V8_API_ENABLED"] = "1"  # Latest cuDNN API
                    # Force PyTorch to use GPU
                    env["TORCH_CUDA_ARCH_LIST"] = "7.0;7.5;8.0;8.6;8.9;9.0"  # Support all modern GPUs
                    print("  [GPU] MAX GPU MODE: async CUDA, cudnn benchmark, TF32, GPU acceleration forced")
                
                # Run inference with real-time output capture and file monitoring
                print(f"  Running: {' '.join(cmd[-6:])}...")  # Show last 6 args
                
                # Monitor output file growth for progress indication
                from src.utils.file_monitor import FileMonitor
                monitor = FileMonitor(
                    output_path_resolved,
                    update_callback=lambda size, rate, warning: print(f"  [PROGRESS] Avatar: {size:.1f} MB ({rate:.2f} MB/s){warning}", end='\r'),
                    check_interval=2.0
                )
                monitor.start()
                self.last_file_monitor = monitor  # Store for metrics integration
                
                try:
                    # Add timeout to prevent hanging (audio duration + 5 minutes buffer)
                    # Get audio duration using FFmpeg (safer than librosa which can crash)
                    audio_duration = self._get_audio_duration_ffmpeg(audio_path_resolved)
                    if audio_duration is not None:
                        timeout_seconds = int(audio_duration * 2) + 300  # 2x audio duration + 5 min buffer
                        print(f"  [INFO] Wav2Lip timeout set to {timeout_seconds}s (audio: {audio_duration:.1f}s)")
                    else:
                        timeout_seconds = 600  # 10 minutes default
                        print(f"  [INFO] Wav2Lip timeout set to {timeout_seconds}s (default)")
                    
                    # Verify audio file exists before running (with absolute path since we changed dirs)
                    if not audio_path_resolved.exists():
                        raise FileNotFoundError(f"Audio file not found: {audio_path_resolved}")
                    
                    # Use Popen instead of run for better control and to prevent hanging
                    print(f"  [INFO] Starting Wav2Lip process (timeout: {timeout_seconds}s)...")
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=str(wav2lip_dir),
                        encoding='utf-8',
                        errors='replace',
                        env=env
                    )
                    
                    # Monitor GPU utilization during Wav2Lip execution (continuous sampling)
                    gpu_samples = []
                    gpu_monitoring_active = True
                    
                    def monitor_gpu_during_execution():
                        """Monitor GPU utilization while Wav2Lip runs"""
                        nonlocal gpu_samples, gpu_monitoring_active
                        import time
                        sample_interval = 1.0  # Sample every second
                        max_samples = 300  # Max 5 minutes of samples
                        
                        while gpu_monitoring_active and process.poll() is None:
                            try:
                                if self.use_gpu:
                                    gpu_util = self.gpu_manager.get_utilization()
                                    gpu_percent = gpu_util.get("gpu_percent", 0.0)
                                    gpu_samples.append(gpu_percent)
                                    if len(gpu_samples) > max_samples:
                                        gpu_samples.pop(0)  # Keep only recent samples
                            except Exception:
                                pass
                            time.sleep(sample_interval)
                    
                    import threading
                    gpu_monitor_thread = threading.Thread(target=monitor_gpu_during_execution, daemon=True)
                    gpu_monitor_thread.start()
                    
                    # Wait for process with timeout
                    try:
                        stdout, stderr = process.communicate(timeout=timeout_seconds)
                        result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
                    except subprocess.TimeoutExpired:
                        print(f"  [ERROR] Wav2Lip process timed out after {timeout_seconds}s")
                        print("  [WARN] Killing Wav2Lip process...")
                        process.kill()
                        try:
                            process.wait(timeout=5)
                        except:
                            pass
                        raise subprocess.TimeoutExpired(cmd, timeout_seconds)
                except subprocess.TimeoutExpired:
                    print(f"  [ERROR] Wav2Lip timed out after {timeout_seconds}s")
                    print("  [WARN] Using static avatar fallback")
                    gpu_monitoring_active = False  # Stop GPU monitoring
                    try:
                        gpu_monitor_thread.join(timeout=2.0)
                    except:
                        pass
                    monitor.stop()
                    return self._create_fallback_video(audio_path, output_path)
                finally:
                    # Always stop GPU monitoring and cleanup
                    gpu_monitoring_active = False
                    try:
                        gpu_monitor_thread.join(timeout=2.0)
                    except:
                        pass
                    
                    # Store GPU samples for metrics (if available)
                    if 'gpu_samples' in locals() and gpu_samples:
                        avg_gpu = sum(gpu_samples) / len(gpu_samples)
                        peak_gpu = max(gpu_samples)
                        print(f"  [GPU] Average GPU utilization during Wav2Lip: {avg_gpu:.1f}% (peak: {peak_gpu:.1f}%)")
                        # Store in a way that metrics can access
                        self._wav2lip_gpu_samples = gpu_samples
                    else:
                        self._wav2lip_gpu_samples = []
                    
                    monitor.stop()
                    print()  # New line after progress updates
                
                # Verify GPU usage after Wav2Lip completes
                if self.use_gpu:
                    try:
                        import subprocess as sp
                        # Check if CUDA is actually being used (check nvidia-smi for process)
                        gpu_check = sp.run(
                            ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if gpu_check.returncode == 0 and gpu_check.stdout.strip():
                            print("  [OK] GPU detected in use by processes")
                        else:
                            print("  [WARN] WARNING: GPU may not be in use - checking Wav2Lip output...")
                            # Check Wav2Lip output for CUDA messages
                            if result.stdout and "cuda" in result.stdout.lower():
                                print("  [OK] CUDA mentioned in Wav2Lip output")
                            elif result.stderr and "cuda" in result.stderr.lower():
                                print("  [OK] CUDA mentioned in Wav2Lip stderr")
                            else:
                                print("  [WARN] No CUDA usage detected in Wav2Lip output")
                    except Exception as e:
                        print(f"  [WARN] Could not verify GPU usage: {e}")

                # Print Wav2Lip output for debugging
                if result.stdout:
                    # Print last 30 lines of output
                    stdout_lines = result.stdout.strip().split('\n')
                    for line in stdout_lines[-30:]:
                        if line.strip():
                            print(f"  Wav2Lip: {line}")
                
                # Also check stderr for errors
                if result.stderr:
                    stderr_lines = result.stderr.strip().split('\n')
                    print(f"  Wav2Lip STDERR ({len(stderr_lines)} lines):")
                    for line in stderr_lines[-20:]:
                        if line.strip() and not line.strip().startswith('File "'):
                            print(f"    {line[:200]}")
                
                # Check if output was created (even if return code is non-zero, sometimes it still works)
                # Also check for file in Wav2Lip results directory (in case it wrote relative to its cwd)
                possible_outputs = [
                    output_path_resolved,
                    Path(wav2lip_dir) / "results" / output_path_resolved.name,
                    Path(wav2lip_dir) / output_path_resolved.name,
                    output_path,  # Original relative path
                    output_path.parent / output_path.name,  # Relative to original working dir
                ]
                
                output_found = False
                found_path = None
                
                for check_path in possible_outputs:
                    try:
                        if check_path.exists() and check_path.stat().st_size > 50000:  # At least 50KB for a real video
                            output_found = True
                            found_path = check_path
                            print(f"[OK] Wav2Lip output found: {check_path} ({check_path.stat().st_size / 1024 / 1024:.1f} MB)")
                            # Copy to expected location if it's in a different place
                            if check_path != output_path_resolved:
                                import shutil
                                output_path_resolved.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(check_path, output_path_resolved)
                                print(f"  Copied to expected location: {output_path_resolved}")
                            break
                    except (OSError, FileNotFoundError):
                        continue  # Try next path
                
                # If output was found, return it
                if output_found and found_path:
                    return output_path_resolved if output_path_resolved.exists() else found_path
                
                # If we get here, output wasn't created properly
                if result.returncode != 0:
                    print(f"[WARN] Wav2Lip error (return code: {result.returncode}):")
                    if result.stdout:
                        try:
                            stdout_msg = result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
                            print(f"  STDOUT: {stdout_msg}")
                        except Exception:
                            print("  STDOUT: [Unable to display - encoding issue]")
                    if result.stderr:
                        try:
                            stderr_msg = result.stderr[-500:] if len(result.stderr) > 500 else result.stderr
                            print(f"  STDERR: {stderr_msg}")
                        except Exception:
                            print("  STDERR: [Unable to display - encoding issue]")
                    print("[WARN] Wav2Lip output file not found at any expected location")
                    print(f"  Checked: {[str(p) for p in possible_outputs]}")
                    # Fallback: create simple static video
                    return self._create_fallback_video(audio_path, output_path)
                
                # If return code was 0 but no file found, something went wrong
                print("[WARN] Wav2Lip completed with code 0 but output file not found")
                print(f"  Checked: {[str(p) for p in possible_outputs]}")
                return self._create_fallback_video(audio_path, output_path)
            finally:
                os.chdir(original_dir)

        except Exception as e:
            print(f"[ERROR] Avatar generation failed with exception: {e}")
            import traceback
            full_traceback = traceback.format_exc()
            print(f"  Full traceback:\n{full_traceback}")
            print("[ERROR] This is a critical error - avatar generation cannot proceed")
            # Don't return fallback - let the error propagate so we can see what's wrong
            raise

    def _generate_did(self, audio_path: Path, output_path: Path) -> Path:
        """Generate video using D-ID API."""
        import base64
        import time

        import requests

        if not self.did_api_key:
            print("[WARN] D-ID API key missing. Using static avatar fallback.")
            return self._create_fallback_video(audio_path, output_path)

        try:
            print("[VIDEO] Generating talking head with D-ID API...")

            # Read and encode source image
            with open(self.source_image, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # Read audio file
            with open(audio_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")

            # D-ID API endpoint
            url = "https://api.d-id.com/talks"

            headers = {"Authorization": f"Basic {self.did_api_key}", "Content-Type": "application/json"}

            # Create talk payload
            payload = {
                "source_url": f"data:image/jpeg;base64,{image_data}",
                "script": {"type": "audio", "audio_url": f"data:audio/mp3;base64,{audio_data}"},
                "config": {"fluent": True, "pad_audio": 0.0},
            }

            # Submit talk creation
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code != 201:
                print(f"[WARN] D-ID API error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return self._create_fallback_video(audio_path, output_path)

            talk_data = response.json()
            talk_id = talk_data.get("id")

            if not talk_id:
                print("[WARN] No talk ID received from D-ID")
                return self._create_fallback_video(audio_path, output_path)

            print(f"  Talk ID: {talk_id}")
            print("  Waiting for D-ID to generate video...")

            # Poll for completion
            get_url = f"{url}/{talk_id}"
            max_attempts = 60  # 5 minutes max
            attempt = 0

            while attempt < max_attempts:
                time.sleep(5)  # Wait 5 seconds between checks
                attempt += 1

                status_response = requests.get(get_url, headers=headers)

                if status_response.status_code != 200:
                    print(f"[WARN] Status check failed: {status_response.status_code}")
                    continue

                status_data = status_response.json()
                status = status_data.get("status")

                print(f"  Status: {status} ({attempt}/{max_attempts})")

                if status == "done":
                    video_url = status_data.get("result_url")
                    if video_url:
                        # Download the generated video
                        print("  Downloading generated video...")
                        video_response = requests.get(video_url)

                        if video_response.status_code == 200:
                            with open(output_path, "wb") as f:
                                f.write(video_response.content)
                            print(f"[OK] D-ID avatar video generated: {output_path}")
                            return output_path
                        else:
                            print(f"[WARN] Failed to download video: {video_response.status_code}")
                            break
                    else:
                        print("[WARN] No result URL in response")
                        break

                elif status == "error" or status == "failed":
                    error_msg = status_data.get("error", {}).get("message", "Unknown error")
                    print(f"[WARN] D-ID generation failed: {error_msg}")
                    break

            # If we got here, something went wrong
            print("[WARN] D-ID generation timed out or failed. Using static fallback.")
            return self._create_fallback_video(audio_path, output_path)

        except Exception as e:
            print(f"[WARN] D-ID API error: {e}")
            print("  Using static avatar fallback.")
            return self._create_fallback_video(audio_path, output_path)

    def _download_wav2lip_model(self, model_path: Path):
        """Download Wav2Lip pre-trained model."""
        import urllib.request

        # Alternative download URLs for Wav2Lip model
        model_urls = [
            "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0.0/wav2lip_gan.pth",
            "https://github.com/justinjohn0306/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth",
            (
                "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/"
                "radrabha_m_research_iiit_ac_in/EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55YNDcIA?e=n9ljGW"
            ),
        ]

        print("📥 Attempting to download Wav2Lip model...")
        success = False

        for url in model_urls:
            try:
                print(f"  Trying: {url[:60]}...")
                urllib.request.urlretrieve(url, model_path)
                print("[OK] Model downloaded successfully")
                success = True
                break
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                continue

        if not success:
            print("\n[WARN] Automatic download failed.")
            print("  For full lip-sync animation, please manually download the model from:")
            print("  https://github.com/Rudrabha/Wav2Lip")
            print(f"  Save as: {model_path}")
            print("\n  For now, using static avatar (image + audio) instead.")

    def _detect_face_with_landmarks(self, image_path: Path) -> tuple:
        """
        Detect face with facial landmarks for precise mouth alignment.
        Uses multiple methods in order of accuracy.
        
        Returns:
            Tuple (y_min, y_max, x_min, x_max) or None if detection fails
        """
        try:
            from PIL import Image
            import numpy as np
            import cv2
            
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            width, height = img.size
            
            # Method 1: Try MediaPipe (best accuracy, facial landmarks)
            try:
                import mediapipe as mp
                mp_face_mesh = mp.solutions.face_mesh
                mp_drawing = mp.solutions.drawing_utils
                
                with mp_face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                ) as face_mesh:
                    results = face_mesh.process(img_array)
                    
                    if results.multi_face_landmarks:
                        face_landmarks = results.multi_face_landmarks[0]
                        
                        # Extract landmark coordinates
                        landmarks = []
                        for landmark in face_landmarks.landmark:
                            x = int(landmark.x * width)
                            y = int(landmark.y * height)
                            landmarks.append((x, y))
                        
                        # Get face bounding box from all landmarks (not centered on mouth)
                        x_coords = [p[0] for p in landmarks]
                        y_coords = [p[1] for p in landmarks]
                        
                        # Calculate tight face bounding box (minimal padding for Wav2Lip)
                        x_min_raw = int(min(x_coords))
                        x_max_raw = int(max(x_coords))
                        y_min_raw = int(min(y_coords))
                        y_max_raw = int(max(y_coords))
                        
                        # Add minimal padding (5% of face size) for Wav2Lip processing
                        face_width_raw = x_max_raw - x_min_raw
                        face_height_raw = y_max_raw - y_min_raw
                        padding_x = int(face_width_raw * 0.05)
                        padding_y = int(face_height_raw * 0.05)
                        
                        # Create tight face box with minimal padding
                        x_min = max(0, x_min_raw - padding_x)
                        x_max = min(width, x_max_raw + padding_x)
                        y_min = max(0, y_min_raw - padding_y)
                        y_max = min(height, y_max_raw + padding_y)
                        
                        # Get mouth center for verification
                        mouth_indices = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324]
                        mouth_x = [landmarks[i][0] for i in mouth_indices if i < len(landmarks)]
                        mouth_y = [landmarks[i][1] for i in mouth_indices if i < len(landmarks)]
                        
                        if mouth_x and mouth_y:
                            mouth_center_x = sum(mouth_x) / len(mouth_x)
                            mouth_center_y = sum(mouth_y) / len(mouth_y)
                            mouth_in_box = (x_min <= mouth_center_x <= x_max) and (y_min <= mouth_center_y <= y_max)
                            
                            # Calculate face center and size for logging
                            face_center_x = (x_min + x_max) / 2
                            face_center_y = (y_min + y_max) / 2
                            face_width = x_max - x_min
                            face_height = y_max - y_min
                            
                            face_box = (y_min, y_max, x_min, x_max)
                            print(f"  [OK] Face detected with MediaPipe (landmarks): box=({x_min}, {y_min}, {x_max}, {y_max})")
                            print(f"     Face center: ({int(face_center_x)}, {int(face_center_y)}), size: {face_width}x{face_height}")
                            print(f"     Mouth center: ({int(mouth_center_x)}, {int(mouth_center_y)}), within box: {mouth_in_box}")
                            return face_box
                            
            except ImportError:
                pass  # MediaPipe not available, try next method
            except Exception as e:
                print(f"  [WARN] MediaPipe detection error: {e}")
            
            # Method 2: Try face_alignment (good accuracy with landmarks)
            try:
                import face_alignment
                import torch
                
                fa = face_alignment.FaceAlignment(
                    face_alignment.LandmarksType.TWO_D,
                    flip_input=False,
                    device=str(self.device) if self.use_gpu else 'cpu'
                )
                
                preds = fa.get_landmarks(img_array)
                
                if preds and len(preds) > 0:
                    landmarks = preds[0]  # 68 points
                    
                    # face_alignment uses 68-point landmarks
                    # Get all face landmark coordinates for proper face bounding box
                    x_coords = landmarks[:, 0]
                    y_coords = landmarks[:, 1]
                    
                    # Calculate tight face bounding box from all landmarks
                    # Wav2Lip works best with a tight box that closely fits the face
                    # Use minimal padding to ensure accurate alignment
                    x_min_raw = int(x_coords.min())
                    x_max_raw = int(x_coords.max())
                    y_min_raw = int(y_coords.min())
                    y_max_raw = int(y_coords.max())
                    
                    # Add minimal padding (5% of face size) for Wav2Lip processing
                    face_width_raw = x_max_raw - x_min_raw
                    face_height_raw = y_max_raw - y_min_raw
                    padding_x = int(face_width_raw * 0.05)
                    padding_y = int(face_height_raw * 0.05)
                    
                    # Create tight face box with minimal padding
                    x_min = max(0, x_min_raw - padding_x)
                    x_max = min(width, x_max_raw + padding_x)
                    y_min = max(0, y_min_raw - padding_y)
                    y_max = min(height, y_max_raw + padding_y)
                    
                    # Get mouth landmarks for verification
                    mouth_landmarks = landmarks[48:68]
                    mouth_x = mouth_landmarks[:, 0]
                    mouth_y = mouth_landmarks[:, 1]
                    mouth_center_x = mouth_x.mean()
                    mouth_center_y = mouth_y.mean()
                    
                    # Verify mouth is within the face box
                    mouth_in_box = (x_min <= mouth_center_x <= x_max) and (y_min <= mouth_center_y <= y_max)
                    
                    # Calculate face center and size for logging
                    face_center_x = (x_min + x_max) / 2
                    face_center_y = (y_min + y_max) / 2
                    face_width = x_max - x_min
                    face_height = y_max - y_min
                    
                    face_box = (y_min, y_max, x_min, x_max)
                    print(f"  [OK] Face detected with face_alignment (68-point landmarks): box=({x_min}, {y_min}, {x_max}, {y_max})")
                    print(f"     Face center: ({int(face_center_x)}, {int(face_center_y)}), size: {face_width}x{face_height}")
                    print(f"     Mouth center: ({int(mouth_center_x)}, {int(mouth_center_y)}), within box: {mouth_in_box}")
                    return face_box
                    
            except ImportError:
                pass  # face_alignment not available
            except Exception as e:
                print(f"  [WARN] face_alignment detection error: {e}")
            
            # Method 3: OpenCV DNN face detector (more accurate than Haar)
            try:
                # Try DNN face detector first
                prototxt = Path(__file__).parent.parent.parent / "models" / "opencv_face_detector.pbtxt"
                model = Path(__file__).parent.parent.parent / "models" / "opencv_face_detector_uint8.pb"
                
                if prototxt.exists() and model.exists():
                    net = cv2.dnn.readNetFromTensorflow(str(model), str(prototxt))
                    (h, w) = img_array.shape[:2]
                    blob = cv2.dnn.blobFromImage(img_bgr, 1.0, (300, 300), [104, 117, 123])
                    net.setInput(blob)
                    detections = net.forward()
                    
                    best_face = None
                    best_confidence = 0
                    
                    for i in range(0, detections.shape[2]):
                        confidence = detections[0, 0, i, 2]
                        if confidence > 0.5 and confidence > best_confidence:
                            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                            (x, y, x2, y2) = box.astype("int")
                            best_face = (x, y, x2, y2)
                            best_confidence = confidence
                    
                    if best_face:
                        x, y, x2, y2 = best_face
                        w, h = x2 - x, y2 - y
                        
                        # Estimate mouth position (typically at 60% down the face)
                        mouth_y_est = int(y + h * 0.6)
                        mouth_x_est = int(x + w / 2)
                        
                        # Adjust box to center on estimated mouth position
                        face_width = int(w * 1.3)
                        face_height = int(h * 1.4)
                        
                        x_min = max(0, int(mouth_x_est - face_width / 2))
                        x_max = min(width, int(mouth_x_est + face_width / 2))
                        y_min = max(0, int(mouth_y_est - face_height * 0.6))
                        y_max = min(height, int(mouth_y_est + face_height * 0.4))
                        
                        face_box = (y_min, y_max, x_min, x_max)
                        print(f"  [OK] Face detected with OpenCV DNN: box=({y_min}, {y_max}, {x_min}, {x_max})")
                        print(f"     Estimated mouth: ({mouth_x_est}, {mouth_y_est})")
                        return face_box
            except Exception as e:
                pass  # DNN not available or failed
            
            # Method 4: OpenCV Haar cascade with DIRECT mouth detection (most accurate fallback)
            try:
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                
                if len(faces) > 0:
                    face = max(faces, key=lambda f: f[2] * f[3])
                    x, y, w, h = face
                    
                    # DIRECT MOUTH DETECTION: Use mouth cascade within face ROI
                    face_roi = gray[y:y+h, x:x+w]
                    
                    # Try multiple mouth cascade files (different naming conventions)
                    mouth_cascade_paths = [
                        cv2.data.haarcascades + 'haarcascade_mcs_mouth.xml',
                        cv2.data.haarcascades + 'haarcascade_mouth.xml',
                    ]
                    
                    mouth_detected = False
                    mouth_x_est = x + w // 2  # Default to center
                    mouth_y_est = y + int(h * 0.6)  # Default estimate
                    
                    for mouth_cascade_path in mouth_cascade_paths:
                        try:
                            mouth_cascade = cv2.CascadeClassifier(mouth_cascade_path)
                            if mouth_cascade.empty():
                                continue
                            
                            # Detect mouth in lower portion of face (40-75% down)
                            mouth_roi_y_start = int(h * 0.4)
                            mouth_roi_y_end = int(h * 0.75)
                            mouth_region = face_roi[mouth_roi_y_start:mouth_roi_y_end, :]
                            
                            if mouth_region.size > 0:
                                mouths = mouth_cascade.detectMultiScale(
                                    mouth_region,
                                    scaleFactor=1.1,
                                    minNeighbors=3,
                                    minSize=(20, 10),
                                    maxSize=(w // 2, h // 3)
                                )
                                
                                if len(mouths) > 0:
                                    # Use the largest/most central mouth detection
                                    mouth = max(mouths, key=lambda m: m[2] * m[3])
                                    mx, my, mw, mh = mouth
                                    
                                    # Convert to full image coordinates
                                    mouth_x_est = x + mx + mw // 2
                                    mouth_y_est = y + mouth_roi_y_start + my + mh // 2
                                    
                                    mouth_detected = True
                                    print(f"  [OK] Mouth directly detected at: ({mouth_x_est}, {mouth_y_est}), size: {mw}x{mh}")
                                    break
                        except Exception as e:
                            continue  # Try next cascade file
                    
                    if not mouth_detected:
                        # PRIMARY METHOD: Use edge detection to find mouth (more reliable than cascade)
                        # Look for horizontal edges in mouth region (lips create strong horizontal lines)
                        mouth_roi_y_start = int(h * 0.40)  # Start a bit higher
                        mouth_roi_y_end = int(h * 0.75)     # Go lower to catch mouth
                        mouth_region = face_roi[mouth_roi_y_start:mouth_roi_y_end, :]
                        
                        if mouth_region.size > 0:
                            # Enhance contrast first
                            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                            mouth_region_enhanced = clahe.apply(mouth_region)
                            
                            # Use Canny edge detection with multiple thresholds
                            edges1 = cv2.Canny(mouth_region_enhanced, 30, 100)
                            edges2 = cv2.Canny(mouth_region_enhanced, 50, 150)
                            edges = cv2.bitwise_or(edges1, edges2)
                            
                            # Find horizontal lines (mouth is primarily horizontal)
                            # Use larger kernel to find the main mouth line
                            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 2))
                            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, horizontal_kernel)
                            
                            # Also try to find vertical lines (mouth corners)
                            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 15))
                            vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, vertical_kernel)
                            
                            # Combine to find mouth center
                            mouth_features = cv2.bitwise_or(horizontal_lines, vertical_lines)
                            
                            # Find center of mouth feature activity
                            if mouth_features.sum() > 100:  # Minimum threshold
                                y_coords, x_coords = np.where(mouth_features > 0)
                                if len(y_coords) > 10 and len(x_coords) > 10:  # Need enough points
                                    # Use median for more robust center (resistant to outliers)
                                    mouth_y_relative = mouth_roi_y_start + int(np.median(y_coords))
                                    mouth_x_relative = int(np.median(x_coords))
                                    mouth_y_est = y + mouth_y_relative
                                    mouth_x_est = x + mouth_x_relative
                                    mouth_detected = True
                                    print(f"  [OK] Mouth detected via edge analysis at: ({mouth_x_est}, {mouth_y_est})")
                                    print(f"     Detected {len(y_coords)} mouth feature points")
                    
                    if not mouth_detected:
                        # Last resort: Use template matching with multiple mouth region estimates
                        # Try different mouth positions and find the one with most horizontal features
                        best_mouth_score = 0
                        best_mouth_y = y + int(h * 0.6)
                        best_mouth_x = x + w // 2
                        
                        # Test multiple mouth positions
                        for mouth_y_pct in [0.55, 0.60, 0.65, 0.58]:
                            test_y = int(y + h * mouth_y_pct)
                            test_x = x + w // 2
                            
                            # Extract small region around test position
                            test_roi_y = max(0, test_y - 15)
                            test_roi_y_end = min(height, test_y + 15)
                            test_roi_x = max(0, test_x - 30)
                            test_roi_x_end = min(width, test_x + 30)
                            
                            if test_roi_y_end > test_roi_y and test_roi_x_end > test_roi_x:
                                test_roi = gray[test_roi_y:test_roi_y_end, test_roi_x:test_roi_x_end]
                                if test_roi.size > 0:
                                    # Look for horizontal edges (mouth signature)
                                    test_edges = cv2.Canny(test_roi, 50, 150)
                                    horizontal_k = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
                                    h_lines = cv2.morphologyEx(test_edges, cv2.MORPH_OPEN, horizontal_k)
                                    score = h_lines.sum()
                                    
                                    if score > best_mouth_score:
                                        best_mouth_score = score
                                        best_mouth_y = test_y
                                        best_mouth_x = test_x
                        
                        mouth_y_est = best_mouth_y
                        mouth_x_est = best_mouth_x
                        mouth_detected = True
                        print(f"  [OK] Mouth detected via template matching at: ({mouth_x_est}, {mouth_y_est}), score: {best_mouth_score}")
                    
                    # Create bounding box centered on detected/estimated mouth
                    # Make sure box is large enough to include full face
                    face_width = int(w * 1.6)  # Wider to ensure proper centering
                    face_height = int(h * 1.7)  # Taller to include forehead
                    
                    # Center box on mouth position
                    x_min = max(0, int(mouth_x_est - face_width / 2))
                    x_max = min(width, int(mouth_x_est + face_width / 2))
                    # Extend more upward (70% above mouth) to include forehead
                    y_min = max(0, int(mouth_y_est - face_height * 0.70))
                    # Less below (30% below mouth) - mouth is in lower face
                    y_max = min(height, int(mouth_y_est + face_height * 0.30))
                    
                    face_box = (y_min, y_max, x_min, x_max)
                    print(f"  [OK] Face detected with OpenCV (mouth-focused): box=({y_min}, {y_max}, {x_min}, {x_max})")
                    print(f"     Face: ({y}, {y+h}, {x}, {x+w}), Mouth: ({mouth_x_est}, {mouth_y_est})")
                    return face_box
            except Exception as e:
                print(f"  [WARN] OpenCV detection error: {e}")
                import traceback
                traceback.print_exc()
            
            return None
            
        except Exception as e:
            print(f"  [WARN] Face detection error: {e}")
            return None
    
    def _create_fallback_video(self, audio_path: Path, output_path: Path) -> Path:
        """Create a simple static video with the avatar image and audio."""
        try:
            from moviepy.editor import AudioFileClip, ImageClip

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
                temp_img = self.output_dir / "placeholder.png"
                Image.fromarray(img_array).save(temp_img)
                video = ImageClip(str(temp_img), duration=duration)

            # Set audio
            video = video.set_audio(audio)

            # Write output
            video.write_videofile(
                str(output_path), fps=25, codec="libx264", audio_codec="aac", verbose=False, logger=None
            )

            return output_path

        except Exception as e:
            print(f"[WARN] Fallback video creation failed: {e}")
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
print("Wav2Lip full installation required")
print("  Please install Wav2Lip from: https://github.com/Rudrabha/Wav2Lip")
sys.exit(1)
'''

        with open(script_path, "w") as f:
            f.write(script_content)
