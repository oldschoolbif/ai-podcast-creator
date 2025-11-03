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
        """
        Initialize video composer.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_dir = Path(config["storage"]["outputs_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.background = Path(config.get("video", {}).get("background_path", "src/assets/backgrounds/studio_01.jpg"))

    def compose(
        self,
        audio_path: Path,
        avatar_image: Optional[Path] = None,
        output_name: Optional[str] = None,
        use_visualization: bool = False,
        avatar_video: Optional[Path] = None,
    ) -> Path:
        """
        Compose final video with audio and static image or visualization.

        Args:
            audio_path: Path to mixed audio file
            avatar_image: Path to avatar image (optional)
            output_name: Optional custom output name
            use_visualization: Use audio-reactive visualization instead of static background

        Returns:
            Path to final video file
        """
        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"podcast_{timestamp}"

        output_path = self.output_dir / f"{output_name}.mp4"

        # If avatar video exists and visualization requested, overlay them
        if avatar_video and avatar_video.exists() and use_visualization:
            return self._overlay_visualization_on_avatar(avatar_video, audio_path, output_path)

        # Use visualization if requested (no avatar)
        if use_visualization and not avatar_video:
            from .audio_visualizer import AudioVisualizer

            visualizer = AudioVisualizer(self.config)
            return visualizer.generate_visualization(audio_path, output_path)

        # Get background image (use default if not exists)
        bg_path = self.background if self.background.exists() else self._create_default_background()

        # Use MoviePy for simple video creation
        try:
            from moviepy.editor import AudioFileClip, ColorClip, CompositeVideoClip, ImageClip
            from PIL import Image, ImageDraw, ImageFont

            # Load audio to get duration
            audio = AudioFileClip(str(audio_path))
            duration = audio.duration

            # Create or load background
            if bg_path.exists():
                background = ImageClip(str(bg_path)).set_duration(duration)
            else:
                # Create a nice gradient background
                resolution = self.config.get("video", {}).get("resolution", [1920, 1080])
                background = ColorClip(size=resolution, color=(20, 30, 48)).set_duration(duration)  # Dark blue

            # Set audio
            background = background.set_audio(audio)

            # Add text overlay (character name)
            try:
                char_name = self.config.get("character", {}).get("name", "Vivienne Sterling")
                txt_img = self._create_text_image(char_name, (1920, 1080))
                txt_clip = ImageClip(txt_img).set_duration(duration).set_position(("center", 50))
                final = CompositeVideoClip([background, txt_clip])
            except Exception:
                final = background

            # Export video
            fps = self.config.get("video", {}).get("fps", 30)
            codec = self.config.get("video", {}).get("codec", "libx264")

            final.write_videofile(str(output_path), codec=codec, fps=fps, audio_codec="aac", verbose=False, logger=None)

            # Clean up
            audio.close()
            final.close()

            return output_path

        except ImportError:
            # Fallback to FFmpeg command line
            return self._compose_with_ffmpeg(audio_path, bg_path, output_path)
        except Exception as e:
            print(f"Warning: MoviePy composition failed ({e}), trying FFmpeg...")
            return self._compose_with_ffmpeg(audio_path, bg_path, output_path)

    def _compose_with_ffmpeg(self, audio_path: Path, image_path: Path, output_path: Path) -> Path:
        """Compose video using FFmpeg with GPU acceleration if available."""
        try:
            from src.utils.gpu_utils import get_gpu_manager

            gpu_manager = get_gpu_manager()

            # Base FFmpeg command
            cmd = ["ffmpeg", "-y"]

            # Try to use GPU encoding if available (NVIDIA)
            if gpu_manager.gpu_available:
                try:
                    # Check if NVENC is available
                    check_cmd = ["ffmpeg", "-hide_banner", "-encoders"]
                    result = subprocess.run(check_cmd, capture_output=True, text=True)

                    if "h264_nvenc" in result.stdout:
                        print("✓ Using GPU-accelerated H.264 encoding (NVENC)")

                        cmd.extend(
                            [
                                "-hwaccel",
                                "cuda",
                                "-hwaccel_output_format",
                                "cuda",
                                "-loop",
                                "1",
                                "-i",
                                str(image_path),
                                "-i",
                                str(audio_path),
                                "-c:v",
                                "h264_nvenc",  # NVIDIA GPU encoder
                                "-profile:v",
                                "baseline",  # Maximum compatibility
                                "-level",
                                "3.0",
                                "-preset",
                                "p7",  # Fastest NVENC preset
                                "-tune",
                                "hq",  # High quality
                                "-rc",
                                "vbr",  # Variable bitrate
                                "-cq",
                                "23",  # Quality level
                                "-b:v",
                                "5M",  # Reasonable bitrate
                                "-maxrate",
                                "6M",
                                "-bufsize",
                                "12M",
                                "-c:a",
                                "aac",
                                "-b:a",
                                "192k",
                                "-ar",
                                "44100",  # Standard sample rate
                                "-ac",
                                "2",  # Stereo
                                "-pix_fmt",
                                "yuv420p",
                                "-movflags",
                                "+faststart",  # Web optimization
                                "-shortest",
                                str(output_path),
                            ]
                        )
                    else:
                        raise Exception("NVENC not available")

                except Exception as e:
                    print(f"⚠ GPU encoding not available, using CPU: {e}")
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
                            "baseline",  # Maximum compatibility
                            "-level",
                            "3.0",
                            "-preset",
                            "faster",  # Faster CPU encoding
                            "-tune",
                            "stillimage",
                            "-crf",
                            "23",
                            "-c:a",
                            "aac",
                            "-b:a",
                            "192k",
                            "-ar",
                            "44100",  # Standard sample rate
                            "-ac",
                            "2",  # Stereo
                            "-pix_fmt",
                            "yuv420p",
                            "-movflags",
                            "+faststart",  # Web optimization
                            "-shortest",
                            str(output_path),
                        ]
                    )
            else:
                # CPU encoding with optimized settings
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
                        "baseline",  # Maximum compatibility
                        "-level",
                        "3.0",
                        "-preset",
                        "faster",
                        "-tune",
                        "stillimage",
                        "-crf",
                        "23",
                        "-c:a",
                        "aac",
                        "-b:a",
                        "192k",
                        "-ar",
                        "44100",  # Standard sample rate
                        "-ac",
                        "2",  # Stereo
                        "-pix_fmt",
                        "yuv420p",
                        "-movflags",
                        "+faststart",  # Web optimization
                        "-shortest",
                        str(output_path),
                    ]
                )

            subprocess.run(cmd, check=True, capture_output=True)
            return output_path

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")
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

        # Try to use a nice font, fallback to default, then None (PIL will use built-in)
        try:
            font = ImageFont.truetype("arial.ttf", 60)  # type: ignore[assignment]
        except Exception:
            try:
                font = ImageFont.load_default()  # type: ignore[assignment]
            except Exception:
                font = None  # PIL will use built-in default

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

    def _overlay_visualization_on_avatar(self, avatar_video: Path, audio_path: Path, output_path: Path) -> Path:
        """Overlay visualization at bottom of avatar video using FFmpeg."""
        try:
            import subprocess

            from .audio_visualizer import AudioVisualizer

            print("🎨 Overlaying visualization on avatar video...")

            # Generate visualization video first
            temp_viz_path = output_path.parent / f"temp_viz_{output_path.stem}.mp4"
            visualizer = AudioVisualizer(self.config)
            visualizer.generate_visualization(audio_path, temp_viz_path)

            # Use FFmpeg to overlay avatar on top of visualization
            # Avatar in center-top, visualization stays at bottom
            ffmpeg_cmd = [
                "ffmpeg",
                "-i",
                str(temp_viz_path),  # Background (visualization)
                "-i",
                str(avatar_video),  # Overlay (avatar)
                "-filter_complex",
                "[1:v]scale=960:720[avatar];"  # Scale avatar to 960x720
                + "[0:v][avatar]overlay=(W-w)/2:50",  # Center avatar, 50px from top
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-c:a",
                "copy",
                str(output_path),
                "-y",
            ]

            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Cleanup temp file
                temp_viz_path.unlink(missing_ok=True)
                print(f"✓ Combined video created: {output_path}")
                return output_path
            else:
                print(f"⚠ FFmpeg overlay failed: {result.stderr[:200]}")
                raise Exception("FFmpeg failed")

        except Exception as e:
            print(f"⚠ Overlay failed: {e}")
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
