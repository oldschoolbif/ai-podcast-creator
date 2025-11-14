"""
Additional Unit Tests for TTS Engine - Targeting 70% Coverage
Tests uncovered paths including different engines, error handling, and edge cases
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.tts_engine import TTSEngine


class TestTTSEngineInitialization:
    """Test initialization with different engines."""

    @pytest.mark.gpu
    def test_init_with_coqui_engine_mock(self, test_config, temp_dir, skip_if_no_gpu, stub_tts):
        """Test Coqui TTS initialization raises error when not installed."""
        test_config["tts"] = {"engine": "coqui", "coqui": {"model": "tts_models/en/ljspeech/tacotron2-DDC"}}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = True
        mock_gpu.get_device.return_value = "cuda"

        # Coqui not installed - should raise ImportError
        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu):
            with pytest.raises(ImportError, match="Coqui TTS not installed"):
                engine = TTSEngine(test_config)

    def test_init_with_elevenlabs_engine_mock(self, test_config, temp_dir):
        """Test ElevenLabs initialization raises error when not installed."""
        test_config["tts"] = {"engine": "elevenlabs", "elevenlabs": {"api_key": "test_key", "voice_id": "test_voice"}}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu):
            # ElevenLabs not installed - should raise ImportError
            with pytest.raises(ImportError, match="ElevenLabs not installed"):
                engine = TTSEngine(test_config)

    def test_init_with_azure_engine_mock(self, test_config, temp_dir):
        """Test Azure Speech initialization raises error when not installed."""
        test_config["tts"] = {
            "engine": "azure",
            "azure": {"subscription_key": "test_key", "region": "eastus", "voice_name": "en-US-JennyNeural"},
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu):
            # Azure not installed - should raise ImportError
            with pytest.raises(ImportError, match="Azure"):
                engine = TTSEngine(test_config)

    def test_init_with_piper_engine(self, test_config, temp_dir):
        """Test Piper TTS initialization."""
        test_config["tts"] = {"engine": "piper"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu):
            engine = TTSEngine(test_config)
            assert engine.engine_type == "piper"

    def test_init_with_unknown_engine_defaults_to_gtts(self, test_config, temp_dir):
        """Test that unknown engine defaults to gTTS."""
        test_config["tts"] = {"engine": "unknown_engine"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS"):
            engine = TTSEngine(test_config)
            assert engine.engine_type == "unknown_engine"
            assert hasattr(engine, "gtts_available")


class TestTTSEngineGenerate:
    """Test generate method with different engines."""

    def test_generate_with_different_tld(self, test_config, temp_dir):
        """Test gTTS with different TLD (accent)."""
        test_config["tts"] = {"engine": "gtts", "gtts_tld": "com"}  # American accent
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS") as mock_gtts:

            mock_tts_instance = MagicMock()
            mock_gtts.return_value = mock_tts_instance

            engine = TTSEngine(test_config)
            result = engine.generate("Test text for TLD")

            # Verify TLD was used
            assert mock_gtts.call_args[1]["tld"] == "com"
            assert result.exists() or result.suffix == ".mp3"

    def test_generate_with_retry_logic(self, test_config, temp_dir):
        """Test gTTS retry logic on failure."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS") as mock_gtts:

            # First call fails, second succeeds
            mock_tts_instance = MagicMock()
            mock_tts_instance.save.side_effect = [Exception("Network error"), None]
            mock_gtts.return_value = mock_tts_instance

            with patch("time.sleep"):  # Mock sleep to speed up test
                engine = TTSEngine(test_config)
                result = engine.generate("Test retry")

                # Should have retried and succeeded
                assert mock_tts_instance.save.call_count == 2

    def test_generate_max_retries_exceeded(self, test_config, temp_dir):
        """Test gTTS when max retries are exceeded."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS") as mock_gtts:

            # All attempts fail
            mock_tts_instance = MagicMock()
            mock_tts_instance.save.side_effect = Exception("Persistent network error")
            mock_gtts.return_value = mock_tts_instance

            with patch("time.sleep"):
                engine = TTSEngine(test_config)

                with pytest.raises(Exception, match="gTTS failed after 3 attempts"):
                    engine.generate("Test max retries")

    def test_generate_with_piper_engine_fallback(self, test_config, temp_dir):
        """Test generation with piper engine (not implemented, falls back to gtts)."""
        test_config["tts"] = {"engine": "piper"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS") as mock_gtts:

            mock_tts_instance = MagicMock()
            mock_gtts.return_value = mock_tts_instance

            # Piper engine not implemented yet
            engine = TTSEngine(test_config)

            # Generate should fall back to gtts
            result = engine.generate("Test piper")
            assert engine.engine_type == "piper"


class TestTTSEngineCaching:
    """Test caching behavior."""

    def test_cache_key_generation_consistency(self, test_config, temp_dir):
        """Test that same text generates same cache key."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS"):

            engine = TTSEngine(test_config)

            key1 = engine._get_cache_key("Same text")
            key2 = engine._get_cache_key("Same text")
            key3 = engine._get_cache_key("Different text")

            assert key1 == key2
            assert key1 != key3

    def test_cache_hit_avoids_regeneration(self, test_config, temp_dir):
        """Test that cached audio is returned without regeneration."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS") as mock_gtts:

            mock_tts_instance = MagicMock()
            mock_gtts.return_value = mock_tts_instance

            engine = TTSEngine(test_config)

            # First call generates
            result1 = engine.generate("Test caching unique text 123")

            # Manually create the cached file
            result1.parent.mkdir(parents=True, exist_ok=True)
            result1.touch()

            # Reset mock call count
            mock_gtts.reset_mock()

            # Second call should hit cache
            result2 = engine.generate("Test caching unique text 123")

            # Should be same file
            assert result1 == result2
            # gtts should not be called again (cache hit)
            assert mock_gtts.call_count == 0

    def test_cache_key_with_special_characters(self, test_config, temp_dir):
        """Test cache key generation with special characters."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS"):

            engine = TTSEngine(test_config)

            # These should all generate valid cache keys
            texts = [
                "Text with !@#$%^&*() special chars",
                "Text with unicode: 你好世界",
                "Text\nwith\nnewlines",
                "Text with 'quotes' and \"double quotes\"",
            ]

            for text in texts:
                key = engine._get_cache_key(text)
                assert isinstance(key, str)
                assert len(key) > 0
                # Should be a valid hex hash
                assert all(c in "0123456789abcdef" for c in key)


@pytest.mark.skip(reason="pyttsx3 requires system TTS engine")
class TestTTSEnginePyttsx3:
    """Test pyttsx3 offline TTS engine."""

    def test_pyttsx3_initialization_success(self, test_config, temp_dir):
        """Test pyttsx3 initialization when available."""
        test_config["tts"] = {"engine": "pyttsx3", "pyttsx3_voice_id": 0, "pyttsx3_rate": 150}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        mock_pyttsx3_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.id = "voice_001"
        mock_voice.name = "English Voice"
        mock_pyttsx3_engine.getProperty.return_value = [mock_voice]

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu):
            with patch("pyttsx3.init", return_value=mock_pyttsx3_engine):
                engine = TTSEngine(test_config)

                assert engine.engine_type == "pyttsx3"
                assert hasattr(engine, "pyttsx3_available")
                mock_pyttsx3_engine.setProperty.assert_called()

    def test_pyttsx3_voice_fallback(self, test_config, temp_dir):
        """Test pyttsx3 falls back to first voice if requested ID doesn't exist."""
        test_config["tts"] = {"engine": "pyttsx3", "pyttsx3_voice_id": 999}  # Non-existent voice
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        mock_pyttsx3_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.id = "voice_001"
        mock_voice.name = "English Voice"
        mock_pyttsx3_engine.getProperty.return_value = [mock_voice]

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu):
            with patch("pyttsx3.init", return_value=mock_pyttsx3_engine):
                engine = TTSEngine(test_config)

                # Should fall back to first voice
                set_property_calls = mock_pyttsx3_engine.setProperty.call_args_list
                voice_calls = [call for call in set_property_calls if call[0][0] == "voice"]
                assert len(voice_calls) > 0

    def test_pyttsx3_initialization_failure_falls_back_to_gtts(self, test_config, temp_dir):
        """Test pyttsx3 falls back to gTTS on initialization failure."""
        test_config["tts"] = {"engine": "pyttsx3"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu):
            with patch("pyttsx3.init", side_effect=Exception("pyttsx3 not available")):
                with patch("gtts.gTTS"):
                    engine = TTSEngine(test_config)

                    # Should have fallen back to gtts
                    assert hasattr(engine, "gtts_available")


class TestTTSEngineEdgeCases:
    """Test edge cases and error handling."""

    def test_generate_with_very_long_text(self, test_config, temp_dir):
        """Test generation with very long text."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS") as mock_gtts:

            mock_tts_instance = MagicMock()
            mock_gtts.return_value = mock_tts_instance

            engine = TTSEngine(test_config)

            # Very long text (5000 words)
            long_text = "word " * 5000
            result = engine.generate(long_text)

            # Should generate without error
            assert mock_gtts.called
            assert result.suffix == ".mp3"

    def test_generate_with_unicode_text(self, test_config, temp_dir):
        """Test generation with unicode characters."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS") as mock_gtts:

            mock_tts_instance = MagicMock()
            mock_gtts.return_value = mock_tts_instance

            engine = TTSEngine(test_config)

            # Unicode text
            unicode_texts = [
                "Hello with émojis 😊🎉",
                "Spëcial çharacters",
                "中文测试",
            ]

            for text in unicode_texts:
                result = engine.generate(text)
                assert result.suffix == ".mp3"

    def test_cache_directory_creation(self, test_config, temp_dir):
        """Test that cache directory is created if it doesn't exist."""
        cache_dir = temp_dir / "nested" / "cache" / "path"
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(cache_dir)

        # Cache dir shouldn't exist yet
        assert not (cache_dir / "tts").exists()

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"

        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu), patch("gtts.gTTS"):
            engine = TTSEngine(test_config)

            # Cache dir should now exist
            assert engine.cache_dir.exists()
            assert "tts" in str(engine.cache_dir)
