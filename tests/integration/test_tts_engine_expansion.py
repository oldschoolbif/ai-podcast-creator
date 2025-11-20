"""
Integration tests for TTS Engine - Expand coverage to 80%+
Focus on missing generation paths and edge cases.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.tts_engine import TTSEngine


@pytest.fixture
def test_tts_config(tmp_path):
    """Create test TTS configuration."""
    return {
        "storage": {"cache_dir": str(tmp_path / "cache")},
        "tts": {
            "engine": "gtts",
            "gtts_tld": "com",
        },
    }


@pytest.mark.integration
class TestCoquiTTSEngineGeneration:
    """Test Coqui TTS generation paths."""

    def test_generate_coqui_xtts_with_speaker_wav(self, test_tts_config, tmp_path):
        """Test Coqui xtts generation with speaker_wav (line 260-263)."""
        test_tts_config["tts"]["engine"] = "coqui"
        test_tts_config["tts"]["coqui"] = {
            "model": "tts_models/multilingual/multi-dataset/xtts_v2",
            "language": "en",
            "speaker": "Andrew Chipper",
            "speaker_wav": str(tmp_path / "speaker.wav"),
        }

        speaker_wav = tmp_path / "speaker.wav"
        speaker_wav.write_bytes(b"fake speaker audio")
        output_path = tmp_path / "output.mp3"

        fake_gpu = MagicMock()
        fake_gpu.gpu_available = True
        fake_gpu.get_device.return_value = "cuda"
        fake_gpu.clear_cache = MagicMock()

        mock_tts = MagicMock()
        mock_tts.tts_to_file = MagicMock()

        with (
            patch("src.core.tts_engine.get_gpu_manager", return_value=fake_gpu),
            patch.dict("sys.modules", {"TTS": MagicMock(), "TTS.api": MagicMock()}),
            patch("torch.inference_mode") if "torch" in sys.modules else patch.dict("sys.modules", {"torch": MagicMock()}),
        ):
            # Mock TTS module before initialization
            mock_tts_module = MagicMock()
            mock_tts_module.api = MagicMock()
            mock_tts_module.api.TTS = MagicMock(return_value=mock_tts)
            sys.modules["TTS"] = mock_tts_module
            sys.modules["TTS.api"] = mock_tts_module.api
            
            try:
                engine = TTSEngine(test_tts_config)
            except (ImportError, Exception):
                # If initialization fails, create engine manually
                engine = TTSEngine.__new__(TTSEngine)
                engine.config = test_tts_config
                engine.engine_type = "coqui"
                engine.cache_dir = tmp_path / "cache" / "tts"
                engine.cache_dir.mkdir(parents=True, exist_ok=True)
                engine.gpu_manager = fake_gpu
                engine.device = "cuda"
                engine.use_gpu = True
            
            engine.tts = mock_tts
            result = engine._generate_coqui("Test text", output_path)

            assert result == output_path
            # Should use speaker_wav
            mock_tts.tts_to_file.assert_called_once()
            call_kwargs = mock_tts.tts_to_file.call_args[1]
            assert "speaker_wav" in call_kwargs
            assert call_kwargs["speaker_wav"] == str(speaker_wav)
            # GPU cache should be cleared before and after
            assert fake_gpu.clear_cache.call_count >= 1

    def test_generate_coqui_xtts_without_speaker_wav(self, test_tts_config, tmp_path):
        """Test Coqui xtts generation without speaker_wav, using speaker (line 265-268)."""
        test_tts_config["tts"]["engine"] = "coqui"
        test_tts_config["tts"]["coqui"] = {
            "model": "tts_models/multilingual/multi-dataset/xtts_v2",
            "language": "en",
            "speaker": "Andrew Chipper",
        }

        output_path = tmp_path / "output.mp3"

        fake_gpu = MagicMock()
        fake_gpu.gpu_available = True
        fake_gpu.get_device.return_value = "cuda"
        fake_gpu.clear_cache = MagicMock()

        mock_tts = MagicMock()
        mock_tts.tts_to_file = MagicMock()

        with (
            patch("src.core.tts_engine.get_gpu_manager", return_value=fake_gpu),
            patch.dict("sys.modules", {"TTS": MagicMock(), "TTS.api": MagicMock()}),
            patch("torch.inference_mode") if "torch" in sys.modules else patch.dict("sys.modules", {"torch": MagicMock()}),
        ):
            # Mock TTS module before initialization
            mock_tts_module = MagicMock()
            mock_tts_module.api = MagicMock()
            mock_tts_module.api.TTS = MagicMock(return_value=mock_tts)
            sys.modules["TTS"] = mock_tts_module
            sys.modules["TTS.api"] = mock_tts_module.api
            
            try:
                engine = TTSEngine(test_tts_config)
            except (ImportError, Exception):
                # If initialization fails, create engine manually
                engine = TTSEngine.__new__(TTSEngine)
                engine.config = test_tts_config
                engine.engine_type = "coqui"
                engine.cache_dir = tmp_path / "cache" / "tts"
                engine.cache_dir.mkdir(parents=True, exist_ok=True)
                engine.gpu_manager = fake_gpu
                engine.device = "cuda"
                engine.use_gpu = True
            
            engine.tts = mock_tts
            result = engine._generate_coqui("Test text", output_path)

            assert result == output_path
            # Should use speaker from config
            mock_tts.tts_to_file.assert_called_once()
            call_kwargs = mock_tts.tts_to_file.call_args[1]
            assert "speaker" in call_kwargs
            assert call_kwargs["speaker"] == "Andrew Chipper"

    def test_generate_coqui_non_xtts_model(self, test_tts_config, tmp_path):
        """Test Coqui non-xtts model generation (line 270-271)."""
        test_tts_config["tts"]["engine"] = "coqui"
        test_tts_config["tts"]["coqui"] = {
            "model": "tts_models/en/ljspeech/tacotron2-DDC",
            "language": "en",
        }

        output_path = tmp_path / "output.mp3"

        fake_gpu = MagicMock()
        fake_gpu.gpu_available = False
        fake_gpu.get_device.return_value = "cpu"

        mock_tts = MagicMock()
        mock_tts.tts_to_file = MagicMock()

        with (
            patch("src.core.tts_engine.get_gpu_manager", return_value=fake_gpu),
            patch.dict("sys.modules", {"TTS": MagicMock(), "TTS.api": MagicMock()}),
            patch("torch.inference_mode") if "torch" in sys.modules else patch.dict("sys.modules", {"torch": MagicMock()}),
        ):
            # Mock TTS module before initialization
            mock_tts_module = MagicMock()
            mock_tts_module.api = MagicMock()
            mock_tts_module.api.TTS = MagicMock(return_value=mock_tts)
            sys.modules["TTS"] = mock_tts_module
            sys.modules["TTS.api"] = mock_tts_module.api
            
            try:
                engine = TTSEngine(test_tts_config)
            except (ImportError, Exception):
                # If initialization fails, create engine manually
                engine = TTSEngine.__new__(TTSEngine)
                engine.config = test_tts_config
                engine.engine_type = "coqui"
                engine.cache_dir = tmp_path / "cache" / "tts"
                engine.cache_dir.mkdir(parents=True, exist_ok=True)
                engine.gpu_manager = fake_gpu
                engine.device = "cuda"
                engine.use_gpu = True
            
            engine.tts = mock_tts
            result = engine._generate_coqui("Test text", output_path)

            assert result == output_path
            # Should not have speaker or speaker_wav for non-xtts
            mock_tts.tts_to_file.assert_called_once()
            call_kwargs = mock_tts.tts_to_file.call_args[1]
            assert "speaker" not in call_kwargs
            assert "speaker_wav" not in call_kwargs

    def test_generate_coqui_gpu_cache_clearing(self, test_tts_config, tmp_path):
        """Test Coqui GPU cache clearing before and after generation (lines 246-247, 274-275)."""
        test_tts_config["tts"]["engine"] = "coqui"
        test_tts_config["tts"]["coqui"] = {"model": "tts_models/en/ljspeech/tacotron2-DDC"}

        output_path = tmp_path / "output.mp3"

        fake_gpu = MagicMock()
        fake_gpu.gpu_available = True
        fake_gpu.get_device.return_value = "cuda"
        fake_gpu.clear_cache = MagicMock()

        mock_tts = MagicMock()
        mock_tts.tts_to_file = MagicMock()

        with (
            patch("src.core.tts_engine.get_gpu_manager", return_value=fake_gpu),
            patch.dict("sys.modules", {"TTS": MagicMock(), "TTS.api": MagicMock()}),
            patch("torch.inference_mode") if "torch" in sys.modules else patch.dict("sys.modules", {"torch": MagicMock()}),
        ):
            # Mock TTS module before initialization
            mock_tts_module = MagicMock()
            mock_tts_module.api = MagicMock()
            mock_tts_module.api.TTS = MagicMock(return_value=mock_tts)
            sys.modules["TTS"] = mock_tts_module
            sys.modules["TTS.api"] = mock_tts_module.api
            
            try:
                engine = TTSEngine(test_tts_config)
            except (ImportError, Exception):
                # If initialization fails, create engine manually
                engine = TTSEngine.__new__(TTSEngine)
                engine.config = test_tts_config
                engine.engine_type = "coqui"
                engine.cache_dir = tmp_path / "cache" / "tts"
                engine.cache_dir.mkdir(parents=True, exist_ok=True)
                engine.gpu_manager = fake_gpu
                engine.device = "cuda"
                engine.use_gpu = True
            
            engine.tts = mock_tts
            initial_cache_calls = fake_gpu.clear_cache.call_count
            result = engine._generate_coqui("Test text", output_path)

            assert result == output_path
            # Should clear cache at least once (before generation)
            assert fake_gpu.clear_cache.call_count > initial_cache_calls

    def test_generate_coqui_exception_handling(self, test_tts_config, tmp_path):
        """Test Coqui generation exception handling (line 279-281)."""
        test_tts_config["tts"]["engine"] = "coqui"
        test_tts_config["tts"]["coqui"] = {"model": "test_model"}

        output_path = tmp_path / "output.mp3"

        fake_gpu = MagicMock()
        fake_gpu.gpu_available = False

        mock_tts = MagicMock()
        mock_tts.tts_to_file.side_effect = Exception("Generation failed")

        with (
            patch("src.core.tts_engine.get_gpu_manager", return_value=fake_gpu),
            patch.dict("sys.modules", {"TTS": MagicMock(), "TTS.api": MagicMock()}) if "TTS" not in sys.modules else MagicMock(),
            patch("torch.inference_mode") if "torch" in sys.modules else patch.dict("sys.modules", {"torch": MagicMock()}),
            patch("builtins.print") as mock_print,
        ):
            # Mock TTS import before initialization
            if "TTS" not in sys.modules:
                mock_tts_module = MagicMock()
                mock_tts_module.api = MagicMock()
                mock_tts_module.api.TTS = MagicMock(return_value=mock_tts)
                sys.modules["TTS"] = mock_tts_module
                sys.modules["TTS.api"] = mock_tts_module.api
            
            engine = TTSEngine(test_tts_config)
            engine.tts = mock_tts

            with pytest.raises(Exception, match="Generation failed"):
                engine._generate_coqui("Test text", output_path)

            # Should print error message
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Coqui TTS generation error" in call for call in print_calls)


@pytest.mark.integration
class TestElevenLabsTTSEngineGeneration:
    """Test ElevenLabs TTS generation paths."""

    def test_generate_elevenlabs_with_config_api_key(self, test_tts_config, tmp_path):
        """Test ElevenLabs generation with API key from config (line 291)."""
        test_tts_config["tts"]["engine"] = "elevenlabs"
        test_tts_config["tts"]["elevenlabs"] = {
            "api_key": "test_api_key",
            "voice_id": "test_voice",
            "model": "eleven_turbo_v2_5",
            "stability": 0.7,
            "similarity_boost": 0.8,
        }

        output_path = tmp_path / "output.mp3"
        output_path.write_bytes(b"fake audio")

        with (
            patch.dict("sys.modules", {"elevenlabs": MagicMock(), "elevenlabs.client": MagicMock(), "elevenlabs.set_api_key": MagicMock()}),
        ):
            # Mock elevenlabs module
            mock_elevenlabs = MagicMock()
            mock_elevenlabs.set_api_key = MagicMock()
            mock_client_class = MagicMock()
            sys.modules["elevenlabs"] = mock_elevenlabs
            sys.modules["elevenlabs.client"] = MagicMock()
            from elevenlabs import VoiceSettings
            from elevenlabs.client import ElevenLabs
            mock_client_class = ElevenLabs
            mock_client = MagicMock()
            mock_audio_gen = [b"chunk1", b"chunk2"]
            mock_client.text_to_speech.convert.return_value = iter(mock_audio_gen)
            mock_client_class.return_value = mock_client
            patch("elevenlabs.client.ElevenLabs", return_value=mock_client).start()
            patch("elevenlabs.set_api_key").start()
            mock_client = MagicMock()
            mock_audio_gen = [b"chunk1", b"chunk2"]
            mock_client.text_to_speech.convert.return_value = iter(mock_audio_gen)
            mock_client_class.return_value = mock_client

            engine = TTSEngine(test_tts_config)
            result = engine._generate_elevenlabs("Test text", output_path)

            assert result == output_path
            # Should use API key from config
            mock_client.text_to_speech.convert.assert_called_once()

    def test_generate_elevenlabs_with_env_api_key(self, test_tts_config, tmp_path):
        """Test ElevenLabs generation with API key from environment (line 293)."""
        test_tts_config["tts"]["engine"] = "elevenlabs"
        test_tts_config["tts"]["elevenlabs"] = {}  # No API key in config

        output_path = tmp_path / "output.mp3"
        output_path.write_bytes(b"fake audio")

        with (
            patch("elevenlabs.client.ElevenLabs") as mock_client_class,
            patch("elevenlabs.set_api_key"),
            patch.dict("os.environ", {"ELEVENLABS_API_KEY": "env_api_key"}),
            patch("os.getenv", return_value="env_api_key"),
        ):
            mock_client = MagicMock()
            mock_audio_gen = [b"chunk1"]
            mock_client.text_to_speech.convert.return_value = iter(mock_audio_gen)
            mock_client_class.return_value = mock_client

            engine = TTSEngine(test_tts_config)
            result = engine._generate_elevenlabs("Test text", output_path)

            assert result == output_path

    def test_generate_elevenlabs_missing_api_key(self, test_tts_config, tmp_path):
        """Test ElevenLabs generation raises error when API key missing (line 295-296)."""
        test_tts_config["tts"]["engine"] = "elevenlabs"
        test_tts_config["tts"]["elevenlabs"] = {}

        output_path = tmp_path / "output.mp3"

        with (
            patch.dict("os.environ", {}, clear=True),
            patch("os.getenv", return_value=None),
        ):
            engine = TTSEngine(test_tts_config)

            with pytest.raises(ValueError, match="ElevenLabs API key not found"):
                engine._generate_elevenlabs("Test text", output_path)

    def test_generate_elevenlabs_voice_settings(self, test_tts_config, tmp_path):
        """Test ElevenLabs uses voice settings from config (lines 299-302)."""
        test_tts_config["tts"]["engine"] = "elevenlabs"
        test_tts_config["tts"]["elevenlabs"] = {
            "api_key": "test_key",
            "voice_id": "custom_voice",
            "model": "custom_model",
            "stability": 0.6,
            "similarity_boost": 0.9,
        }

        output_path = tmp_path / "output.mp3"

        with (
            patch("elevenlabs.client.ElevenLabs") as mock_client_class,
            patch("elevenlabs.set_api_key"),
            patch("elevenlabs.VoiceSettings"),
        ):
            mock_client = MagicMock()
            mock_audio_gen = [b"chunk1"]
            mock_client.text_to_speech.convert.return_value = iter(mock_audio_gen)
            mock_client_class.return_value = mock_client

            engine = TTSEngine(test_tts_config)
            result = engine._generate_elevenlabs("Test text", output_path)

            assert result == output_path
            # Verify voice settings were used
            call_args = mock_client.text_to_speech.convert.call_args
            assert call_args[1]["voice_id"] == "custom_voice"
            assert call_args[1]["model_id"] == "custom_model"


@pytest.mark.integration
class TestAzureTTSEngineGeneration:
    """Test Azure TTS generation paths."""

    def test_generate_azure_full_path(self, test_tts_config, tmp_path):
        """Test Azure generation full path (lines 324-331)."""
        test_tts_config["tts"]["engine"] = "azure"
        test_tts_config["tts"]["azure"] = {"api_key": "test_key", "region": "eastus"}

        output_path = tmp_path / "output.mp3"

        with (
            patch("azure.cognitiveservices.speech.SpeechConfig") as mock_speech_config,
            patch("azure.cognitiveservices.speech.audio.AudioOutputConfig") as mock_audio_config,
            patch("azure.cognitiveservices.speech.SpeechSynthesizer") as mock_synthesizer_class,
        ):
            mock_synthesizer = MagicMock()
            mock_synthesizer_class.return_value = mock_synthesizer

            engine = TTSEngine(test_tts_config)
            result = engine._generate_azure("Test text", output_path)

            assert result == output_path
            mock_synthesizer.speak_text.assert_called_once_with("Test text")


@pytest.mark.integration
class TestEdgeTTSEngineGeneration:
    """Test Edge TTS generation paths."""

    def test_generate_edge_async_generation(self, test_tts_config, tmp_path):
        """Test Edge TTS async generation (lines 373-379)."""
        test_tts_config["tts"]["engine"] = "edge"
        test_tts_config["tts"]["edge_voice"] = "en-US-GuyNeural"
        test_tts_config["tts"]["edge_rate"] = "+10%"
        test_tts_config["tts"]["edge_pitch"] = "+5Hz"

        output_path = tmp_path / "output.mp3"

        with (
            patch("edge_tts.Communicate") as mock_communicate_class,
            patch("asyncio.run") as mock_asyncio_run,
        ):
            mock_communicate = AsyncMock()
            mock_communicate.save = AsyncMock()
            mock_communicate_class.return_value = mock_communicate

            async def mock_run(coro):
                await coro

            mock_asyncio_run.side_effect = mock_run

            engine = TTSEngine(test_tts_config)
            result = engine._generate_edge("Test text", output_path)

            assert result == output_path
            # Verify voice, rate, and pitch from config
            mock_communicate_class.assert_called_once_with(
                "Test text", "en-US-GuyNeural", rate="+10%", pitch="+5Hz"
            )

    def test_generate_edge_event_loop_existing(self, test_tts_config, tmp_path):
        """Test Edge TTS when event loop already exists (lines 380-383)."""
        test_tts_config["tts"]["engine"] = "edge"

        output_path = tmp_path / "output.mp3"

        with (
            patch("edge_tts.Communicate") as mock_communicate_class,
            patch("asyncio.run", side_effect=RuntimeError("Event loop already exists")),
            patch("asyncio.get_event_loop") as mock_get_loop,
        ):
            mock_communicate = AsyncMock()
            mock_communicate.save = AsyncMock()
            mock_communicate_class.return_value = mock_communicate

            mock_loop = MagicMock()
            mock_loop.run_until_complete = MagicMock()
            mock_get_loop.return_value = mock_loop

            engine = TTSEngine(test_tts_config)
            result = engine._generate_edge("Test text", output_path)

            assert result == output_path
            # Should use existing event loop
            mock_loop.run_until_complete.assert_called_once()


@pytest.mark.integration
class TestPyttsx3TTSEngineGeneration:
    """Test pyttsx3 TTS generation paths."""

    def test_generate_pyttsx3_wav_to_mp3_conversion_success(self, test_tts_config, tmp_path):
        """Test pyttsx3 WAV to MP3 conversion success (lines 349-354)."""
        test_tts_config["tts"]["engine"] = "pyttsx3"

        output_path = tmp_path / "output.mp3"
        wav_path = tmp_path / "output.wav"
        wav_path.write_bytes(b"fake wav")

        mock_engine = MagicMock()
        mock_engine.save_to_file = MagicMock()
        mock_engine.runAndWait = MagicMock()

        with (
            patch("pyttsx3.init", return_value=mock_engine),
            patch("pydub.AudioSegment.from_wav") as mock_audio_segment,
        ):
            mock_audio = MagicMock()
            mock_audio.export = MagicMock()
            mock_audio_segment.return_value = mock_audio

            engine = TTSEngine(test_tts_config)
            result = engine._generate_pyttsx3("Test text", output_path)

            assert result == output_path
            # Should convert WAV to MP3
            mock_audio.export.assert_called_once_with(str(output_path), format="mp3")

    def test_generate_pyttsx3_wav_to_mp3_conversion_failure(self, test_tts_config, tmp_path):
        """Test pyttsx3 WAV to MP3 conversion failure fallback (lines 355-358)."""
        test_tts_config["tts"]["engine"] = "pyttsx3"

        output_path = tmp_path / "output.mp3"
        wav_path = tmp_path / "output.wav"
        wav_path.write_bytes(b"fake wav")

        mock_engine = MagicMock()
        mock_engine.save_to_file = MagicMock()
        mock_engine.runAndWait = MagicMock()

        with (
            patch("pyttsx3.init", return_value=mock_engine),
            patch("pydub.AudioSegment.from_wav", side_effect=Exception("Conversion failed")),
            patch("builtins.print") as mock_print,
        ):
            engine = TTSEngine(test_tts_config)
            result = engine._generate_pyttsx3("Test text", output_path)

            # Should fallback to WAV (rename)
            assert result == output_path
            # Should print warning
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("MP3 conversion failed" in call for call in print_calls)


@pytest.mark.integration
class TestTTSEngineCacheKeyGeneration:
    """Test TTS engine cache key generation with voice parameters."""

    def test_cache_key_gtts_with_tld(self, test_tts_config, tmp_path):
        """Test cache key includes TLD for gTTS (lines 400-403)."""
        test_tts_config["tts"]["engine"] = "gtts"
        test_tts_config["tts"]["gtts_tld"] = "co.uk"

        engine = TTSEngine(test_tts_config)

        key1 = engine._get_cache_key("test text")
        test_tts_config["tts"]["gtts_tld"] = "com"
        engine2 = TTSEngine(test_tts_config)
        key2 = engine2._get_cache_key("test text")

        # Different TLD should give different cache keys
        assert key1 != key2

    def test_cache_key_coqui_with_speaker(self, test_tts_config, tmp_path):
        """Test cache key includes speaker for Coqui (lines 404-407)."""
        test_tts_config["tts"]["engine"] = "coqui"
        test_tts_config["tts"]["coqui"] = {"model": "test", "speaker": "Speaker1"}

        fake_gpu = MagicMock()
        fake_gpu.gpu_available = False

        with (
            patch("src.core.tts_engine.get_gpu_manager", return_value=fake_gpu),
            patch.dict("sys.modules", {"TTS": MagicMock(), "TTS.api": MagicMock()}),
        ):
            # Mock TTS module before initialization
            mock_tts_module = MagicMock()
            mock_tts_module.api = MagicMock()
            mock_tts_module.api.TTS = MagicMock()
            sys.modules["TTS"] = mock_tts_module
            sys.modules["TTS.api"] = mock_tts_module.api
            
            try:
                engine = TTSEngine(test_tts_config)
            except (ImportError, Exception):
                # If initialization fails, create engine manually
                engine = TTSEngine.__new__(TTSEngine)
                engine.config = test_tts_config
                engine.engine_type = "coqui"
                engine.cache_dir = tmp_path / "cache" / "tts"
                engine.cache_dir.mkdir(parents=True, exist_ok=True)
                engine.gpu_manager = fake_gpu
                engine.device = "cpu"
                engine.use_gpu = False
            
            engine = TTSEngine(test_tts_config)
            key1 = engine._get_cache_key("test text")

            test_tts_config["tts"]["coqui"]["speaker"] = "Speaker2"
            engine2 = TTSEngine(test_tts_config)
            key2 = engine2._get_cache_key("test text")

            # Different speaker should give different cache keys
            assert key1 != key2

    def test_cache_key_elevenlabs_with_voice_id(self, test_tts_config, tmp_path):
        """Test cache key includes voice_id for ElevenLabs (lines 416-419)."""
        test_tts_config["tts"]["engine"] = "elevenlabs"
        test_tts_config["tts"]["elevenlabs"] = {"api_key": "test", "voice_id": "voice1"}

        with patch("elevenlabs.set_api_key"):
            engine = TTSEngine(test_tts_config)
            key1 = engine._get_cache_key("test text")

            test_tts_config["tts"]["elevenlabs"]["voice_id"] = "voice2"
            engine2 = TTSEngine(test_tts_config)
            key2 = engine2._get_cache_key("test text")

            # Different voice_id should give different cache keys
            assert key1 != key2

