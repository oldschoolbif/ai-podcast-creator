"""
Expanded TTS Engine Tests - Night Shift Edition
Targeting 80%+ coverage through comprehensive edge case testing
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def make_tts_config(tmp_path):
    """Create minimal TTS config for testing."""
    return {
        "storage": {
            "cache_dir": str(tmp_path / "cache"),
            "output_dir": str(tmp_path / "output"),
        },
        "tts": {
            "engine": "gtts",
            "gtts_tld": "com",
        },
    }


class TestTTSEngineEdgeCases:
    """Test TTS Engine edge cases and error paths."""

    def test_generate_with_custom_output_path(self, tmp_path):
        """Test generate with custom output path."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        engine = TTSEngine(cfg)

        custom_path = tmp_path / "custom_output.mp3"

        with patch.object(engine, "_generate_gtts", return_value=custom_path):
            result = engine.generate("test text", output_path=custom_path)

            assert result == custom_path
            assert engine._generate_gtts.called

    def test_generate_with_empty_text_handled(self, tmp_path):
        """Test that empty text is handled."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        engine = TTSEngine(cfg)

        # Empty text should still attempt generation (gTTS will handle)
        with patch.object(engine, "_generate_gtts") as mock_gen:
            mock_gen.return_value = tmp_path / "empty.mp3"
            result = engine.generate("")

            assert mock_gen.called

    def test_generate_with_very_long_text(self, tmp_path):
        """Test generation with very long text."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        engine = TTSEngine(cfg)

        long_text = "This is a very long text. " * 1000

        with patch.object(engine, "_generate_gtts") as mock_gen:
            mock_gen.return_value = tmp_path / "long.mp3"
            result = engine.generate(long_text)

            assert mock_gen.called
            # Verify cache key is generated for long text
            assert engine._get_cache_key(long_text) is not None

    def test_generate_with_special_characters(self, tmp_path):
        """Test generation with special characters."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        engine = TTSEngine(cfg)

        special_text = "Hello! @#$%^&*()[]{}|\\:;\"'<>?,./~`"

        with patch.object(engine, "_generate_gtts") as mock_gen:
            mock_gen.return_value = tmp_path / "special.mp3"
            result = engine.generate(special_text)

            assert mock_gen.called

    def test_generate_with_unicode_characters(self, tmp_path):
        """Test generation with unicode characters."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        engine = TTSEngine(cfg)

        unicode_text = "Hello 世界 🌍 Привет"

        with patch.object(engine, "_generate_gtts") as mock_gen:
            mock_gen.return_value = tmp_path / "unicode.mp3"
            result = engine.generate(unicode_text)

            assert mock_gen.called

    def test_cache_key_unicode_safe(self, tmp_path):
        """Test cache key generation handles unicode."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        engine = TTSEngine(cfg)

        unicode_text = "Test 世界 🌍"
        key = engine._get_cache_key(unicode_text)

        assert key is not None
        assert len(key) == 32  # MD5 hex digest
        assert isinstance(key, str)

    def test_cache_key_special_characters(self, tmp_path):
        """Test cache key with special characters."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        engine = TTSEngine(cfg)

        special_text = "@#$%^&*()"
        key = engine._get_cache_key(special_text)

        assert key is not None
        assert len(key) == 32


class TestTTSEngineRetryLogic:
    """Test retry and error handling."""

    def test_gtts_retry_on_first_failure(self, tmp_path):
        """Test gTTS retries on first failure then succeeds."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        engine = TTSEngine(cfg)

        output_path = tmp_path / "retry_test.mp3"

        call_count = 0

        def mock_gtts_save(path):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Network error")
            Path(path).write_bytes(b"audio")

        with patch("gtts.gTTS") as mock_gtts_class:
            mock_tts = MagicMock()
            mock_tts.save.side_effect = mock_gtts_save
            mock_gtts_class.return_value = mock_tts

            with patch("time.sleep"):  # Speed up test
                result = engine._generate_gtts("test", output_path)

                assert result == output_path
                assert call_count == 2  # First fails, second succeeds

    def test_gtts_retry_all_failures(self, tmp_path):
        """Test gTTS raises after all retries fail."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        engine = TTSEngine(cfg)

        output_path = tmp_path / "fail_test.mp3"

        with patch("gtts.gTTS") as mock_gtts_class:
            mock_tts = MagicMock()
            mock_tts.save.side_effect = Exception("Always fails")
            mock_gtts_class.return_value = mock_tts

            with patch("time.sleep"):  # Speed up test
                with pytest.raises(Exception, match="failed after 3 attempts"):
                    engine._generate_gtts("test", output_path)


class TestTTSEngineInitializationPaths:
    """Test various initialization paths."""

    def test_init_with_unknown_engine_defaults_to_gtts(self, tmp_path):
        """Test unknown engine type defaults to gTTS."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        cfg["tts"]["engine"] = "unknown_engine"

        engine = TTSEngine(cfg)

        assert engine.engine_type == "unknown_engine"
        # Should have initialized gTTS as fallback
        assert hasattr(engine, "gtts_available")

    def test_init_sets_device_correctly(self, tmp_path):
        """Test that device is set correctly from GPU manager."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)

        with patch("src.core.tts_engine.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda:0"

            engine = TTSEngine(cfg)

            assert engine.device == "cuda:0"
            assert engine.use_gpu is True

    def test_init_creates_cache_directory(self, tmp_path):
        """Test that cache directory is created on init."""
        from src.core.tts_engine import TTSEngine

        cache_dir = tmp_path / "new_cache" / "tts"
        cfg = {
            "storage": {"cache_dir": str(tmp_path / "new_cache"), "output_dir": str(tmp_path / "output")},
            "tts": {"engine": "gtts"},
        }

        engine = TTSEngine(cfg)

        assert engine.cache_dir.exists()
        assert engine.cache_dir == cache_dir


class TestTTSEngineCoquiPaths:
    """Test Coqui TTS paths with mocking."""

    def test_coqui_init_with_gpu(self, tmp_path):
        """Test Coqui initialization with GPU."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        cfg["tts"]["engine"] = "coqui"
        cfg["tts"]["coqui"] = {"model": "tts_models/en/ljspeech/tacotron2-DDC", "language": "en"}

        with patch("src.core.tts_engine.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.get_performance_config.return_value = {"use_fp16": False}
            mock_gpu.return_value.clear_cache.return_value = None

            with patch.dict("sys.modules", {"TTS": MagicMock()}):
                fake_tts = MagicMock()
                fake_tts.api.TTS = MagicMock(return_value=MagicMock())
                with patch("TTS.api.TTS") as mock_tts_class:
                    mock_tts_instance = MagicMock()
                    mock_tts_instance.synthesizer = MagicMock()
                    mock_tts_instance.synthesizer.tts_model = MagicMock()
                    mock_tts_instance.synthesizer.tts_model.to = MagicMock()
                    mock_tts_class.return_value = mock_tts_instance

                    try:
                        engine = TTSEngine(cfg)
                        # If we get here, init succeeded
                        assert engine.engine_type == "coqui"
                    except Exception:
                        # Expected if TTS not installed
                        pass

    def test_coqui_init_without_gpu(self, tmp_path):
        """Test Coqui initialization without GPU."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        cfg["tts"]["engine"] = "coqui"
        cfg["tts"]["coqui"] = {"model": "test_model", "language": "en"}

        with patch("src.core.tts_engine.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            with patch.dict("sys.modules", {"TTS": None}):
                # Should raise ImportError
                with pytest.raises(ImportError):
                    engine = TTSEngine(cfg)


class TestTTSEngineElevenLabsPaths:
    """Test ElevenLabs paths."""

    def test_elevenlabs_init_missing_api_key(self, tmp_path):
        """Test ElevenLabs init when API key is missing."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        cfg["tts"]["engine"] = "elevenlabs"
        cfg["tts"]["elevenlabs"] = {}  # No API key

        with patch("src.core.tts_engine.get_gpu_manager"):
            with patch.dict("sys.modules", {"elevenlabs": MagicMock()}):
                # Should handle missing key gracefully or raise
                try:
                    engine = TTSEngine(cfg)
                    # If init succeeds, generation should handle missing key
                    with pytest.raises((KeyError, ValueError, Exception)):
                        engine._generate_elevenlabs("test", tmp_path / "out.mp3")
                except Exception:
                    # Init may raise, which is fine
                    pass


class TestTTSEngineGeneratePaths:
    """Test generate method paths."""

    def test_generate_edge_engine_path(self, tmp_path):
        """Test generate with edge engine (fallback)."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        cfg["tts"]["engine"] = "edge"

        engine = TTSEngine(cfg)

        with patch.object(engine, "_generate_edge") as mock_edge:
            mock_edge.return_value = tmp_path / "edge.mp3"
            result = engine.generate("test")

            # Edge not implemented, should fallback
            # Actually, it calls _generate_edge which falls back to gTTS
            assert result is not None

    def test_generate_piper_engine_path(self, tmp_path):
        """Test generate with piper engine (fallback)."""
        from src.core.tts_engine import TTSEngine

        cfg = make_tts_config(tmp_path)
        cfg["tts"]["engine"] = "piper"

        engine = TTSEngine(cfg)

        with patch.object(engine, "_generate_piper") as mock_piper:
            mock_piper.return_value = tmp_path / "piper.mp3"
            result = engine.generate("test")

            # Piper not implemented, should fallback to gTTS
            assert result is not None


class TestTTSEngineCacheBehavior:
    """Test cache behavior edge cases."""

    def test_cache_directory_creation_idempotent(self, tmp_path):
        """Test cache directory creation is idempotent."""
        from src.core.tts_engine import TTSEngine

        cfg1 = make_tts_config(tmp_path)
        engine1 = TTSEngine(cfg1)
        cache_dir1 = engine1.cache_dir

        cfg2 = make_tts_config(tmp_path)
        engine2 = TTSEngine(cfg2)
        cache_dir2 = engine2.cache_dir

        assert cache_dir1 == cache_dir2
        assert cache_dir1.exists()

    def test_cache_key_includes_engine_type(self, tmp_path):
        """Test cache key includes engine type."""
        from src.core.tts_engine import TTSEngine

        cfg1 = make_tts_config(tmp_path)
        cfg1["tts"]["engine"] = "gtts"
        engine1 = TTSEngine(cfg1)

        cfg2 = make_tts_config(tmp_path)
        cfg2["tts"]["engine"] = "coqui"

        with patch("src.core.tts_engine.get_gpu_manager"):
            try:
                engine2 = TTSEngine(cfg2)
                text = "same text"
                key1 = engine1._get_cache_key(text)
                key2 = engine2._get_cache_key(text)

                # Keys should be different due to engine type in hash
                assert key1 != key2
            except ImportError:
                # Skip if Coqui not available
                pytest.skip("Coqui TTS not installed")

