"""
Audio Mixer Module
Mixes voice and background music with ducking
"""

import shutil
from pathlib import Path
from typing import Any, Dict, Optional


class AudioMixer:
    """Mix voice audio with background music."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize audio mixer.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.ducking_config = config.get("music", {}).get("ducking", {})
        self.output_dir = Path(config["storage"]["cache_dir"]) / "mixed"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def mix(self, voice_path: Path, music_path: Optional[Path] = None, music_start_offset: float = 0.0) -> Path:
        """
        Mix voice and music audio.

        Args:
            voice_path: Path to voice audio file
            music_path: Path to music audio file (optional)
            music_start_offset: Start music this many seconds into the track (default: 0.0)

        Returns:
            Path to mixed audio file
        """
        output_path = self.output_dir / f"mixed_{voice_path.stem}.mp3"

        if music_path is None or not music_path.exists():
            # No music, just copy voice audio
            shutil.copy2(voice_path, output_path)
            return output_path

        # Implement mixing with pydub
        try:
            from pydub import AudioSegment

            # Load audio files
            voice = AudioSegment.from_file(str(voice_path))
            music = AudioSegment.from_file(str(music_path))

            # Apply music start offset (skip first N seconds)
            if music_start_offset > 0:
                offset_ms = int(music_start_offset * 1000)  # Convert to milliseconds
                if offset_ms < len(music):
                    music = music[offset_ms:]  # Skip to offset position
                    print(f"✓ Music starts at {music_start_offset}s into track")
                else:
                    print(f"⚠ Warning: Offset {music_start_offset}s exceeds music length, using full track")

            # Get ducking settings
            voice_volume = self.ducking_config.get("voice_volume", 1.0)
            _music_volume_speech = self.ducking_config.get("music_volume_during_speech", 0.2)
            _music_volume_no_speech = self.ducking_config.get("music_volume_no_speech", 0.5)

            # Adjust volumes (in dB)
            voice = voice + (20 * (voice_volume - 1))  # Adjust voice volume

            # Simple ducking: lower music volume during speech
            # For basic version, just reduce music volume overall
            music_db_reduction = -15  # Reduce music by 15dB so voice is clear
            music = music + music_db_reduction

            # Loop music if it's shorter than voice (from offset position)
            if len(music) < len(voice):
                loops_needed = (len(voice) // len(music)) + 1
                music = music * loops_needed
                print(f"✓ Music looped {loops_needed} times to match voice duration")

            # Trim music to match voice length
            music = music[: len(voice)]

            # Mix: overlay music under voice
            mixed = voice.overlay(music)

            # Export
            mixed.export(str(output_path), format="mp3", bitrate="192k")

            return output_path

        except ImportError:
            # If pydub not available, just return voice
            shutil.copy2(voice_path, output_path)
            return output_path
        except Exception as e:
            # On any error, return voice only
            print(f"Warning: Audio mixing failed ({e}), using voice only")
            shutil.copy2(voice_path, output_path)
            return output_path

    def _apply_ducking(self, voice, music):
        """
        Apply audio ducking to music based on voice presence.

        Args:
            voice: Voice audio segment
            music: Music audio segment

        Returns:
            Ducked music audio segment
        """
        # TODO: Implement smart ducking with voice activity detection
        # For now, simple volume reduction is applied in mix()
        return music
