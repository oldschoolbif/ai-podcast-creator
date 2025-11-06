"""
Video Composer Module
Composes final video with background and effects
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class VideoComposer:
    """Compose final video with all elements."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize video composer."""
        self.config = config
        self.last_file_monitor = None  # Store last file monitor for metrics
        self.output_dir = Path(config["storage"]["outputs_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.background = Path(config.get("video", {}).get("background_path", "src/assets/backgrounds/studio_01.jpg"))
    
    def get_file_monitor(self):
        """Get the last file monitor used for metrics tracking."""
        return self.last_file_monitor
    
    def _validate_audio_file(self, audio_path: Path) -> tuple[bool, str]:
        """
        Validate audio file before processing.
        
        Returns:
            (is_valid, error_message): Tuple indicating if file is valid and error message if not
        """
        # Check if file exists
        if not audio_path.exists():
            return False, f"Audio file does not exist: {audio_path}"
        
        # Check if file is empty
        if audio_path.stat().st_size == 0:
            return False, f"Audio file is empty (0 bytes): {audio_path}"
        
        # Check if file is too small (likely corrupted)
        if audio_path.stat().st_size < 100:  # Less than 100 bytes is suspicious
            return False, f"Audio file is too small ({audio_path.stat().st_size} bytes), likely corrupted: {audio_path}"
        
        # Use ffprobe to validate the audio file format
        try:
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
            
            # Check for common corruption indicators in stderr
            stderr_lower = result.stderr.lower()
            if "illegal" in stderr_lower or "invalid" in stderr_lower or "corrupt" in stderr_lower:
                return False, f"Audio file appears corrupted (FFprobe error): {audio_path}\n  FFprobe stderr: {result.stderr[:200]}"
            
            if result.returncode != 0:
                return False, f"Audio file validation failed (FFprobe returned {result.returncode}): {audio_path}\n  FFprobe stderr: {result.stderr[:200]}"
            
            # Check if we got a valid duration
            if not result.stdout.strip():
                return False, f"Audio file has no duration information (may be corrupted): {audio_path}\n  FFprobe stderr: {result.stderr[:200]}"
            
            try:
                duration = float(result.stdout.strip())
                if duration <= 0:
                    return False, f"Audio file has invalid duration ({duration}s): {audio_path}"
            except ValueError:
                return False, f"Audio file duration could not be parsed: {audio_path}\n  FFprobe output: {result.stdout[:200]}"
            
            return True, ""
            
        except subprocess.TimeoutExpired:
            return False, f"Audio file validation timed out (file may be corrupted or unreadable): {audio_path}"
        except FileNotFoundError:
            return False, f"FFprobe not found - cannot validate audio file: {audio_path}"
        except Exception as e:
            return False, f"Error validating audio file: {audio_path}\n  Error: {str(e)}"
    
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
    
    def _cleanup_ffmpeg_process(self, process, timeout=2.0):
        """Properly cleanup FFmpeg process, closing all pipes and terminating/killing if needed."""
        import subprocess
        try:
            # Close all pipes first
            if hasattr(process, 'stdin') and process.stdin and not process.stdin.closed:
                process.stdin.close()
        except Exception:
            pass
        try:
            if hasattr(process, 'stderr') and process.stderr and not process.stderr.closed:
                process.stderr.close()
        except Exception:
            pass
        try:
            if hasattr(process, 'stdout') and process.stdout and not process.stdout.closed:
                process.stdout.close()
        except Exception:
            pass
        
        # Terminate gracefully first
        if process.poll() is None:  # Process still running
            try:
                process.terminate()
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Force kill if graceful termination fails
                try:
                    process.kill()
                    process.wait(timeout=1.0)
                except Exception:
                    pass
            except Exception:
                # If terminate fails, try kill directly
                try:
                    process.kill()
                    process.wait(timeout=1.0)
                except Exception:
                    pass

    # Quality presets for encoding
    QUALITY_PRESETS = {
        "fastest": {
            "resolution": [854, 480],
            "preset": "p7",  # Fastest NVENC preset
            "cq": "28",  # Lower quality (faster)
            "bitrate": "2M",
            "maxrate": "3M",
            "bufsize": "6M",
            "audio_bitrate": "128k",
        },
        "fast": {
            "resolution": [1280, 720],
            "preset": "p6",
            "cq": "26",
            "bitrate": "3M",
            "maxrate": "4M",
            "bufsize": "8M",
            "audio_bitrate": "160k",
        },
        "medium": {
            "resolution": [1280, 720],
            "preset": "p5",
            "cq": "24",
            "bitrate": "4M",
            "maxrate": "5M",
            "bufsize": "10M",
            "audio_bitrate": "192k",
        },
        "high": {
            "resolution": [1920, 1080],
            "preset": "p4",
            "cq": "23",
            "bitrate": "5M",
            "maxrate": "6M",
            "bufsize": "12M",
            "audio_bitrate": "192k",
        },
    }


    def compose(
        self,
        audio_path: Path,
        avatar_image: Optional[Path] = None,
        output_name: Optional[str] = None,
        use_visualization: bool = False,
        use_background: bool = False,
        avatar_video: Optional[Path] = None,
        quality: Optional[str] = None,
    ) -> Path:
        """
        Compose final video with audio and optional effects.
        
        Default: Creates minimal video (black frame + audio) - audio-only mode
        Flags enable effects:
        - use_visualization: Add waveform/visualization effects
        - use_background: Add static background image
        - avatar_video: Use lip-sync avatar video

        Args:
            audio_path: Path to mixed audio file
            avatar_image: Path to avatar image (optional)
            output_name: Optional custom output name
            use_visualization: Add audio-reactive visualization (waveform, etc.)
            use_background: Add static background image
            avatar_video: Path to pre-generated avatar video (for lip-sync)

        Returns:
            Path to final video file
        """
        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"podcast_{timestamp}"

        output_path = self.output_dir / f"{output_name}.mp4"

        # Priority 1: Avatar video (if provided)
        if avatar_video:
            print(f"[DEBUG] Avatar video received: {avatar_video}")
            print(f"[DEBUG] Avatar exists: {avatar_video.exists()}")
            if avatar_video.exists():
                print(f"[DEBUG] Avatar size: {avatar_video.stat().st_size} bytes")
        
        if avatar_video and avatar_video.exists() and avatar_video.stat().st_size > 0:
            print(f"[VIDEO] Using avatar video for composition: {avatar_video}")
            if use_visualization and use_background:
                # Avatar + background + visualization (all three)
                bg_path = self.background if self.background.exists() else self._create_default_background()
                return self._compose_avatar_background_visualization(avatar_video, audio_path, bg_path, output_path, quality=quality)
            elif use_visualization:
                # Avatar + visualization overlay
                return self._overlay_visualization_on_avatar(avatar_video, audio_path, output_path, quality=quality)
            elif use_background:
                # Avatar + background (no visualization)
                bg_path = self.background if self.background.exists() else self._create_default_background()
                return self._compose_avatar_with_background(avatar_video, audio_path, bg_path, output_path, quality=quality)
            else:
                # Just avatar video
                import shutil
                shutil.copy(avatar_video, output_path)
                return output_path

        # Priority 2: Visualization (waveform, spectrum, etc.)
        if use_visualization:
            if use_background:
                # Visualization + background image
                bg_path = self.background if self.background.exists() else self._create_default_background()
                return self._compose_visualization_with_background(audio_path, bg_path, output_path, quality=quality)
            else:
                # Visualization only (no background - pure visualization)
                return self._compose_visualization_only(audio_path, output_path, quality=quality)

        # Priority 3: Background image (static)
        if use_background:
            bg_path = self.background if self.background.exists() else self._create_default_background()
            return self._compose_with_ffmpeg(audio_path, bg_path, output_path, quality=quality)

        # Default: Minimal video (black frame + audio) - audio-only mode
        return self._compose_minimal_video(audio_path, output_path, quality=quality)

    def _compose_with_ffmpeg(self, audio_path: Path, image_path: Path, output_path: Path, quality: Optional[str] = None) -> Path:
        """Compose video using FFmpeg with GPU acceleration if available."""
        # Validate audio file before processing
        is_valid, error_msg = self._validate_audio_file(audio_path)
        if not is_valid:
            error_details = (
                f"Audio file validation failed: {error_msg}\n"
                f"  This usually indicates:\n"
                f"  - The audio file was corrupted during generation\n"
                f"  - The audio file is empty or incomplete\n"
                f"  - The audio file format is invalid or unsupported\n"
                f"  - The file path is incorrect\n"
                f"  Troubleshooting steps:\n"
                f"  1. Check if the audio file exists and is readable\n"
                f"  2. Verify the file size is reasonable (not 0 bytes)\n"
                f"  3. Try regenerating the audio file\n"
                f"  4. Check the TTS/audio generation step for errors"
            )
            raise ValueError(error_details)
        
        try:
            from src.utils.gpu_utils import get_gpu_manager

            gpu_manager = get_gpu_manager()

            # Get quality preset (default to 'fastest' for testing)
            quality_key = quality or self.config.get("video", {}).get("quality", "fastest")
            if quality_key not in self.QUALITY_PRESETS:
                # Support legacy quality strings
                if "fastest" in quality_key.lower() or "testing" in quality_key.lower():
                    quality_key = "fastest"
                elif "fast" in quality_key.lower():
                    quality_key = "fast"
                elif "high" in quality_key.lower() or "1080" in quality_key:
                    quality_key = "high"
                elif "medium" in quality_key.lower() or "720" in quality_key:
                    quality_key = "medium"
                else:
                    quality_key = "fastest"
            
            preset = self.QUALITY_PRESETS[quality_key]
            print(f"[Quality] Using preset: {quality_key} ({preset['resolution'][0]}x{preset['resolution'][1]})")

            # Base FFmpeg command
            cmd = ["ffmpeg", "-y"]

            # Try to use GPU encoding if available (NVIDIA)
            if gpu_manager.gpu_available:
                try:
                    # Check if NVENC is available
                    check_cmd = ["ffmpeg", "-hide_banner", "-encoders"]
                    result = subprocess.run(check_cmd, capture_output=True, text=True)

                    if "h264_nvenc" in result.stdout:
                        print("[GPU] Using GPU-accelerated H.264 encoding (NVENC)")

                        cmd.extend(
                            [
                                "-loop",
                                "1",
                                "-i",
                                str(image_path),
                                "-i",
                                str(audio_path),
                                "-c:v",
                                "h264_nvenc",  # NVIDIA GPU encoder
                                "-preset",
                                preset["preset"],
                                "-tune",
                                "1",  # NVENC tune: 1=hq (high quality), 2=low-latency, 3=ultra-low-latency, 4=lossless
                                "-rc",
                                "vbr",  # Variable bitrate
                                "-cq",
                                preset["cq"],
                                "-b:v",
                                preset["bitrate"],
                                "-maxrate",
                                preset["maxrate"],
                                "-bufsize",
                                preset["bufsize"],
                                "-g",
                                "30",  # GOP size: keyframe every 30 frames (1 second at 30fps) - enables seeking
                                "-keyint_min",
                                "30",  # Minimum keyframe interval
                                "-sc_threshold",
                                "0",  # Disable scene change detection for consistent keyframes
                                "-vf",
                                f"scale={preset['resolution'][0]}:{preset['resolution'][1]}:force_original_aspect_ratio=decrease:eval=frame,pad={preset['resolution'][0]}:{preset['resolution'][1]}:(ow-iw)/2:(oh-ih)/2:color=0x141E30",  # Scale image and pad with dark blue background
                                "-r",
                                "30",  # Set output frame rate to match video settings
                                "-c:a",
                                "aac",
                                "-b:a",
                                preset["audio_bitrate"],
                                "-ar",
                                "44100",  # Standard sample rate - universal compatibility
                                "-ac",
                                "2",  # Stereo
                                "-pix_fmt",
                                "yuv420p",  # Universal pixel format - works everywhere
                                "-shortest",  # Match shortest input stream
                                "-f",
                                "mp4",  # Explicitly set container format
                                "-movflags",
                                "+faststart",  # Web optimization - moov atom at beginning
                                str(output_path),
                            ]
                        )
                    else:
                        raise Exception("NVENC not available")

                except Exception as e:
                    print(f"[WARN] GPU encoding not available, using CPU: {e}")
                    # Fallback to CPU with optimized settings
                    cmd.extend(
                        [
                            "-loop",
                            "1",
                            "-i",
                            str(image_path),
                            "-i",
                            str(audio_path),
                            "-c:v",
                            "libx264",
                            "-profile:v",
                            "baseline",  # Maximum compatibility - works on all devices
                            "-level",
                            "3.1",  # Level 3.1 for universal compatibility (not 3.0)
                            "-preset",
                            "faster",  # Faster CPU encoding
                            "-tune",
                            "stillimage",
                            "-crf",
                            preset["cq"],  # Use quality preset CQ
                            "-g",
                            "30",  # GOP size: keyframe every 30 frames (1 second at 30fps) - enables seeking
                            "-keyint_min",
                            "30",  # Minimum keyframe interval
                            "-sc_threshold",
                            "0",  # Disable scene change detection for consistent keyframes
                            "-vf",
                            f"scale={preset['resolution'][0]}:{preset['resolution'][1]}",  # Apply resolution
                            "-c:a",
                            "aac",
                            "-b:a",
                            preset["audio_bitrate"],
                            "-ar",
                            "44100",  # Standard sample rate
                            "-ac",
                            "2",  # Stereo
                            "-pix_fmt",
                            "yuv420p",
                            "-shortest",  # Match shortest input stream
                            "-f",
                            "mp4",  # Explicitly set container format
                            "-movflags",
                            "+faststart",  # Web optimization - moov atom at beginning
                            str(output_path),
                        ]
                    )
            else:
                # CPU encoding with optimized settings
                preset = self.QUALITY_PRESETS.get(quality_key, self.QUALITY_PRESETS["fastest"])
                cmd.extend(
                    [
                        "-loop",
                        "1",
                        "-i",
                        str(image_path),
                        "-i",
                        str(audio_path),
                        "-c:v",
                        "libx264",
                        "-profile:v",
                        "baseline",  # Maximum compatibility - works on all devices
                        "-level",
                        "3.1",  # Level 3.1 for universal compatibility (not 3.0)
                        "-preset",
                        "faster",
                        "-tune",
                        "stillimage",
                        "-crf",
                        preset["cq"],  # Use quality preset CQ
                        "-g",
                        "30",  # GOP size: keyframe every 30 frames (1 second at 30fps) - enables seeking
                        "-keyint_min",
                        "30",  # Minimum keyframe interval
                        "-sc_threshold",
                        "0",  # Disable scene change detection for consistent keyframes
                        "-vf",
                        f"scale={preset['resolution'][0]}:{preset['resolution'][1]}:force_original_aspect_ratio=decrease:eval=frame,pad={preset['resolution'][0]}:{preset['resolution'][1]}:(ow-iw)/2:(oh-ih)/2:color=0x141E30",  # Scale image and pad with dark blue background
                        "-r",
                        "30",  # Set output frame rate
                        "-c:a",
                        "aac",
                        "-b:a",
                        preset["audio_bitrate"],
                        "-ar",
                        "44100",  # Standard sample rate - universal compatibility
                        "-ac",
                        "2",  # Stereo
                        "-pix_fmt",
                                "yuv420p",  # Universal pixel format - works everywhere
                                "-shortest",  # Match shortest input stream
                                "-f",
                                "mp4",  # Explicitly set container format
                        "-movflags",
                                "+faststart",  # Web optimization - moov atom at beginning
                        str(output_path),
                    ]
                )

            # Run FFmpeg with proper timeout and error handling using Popen for better control
            # Use a longer timeout for video encoding (audio duration + 5 minutes buffer)
            # Get audio duration using FFmpeg (safer than librosa which can crash)
            audio_duration = self._get_audio_duration_ffmpeg(audio_path)
            if audio_duration is not None:
                timeout_seconds = int(audio_duration * 2) + 300  # 2x audio duration + 5 min buffer
            else:
                timeout_seconds = 600  # 10 minutes default
            
            try:
                # Use Popen for better process control
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    errors='replace'
                )
                
                try:
                    stdout, stderr = process.communicate(timeout=timeout_seconds)
                    result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
                except subprocess.TimeoutExpired:
                    print(f"[ERROR] FFmpeg encoding timed out after {timeout_seconds}s")
                    self._cleanup_ffmpeg_process(process)
                    raise RuntimeError(f"FFmpeg encoding timed out after {timeout_seconds}s. File may be incomplete: {output_path}")
            except subprocess.TimeoutExpired:
                raise RuntimeError(f"FFmpeg encoding timed out after {timeout_seconds}s. File may be incomplete: {output_path}")
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                print(f"[ERROR] FFmpeg command failed:")
                print(f"  Exit code: {result.returncode}")
                print(f"  Command: {' '.join(str(x) for x in cmd)}")
                print(f"  STDOUT: {result.stdout[:1000] if result.stdout else '(empty)'}")
                print(f"  STDERR: {error_msg[:1000]}")
                raise RuntimeError(f"FFmpeg failed (exit code {result.returncode}): {error_msg[:500]}")
            
            # Verify the output file exists and is valid
            if not output_path.exists():
                raise RuntimeError(f"Output file was not created: {output_path}")
            
            # Check file size (should be > 0)
            if output_path.stat().st_size == 0:
                raise RuntimeError(f"Output file is empty: {output_path}")
            
            # Verify the file is a valid MP4 by checking for moov atom
            try:
                verify_cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(output_path)]
                verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, timeout=10)
                if verify_result.returncode != 0:
                    print(f"[WARN] File verification warning: {verify_result.stderr[:200]}")
            except Exception as e:
                print(f"[WARN] Could not verify file: {e}")
            
            print(f"[OK] Video file created successfully: {output_path} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)")
            return output_path

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode(errors='replace') if isinstance(e.stderr, bytes) else str(e.stderr)
            raise RuntimeError(f"FFmpeg failed: {error_msg}")
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")

    def _create_default_background(self) -> Path:
        """Create a default background image."""
        from PIL import Image, ImageDraw

        # Create a gradient background
        width, height = 1920, 1080
        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)

        # Create gradient
        for y in range(height):
            # Blue gradient
            r = int(20 + (y / height) * 20)
            g = int(30 + (y / height) * 40)
            b = int(48 + (y / height) * 80)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Save to cache
        bg_path = Path(self.config["storage"]["cache_dir"]) / "default_background.jpg"
        bg_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(bg_path), quality=95)

        return bg_path

    def _create_text_image(self, text: str, size: tuple) -> str:
        """Create an image with text overlay."""
        import tempfile

        from PIL import Image, ImageDraw, ImageFont

        # Create transparent image
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Try to use a nice font, fallback to default
        # Note: PIL requires a font object - it calls load_default internally if None is passed
        # So we must ensure at least load_default succeeds, or create a basic font object
        font = None
        try:
            font = ImageFont.truetype("arial.ttf", 60)  # type: ignore[assignment]
        except Exception:
            try:
                font = ImageFont.load_default()  # type: ignore[assignment]
            except Exception:
                # Last resort: PIL will try to load default internally when font=None
                # If that also fails, we'll let it raise - this is a system configuration issue
                pass

        # Get text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        _text_height = bbox[3] - bbox[1]  # Reserved for future vertical centering

        # Center text
        x = (size[0] - text_width) // 2
        y = 50

        # Draw text with shadow
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 180))  # Shadow
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))  # Text

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(temp_file.name)

        return temp_file.name

    def _compose_minimal_video(self, audio_path: Path, output_path: Path, quality: Optional[str] = None) -> Path:
        """Create minimal video (black frame + audio) - default audio-only mode."""
        preset = self.QUALITY_PRESETS.get(quality or "fastest", self.QUALITY_PRESETS["fastest"])
        
        # Validate audio file before processing
        is_valid, error_msg = self._validate_audio_file(audio_path)
        if not is_valid:
            error_details = (
                f"Audio file validation failed: {error_msg}\n"
                f"  This usually indicates:\n"
                f"  - The audio file was corrupted during generation\n"
                f"  - The audio file is empty or incomplete\n"
                f"  - The audio file format is invalid or unsupported\n"
                f"  - The file path is incorrect\n"
                f"  Troubleshooting steps:\n"
                f"  1. Check if the audio file exists and is readable\n"
                f"  2. Verify the file size is reasonable (not 0 bytes)\n"
                f"  3. Try regenerating the audio file\n"
                f"  4. Check the TTS/audio generation step for errors"
            )
            raise ValueError(error_details)
        
        try:
            from src.utils.gpu_utils import get_gpu_manager
            gpu_manager = get_gpu_manager()
            
            cmd = ["ffmpeg", "-y"]
            use_gpu = gpu_manager.gpu_available and self._check_nvenc()
            
            if use_gpu:
                cmd.extend([
                    "-f", "lavfi", "-i", f"color=c=black:s={preset['resolution'][0]}x{preset['resolution'][1]}:r=30:d=1",
                    "-stream_loop", "-1",  # Loop the color source
                    "-i", str(audio_path),
                    "-c:v", "h264_nvenc",
                    "-profile:v", "baseline",
                    "-level", "3.1",
                    "-preset", preset["preset"],
                    "-tune", "1",
                    "-rc", "vbr",
                    "-cq", preset["cq"],
                    "-b:v", "1M",  # Very low bitrate for black frame
                    "-g", "30",
                    "-keyint_min", "30",
                    "-sc_threshold", "0",
                    "-c:a", "aac",
                    "-b:a", preset["audio_bitrate"],
                    "-ar", "44100",
                    "-ac", "2",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    "-f", "mp4",
                    "-movflags", "+faststart",
                    str(output_path)
                ])
            else:
                cmd.extend([
                    "-f", "lavfi", "-i", f"color=c=black:s={preset['resolution'][0]}x{preset['resolution'][1]}:r=30:d=1",
                    "-stream_loop", "-1",
                    "-i", str(audio_path),
                    "-c:v", "libx264",
                    "-profile:v", "baseline",
                    "-level", "3.1",
                    "-preset", "faster",
                    "-tune", "stillimage",
                    "-crf", "28",  # High CRF for minimal quality black frame
                    "-g", "30",
                    "-keyint_min", "30",
                    "-sc_threshold", "0",
                    "-c:a", "aac",
                    "-b:a", preset["audio_bitrate"],
                    "-ar", "44100",
                    "-ac", "2",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    "-f", "mp4",
                    "-movflags", "+faststart",
                    str(output_path)
                ])
            
            # Use Popen with timeout for better cleanup
            # Get audio duration using FFmpeg (safer than librosa which can crash)
            audio_duration = self._get_audio_duration_ffmpeg(audio_path)
            if audio_duration is not None:
                timeout_seconds = int(audio_duration * 2) + 300
            else:
                timeout_seconds = 600
            
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    errors='replace'
                )
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
            except subprocess.TimeoutExpired:
                print(f"[ERROR] FFmpeg timed out after {timeout_seconds}s")
                self._cleanup_ffmpeg_process(process)
                raise RuntimeError(f"FFmpeg timed out after {timeout_seconds}s")
            
            if result.returncode != 0:
                # Analyze FFmpeg error to provide better diagnostics
                stderr_lower = result.stderr.lower() if result.stderr else ""
                error_analysis = []
                
                # Check for common corruption indicators
                if "illegal" in stderr_lower or "invalid" in stderr_lower:
                    error_analysis.append("Audio file appears corrupted or invalid")
                if "no such file" in stderr_lower or "cannot find" in stderr_lower:
                    error_analysis.append("Audio file not found or path is incorrect")
                if "end of file" in stderr_lower or "unexpected end" in stderr_lower:
                    error_analysis.append("Audio file is incomplete or truncated")
                if "codec" in stderr_lower and "not found" in stderr_lower:
                    error_analysis.append("Required audio codec not available")
                
                # Build detailed error message
                error_msg_parts = [
                    f"FFmpeg failed to create minimal video (exit code {result.returncode})"
                ]
                
                if error_analysis:
                    error_msg_parts.append("  Detected issues:")
                    for issue in error_analysis:
                        error_msg_parts.append(f"    - {issue}")
                
                error_msg_parts.extend([
                    f"  Audio file: {audio_path}",
                    f"  File size: {audio_path.stat().st_size if audio_path.exists() else 'N/A'} bytes",
                    f"  FFmpeg stderr (last 500 chars):",
                    f"    {result.stderr[-500:] if result.stderr else '(empty)'}",
                    "",
                    "  Troubleshooting:",
                    "  1. Verify the audio file is valid and not corrupted",
                    "  2. Check if the audio file was generated correctly",
                    "  3. Try regenerating the audio file",
                    "  4. Verify FFmpeg can read the audio file format",
                    "  5. Check disk space and file permissions"
                ])
                
                raise RuntimeError("\n".join(error_msg_parts))
            
            return output_path
        except ValueError as e:
            # Re-raise validation errors as-is (they already have good messages)
            raise
        except RuntimeError as e:
            # Re-raise RuntimeErrors as-is (they're already detailed)
            raise
        except Exception as e:
            # Wrap other exceptions with context
            error_details = (
                f"Failed to create minimal video: {str(e)}\n"
                f"  Audio file: {audio_path}\n"
                f"  Output path: {output_path}\n"
                f"  Error type: {type(e).__name__}\n"
                f"  This may indicate:\n"
                f"  - Audio file corruption or invalid format\n"
                f"  - FFmpeg installation or configuration issue\n"
                f"  - Insufficient disk space or permissions\n"
                f"  - System resource limitations"
            )
            raise RuntimeError(error_details) from e
    
    def _compose_visualization_only(self, audio_path: Path, output_path: Path, quality: Optional[str] = None) -> Path:
        """Compose visualization video without background (pure visualization)."""
        from .audio_visualizer import AudioVisualizer
        
        visualizer = AudioVisualizer(self.config)
        return visualizer.generate_visualization(audio_path, output_path)
    
    def _compose_visualization_with_background(self, audio_path: Path, bg_path: Path, output_path: Path, quality: Optional[str] = None) -> Path:
        """Compose visualization video with background image base."""
        from .audio_visualizer import AudioVisualizer
        from src.utils.gpu_utils import get_gpu_manager
        import tempfile
        
        # Generate visualization video first
        visualizer = AudioVisualizer(self.config)
        temp_viz_path = Path(tempfile.mktemp(suffix=".mp4"))
        
        try:
            # Generate visualization frames and create temp video
            visualizer.generate_visualization(audio_path, temp_viz_path)
            
            # Now overlay visualization on background using FFmpeg
            preset = self.QUALITY_PRESETS.get(quality or "fastest", self.QUALITY_PRESETS["fastest"])
            
            # Check GPU availability and NVENC support
            gpu_manager = get_gpu_manager()
            use_nvenc = gpu_manager.gpu_available and self._check_nvenc()
            
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(bg_path),  # Background image
                "-i", str(temp_viz_path),  # Visualization video
                "-filter_complex",
                f"[0:v]scale={preset['resolution'][0]}:{preset['resolution'][1]}:force_original_aspect_ratio=decrease:eval=frame,pad={preset['resolution'][0]}:{preset['resolution'][1]}:(ow-iw)/2:(oh-ih)/2:color=0x141E30[bg];"
                f"[1:v]scale={preset['resolution'][0]}:{preset['resolution'][1]}[viz];"
                f"[bg][viz]blend=all_mode=screen:all_opacity=0.7[out]",  # Blend visualization over background
                "-map", "[out]",
                "-map", "1:a",  # Audio from visualization video
            ]
            
            if use_nvenc:
                print("[GPU] Using NVENC for visualization+background encoding")
                cmd.extend([
                    "-c:v", "h264_nvenc",
                    "-profile:v", "baseline",
                    "-level", "3.1",
                    "-preset", preset["preset"],
                    "-tune", "1",  # NVENC tune: 1=hq (high quality)
                    "-rc", "vbr",
                    "-cq", preset["cq"],
                    "-b:v", preset["bitrate"],
                    "-maxrate", preset["maxrate"],
                    "-bufsize", preset["bufsize"],
                    "-g", "30",
                    "-keyint_min", "30",
                    "-sc_threshold", "0",
                ])
            else:
                print("[CPU] Using libx264 for visualization+background encoding")
                cmd.extend([
                    "-c:v", "libx264",
                    "-profile:v", "baseline",
                    "-level", "3.1",
                    "-preset", "faster",
                    "-tune", "stillimage",
                    "-crf", "23",
                    "-g", "30",
                    "-keyint_min", "30",
                    "-sc_threshold", "0",
                ])
            
            cmd.extend([
                "-c:a", "aac",
                "-b:a", preset["audio_bitrate"],
                "-ar", "44100",
                "-ac", "2",
                "-pix_fmt", "yuv420p",
                "-shortest",
                "-f", "mp4",
                "-movflags", "+faststart",
                "-r", "30",
                str(output_path)
            ])
            
            # Use Popen with timeout for better cleanup
            # Get audio duration using FFmpeg (safer than librosa which can crash)
            audio_duration = self._get_audio_duration_ffmpeg(audio_path)
            if audio_duration is not None:
                timeout_seconds = int(audio_duration * 2) + 300
            else:
                timeout_seconds = 600
            
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    errors='replace'
                )
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
            except subprocess.TimeoutExpired:
                print(f"[ERROR] FFmpeg timed out after {timeout_seconds}s")
                self._cleanup_ffmpeg_process(process)
                raise RuntimeError(f"FFmpeg timed out after {timeout_seconds}s")
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to combine visualization with background: {result.stderr[:500]}")
            
            return output_path
        finally:
            if temp_viz_path.exists():
                temp_viz_path.unlink(missing_ok=True)
    
    def _check_nvenc(self) -> bool:
        """Check if NVENC is available."""
        try:
            result = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True)
            return "h264_nvenc" in result.stdout
        except:
            return False
    
    def _overlay_visualization_on_avatar(self, avatar_video: Path, audio_path: Path, output_path: Path, quality: Optional[str] = None) -> Path:
        """Overlay visualization at bottom of avatar video using FFmpeg."""
        try:
            import subprocess

            from .audio_visualizer import AudioVisualizer

            print("[COMPOSE] Overlaying visualization on avatar video...")

            # Generate visualization video first
            temp_viz_path = output_path.parent / f"temp_viz_{output_path.stem}.mp4"
            visualizer = AudioVisualizer(self.config)
            visualizer.generate_visualization(audio_path, temp_viz_path)

            # Use FFmpeg to overlay avatar on top of visualization
            # Avatar in center-top, visualization stays at bottom
            # Try GPU encoding first, fallback to CPU
            from src.utils.gpu_utils import get_gpu_manager
            
            gpu_manager = get_gpu_manager()
            ffmpeg_cmd = [
                "ffmpeg",
                "-i",
                str(temp_viz_path),  # Background (visualization)
                "-i",
                str(avatar_video),  # Overlay (avatar)
                "-filter_complex",
                "[1:v]scale=960:720[avatar];"  # Scale avatar to 960x720
                + "[0:v][avatar]overlay=(W-w)/2:50",  # Center avatar, 50px from top
            ]
            
            # Use GPU encoding if available
            if gpu_manager.gpu_available:
                try:
                    # Check if NVENC is available
                    check_cmd = ["ffmpeg", "-hide_banner", "-encoders"]
                    check_result = subprocess.run(check_cmd, capture_output=True, text=True)
                    if "h264_nvenc" in check_result.stdout:
                        print("[GPU] Using GPU-accelerated encoding for avatar overlay")
                        # Note: filter_complex runs on CPU, then we encode with GPU
                        preset = self.QUALITY_PRESETS.get(quality or "fastest", self.QUALITY_PRESETS["fastest"])
                        ffmpeg_cmd.extend([
                            "-c:v", "h264_nvenc",
                            "-profile:v", "baseline",
                            "-level", "3.1",
                            "-preset", preset["preset"],
                            "-tune", "1",  # NVENC tune: 1=hq (not "hq" string)
                            "-rc", "vbr",
                            "-cq", preset["cq"],
                            "-b:v", preset["bitrate"],
                            "-maxrate", preset["maxrate"],
                            "-bufsize", preset["bufsize"],
                            "-g", "30",
                            "-keyint_min", "30",
                            "-sc_threshold", "0",
                            "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart",
                        ])
                    else:
                        raise Exception("NVENC not available")
                except Exception:
                    # Fallback to CPU encoding
                    ffmpeg_cmd.extend([
                        "-c:v", "libx264",
                        "-preset", "medium",
                        "-pix_fmt", "yuv420p",
                    ])
            else:
                # CPU encoding
                ffmpeg_cmd.extend([
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-pix_fmt", "yuv420p",
                ])
            
            ffmpeg_cmd.extend([
                "-c:a", "copy",
                str(output_path),
                "-y",
            ])

            # Use Popen with timeout for better cleanup
            # Get audio duration using FFmpeg (safer than librosa which can crash)
            audio_duration = self._get_audio_duration_ffmpeg(audio_path)
            if audio_duration is not None:
                timeout_seconds = int(audio_duration * 2) + 300
            else:
                timeout_seconds = 600
            
            try:
                process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    errors='replace'
                )
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                result = subprocess.CompletedProcess(ffmpeg_cmd, process.returncode, stdout, stderr)
            except subprocess.TimeoutExpired:
                print(f"[ERROR] FFmpeg overlay timed out after {timeout_seconds}s")
                self._cleanup_ffmpeg_process(process)
                raise Exception(f"FFmpeg overlay timed out after {timeout_seconds}s")

            if result.returncode == 0:
                # Cleanup temp file
                temp_viz_path.unlink(missing_ok=True)
                print(f"[OK] Combined video created: {output_path}")
                return output_path
            else:
                print(f"[WARN] FFmpeg overlay failed: {result.stderr[:200]}")
                raise Exception("FFmpeg failed")

        except Exception as e:
            print(f"[WARN] Overlay failed: {e}")
            print("  Using visualization only (avatar fallback)")
            # Fallback: use visualization video
            try:
                if temp_viz_path.exists():
                    import shutil

                    shutil.copy(temp_viz_path, output_path)
                    temp_viz_path.unlink(missing_ok=True)
                else:
                    # Regenerate visualization
                    from .audio_visualizer import AudioVisualizer

                    visualizer = AudioVisualizer(self.config)
                    visualizer.generate_visualization(audio_path, output_path)
                return output_path
            except Exception:
                # Last resort: copy avatar
                import shutil

                shutil.copy(avatar_video, output_path)
                return output_path
    
    def _compose_avatar_background_visualization(self, avatar_video: Path, audio_path: Path, background_path: Path, output_path: Path, quality: Optional[str] = None) -> Path:
        """Compose video with avatar (lip-sync), background image, and visualization overlay."""
        try:
            import subprocess
            from src.utils.gpu_utils import get_gpu_manager
            
            print("[VIDEO] Composing avatar + background + visualization...")
            
            # Generate visualization video first
            from .audio_visualizer import AudioVisualizer
            temp_viz_path = output_path.parent / f"temp_viz_{output_path.stem}.mp4"
            visualizer = AudioVisualizer(self.config)
            visualizer.generate_visualization(audio_path, temp_viz_path)
            
            gpu_manager = get_gpu_manager()
            preset = self.QUALITY_PRESETS.get(quality or "fastest", self.QUALITY_PRESETS["fastest"])
            
            # Verify avatar video exists and is valid before using it
            if not avatar_video.exists():
                raise FileNotFoundError(f"Avatar video not found: {avatar_video}")
            if avatar_video.stat().st_size == 0:
                raise ValueError(f"Avatar video is empty: {avatar_video}")
            
            print(f"[DEBUG] Using avatar video: {avatar_video} ({avatar_video.stat().st_size / 1024:.1f} KB)")
            print(f"[DEBUG] Background: {background_path}")
            print(f"[DEBUG] Visualization: {temp_viz_path}")
            print(f"[DEBUG] Audio: {audio_path}")
            
            # Get avatar video dimensions to calculate proper scaling
            # Avatar video is typically 1024x640 (wider than tall), so we need to ensure it fits without cropping
            try:
                import subprocess
                probe_result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-select_streams', 'v:0', 
                     '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', str(avatar_video)],
                    capture_output=True, text=True, timeout=5
                )
                if probe_result.returncode == 0:
                    avatar_dims = probe_result.stdout.strip().split('x')
                    if len(avatar_dims) == 2:
                        avatar_width = int(avatar_dims[0])
                        avatar_height = int(avatar_dims[1])
                        avatar_aspect = avatar_width / avatar_height
                        print(f"[DEBUG] Avatar video dimensions: {avatar_width}x{avatar_height} (aspect: {avatar_aspect:.2f})")
                    else:
                        avatar_width, avatar_height = 1024, 640  # Default fallback
                        avatar_aspect = avatar_width / avatar_height
                else:
                    avatar_width, avatar_height = 1024, 640  # Default fallback
                    avatar_aspect = avatar_width / avatar_height
            except Exception:
                avatar_width, avatar_height = 1024, 640  # Default fallback
                avatar_aspect = avatar_width / avatar_height
            
            # Calculate avatar canvas size - ensure it's large enough to fit the avatar without cropping
            # Scale based on output resolution but ensure avatar fits fully
            output_aspect = preset['resolution'][0] / preset['resolution'][1]
            
            # If avatar is wider than output, scale by width; if taller, scale by height
            if avatar_aspect > output_aspect:
                # Avatar is wider - scale by width, ensure height fits
                avatar_scale_width = min(1280, preset['resolution'][0])
                avatar_scale_height = int(avatar_scale_width / avatar_aspect)
            else:
                # Avatar is taller - scale by height, ensure width fits
                avatar_scale_height = min(960, preset['resolution'][1])
                avatar_scale_width = int(avatar_scale_height * avatar_aspect)
            
            # Ensure even dimensions for video encoding
            avatar_scale_width = (avatar_scale_width // 2) * 2
            avatar_scale_height = (avatar_scale_height // 2) * 2
            
            print(f"[DEBUG] Avatar scaling: {avatar_scale_width}x{avatar_scale_height} (preserves {avatar_width}x{avatar_height} aspect ratio)")
            
            # FFmpeg filter: background (scaled) + visualization (position-based) + avatar (center-top)
            # IMPORTANT: The avatar video (Wav2Lip output) already contains lip-synced audio
            # We should use the avatar's audio, NOT the separate audio_path, to preserve lip-sync
            # Layers: background (bottom) -> visualization (position-based) -> avatar (top)
            
            # Get waveform position from config to determine where to place visualization
            viz_config = self.config.get("visualization", {})
            waveform_config = viz_config.get("waveform", {})
            position = waveform_config.get("position", "bottom")
            height_percent = waveform_config.get("height_percent", 25)
            width_percent = waveform_config.get("width_percent", 25)
            
            # Parse position to get primary position
            positions = [p.strip() for p in str(position).split(",")]
            primary_position = positions[0] if positions else "bottom"
            
            # Calculate crop and overlay positions based on waveform position
            output_height = preset['resolution'][1]
            output_width = preset['resolution'][0]
            
            # Determine if horizontal or vertical waveform
            is_vertical = primary_position in ["left", "right"]
            
            if is_vertical:
                # Vertical waveform - crop width and position horizontally
                crop_width = int(output_width * (width_percent / 100))
                if primary_position == "left":
                    crop_x = 0
                    overlay_x = 0
                else:  # right
                    crop_x = output_width - crop_width
                    overlay_x = output_width - crop_width
                # Full height for vertical
                crop_height = output_height
                crop_y = 0
                overlay_y = 0
            else:
                # Horizontal waveform - crop height and position vertically
                crop_height = int(output_height * (height_percent / 100))
                if primary_position == "top":
                    crop_y = 0
                    overlay_y = 0
                elif primary_position == "middle":
                    crop_y = (output_height - crop_height) // 2
                    overlay_y = crop_y
                else:  # bottom (default)
                    crop_y = output_height - crop_height
                    overlay_y = output_height - crop_height
                # Full width for horizontal
                crop_width = output_width
                crop_x = 0
                overlay_x = 0
            
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(background_path),  # Background image (input 0)
                "-i", str(temp_viz_path),  # Visualization video (input 1) - no audio
                "-i", str(avatar_video),  # Avatar video (input 2) - THIS IS THE LIP-SYNC VIDEO WITH AUDIO
                "-filter_complex",
                f"[0:v]scale={preset['resolution'][0]}:{preset['resolution'][1]}:force_original_aspect_ratio=decrease,pad={preset['resolution'][0]}:{preset['resolution'][1]}:(ow-iw)/2:(oh-ih)/2:color=0x141E30[bg];"  # Scale and pad background
                + f"[1:v]scale={preset['resolution'][0]}:{preset['resolution'][1]}[viz_full];"  # Scale visualization to full resolution
                + f"[viz_full]crop={crop_width}:{crop_height}:{crop_x}:{crop_y}[viz_cropped];"  # Crop visualization to position-specific region
                + f"[viz_cropped]chromakey=color=0x000000:similarity=0.05:blend=0.0[viz_transparent];"  # Make black transparent via chromakey (similarity=0.05 to preserve bright green, blend=0.0 for no fade)
                + f"[2:v]scale={avatar_scale_width}:{avatar_scale_height}:force_original_aspect_ratio=decrease[avatar_scaled];"  # Scale avatar preserving aspect ratio (no cropping)
                + f"[avatar_scaled]pad={avatar_scale_width}:{avatar_scale_height}:(ow-iw)/2:(oh-ih)/2:color=black[avatar];"  # Pad to exact size if needed, centered
                + f"[bg][avatar]overlay=(W-w)/2:(H-h)/2[bg_avatar];"  # Overlay avatar on background first
                + f"[bg_avatar][viz_transparent]overlay={overlay_x}:{overlay_y}[vout_raw];"  # Overlay transparent visualization
                + f"[vout_raw]eq=saturation=1.3[vout]",  # Boost saturation to preserve waveform vibrancy after overlay (1.3 = 30% boost)
                "-map", "[vout]",  # Use the overlay output directly (already at target resolution)
                "-map", "2:a",  # Use audio from avatar video (input 2) - THIS PRESERVES LIP-SYNC!
            ]
            
            print(f"[DEBUG] Waveform position: {position} (primary: {primary_position})")
            print(f"[DEBUG] Crop: {crop_width}x{crop_height} at ({crop_x}, {crop_y})")
            print(f"[DEBUG] Overlay: ({overlay_x}, {overlay_y})")
            print(f"[DEBUG] FFmpeg command includes avatar video as input 2")
            print(f"[DEBUG] Avatar video path: {avatar_video}")
            print(f"[DEBUG] Avatar video exists: {avatar_video.exists()}")
            print(f"[DEBUG] Background path: {background_path}")
            print(f"[DEBUG] Visualization path: {temp_viz_path}")
            
            # Add encoding parameters
            # Note: Don't use -s with filter_complex as it conflicts - the filter_complex output [vout] is already at target resolution
            ffmpeg_cmd.extend([
                "-shortest",  # Match shortest input duration
                "-r", "30",  # Set frame rate
            ])
            
            # Try GPU encoding first (NVENC), fallback to CPU if needed
            # Using temp file approach instead of pipes to avoid hanging issues
            use_gpu_encoding = False
            if gpu_manager.gpu_available and self._check_nvenc():
                try:
                    print("[GPU] Attempting GPU-accelerated encoding (NVENC) for final composition...")
                    use_gpu_encoding = True
                except Exception as e:
                    print(f"[WARN] GPU encoding setup failed: {e}, falling back to CPU")
                    use_gpu_encoding = False
            
            if use_gpu_encoding:
                # GPU encoding with NVENC (direct - filter_complex output can go to NVENC)
                print("[GPU] Using NVENC for final composition")
                ffmpeg_cmd.extend([
                    "-c:v", "h264_nvenc",
                    "-preset", preset["preset"],
                    "-rc", "vbr",
                    "-cq", preset["cq"],
                    "-b:v", preset["bitrate"],
                    "-maxrate", preset["maxrate"],
                    "-bufsize", preset["bufsize"],
                    "-g", "30",
                    "-keyint_min", "30",
                    "-sc_threshold", "0",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", preset["audio_bitrate"],
                    "-ar", "44100",
                    "-ac", "2",
                    "-f", "mp4",
                    "-movflags", "+faststart",
                    str(output_path),
                ])
                
                # Start file monitoring for progress indication
                from src.utils.file_monitor import FileMonitor
                monitor = FileMonitor(
                    output_path,
                    update_callback=lambda size, rate, warning: print(f"  [PROGRESS] File size: {size:.1f} MB, rate: {rate:.2f} MB/s{warning}", end='\r'),
                    check_interval=2.0
                )
                monitor.start()
                self.last_file_monitor = monitor  # Store for metrics
                
                try:
                    # Use Popen instead of run() to avoid buffering all output in memory
                    process = subprocess.Popen(
                        ffmpeg_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        errors='replace'
                    )
                    
                    # Process stderr in real-time to catch errors immediately
                    stderr_lines = []
                    stderr_thread_running = True
                    
                    def read_stderr():
                        nonlocal stderr_lines, stderr_thread_running
                        try:
                            for line in process.stderr:
                                stderr_lines.append(line)
                                if len(stderr_lines) > 200:  # Keep last 200 lines
                                    stderr_lines.pop(0)
                                # Check for critical errors
                                if "error" in line.lower() or "failed" in line.lower():
                                    print(f"[FFmpeg Error] {line.strip()}")
                        except Exception as e:
                            # Only print error if it's not just "closed file"
                            if "closed file" not in str(e).lower():
                                print(f"[ERROR] Error reading FFmpeg stderr: {e}")
                        finally:
                            stderr_thread_running = False
                    
                    import threading
                    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                    stderr_thread.start()
                    
                    # Calculate timeout based on audio duration
                    # Get audio duration using FFmpeg (safer than librosa which can crash)
                    audio_duration = self._get_audio_duration_ffmpeg(audio_path)
                    if audio_duration is not None:
                        timeout_seconds = int(audio_duration * 2) + 300
                    else:
                        timeout_seconds = 600
                    
                    # Wait for process to complete with timeout
                    try:
                        stdout, remaining_stderr = process.communicate(timeout=timeout_seconds)
                        # Wait for stderr thread to finish
                        import time
                        timeout_count = 0
                        while stderr_thread_running and timeout_count < 10:
                            time.sleep(0.1)
                            timeout_count += 1
                        stderr_text = ''.join(stderr_lines) + (remaining_stderr if remaining_stderr else "")
                        result = subprocess.CompletedProcess(ffmpeg_cmd, process.returncode, stdout, stderr_text)
                        
                        if result.returncode != 0:
                            print(f"[ERROR] FFmpeg GPU encoding failed with return code {result.returncode}")
                            print(f"[ERROR] FFmpeg stderr (last 1000 chars): {result.stderr[-1000:] if result.stderr else 'No stderr'}")
                            print(f"[ERROR] Full command: {' '.join(ffmpeg_cmd)}")
                            raise RuntimeError(f"FFmpeg GPU encoding failed: {result.stderr[-500:] if result.stderr else 'Unknown error'}")
                        else:
                            print(f"[OK] GPU encoding successful - avatar video included in output")
                            print(f"[OK] Final composition created: {output_path}")
                            # Verify output exists and has content
                            if output_path.exists() and output_path.stat().st_size > 0:
                                print(f"[OK] Output verified: {output_path.stat().st_size / 1024:.1f} KB")
                            else:
                                raise RuntimeError(f"Output file missing or empty: {output_path}")
                    except subprocess.TimeoutExpired:
                        print(f"[ERROR] FFmpeg GPU encoding timed out after {timeout_seconds}s")
                        self._cleanup_ffmpeg_process(process)
                        raise RuntimeError(f"FFmpeg GPU encoding timed out after {timeout_seconds}s")
                finally:
                    monitor.stop()
                    print()  # New line after progress updates
                
                if result.returncode == 0:
                    temp_viz_path.unlink(missing_ok=True)
                    print(f"[OK] Full composition created: {output_path}")
                    return output_path
                else:
                    error_msg = result.stderr[-1000:] if result.stderr else "Unknown error"
                    print(f"[ERROR] FFmpeg failed with return code {result.returncode}")
                    print(f"[ERROR] Error: {error_msg}")
                    raise RuntimeError(f"FFmpeg failed with return code {result.returncode}: {error_msg[-500:]}")
            else:
                # Fallback to CPU encoding (single-pass, simpler)
                print("[CPU] Using libx264 for final composition")
                ffmpeg_cmd.extend([
                    "-c:v", "libx264",
                    "-profile:v", "baseline",
                    "-level", "3.1",
                    "-preset", "medium",
                    "-crf", "23",
                    "-g", "30",
                    "-keyint_min", "30",
                    "-sc_threshold", "0",
                    "-pix_fmt", "yuv420p",
                ])
                
                ffmpeg_cmd.extend([
                    "-c:a", "aac",
                    "-b:a", preset["audio_bitrate"],
                    "-ar", "44100",
                    "-ac", "2",
                    "-f", "mp4",
                    "-movflags", "+faststart",
                    str(output_path),
                ])
                
                # Start file monitoring for progress indication
                from src.utils.file_monitor import FileMonitor
                monitor = FileMonitor(
                    output_path,
                    update_callback=lambda size, rate, warning: print(f"  [PROGRESS] File size: {size:.1f} MB, rate: {rate:.2f} MB/s{warning}", end='\r'),
                    check_interval=2.0
                )
                monitor.start()
                self.last_file_monitor = monitor  # Store for metrics
                
                try:
                    # Use Popen instead of run() to avoid buffering all output in memory
                    process = subprocess.Popen(
                        ffmpeg_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        errors='replace'
                    )
                    
                    # Process stderr in real-time to catch errors immediately
                    stderr_lines = []
                    stderr_thread_running = True
                    
                    def read_stderr():
                        nonlocal stderr_lines, stderr_thread_running
                        try:
                            for line in process.stderr:
                                stderr_lines.append(line)
                                if len(stderr_lines) > 200:  # Keep last 200 lines
                                    stderr_lines.pop(0)
                                # Check for critical errors
                                if "error" in line.lower() or "failed" in line.lower():
                                    print(f"[FFmpeg Error] {line.strip()}")
                        except Exception as e:
                            # Only print error if it's not just "closed file"
                            if "closed file" not in str(e).lower():
                                print(f"[ERROR] Error reading FFmpeg stderr: {e}")
                        finally:
                            stderr_thread_running = False
                    
                    import threading
                    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                    stderr_thread.start()
                    
                    # Calculate timeout based on audio duration
                    # Get audio duration using FFmpeg (safer than librosa which can crash)
                    audio_duration = self._get_audio_duration_ffmpeg(audio_path)
                    if audio_duration is not None:
                        timeout_seconds = int(audio_duration * 2) + 300
                    else:
                        timeout_seconds = 600
                    
                    # Wait for process to complete with timeout
                    try:
                        stdout, remaining_stderr = process.communicate(timeout=timeout_seconds)
                        # Wait for stderr thread to finish
                        import time
                        timeout_count = 0
                        while stderr_thread_running and timeout_count < 10:
                            time.sleep(0.1)
                            timeout_count += 1
                        stderr_text = ''.join(stderr_lines) + (remaining_stderr if remaining_stderr else "")
                        result = subprocess.CompletedProcess(ffmpeg_cmd, process.returncode, stdout, stderr_text)
                        
                        if result.returncode != 0:
                            print(f"[ERROR] FFmpeg CPU encoding failed with return code {result.returncode}")
                            print(f"[ERROR] FFmpeg stderr (last 1000 chars): {result.stderr[-1000:] if result.stderr else 'No stderr'}")
                            print(f"[ERROR] Full command: {' '.join(ffmpeg_cmd)}")
                            raise RuntimeError(f"FFmpeg CPU encoding failed: {result.stderr[-500:] if result.stderr else 'Unknown error'}")
                        else:
                            print(f"[OK] CPU encoding successful - avatar video included in output")
                            print(f"[OK] Final composition created: {output_path}")
                            # Verify output exists and has content
                            if output_path.exists() and output_path.stat().st_size > 0:
                                print(f"[OK] Output verified: {output_path.stat().st_size / 1024:.1f} KB")
                            else:
                                raise RuntimeError(f"Output file missing or empty: {output_path}")
                    except subprocess.TimeoutExpired:
                        print(f"[ERROR] FFmpeg CPU encoding timed out after {timeout_seconds}s")
                        self._cleanup_ffmpeg_process(process)
                        raise RuntimeError(f"FFmpeg CPU encoding timed out after {timeout_seconds}s")
                finally:
                    monitor.stop()
                    print()  # New line after progress updates
                
                if result.returncode == 0:
                    temp_viz_path.unlink(missing_ok=True)
                    print(f"[OK] Full composition created: {output_path}")
                    return output_path
                else:
                    error_msg = result.stderr[-1000:] if result.stderr else "Unknown error"
                    print(f"[ERROR] FFmpeg failed with return code {result.returncode}")
                    print(f"[ERROR] Error: {error_msg}")
                    raise RuntimeError(f"FFmpeg failed with return code {result.returncode}: {error_msg[-500:]}")
                
        except Exception as e:
            print(f"[WARN] Full composition failed: {e}")
            # Fallback: try avatar + background only
            try:
                return self._compose_avatar_with_background(avatar_video, audio_path, background_path, output_path, quality=quality)
            except Exception:
                # Last resort: just avatar
                import shutil
                shutil.copy(avatar_video, output_path)
                return output_path
    
    def _compose_avatar_with_background(self, avatar_video: Path, audio_path: Path, background_path: Path, output_path: Path, quality: Optional[str] = None) -> Path:
        """Compose video with avatar (lip-sync) and background image."""
        try:
            import subprocess
            from src.utils.gpu_utils import get_gpu_manager
            
            print("[VIDEO] Composing avatar + background...")
            
            gpu_manager = get_gpu_manager()
            preset = self.QUALITY_PRESETS.get(quality or "fastest", self.QUALITY_PRESETS["fastest"])
            
            # Get avatar dimensions for proper scaling
            try:
                import subprocess as sp
                probe_result = sp.run(
                    ['ffprobe', '-v', 'error', '-select_streams', 'v:0', 
                     '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', str(avatar_video)],
                    capture_output=True, text=True, timeout=5
                )
                if probe_result.returncode == 0:
                    avatar_dims = probe_result.stdout.strip().split('x')
                    if len(avatar_dims) == 2:
                        avatar_width = int(avatar_dims[0])
                        avatar_height = int(avatar_dims[1])
                        avatar_aspect = avatar_width / avatar_height
                        # Scale to fit within canvas while preserving aspect ratio
                        if avatar_aspect > (preset['resolution'][0] / preset['resolution'][1]):
                            avatar_scale_width = preset['resolution'][0]
                            avatar_scale_height = int(preset['resolution'][0] / avatar_aspect)
                        else:
                            avatar_scale_height = preset['resolution'][1]
                            avatar_scale_width = int(preset['resolution'][1] * avatar_aspect)
                        # Ensure even dimensions
                        avatar_scale_width = (avatar_scale_width // 2) * 2
                        avatar_scale_height = (avatar_scale_height // 2) * 2
                    else:
                        avatar_scale_width, avatar_scale_height = 768, 480
                else:
                    avatar_scale_width, avatar_scale_height = 768, 480
            except Exception:
                avatar_scale_width, avatar_scale_height = 768, 480
            
            print(f"[DEBUG] Avatar scaling for background overlay: {avatar_scale_width}x{avatar_scale_height}")
            
            # FFmpeg filter: background (scaled) + avatar (centered)
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(background_path),  # Background image (input 0)
                "-i", str(avatar_video),  # Avatar video (input 1) - LIP-SYNC VIDEO WITH AUDIO
                "-i", str(audio_path),  # Audio (input 2) - but we'll use avatar's audio instead
                "-filter_complex",
                f"[0:v]scale={preset['resolution'][0]}:{preset['resolution'][1]}:force_original_aspect_ratio=decrease,pad={preset['resolution'][0]}:{preset['resolution'][1]}:(ow-iw)/2:(oh-ih)/2:color=0x141E30[bg];"  # Scale and pad background
                + f"[1:v]scale={avatar_scale_width}:{avatar_scale_height}:force_original_aspect_ratio=decrease[avatar_scaled];"  # Scale avatar preserving aspect ratio
                + f"[avatar_scaled]pad={avatar_scale_width}:{avatar_scale_height}:(ow-iw)/2:(oh-ih)/2:color=black[avatar];"  # Pad avatar to exact size
                + f"[bg][avatar]overlay=(W-w)/2:(H-h)/2[vout]",  # Overlay avatar centered on background
                "-map", "[vout]",  # Use the overlay output
                "-map", "1:a",  # Use audio from avatar video (input 1) - preserves lip-sync!
            ]
            
            # Add encoding parameters - must set video size explicitly for NVENC
            ffmpeg_cmd.extend([
                "-shortest",  # Match shortest input duration
                "-s", f"{preset['resolution'][0]}x{preset['resolution'][1]}",  # Explicitly set output size
                "-r", "30",  # Set frame rate
            ])
            
            # Try GPU encoding first (NVENC), fallback to CPU if needed
            use_gpu_encoding = False
            if gpu_manager.gpu_available and self._check_nvenc():
                try:
                    print("[GPU] Attempting GPU-accelerated encoding (NVENC) for avatar+background composition...")
                    ffmpeg_cmd.extend([
                        "-c:v", "h264_nvenc",
                        "-profile:v", "baseline",
                        "-level", "3.1",
                        "-preset", preset["preset"],
                        "-tune", "1",
                        "-rc", "vbr",
                        "-cq", preset["cq"],
                        "-b:v", preset["bitrate"],
                        "-maxrate", preset["maxrate"],
                        "-bufsize", preset["bufsize"],
                        "-g", "30",
                        "-keyint_min", "30",
                        "-sc_threshold", "0",
                        "-pix_fmt", "yuv420p",
                    ])
                    use_gpu_encoding = True
                except Exception as e:
                    print(f"[WARN] GPU encoding setup failed: {e}, falling back to CPU")
                    use_gpu_encoding = False
            
            if not use_gpu_encoding:
                # Fallback to CPU encoding
                print("[CPU] Using libx264 for avatar+background composition (GPU used for avatar generation)")
                ffmpeg_cmd.extend([
                    "-c:v", "libx264",
                    "-profile:v", "baseline",
                    "-level", "3.1",
                    "-preset", "medium",
                    "-crf", "23",
                    "-g", "30",
                    "-keyint_min", "30",
                    "-sc_threshold", "0",
                    "-pix_fmt", "yuv420p",
                ])
            
            ffmpeg_cmd.extend([
                "-c:a", "aac",
                "-b:a", preset["audio_bitrate"],
                "-ar", "44100",
                "-ac", "2",
                "-f", "mp4",
                "-movflags", "+faststart",
                str(output_path),
            ])
            
            # Monitor file growth for progress indication
            from src.utils.file_monitor import FileMonitor
            monitor = FileMonitor(
                output_path,
                update_callback=lambda size, rate, warning: print(f"  [PROGRESS] File size: {size:.1f} MB, rate: {rate:.2f} MB/s{warning}", end='\r'),
                check_interval=2.0
            )
            monitor.start()
            self.last_file_monitor = monitor  # Store for metrics
            
            try:
                # Use Popen instead of run() to avoid buffering all output in memory
                process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    errors='replace'
                )
                
                # Process stderr in real-time to catch errors immediately
                stderr_lines = []
                stderr_thread_running = True
                
                def read_stderr():
                    nonlocal stderr_lines, stderr_thread_running
                    try:
                        for line in process.stderr:
                            stderr_lines.append(line)
                            if len(stderr_lines) > 200:  # Keep last 200 lines
                                stderr_lines.pop(0)
                            # Check for critical errors
                            if "error" in line.lower() or "failed" in line.lower():
                                print(f"[FFmpeg Error] {line.strip()}")
                    except Exception:
                        pass
                    finally:
                        stderr_thread_running = False
                
                import threading
                stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                stderr_thread.start()
                
                stdout, remaining_stderr = process.communicate(timeout=600)
                stderr_text = ''.join(stderr_lines) + (remaining_stderr if remaining_stderr else "")
                
            except subprocess.TimeoutExpired:
                print(f"[ERROR] FFmpeg timed out after 600s")
                self._cleanup_ffmpeg_process(process)
                raise RuntimeError("FFmpeg composition timed out")
            except Exception as e:
                print(f"[ERROR] FFmpeg composition error: {e}")
                self._cleanup_ffmpeg_process(process)
                raise
            finally:
                monitor.stop()
                print()  # New line after progress updates
            
            if process.returncode == 0:
                print(f"[OK] Avatar+background composition created: {output_path}")
                return output_path
            else:
                # Show full error for debugging
                print(f"[ERROR] FFmpeg composition failed with return code {process.returncode}")
                print(f"[ERROR] FFmpeg stderr (last 500 chars): {stderr_text[-500:]}")
                print(f"[ERROR] FFmpeg command: {' '.join(ffmpeg_cmd[:10])}...")
                error_msg = stderr_text if stderr_text else (stdout if stdout else "Unknown error")
                print(f"[ERROR] FFmpeg composition failed (code {process.returncode}):")
                print(f"Command: {' '.join(ffmpeg_cmd[:10])}...")
                print(f"Error: {error_msg[-1000:] if len(error_msg) > 1000 else error_msg}")
                raise Exception(f"FFmpeg failed with code {process.returncode}")
                
        except Exception as e:
            print(f"[WARN] Avatar+background composition failed: {e}")
            # Fallback: just avatar
            import shutil
            shutil.copy(avatar_video, output_path)
            return output_path
