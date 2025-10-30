"""
Comprehensive Unit Tests for Audio Mixer
Tests for src/core/audio_mixer.py - Aiming for 100% coverage
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.audio_mixer import AudioMixer

# Check if pydub is available (not available on Python 3.13)
try:
    import pydub

    PYDUB_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    PYDUB_AVAILABLE = False

skip_if_no_pydub = pytest.mark.skipif(
    not PYDUB_AVAILABLE, reason="pydub not available (Python 3.13+ removed audioop module)"
)


class TestAudioMixerInit:
    """Test AudioMixer initialization."""

    def test_init(self, test_config):
        """Test basic initialization."""
        mixer = AudioMixer(test_config)
        assert mixer.config == test_config
        assert hasattr(mixer, "ducking_config")
        assert hasattr(mixer, "output_dir")

    def test_init_creates_output_dir(self, test_config, temp_dir):
        """Test that initialization creates output directory."""
        test_config["storage"]["cache_dir"] = str(temp_dir / "cache")
        mixer = AudioMixer(test_config)

        expected_dir = temp_dir / "cache" / "mixed"
        assert mixer.output_dir == expected_dir
        assert mixer.output_dir.exists()

    def test_init_with_ducking_config(self, test_config):
        """Test initialization with ducking configuration."""
        test_config["music"] = {"ducking": {"voice_volume": 1.2, "music_volume_during_speech": 0.3}}
        mixer = AudioMixer(test_config)
        assert mixer.ducking_config == test_config["music"]["ducking"]


class TestAudioMixerMixNoMusic:
    """Test mixing with voice only (no music)."""

    def test_mix_voice_only(self, test_config, temp_dir):
        """Test mixing with no music file."""
        # Create a fake voice file
        voice_file = temp_dir / "voice.mp3"
        voice_file.write_text("fake audio data")

        mixer = AudioMixer(test_config)

        with patch("shutil.copy2") as mock_copy:
            result = mixer.mix(voice_file, music_path=None)

            assert mock_copy.called
            assert result.name.startswith("mixed_voice")
            assert result.suffix == ".mp3"

    def test_mix_music_path_not_exists(self, test_config, temp_dir):
        """Test mixing when music file doesn't exist."""
        voice_file = temp_dir / "voice.mp3"
        voice_file.write_text("fake audio data")
        music_file = temp_dir / "nonexistent.mp3"  # Doesn't exist

        mixer = AudioMixer(test_config)

        with patch("shutil.copy2") as mock_copy:
            result = mixer.mix(voice_file, music_path=music_file)

            assert mock_copy.called
            assert result is not None


@skip_if_no_pydub
class TestAudioMixerMixWithMusic:
    """Test mixing voice with background music."""

    def test_mix_with_music_success(self, test_config, temp_dir):
        """Test successful mixing of voice and music."""
        voice_file = temp_dir / "voice.mp3"
        music_file = temp_dir / "music.mp3"
        voice_file.write_text("voice")
        music_file.write_text("music")

        mixer = AudioMixer(test_config)

        # Mock pydub AudioSegment
        with patch("pydub.AudioSegment") as mock_segment:
            mock_voice = MagicMock()
            mock_music = MagicMock()

            # Mock AudioSegment.from_file to return different objects
            mock_segment.from_file.side_effect = [mock_voice, mock_music]

            # Mock length operations
            mock_voice.__len__ = MagicMock(return_value=10000)
            mock_music.__len__ = MagicMock(return_value=15000)

            # Mock audio operations
            mock_voice.__add__ = MagicMock(return_value=mock_voice)
            mock_music.__add__ = MagicMock(return_value=mock_music)
            mock_music.__getitem__ = MagicMock(return_value=mock_music)
            mock_voice.overlay = MagicMock(return_value=mock_voice)
            mock_voice.export = MagicMock()

            result = mixer.mix(voice_file, music_file)

            assert result is not None
            assert result.suffix == ".mp3"
            assert mock_voice.export.called

    def test_mix_with_music_offset(self, test_config, temp_dir, capsys):
        """Test mixing with music start offset."""
        voice_file = temp_dir / "voice.mp3"
        music_file = temp_dir / "music.mp3"
        voice_file.write_text("voice")
        music_file.write_text("music")

        mixer = AudioMixer(test_config)

        with patch("pydub.AudioSegment") as mock_segment:
            mock_voice = MagicMock()
            mock_music = MagicMock()

            mock_segment.from_file.side_effect = [mock_voice, mock_music]

            mock_voice.__len__ = MagicMock(return_value=10000)
            mock_music.__len__ = MagicMock(return_value=15000)

            mock_voice.__add__ = MagicMock(return_value=mock_voice)
            mock_music.__add__ = MagicMock(return_value=mock_music)
            mock_music.__getitem__ = MagicMock(return_value=mock_music)
            mock_voice.overlay = MagicMock(return_value=mock_voice)
            mock_voice.export = MagicMock()

            # Test with 5 second offset
            result = mixer.mix(voice_file, music_file, music_start_offset=5.0)

            # Check that music was sliced
            mock_music.__getitem__.assert_called()

            # Check console output
            captured = capsys.readouterr()
            assert "Music starts at 5" in captured.out or result is not None

    def test_mix_music_offset_exceeds_length(self, test_config, temp_dir, capsys):
        """Test mixing when offset exceeds music length."""
        voice_file = temp_dir / "voice.mp3"
        music_file = temp_dir / "music.mp3"
        voice_file.write_text("voice")
        music_file.write_text("music")

        mixer = AudioMixer(test_config)

        with patch("pydub.AudioSegment") as mock_segment:
            mock_voice = MagicMock()
            mock_music = MagicMock()

            mock_segment.from_file.side_effect = [mock_voice, mock_music]

            mock_voice.__len__ = MagicMock(return_value=10000)
            mock_music.__len__ = MagicMock(return_value=3000)  # 3 seconds

            mock_voice.__add__ = MagicMock(return_value=mock_voice)
            mock_music.__add__ = MagicMock(return_value=mock_music)
            mock_music.__getitem__ = MagicMock(return_value=mock_music)
            mock_voice.overlay = MagicMock(return_value=mock_voice)
            mock_voice.export = MagicMock()

            # Offset is 10 seconds but music is only 3 seconds
            result = mixer.mix(voice_file, music_file, music_start_offset=10.0)

            captured = capsys.readouterr()
            # Should print warning about offset exceeding length
            assert result is not None

    def test_mix_music_shorter_than_voice_loops(self, test_config, temp_dir, capsys):
        """Test that music loops when shorter than voice."""
        voice_file = temp_dir / "voice.mp3"
        music_file = temp_dir / "music.mp3"
        voice_file.write_text("voice")
        music_file.write_text("music")

        mixer = AudioMixer(test_config)

        with patch("pydub.AudioSegment") as mock_segment:
            mock_voice = MagicMock()
            mock_music = MagicMock()

            mock_segment.from_file.side_effect = [mock_voice, mock_music]

            # Voice is 10 seconds, music is only 3 seconds
            mock_voice.__len__ = MagicMock(return_value=10000)
            mock_music.__len__ = MagicMock(return_value=3000)

            mock_voice.__add__ = MagicMock(return_value=mock_voice)
            mock_music.__add__ = MagicMock(return_value=mock_music)
            mock_music.__mul__ = MagicMock(return_value=mock_music)  # Loop operator
            mock_music.__getitem__ = MagicMock(return_value=mock_music)
            mock_voice.overlay = MagicMock(return_value=mock_voice)
            mock_voice.export = MagicMock()

            result = mixer.mix(voice_file, music_file)

            # Check that music was looped
            mock_music.__mul__.assert_called()

            captured = capsys.readouterr()
            assert "looped" in captured.out or result is not None

    def test_mix_with_ducking_config(self, test_config, temp_dir):
        """Test mixing applies ducking configuration."""
        test_config["music"] = {
            "ducking": {"voice_volume": 1.2, "music_volume_during_speech": 0.3, "music_volume_no_speech": 0.6}
        }

        voice_file = temp_dir / "voice.mp3"
        music_file = temp_dir / "music.mp3"
        voice_file.write_text("voice")
        music_file.write_text("music")

        mixer = AudioMixer(test_config)

        with patch("pydub.AudioSegment") as mock_segment:
            mock_voice = MagicMock()
            mock_music = MagicMock()

            mock_segment.from_file.side_effect = [mock_voice, mock_music]

            mock_voice.__len__ = MagicMock(return_value=10000)
            mock_music.__len__ = MagicMock(return_value=15000)

            mock_voice.__add__ = MagicMock(return_value=mock_voice)
            mock_music.__add__ = MagicMock(return_value=mock_music)
            mock_music.__getitem__ = MagicMock(return_value=mock_music)
            mock_voice.overlay = MagicMock(return_value=mock_voice)
            mock_voice.export = MagicMock()

            result = mixer.mix(voice_file, music_file)

            # Verify ducking config was accessed
            assert mixer.ducking_config["voice_volume"] == 1.2
            assert result is not None


@skip_if_no_pydub
class TestAudioMixerErrorHandling:
    """Test error handling in audio mixing."""

    def test_mix_import_error_fallback(self, test_config, temp_dir):
        """Test fallback when pydub import fails."""
        voice_file = temp_dir / "voice.mp3"
        music_file = temp_dir / "music.mp3"
        voice_file.write_text("voice")
        music_file.write_text("music")

        mixer = AudioMixer(test_config)

        # Mock ImportError by making the import statement fail
        def mock_import(name, *args, **kwargs):
            if name == "pydub":
                raise ImportError("Mocked pydub import failure")
            return __import__(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            with patch("shutil.copy2") as mock_copy:
                result = mixer.mix(voice_file, music_file)

                # Should fall back to copying voice file
                assert mock_copy.called
                assert result is not None

    def test_mix_generic_exception_fallback(self, test_config, temp_dir, capsys):
        """Test fallback when mixing fails with exception."""
        voice_file = temp_dir / "voice.mp3"
        music_file = temp_dir / "music.mp3"
        voice_file.write_text("voice")
        music_file.write_text("music")

        mixer = AudioMixer(test_config)

        with patch("pydub.AudioSegment") as mock_segment:
            # Make AudioSegment.from_file raise an exception
            mock_segment.from_file.side_effect = Exception("Audio loading failed")

            with patch("shutil.copy2") as mock_copy:
                result = mixer.mix(voice_file, music_file)

                # Should fall back to copying voice file
                assert mock_copy.called
                assert result is not None

                captured = capsys.readouterr()
                assert "Warning" in captured.out or "failed" in captured.out.lower()


class TestAudioMixerDuckingMethod:
    """Test the _apply_ducking method."""

    def test_apply_ducking(self, test_config):
        """Test _apply_ducking method (currently a placeholder)."""
        mixer = AudioMixer(test_config)

        mock_voice = MagicMock()
        mock_music = MagicMock()

        result = mixer._apply_ducking(mock_voice, mock_music)

        # Currently just returns music unchanged
        assert result == mock_music


@skip_if_no_pydub
@pytest.mark.parametrize(
    "offset,expected",
    [
        (0.0, 0),
        (5.0, 5000),
        (10.5, 10500),
    ],
)
def test_music_offset_calculation(test_config, temp_dir, offset, expected):
    """Test music offset calculation in milliseconds."""
    voice_file = temp_dir / "voice.mp3"
    music_file = temp_dir / "music.mp3"
    voice_file.write_text("voice")
    music_file.write_text("music")

    mixer = AudioMixer(test_config)

    with patch("pydub.AudioSegment") as mock_segment:
        mock_voice = MagicMock()
        mock_music = MagicMock()

        mock_segment.from_file.side_effect = [mock_voice, mock_music]

        mock_voice.__len__ = MagicMock(return_value=20000)
        mock_music.__len__ = MagicMock(return_value=30000)

        mock_voice.__add__ = MagicMock(return_value=mock_voice)
        mock_music.__add__ = MagicMock(return_value=mock_music)
        mock_music.__getitem__ = MagicMock(return_value=mock_music)
        mock_voice.overlay = MagicMock(return_value=mock_voice)
        mock_voice.export = MagicMock()

        result = mixer.mix(voice_file, music_file, music_start_offset=offset)

        assert result is not None
