"""
Desktop GUI Controller - Business Logic Layer
Separates business logic from GUI components for testability.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from src.core.audio_mixer import AudioMixer
from src.core.music_generator import MusicGenerator
from src.core.script_parser import ScriptParser
from src.core.tts_engine import TTSEngine
from src.core.video_composer import VideoComposer


class PodcastCreatorController:
    """Business logic controller for podcast creation (GUI-agnostic)."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize controller with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.script_file: Optional[str] = None
        self.music_file: Optional[str] = None
        self.music_description: Optional[str] = None
        self.voice_type: str = "gtts"
        self.avatar_style: str = "Professional Studio"
        self.video_quality: str = "Fastest (Testing)"
        self.visualize: bool = False
        self.background: bool = False
        self.avatar: bool = False
        self.output_name: Optional[str] = None

    def validate_inputs(self) -> tuple[bool, Optional[str]]:
        """
        Validate user inputs before podcast creation.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.script_file:
            return False, "Please select a script file!"
        
        script_path = Path(self.script_file)
        if not script_path.exists():
            return False, f"Script file not found: {script_path}"
        
        if not script_path.is_file():
            return False, f"Script path is not a file: {script_path}"
        
        return True, None

    def prepare_podcast_creation_params(self) -> Dict[str, Any]:
        """
        Prepare parameters for podcast creation.

        Returns:
            Dictionary with creation parameters
        """
        script_path = Path(self.script_file)
        
        # Map UI quality strings to internal quality presets
        quality_map = {
            "Fastest (Testing)": "fastest",
            "Fast (720p)": "fast",
            "Medium (720p)": "medium",
            "High (1080p)": "high",
        }
        
        # Support legacy format
        video_quality_str = self.video_quality
        if "1080p" in video_quality_str and "High" in video_quality_str:
            quality = "high"
        elif "720p" in video_quality_str and "Medium" in video_quality_str:
            quality = "medium"
        elif "720p" in video_quality_str and "Fast" in video_quality_str:
            quality = "fast"
        else:
            quality = quality_map.get(video_quality_str, "fastest")
        
        output_name = self.output_name or script_path.stem
        
        return {
            "script_path": script_path,
            "music_file": Path(self.music_file) if self.music_file else None,
            "music_description": self.music_description,
            "output_name": output_name,
            "quality": quality,
            "use_visualization": self.visualize,
            "use_background": self.background,
            "use_avatar": self.avatar,
        }

    def create_podcast(self, progress_callback=None, log_callback=None) -> Path:
        """
        Create podcast using the configured parameters.

        Args:
            progress_callback: Optional callback for progress updates (message, status)
            log_callback: Optional callback for log messages (message, color)

        Returns:
            Path to the created video file

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If podcast creation fails
        """
        # Validate inputs
        is_valid, error_msg = self.validate_inputs()
        if not is_valid:
            raise ValueError(error_msg)
        
        # Prepare parameters
        params = self.prepare_podcast_creation_params()
        
        # Helper to call callbacks safely
        def progress(msg: str, status: str = "info"):
            if progress_callback:
                progress_callback(msg, status)
        
        def log(msg: str, color: str = "black"):
            if log_callback:
                log_callback(msg, color)
        
        try:
            progress("Processing...", "blue")
            log("=" * 60)
            log("🎙️ Starting podcast creation...")

            # Read script
            script_path = params["script_path"]
            log(f"📄 Reading script: {script_path.name}")

            with open(script_path, "r", encoding="utf-8") as f:
                script_text = f.read()

            # Parse script
            log("🔍 Parsing script...")
            parser = ScriptParser(self.config)
            parsed_data = parser.parse(script_text)
            log(f"✅ Parsed {len(parsed_data['text'])} characters")

            # Generate TTS
            log("🗣️ Generating speech...")
            tts_engine = TTSEngine(self.config)
            audio_path = tts_engine.generate(parsed_data["text"])
            log(f"✅ Speech generated: {audio_path.name}")

            # Handle music
            music_path = None
            if params["music_file"]:
                music_path = params["music_file"]
                log(f"🎵 Using music file: {music_path.name}")
            elif params["music_description"]:
                log(f"🎵 Generating music: {params['music_description']}")
                music_gen = MusicGenerator(self.config)
                music_path = music_gen.generate(params["music_description"])

            # Mix audio
            if music_path:
                log("🎛️ Mixing audio...")
                mixer = AudioMixer(self.config)
                mixed_audio = mixer.mix(audio_path, music_path)
                log("✅ Audio mixed")
            else:
                mixed_audio = audio_path
                log("⏭️ Skipping audio mixing (no music)")

            # Generate avatar if requested
            avatar_video_path = None
            if params["use_avatar"]:
                try:
                    log("🎭 Generating avatar with lip-sync...")
                    from src.core.avatar_generator import AvatarGenerator
                    avatar_gen = AvatarGenerator(self.config)
                    avatar_video_path = avatar_gen.generate(mixed_audio)
                    if avatar_video_path and avatar_video_path.exists() and avatar_video_path.stat().st_size > 0:
                        log(f"✅ Avatar generated: {avatar_video_path.name}")
                    else:
                        log("⚠️ Avatar generation failed, continuing without avatar...")
                        avatar_video_path = None
                except Exception as e:
                    log(f"⚠️ Avatar generation error: {e}, continuing without avatar...")
                    avatar_video_path = None

            # Create video
            log("🎬 Creating video...")
            composer = VideoComposer(self.config)

            final_video = composer.compose(
                mixed_audio,
                output_name=params["output_name"],
                use_visualization=params["use_visualization"],
                use_background=params["use_background"],
                avatar_video=avatar_video_path,
                quality=params["quality"]
            )

            log("=" * 60)
            log("✅ Podcast created successfully!")
            log(f"📹 Video saved to: {final_video}")
            log("=" * 60)

            progress("✅ Complete!", "green")

            return final_video

        except Exception as e:
            log(f"❌ Error: {str(e)}", "red")
            progress("❌ Error", "red")
            raise RuntimeError(f"Failed to create podcast: {str(e)}") from e

    def map_quality_string(self, quality_str: str) -> str:
        """
        Map UI quality string to internal quality preset.

        Args:
            quality_str: Quality string from UI

        Returns:
            Internal quality preset name
        """
        quality_map = {
            "Fastest (Testing)": "fastest",
            "Fast (720p)": "fast",
            "Medium (720p)": "medium",
            "High (1080p)": "high",
        }
        
        # Support legacy format
        if "1080p" in quality_str and "High" in quality_str:
            return "high"
        elif "720p" in quality_str and "Medium" in quality_str:
            return "medium"
        elif "720p" in quality_str and "Fast" in quality_str:
            return "fast"
        else:
            return quality_map.get(quality_str, "fastest")

