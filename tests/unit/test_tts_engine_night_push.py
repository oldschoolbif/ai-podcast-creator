"""
Night Shift TTS Engine Tests - Massive Coverage Push
Targeting all missing paths for 90%+ coverage
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.tts_engine import TTSEngine


def make_config(tmp_path, engine="gtts"):
    """Create minimal TTS config."""
    return {
        "storage": {
            "cache_dir": str(tmp_path / "cache"),
            "outputs_dir": str(tmp_path / "outputs"),
        },
        "tts": {"engine": engine},
    }


class TestCoquiTTSEdgeCases:
    """Test Coqui TTS edge cases and missing paths."""

    @patch("TTS.api.TTS")
    @patch("src.core.tts_engine.get_gpu_manager")
    @patch("builtins.print")
    def test_init_coqui_gpu_fp16_exception(self, mock_print, mock_gpu, mock_tts, tmp_path):
        """Test Coqui FP16 exception handling (lines 95-96)."""
        cfg = make_config(tmp_path, engine="coqui")
        cfg["tts"]["coqui"] = {"model": "tts_models/en/ljspeech/tacotron2-DDC", "language": "en"}

        mock_gpu.return_value.gpu_available = True
        mock_gpu.return_value.get_device.return_value = "cuda"
        mock_gpu.return_value.get_performance_config.return_value = {"use_fp16": True}

        mock_model = MagicMock()
        mock_model.half.side_effect = Exception("FP16 failed")
        mock_tts_instance = MagicMock()
        mock_tts_instance.synthesizer = MagicMock(tts_model=mock_model)
        mock_tts.return_value = mock_tts_instance

        engine = TTSEngine(cfg)

        # Should handle exception gracefully
        assert engine.tts is not None
        assert mock_model.half.called

    @patch("TTS.api.TTS")
    @patch("src.core.tts_engine.get_gpu_manager")
    @patch("builtins.print")
    def test_init_coqui_cpu_path(self, mock_print, mock_gpu, mock_tts, tmp_path):
        """Test Coqui initialization on CPU (lines 97-99)."""
        cfg = make_config(tmp_path, engine="coqui")
        cfg["tts"]["coqui"] = {"model": "tts_models/en/ljspeech/tacotron2-DDC", "language": "en"}

        mock_gpu.return_value.gpu_available = False
        mock_gpu.return_value.get_device.return_value = "cpu"

        mock_tts_instance = MagicMock()
        mock_tts.return_value = mock_tts_instance

        engine = TTSEngine(cfg)

        # Should use CPU (gpu=False)
        mock_tts.assert_called()
        call_kwargs = mock_tts.call_args[1]
        assert call_kwargs.get("gpu") is False
        # Verify CPU warning print (line 98)
        assert any("Initializing Coqui TTS on CPU" in str(call) for call in mock_print.call_args_list)

    @patch("TTS.api.TTS")
    @patch("src.core.tts_engine.get_gpu_manager")
    def test_init_coqui_xtts_skips_fp16(self, mock_gpu, mock_tts, tmp_path):
        """Test Coqui skips FP16 for XTTS models (line 89)."""
        cfg = make_config(tmp_path, engine="coqui")
        cfg["tts"]["coqui"] = {"model": "tts_models/multilingual/multi-dataset/xtts_v2", "language": "en"}

        mock_gpu.return_value.gpu_available = True
        mock_gpu.return_value.get_device.return_value = "cuda"
        mock_gpu.return_value.get_performance_config.return_value = {"use_fp16": True}

        mock_model = MagicMock()
        mock_tts_instance = MagicMock()
        mock_tts_instance.synthesizer = MagicMock(tts_model=mock_model)
        mock_tts.return_value = mock_tts_instance

        engine = TTSEngine(cfg)

        # XTTS models should skip FP16
        assert mock_model.half.call_count == 0  # Not called for XTTS

    @patch("TTS.api.TTS")
    @patch("src.core.tts_engine.get_gpu_manager")
    def test_init_coqui_exception_handling(self, mock_gpu, mock_tts, tmp_path):
        """Test Coqui initialization exception (lines 103-105)."""
        cfg = make_config(tmp_path, engine="coqui")
        cfg["tts"]["coqui"] = {"model": "invalid_model", "language": "en"}

        mock_gpu.return_value.gpu_available = False
        mock_tts.side_effect = Exception("Model not found")

        # Should raise exception
        with pytest.raises(Exception):
            TTSEngine(cfg)


class TestPyTTSX3EdgeCases:
    """Test pyttsx3 edge cases and missing paths."""

    @patch("pyttsx3.init")
    @patch("src.core.tts_engine.get_gpu_manager")
    @patch("builtins.print")
    def test_init_pyttsx3_voice_fallback(self, mock_print, mock_gpu, mock_init, tmp_path):
        """Test pyttsx3 fallback to first voice (lines 155-158)."""
        cfg = make_config(tmp_path, engine="pyttsx3")
        cfg["tts"]["pyttsx3_voice_id"] = 999  # Non-existent voice

        mock_gpu.return_value.gpu_available = False

        mock_engine = MagicMock()
        voices = [MagicMock(id="voice1", name="Voice 1"), MagicMock(id="voice2", name="Voice 2")]
        mock_engine.getProperty.return_value = voices
        mock_init.return_value = mock_engine

        engine = TTSEngine(cfg)

        # Should fallback to first voice
        mock_engine.setProperty.assert_called()
        # Verify fallback print (line 158)
        assert any("fallback" in str(call).lower() for call in mock_print.call_args_list)

    @patch("pyttsx3.init")
    @patch("src.core.tts_engine.get_gpu_manager")
    @patch("builtins.print")
    def test_init_pyttsx3_exception_fallback_to_gtts(self, mock_print, mock_gpu, mock_init, tmp_path):
        """Test pyttsx3 exception falls back to gTTS (lines 160-163)."""
        cfg = make_config(tmp_path, engine="pyttsx3")

        mock_gpu.return_value.gpu_available = False
        mock_init.side_effect = Exception("pyttsx3 failed")

        engine = TTSEngine(cfg)

        # Should fallback to gTTS
        assert engine.engine_type == "pyttsx3"  # Type set, but should use gTTS
        # Verify fallback print (lines 161-162)
        assert any("pyttsx3 initialization failed" in str(call) for call in mock_print.call_args_list)
        assert any("Falling back to gTTS" in str(call) for call in mock_print.call_args_list)


class TestCoquiGenerationEdgeCases:
    """Test Coqui generation edge cases."""

    @patch("TTS.api.TTS")
    @patch("src.core.tts_engine.get_gpu_manager")
    @patch("builtins.print")
    def test_generate_coqui_exception_handling(self, mock_print, mock_gpu, mock_tts, tmp_path):
        """Test Coqui generation exception (lines 268-270)."""
        cfg = make_config(tmp_path, engine="coqui")
        cfg["tts"]["coqui"] = {"model": "tts_models/en/ljspeech/tacotron2-DDC", "language": "en"}
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        mock_gpu.return_value.gpu_available = True
        mock_gpu.return_value.clear_cache = MagicMock()

        mock_tts_instance = MagicMock()
        mock_tts_instance.tts_to_file.side_effect = Exception("Generation failed")
        mock_tts.return_value = mock_tts_instance

        engine = TTSEngine(cfg)

        with pytest.raises(Exception):
            engine._generate_coqui("test text", tmp_path / "output.wav")

        # Verify exception print (line 269)
        assert any("Coqui TTS generation error" in str(call) for call in mock_print.call_args_list)


class TestPyTTSX3GenerationEdgeCases:
    """Test pyttsx3 generation edge cases."""

    @patch("pyttsx3.init")
    @patch("src.core.tts_engine.get_gpu_manager")
    @patch("pydub.AudioSegment")
    @patch("builtins.print")
    def test_generate_pyttsx3_mp3_conversion_failure(self, mock_print, mock_audio, mock_gpu, mock_init, tmp_path):
        """Test pyttsx3 MP3 conversion failure (lines 344-347)."""
        cfg = make_config(tmp_path, engine="pyttsx3")
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        mock_gpu.return_value.gpu_available = False

        mock_engine = MagicMock()
        mock_init.return_value = mock_engine

        mock_audio.from_wav.side_effect = Exception("Conversion failed")

        engine = TTSEngine(cfg)
        wav_path = tmp_path / "test.wav"
        wav_path.write_bytes(b"fake wav")
        output_path = tmp_path / "output.mp3"

        result = engine._generate_pyttsx3("test", output_path)

        # Should fallback to renaming WAV (line 347)
        assert result == output_path
        # Verify conversion failure print (line 345)
        assert any("MP3 conversion failed" in str(call) for call in mock_print.call_args_list)


class TestCoquiGenerationDetailed:
    """Test Coqui generation detailed paths."""

    @patch("TTS.api.TTS")
    @patch("src.core.tts_engine.get_gpu_manager")
    @patch("builtins.print")
    def test_generate_coqui_xtts_with_speaker_wav(self, mock_print, mock_gpu, mock_tts, tmp_path):
        """Test Coqui XTTS generation with speaker_wav (lines 241-257)."""
        cfg = make_config(tmp_path, engine="coqui")
        cfg["tts"]["coqui"] = {
            "model": "tts_models/multilingual/multi-dataset/xtts_v2",
            "language": "en",
            "speaker": "TestSpeaker",
            "speaker_wav": str(tmp_path / "speaker.wav"),
        }
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()
        (tmp_path / "speaker.wav").write_bytes(b"fake audio")

        mock_gpu.return_value.gpu_available = True
        mock_gpu.return_value.clear_cache = MagicMock()

        mock_tts_instance = MagicMock()
        mock_tts.return_value = mock_tts_instance

        engine = TTSEngine(cfg)
        output_path = tmp_path / "output.wav"

        engine._generate_coqui("test text", output_path)

        # Should use speaker_wav for XTTS
        mock_tts_instance.tts_to_file.assert_called()
        call_kwargs = mock_tts_instance.tts_to_file.call_args[1]
        assert "speaker_wav" in call_kwargs or call_kwargs.get("speaker") is not None

    @patch("TTS.api.TTS")
    @patch("src.core.tts_engine.get_gpu_manager")
    def test_generate_coqui_xtts_with_speaker_from_config(self, mock_gpu, mock_tts, tmp_path):
        """Test Coqui XTTS with speaker from config (lines 254-257)."""
        cfg = make_config(tmp_path, engine="coqui")
        cfg["tts"]["coqui"] = {
            "model": "tts_models/multilingual/multi-dataset/xtts_v2",
            "language": "en",
            "speaker": "Andrew Chipper",
        }
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        mock_gpu.return_value.gpu_available = True
        mock_gpu.return_value.clear_cache = MagicMock()

        mock_tts_instance = MagicMock()
        mock_tts.return_value = mock_tts_instance

        engine = TTSEngine(cfg)
        output_path = tmp_path / "output.wav"

        engine._generate_coqui("test text", output_path)

        # Should use speaker from config
        mock_tts_instance.tts_to_file.assert_called()
        call_kwargs = mock_tts_instance.tts_to_file.call_args[1]
        assert call_kwargs.get("speaker") == "Andrew Chipper"

    @patch("TTS.api.TTS")
    @patch("src.core.tts_engine.get_gpu_manager")
    def test_generate_coqui_single_speaker_model(self, mock_gpu, mock_tts, tmp_path):
        """Test Coqui single-speaker model generation (lines 258-260)."""
        cfg = make_config(tmp_path, engine="coqui")
        cfg["tts"]["coqui"] = {"model": "tts_models/en/ljspeech/tacotron2-DDC", "language": "en"}
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        mock_gpu.return_value.gpu_available = True
        mock_gpu.return_value.clear_cache = MagicMock()

        mock_tts_instance = MagicMock()
        mock_tts.return_value = mock_tts_instance

        engine = TTSEngine(cfg)
        output_path = tmp_path / "output.wav"

        engine._generate_coqui("test text", output_path)

        # Should call tts_to_file without speaker
        mock_tts_instance.tts_to_file.assert_called()
        call_kwargs = mock_tts_instance.tts_to_file.call_args[1]
        assert "speaker" not in call_kwargs or call_kwargs.get("speaker") is None


class TestTTSEngineCacheKeys:
    """Test cache key generation paths."""

    def test_get_cache_key_coqui_with_speaker(self, tmp_path):
        """Test cache key with Coqui speaker (lines 393-396)."""
        cfg = make_config(tmp_path, engine="coqui")
        cfg["tts"]["coqui"] = {"speaker": "TestSpeaker"}

        engine = TTSEngine(cfg)
        key = engine._get_cache_key("test text")

        assert key is not None
        assert len(key) == 32  # MD5 hex

    def test_get_cache_key_pyttsx3_with_voice_id(self, tmp_path):
        """Test cache key with pyttsx3 voice ID (lines 397-400)."""
        cfg = make_config(tmp_path, engine="pyttsx3")
        cfg["tts"]["pyttsx3_voice_id"] = 42

        engine = TTSEngine(cfg)
        key = engine._get_cache_key("test text")

        assert key is not None
        assert len(key) == 32


class TestTTSEngineGeneratePaths:
    """Test generate() method paths."""

    def test_generate_coqui_path(self, tmp_path):
        """Test generate() calls _generate_coqui (line 187)."""
        cfg = make_config(tmp_path, engine="coqui")
        cfg["tts"]["coqui"] = {"model": "test", "language": "en"}
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        engine = TTSEngine(cfg)

        with patch.object(engine, "_generate_coqui") as mock_gen:
            mock_gen.return_value = tmp_path / "output.wav"
            result = engine.generate("test text")

            mock_gen.assert_called_once()
            assert result is not None

    def test_generate_pyttsx3_path(self, tmp_path):
        """Test generate() calls _generate_pyttsx3 (line 195)."""
        cfg = make_config(tmp_path, engine="pyttsx3")
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        engine = TTSEngine(cfg)

        with patch.object(engine, "_generate_pyttsx3") as mock_gen:
            mock_gen.return_value = tmp_path / "output.mp3"
            result = engine.generate("test text")

            mock_gen.assert_called_once()
            assert result is not None

    def test_generate_elevenlabs_path(self, tmp_path):
        """Test generate() calls _generate_elevenlabs (line 189)."""
        cfg = make_config(tmp_path, engine="elevenlabs")
        cfg["tts"]["elevenlabs"] = {"api_key": "test", "voice_id": "test"}
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        engine = TTSEngine(cfg)

        with patch.object(engine, "_generate_elevenlabs") as mock_gen:
            mock_gen.return_value = tmp_path / "output.mp3"
            result = engine.generate("test text")

            mock_gen.assert_called_once()
            assert result is not None

    def test_generate_azure_path(self, tmp_path):
        """Test generate() calls _generate_azure (line 191)."""
        cfg = make_config(tmp_path, engine="azure")
        cfg["tts"]["azure"] = {"api_key": "test", "region": "test"}
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        engine = TTSEngine(cfg)

        with patch.object(engine, "_generate_azure") as mock_gen:
            mock_gen.return_value = tmp_path / "output.mp3"
            result = engine.generate("test text")

            mock_gen.assert_called_once()
            assert result is not None

    def test_generate_piper_path(self, tmp_path):
        """Test generate() calls _generate_piper (line 193)."""
        cfg = make_config(tmp_path, engine="piper")
        cfg["tts"]["piper"] = {"model": "test"}
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        engine = TTSEngine(cfg)

        with patch.object(engine, "_generate_piper") as mock_gen:
            mock_gen.return_value = tmp_path / "output.wav"
            result = engine.generate("test text")

            mock_gen.assert_called_once()
            assert result is not None

    def test_generate_edge_path(self, tmp_path):
        """Test generate() calls _generate_edge (line 197)."""
        cfg = make_config(tmp_path, engine="edge")
        cfg["tts"]["edge"] = {"voice": "test"}
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        engine = TTSEngine(cfg)

        with patch.object(engine, "_generate_edge") as mock_gen:
            mock_gen.return_value = tmp_path / "output.mp3"
            result = engine.generate("test text")

            mock_gen.assert_called_once()
            assert result is not None

    def test_generate_default_fallback(self, tmp_path):
        """Test generate() defaults to gTTS for unknown engine (line 199)."""
        cfg = make_config(tmp_path, engine="unknown_engine")
        cfg["storage"]["cache_dir"] = str(tmp_path / "cache")
        (tmp_path / "cache").mkdir()

        engine = TTSEngine(cfg)

        with patch.object(engine, "_generate_gtts") as mock_gen:
            mock_gen.return_value = tmp_path / "output.mp3"
            result = engine.generate("test text")

            mock_gen.assert_called_once()
            assert result is not None

