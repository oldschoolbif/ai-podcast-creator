"""
Integration tests for TTS engines - Test REAL generation workflows
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.tts_engine import TTSEngine


@pytest.mark.integration
class TestTTSIntegration:
    """Integration tests for TTS engine with real generation."""

    def test_gtts_real_generation(self, test_config, temp_dir):
        """Test real gTTS generation end-to-end."""
        test_config["tts"] = {"engine": "gtts", "gtts_tld": "com"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        engine = TTSEngine(test_config)

        # Generate real audio
        text = "This is a test of the text to speech system."
        audio_path = engine.generate(text)

        # Verify real file was created
        assert audio_path.exists()
        assert audio_path.suffix == ".mp3"
        assert audio_path.stat().st_size > 1000  # At least 1KB

        # Test caching works with real files
        audio_path2 = engine.generate(text)
        assert audio_path == audio_path2  # Same file

        # Different text creates different file
        audio_path3 = engine.generate("Different text here.")
        assert audio_path3 != audio_path
        assert audio_path3.exists()

    def test_gtts_multiple_generations(self, test_config, temp_dir):
        """Test multiple generations in sequence."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        engine = TTSEngine(test_config)

        texts = [
            "First sentence.",
            "Second sentence is longer.",
            "Third sentence has numbers like 123.",
            "Fourth sentence has punctuation! Question?",
        ]

        audio_files = []
        for text in texts:
            audio = engine.generate(text)
            assert audio.exists()
            audio_files.append(audio)

        # All files should exist
        assert len(audio_files) == 4
        # All files should be different
        assert len(set(audio_files)) == 4

    def test_gtts_empty_text_handling(self, test_config, temp_dir):
        """Test handling of edge cases."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        engine = TTSEngine(test_config)

        # Empty string should raise an exception (gTTS doesn't support empty text)
        with pytest.raises(Exception):
            audio = engine.generate("")

        # Single character should work
        audio = engine.generate("A")
        assert audio.exists()

        # Very long text
        long_text = "This is a sentence. " * 100
        audio = engine.generate(long_text)
        assert audio.exists()
        assert audio.stat().st_size > 10000  # Should be larger file

    def test_gtts_special_characters(self, test_config, temp_dir):
        """Test special characters in text."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        engine = TTSEngine(test_config)

        special_texts = [
            "Hello! How are you?",
            "Numbers: 123, 456, 789",
            "Email: test@example.com",
            "Symbols: $100, 50%, #hashtag",
            "Quote: 'single' and \"double\"",
        ]

        for text in special_texts:
            audio = engine.generate(text)
            assert audio.exists()
            assert audio.stat().st_size > 500

    def test_gtts_british_vs_american_accent(self, test_config, temp_dir):
        """Test different accents produce different files."""
        test_config["storage"]["cache_dir"] = str(temp_dir)

        text = "Hello, this is a test."

        # British accent
        test_config["tts"] = {"engine": "gtts", "gtts_tld": "co.uk"}
        engine_uk = TTSEngine(test_config)
        audio_uk = engine_uk.generate(text)

        # American accent
        test_config["tts"] = {"engine": "gtts", "gtts_tld": "com"}
        engine_us = TTSEngine(test_config)
        audio_us = engine_us.generate(text)

        # Both should exist
        assert audio_uk.exists()
        assert audio_us.exists()

        # Files should be different (different cache keys due to TLD)
        assert audio_uk != audio_us

    def test_cache_directory_organization(self, test_config, temp_dir):
        """Test cache directory is properly organized."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        engine = TTSEngine(test_config)

        # Generate multiple files
        texts = ["Test one", "Test two", "Test three"]
        for text in texts:
            engine.generate(text)

        # Check cache directory structure
        cache_dir = temp_dir / "tts"
        assert cache_dir.exists()

        # Should have 3 files
        audio_files = list(cache_dir.glob("*.mp3"))
        assert len(audio_files) == 3

        # All files should have MD5-like names
        for audio_file in audio_files:
            assert len(audio_file.stem) == 32  # MD5 hex length

    def test_gpu_manager_integration(self, test_config, temp_dir):
        """Test TTS integrates with GPU manager."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        engine = TTSEngine(test_config)

        # GPU manager should be initialized
        assert engine.gpu_manager is not None
        assert engine.device in ["cpu", "cuda", "cuda:0"]
        assert isinstance(engine.use_gpu, bool)

        # Should still generate audio
        audio = engine.generate("GPU integration test")
        assert audio.exists()

    def test_concurrent_generations(self, test_config, temp_dir):
        """Test multiple generations don't interfere."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        engine = TTSEngine(test_config)

        # Generate same text twice simultaneously-ish
        text = "Concurrent test"
        audio1 = engine.generate(text)
        audio2 = engine.generate(text)

        # Should get same cached file
        assert audio1 == audio2
        assert audio1.exists()

        # Verify file is valid
        assert audio1.stat().st_size > 500


@pytest.mark.integration
@pytest.mark.skipif(True, reason="Requires pyttsx3 engine setup")
class TestPyttsx3Integration:
    """Integration tests for pyttsx3 (offline TTS)."""

    def test_pyttsx3_generation(self, test_config, temp_dir):
        """Test pyttsx3 real generation."""
        test_config["tts"] = {"engine": "pyttsx3"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        try:
            engine = TTSEngine(test_config)
            audio = engine.generate("Offline text to speech test")
            assert audio.exists()
        except Exception as e:
            pytest.skip(f"pyttsx3 not available: {e}")
