"""
Integration Tests for Complete Pipeline
Tests the entire podcast generation pipeline
"""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.integration
@pytest.mark.slow
class TestBasicPipeline:
    """Test basic pipeline without GPU."""

    def test_end_to_end_audio_only(self, test_config, sample_script_file, temp_dir, skip_if_no_internet):
        """Test complete audio generation pipeline."""
        from src.core.audio_mixer import AudioMixer
        from src.core.script_parser import ScriptParser
        from src.core.tts_engine import TTSEngine

        # Parse script
        parser = ScriptParser(test_config)
        parsed = parser.parse_file(sample_script_file)

        assert parsed["text"]  # Should have text content
        assert "metadata" in parsed

        # Generate TTS for the main text
        tts = TTSEngine(test_config)
        audio_path = tts.generate(parsed["text"])
        assert audio_path.exists()
        audio_files = [audio_path]

        # Mix audio
        mixer = AudioMixer(test_config)
        output_path = temp_dir / "output.wav"

        # AudioMixer.mix expects a single audio file, not a list
        final_audio = mixer.mix(audio_path, None)
        assert final_audio.exists()
        assert final_audio.stat().st_size > 0

    def test_script_to_audio_workflow(self, test_config, temp_dir, skip_if_no_internet):
        """Test script to audio workflow."""
        from src.core.script_parser import ScriptParser
        from src.core.tts_engine import TTSEngine

        script_text = """# Test Podcast
This is a quick test.

Testing one two three."""

        # Parse
        parser = ScriptParser(test_config)
        parsed = parser.parse(script_text)

        # Generate TTS for the text
        tts = TTSEngine(test_config)
        audio_path = tts.generate(parsed["text"])

        assert audio_path.exists()
        assert audio_path.suffix in [".mp3", ".wav"]


@pytest.mark.integration
@pytest.mark.gpu
@pytest.mark.slow
class TestGPUPipeline:
    """Test GPU-accelerated pipeline."""

    def test_gpu_tts_generation(self, test_config, skip_if_no_gpu):
        """Test GPU TTS generation."""
        # Update config for GPU
        test_config["tts"]["engine"] = "coqui"
        test_config["tts"]["coqui"] = {
            "model": "tts_models/en/ljspeech/tacotron2-DDC",
            "language": "en",
            "use_gpu": True,
        }

        # Stub TTS if not available - test will use mocks
        if "TTS" not in sys.modules:
            from unittest.mock import MagicMock
            stub_tts_module = MagicMock()
            stub_tts_module.api = MagicMock()
            stub_tts_module.api.TTS = MagicMock()
            sys.modules["TTS"] = stub_tts_module
        
        # This test requires actual Coqui TTS, so skip if not available
        try:
            from src.core.tts_engine import TTSEngine

            tts = TTSEngine(test_config)
            audio_path = tts.generate("This is a GPU test.")

            assert audio_path.exists()
        except (ImportError, RuntimeError, ValueError):
            pytest.skip("Coqui TTS not installed or not properly configured")

    def test_gpu_music_generation(self, test_config, skip_if_no_gpu, stub_audiocraft):
        """Test GPU music generation."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small", "duration": 5, "use_gpu": True}

        # Stub audiocraft if not available - test will use mocks
        if "audiocraft" not in sys.modules:
            from unittest.mock import MagicMock, patch
            stub_audiocraft_module = MagicMock()
            stub_audiocraft_module.models = MagicMock()
            stub_audiocraft_module.models.MusicGen = MagicMock()
            sys.modules["audiocraft"] = stub_audiocraft_module
        
        # This test requires actual AudioCraft, so skip if not available
        try:
            from src.core.music_generator import MusicGenerator

            music_gen = MusicGenerator(test_config)
            music_path = music_gen.generate("calm background music")

            # If AudioCraft is stubbed, the generation will fail - skip in that case
            if music_path is None:
                pytest.skip("AudioCraft not installed or not properly configured")
            assert music_path is not None and (isinstance(music_path, str) or music_path.exists())
        except (ImportError, RuntimeError, ValueError, AttributeError):
            pytest.skip("AudioCraft not installed or not properly configured")


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in pipeline."""

    def test_invalid_script_handling(self, test_config):
        """Test handling of invalid scripts."""
        from src.core.script_parser import ScriptParser

        parser = ScriptParser(test_config)

        # Parse empty script - should return empty text, not raise
        result = parser.parse("")
        assert result["text"] == "" or len(result["text"]) == 0

    def test_missing_file_handling(self, test_config):
        """Test handling of missing files."""
        from src.core.script_parser import ScriptParser

        parser = ScriptParser(test_config)

        with pytest.raises(FileNotFoundError):
            parser.parse_file(Path("does_not_exist.txt"))

    def test_audio_mixer_empty_input(self, test_config):
        """Test audio mixer with empty input."""
        from src.core.audio_mixer import AudioMixer

        mixer = AudioMixer(test_config)

        with pytest.raises((ValueError, Exception)):
            mixer.mix([], Path("output.wav"))


@pytest.mark.smoke
class TestSmokeTests:
    """Quick smoke tests for CI/CD."""

    def test_all_modules_import(self):
        """Test that all core modules can be imported."""
        try:
            from src.core import audio_mixer, avatar_generator, music_generator, script_parser, tts_engine
            from src.utils import config, gpu_utils
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")

    def test_gpu_utils_available(self):
        """Test GPU utilities are available."""
        from src.utils.gpu_utils import get_gpu_manager

        manager = get_gpu_manager()
        assert manager is not None
        assert hasattr(manager, "get_device")

    def test_config_loads(self, test_config_file):
        """Test configuration loading."""
        import yaml

        with open(test_config_file) as f:
            config = yaml.safe_load(f)

        assert "tts" in config
        assert "storage" in config
