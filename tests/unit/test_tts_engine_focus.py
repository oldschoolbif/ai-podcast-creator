import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def make_config(tmp_path):
    return {
        "storage": {
            "cache_dir": str(tmp_path / "cache"),
            "outputs_dir": str(tmp_path / "out"),
        },
        "tts": {"engine": "gtts", "gtts_tld": "com"},
    }


@pytest.mark.unit
def test_gtts_retry_then_success(tmp_path, monkeypatch):
    from src.core.tts_engine import TTSEngine

    calls = {"count": 0}

    class FakeGTTS:
        def __init__(self, *args, **kwargs):
            pass

        def save(self, path):
            calls["count"] += 1
            # Fail first two calls to exercise retry, succeed on third
            if calls["count"] < 3:
                raise Exception("network")
            Path(path).write_bytes(b"mp3")

    # Mock gtts and gpu manager
    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        with patch.dict(sys.modules, {"gtts": MagicMock(gTTS=FakeGTTS)}):
            cfg = make_config(tmp_path)
            engine = TTSEngine(cfg)
            out = engine.generate("hello")
            assert out.exists()
            assert calls["count"] == 3


@pytest.mark.unit
def test_cache_key_varies_by_engine(tmp_path):
    from src.core.tts_engine import TTSEngine

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        base = {"storage": {"cache_dir": str(tmp_path / "c"), "outputs_dir": str(tmp_path / "o")}}

        # gTTS
        cfg_g = {**base, "tts": {"engine": "gtts", "gtts_tld": "co.uk"}}
        g = TTSEngine(cfg_g)
        k1 = g._get_cache_key("text")

        # Edge includes voice name
        cfg_e = {**base, "tts": {"engine": "edge", "edge_voice": "en-US-GuyNeural"}}
        e = TTSEngine(cfg_e)
        k2 = e._get_cache_key("text")

        # ElevenLabs includes voice id (avoid initializing real SDK)
        cfg_el = {**base, "tts": {"engine": "elevenlabs", "elevenlabs": {"voice_id": "ABC"}}}
        with patch.object(TTSEngine, "_init_elevenlabs", return_value=None):
            el = TTSEngine(cfg_el)
        k3 = el._get_cache_key("text")

        assert k1 != k2 != k3


@pytest.mark.unit
def test_elevenlabs_missing_dependency(tmp_path):
    from src.core.tts_engine import TTSEngine

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        cfg = {
            "storage": {"cache_dir": str(tmp_path / "c"), "outputs_dir": str(tmp_path / "o")},
            "tts": {"engine": "elevenlabs", "elevenlabs": {"voice_id": "abc"}},
        }

        # Avoid import path by patching initializer to raise expected ImportError
        with patch.object(TTSEngine, "_init_elevenlabs", side_effect=ImportError("not installed")):
            with pytest.raises(ImportError):
                TTSEngine(cfg)


@pytest.mark.unit
def test_azure_missing_dependency(tmp_path):
    from src.core.tts_engine import TTSEngine

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        cfg = {
            "storage": {"cache_dir": str(tmp_path / "c"), "outputs_dir": str(tmp_path / "o")},
            "tts": {"engine": "azure", "azure": {"api_key": "x", "region": "eastus"}},
        }

        with patch.object(TTSEngine, "_init_azure", side_effect=ImportError("no azure")):
            with pytest.raises(ImportError):
                TTSEngine(cfg)


@pytest.mark.unit
def test_piper_placeholder_generation(tmp_path):
    from src.core.tts_engine import TTSEngine

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        cfg = make_config(tmp_path)
        cfg["tts"]["engine"] = "piper"

        engine = TTSEngine(cfg)
        out = engine.generate("hi there")
        # _generate_piper touches a file
        assert out.exists()


@pytest.mark.unit
@pytest.mark.skip(reason="pyttsx3 requires system TTS engine and module not available in CI")
def test_pyttsx3_conversion_fallback(tmp_path):
    from src.core.tts_engine import TTSEngine

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        cfg = make_config(tmp_path)
        cfg["tts"]["engine"] = "pyttsx3"

        # Stub pyttsx3 engine on instance and force pydub conversion to raise
        with patch.object(TTSEngine, "_init_pyttsx3", return_value=None):
            engine = TTSEngine(cfg)
            engine.pyttsx3_engine = MagicMock()

            # Make save_to_file produce a wav file that code later renames
            def save_to_file(text, path):
                Path(path).write_bytes(b"wav")

            engine.pyttsx3_engine.save_to_file.side_effect = save_to_file
            engine.pyttsx3_engine.runAndWait.return_value = None

            def raise_convert(*args, **kwargs):
                raise Exception("no ffmpeg")

            fake_audio = MagicMock()
            fake_audio.export.side_effect = raise_convert

            with patch.dict(sys.modules, {"pydub": MagicMock(AudioSegment=MagicMock(from_wav=MagicMock(return_value=fake_audio))) }):
                out = engine.generate("hello")
                assert out.exists()


@pytest.mark.unit
def test_elevenlabs_missing_api_key_raises_valueerror(tmp_path):
    from src.core.tts_engine import TTSEngine

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        cfg = {
            "storage": {"cache_dir": str(tmp_path / "c"), "outputs_dir": str(tmp_path / "o")},
            "tts": {"engine": "elevenlabs", "elevenlabs": {}},
        }

        # Mock elevenlabs import success, but no API key
        with patch.object(TTSEngine, "_init_elevenlabs", return_value=None):
            engine = TTSEngine(cfg)

            # Mock the imports inside _generate_elevenlabs
            fake_elevenlabs = MagicMock()
            fake_elevenlabs.client = MagicMock()
            fake_elevenlabs.client.ElevenLabs = MagicMock()
            fake_elevenlabs.VoiceSettings = MagicMock()

            with patch.dict(sys.modules, {"elevenlabs": fake_elevenlabs, "elevenlabs.client": fake_elevenlabs.client}):
                with patch("os.getenv", return_value=None):
                    with pytest.raises(ValueError, match="API key"):
                        engine._generate_elevenlabs("text", tmp_path / "out.mp3")


@pytest.mark.unit
def test_azure_speak_text_call_verified(tmp_path):
    from src.core.tts_engine import TTSEngine

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        cfg = {
            "storage": {"cache_dir": str(tmp_path / "c"), "outputs_dir": str(tmp_path / "o")},
            "tts": {"engine": "azure", "azure": {"api_key": "test", "region": "eastus"}},
        }

        fake_synthesizer = MagicMock()
        fake_audio_config = MagicMock()

        fake_azure_speech = MagicMock()
        fake_azure_speech.SpeechSynthesizer = MagicMock(return_value=fake_synthesizer)
        fake_azure_speech.audio = MagicMock()
        fake_azure_speech.audio.AudioOutputConfig = MagicMock(return_value=fake_audio_config)

        with patch.object(TTSEngine, "_init_azure", return_value=None):
            engine = TTSEngine(cfg)
            engine.speech_config = MagicMock()

            # Mock the azure module hierarchy so the import works
            fake_azure = MagicMock()
            fake_azure.cognitiveservices = MagicMock()
            fake_azure.cognitiveservices.speech = fake_azure_speech

            with patch.dict(
                sys.modules,
                {
                    "azure": fake_azure,
                    "azure.cognitiveservices": fake_azure.cognitiveservices,
                    "azure.cognitiveservices.speech": fake_azure_speech,
                },
            ):
                # Now when the method imports, it will get our mock
                out = engine._generate_azure("test text", tmp_path / "out.mp3")
                assert fake_synthesizer.speak_text.called
                assert fake_synthesizer.speak_text.call_args[0][0] == "test text"
                assert out == tmp_path / "out.mp3"


