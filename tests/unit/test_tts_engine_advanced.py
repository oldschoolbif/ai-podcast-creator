import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def make_config(tmp_path, engine="gtts"):
    cache = tmp_path / "cache"
    cache.mkdir(exist_ok=True)
    return {
        "storage": {"cache_dir": str(cache), "outputs_dir": str(tmp_path / "outputs")},
        "tts": {"engine": engine},
    }


@pytest.mark.unit
def test_init_coqui_gpu_fp16_enables_mixed_precision(tmp_path):
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path, engine="coqui")
    cfg["tts"]["coqui"] = {"model": "my_model", "language": "en"}

    fake_gpu = MagicMock()
    fake_gpu.gpu_available = True
    fake_gpu.get_device.return_value = "cuda"
    fake_gpu.get_performance_config.return_value = {"use_fp16": True}

    class DummyModel:
        def __init__(self):
            self.to_called = False
            self.half_called = False

        def to(self, device):
            self.to_called = True
            self.device = device

        def half(self):
            self.half_called = True

    dummy_model = DummyModel()
    fake_tts_instance = MagicMock()
    fake_tts_instance.synthesizer = MagicMock(tts_model=dummy_model)

    def fake_tts_factory(model_name, gpu=True, progress_bar=True):
        return fake_tts_instance

    fake_TTS_module = ModuleType("TTS")
    fake_TTS_api = ModuleType("TTS.api")
    fake_TTS_api.TTS = fake_tts_factory
    fake_TTS_module.api = fake_TTS_api

    class FakeInference:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    fake_torch = SimpleNamespace(
        inference_mode=lambda: FakeInference(),
        backends=SimpleNamespace(),
    )

    with patch.dict(sys.modules, {"TTS": fake_TTS_module, "TTS.api": fake_TTS_api, "torch": fake_torch}):
        with patch("src.core.tts_engine.get_gpu_manager", return_value=fake_gpu):
            engine = TTSEngine(cfg)

    assert engine.tts is fake_tts_instance
    assert dummy_model.to_called is True
    assert dummy_model.half_called is True


@pytest.mark.unit
def test_generate_coqui_xtts_with_reference_audio(tmp_path):
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path)
    engine = TTSEngine(cfg)

    engine.engine_type = "coqui"
    engine.use_gpu = True
    engine.gpu_manager = MagicMock()
    engine.gpu_manager.clear_cache = MagicMock()
    speaker_wav = tmp_path / "speaker.wav"
    speaker_wav.write_bytes(b"wav")
    engine.config.setdefault("tts", {})["coqui"] = {
        "model": "xtts_v2",
        "language": "en",
        "speaker": "TestSpeaker",
        "speaker_wav": str(speaker_wav),
    }

    class DummyCoqui:
        def __init__(self):
            self.calls = []

        def tts_to_file(self, text, file_path, **kwargs):
            Path(file_path).write_bytes(b"coqui")
            self.calls.append((text, file_path, kwargs))

    engine.tts = DummyCoqui()

    class FakeInference:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    fake_torch = SimpleNamespace(inference_mode=lambda: FakeInference())

    with patch.dict(sys.modules, {"torch": fake_torch}):
        out = engine._generate_coqui("hello", tmp_path / "out.mp3")

    assert out.exists()
    engine.gpu_manager.clear_cache.assert_called()


@pytest.mark.unit
def test_generate_coqui_single_speaker(tmp_path):
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path)
    engine = TTSEngine(cfg)
    engine.engine_type = "coqui"
    engine.use_gpu = False
    engine.gpu_manager = MagicMock()
    engine.config.setdefault("tts", {})["coqui"] = {
        "model": "tacotron2",
        "language": "en",
        "speaker": "Solo",
    }

    class DummyCoqui:
        def __init__(self):
            self.calls = []

        def tts_to_file(self, text, file_path, **kwargs):
            Path(file_path).write_bytes(b"coqui")
            self.calls.append((text, file_path, kwargs))

    engine.tts = DummyCoqui()

    class FakeInference:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    fake_torch = SimpleNamespace(inference_mode=lambda: FakeInference())

    with patch.dict(sys.modules, {"torch": fake_torch}):
        out = engine._generate_coqui("hello", tmp_path / "solo.mp3")

    assert out.exists()


@pytest.mark.unit
def test_elevenlabs_generate_success(tmp_path):
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path, engine="elevenlabs")
    cfg["tts"]["elevenlabs"] = {"api_key": "abc", "voice_id": "voice123", "model": "fast"}

    class DummyVoiceSettings:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class DummyTextToSpeech:
        def convert(self, **kwargs):
            yield b"audio"

    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.text_to_speech = DummyTextToSpeech()

    fake_elevenlabs = ModuleType("elevenlabs")
    fake_elevenlabs.VoiceSettings = DummyVoiceSettings
    fake_elevenlabs.generate = lambda *args, **kwargs: None
    fake_elevenlabs.set_api_key = lambda key: None
    fake_elevenlabs_client = ModuleType("elevenlabs.client")
    fake_elevenlabs_client.ElevenLabs = DummyClient

    with patch.dict(sys.modules, {"elevenlabs": fake_elevenlabs, "elevenlabs.client": fake_elevenlabs_client}):
        with patch("src.core.tts_engine.get_gpu_manager"):
            engine = TTSEngine(cfg)
            out = engine._generate_elevenlabs("hello", tmp_path / "eleven.mp3")

    assert out.exists()


@pytest.mark.unit
def test_elevenlabs_generate_missing_key_raises(tmp_path):
    from src.core.tts_engine import TTSEngine

    base_cfg = make_config(tmp_path)
    engine = TTSEngine(base_cfg)
    engine.engine_type = "elevenlabs"
    engine.config.setdefault("tts", {}).setdefault("elevenlabs", {})

    class DummyVoiceSettings:
        def __init__(self, **kwargs):
            pass

    class DummyClient:
        def __init__(self, api_key):
            self.text_to_speech = SimpleNamespace(convert=lambda **_: iter([b"data"]))

    fake_elevenlabs = ModuleType("elevenlabs")
    fake_elevenlabs.VoiceSettings = DummyVoiceSettings
    fake_elevenlabs.generate = lambda *args, **kwargs: None
    fake_elevenlabs.set_api_key = lambda key: None
    fake_elevenlabs_client = ModuleType("elevenlabs.client")
    fake_elevenlabs_client.ElevenLabs = DummyClient

    with patch.dict(sys.modules, {"elevenlabs": fake_elevenlabs, "elevenlabs.client": fake_elevenlabs_client}):
        with pytest.raises(ValueError):
            engine._generate_elevenlabs("hi", tmp_path / "fail.mp3")


@pytest.mark.unit
def test_azure_generate_success(tmp_path):
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path, engine="azure")
    cfg["tts"]["azure"] = {"api_key": "key", "region": "westus"}

    class DummyAudioOutput:
        def __init__(self, filename):
            self.filename = filename

    class DummySynthesizer:
        def __init__(self, speech_config, audio_config):
            self.speech_config = speech_config
            self.audio_config = audio_config
            self.spoken = []

        def speak_text(self, text):
            self.spoken.append(text)
            Path(self.audio_config.filename).write_bytes(b"azure")

    fake_audio_module = SimpleNamespace(AudioOutputConfig=lambda filename: DummyAudioOutput(filename))

    class DummySpeechConfig:
        def __init__(self, subscription, region):
            self.subscription = subscription
            self.region = region

    def fake_synthesizer(speech_config, audio_config):
        return DummySynthesizer(speech_config, audio_config)

    fake_speechsdk = ModuleType("azure.cognitiveservices.speech")
    fake_speechsdk.audio = fake_audio_module
    fake_speechsdk.SpeechConfig = DummySpeechConfig
    fake_speechsdk.SpeechSynthesizer = fake_synthesizer

    fake_azure = ModuleType("azure")
    fake_cognitiveservices = ModuleType("azure.cognitiveservices")
    fake_azure.cognitiveservices = fake_cognitiveservices
    fake_cognitiveservices.speech = fake_speechsdk

    with patch.dict(
        sys.modules,
        {
            "azure": fake_azure,
            "azure.cognitiveservices": fake_cognitiveservices,
            "azure.cognitiveservices.speech": fake_speechsdk,
        },
    ):
        with patch("src.core.tts_engine.get_gpu_manager"):
            engine = TTSEngine(cfg)
            out = engine._generate_azure("hello", tmp_path / "azure.mp3")

    assert out.exists()


@pytest.mark.unit
def test_piper_generate_creates_file(tmp_path):
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path)
    engine = TTSEngine(cfg)
    out = engine._generate_piper("hello", tmp_path / "piper.mp3")
    assert out.exists()


@pytest.mark.unit
def test_pyttsx3_generate_success(tmp_path):
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path, engine="pyttsx3")
    cfg["tts"].update({"pyttsx3_voice_id": 0, "pyttsx3_rate": 150})

    class DummyVoice:
        def __init__(self, name):
            self.name = name
            self.id = name

    class DummyEngine:
        def __init__(self):
            self.voices = [DummyVoice("Voice")]
            self.saved_paths = []

        def getProperty(self, name):
            if name == "voices":
                return self.voices
            return []

        def setProperty(self, name, value):
            pass

        def save_to_file(self, text, path):
            Path(path).write_bytes(b"wav")
            self.saved_paths.append(path)

        def runAndWait(self):
            pass

    class DummyAudioSegment:
        @staticmethod
        def from_wav(path):
            class DummyAudio:
                def export(self, output_path, format="mp3"):
                    Path(output_path).write_bytes(b"mp3")

            return DummyAudio()

    fake_pyttsx3 = ModuleType("pyttsx3")
    fake_pyttsx3.init = lambda: DummyEngine()

    fake_pydub = ModuleType("pydub")
    fake_pydub.AudioSegment = DummyAudioSegment

    with patch.dict(sys.modules, {"pyttsx3": fake_pyttsx3, "pydub": fake_pydub}):
        with patch("src.core.tts_engine.get_gpu_manager"):
            engine = TTSEngine(cfg)
            out = engine._generate_pyttsx3("hello", tmp_path / "pyttsx3.mp3")

    assert out.exists()


@pytest.mark.unit
@pytest.mark.network
def test_edge_generate_async_success(tmp_path):
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path)
    engine = TTSEngine(cfg)
    engine.engine_type = "edge"

    class DummyCommunicate:
        def __init__(self, text, voice, rate="+0%", pitch="+0Hz"):
            self.text = text
            self.voice = voice
            self.rate = rate
            self.pitch = pitch

        async def save(self, path):
            Path(path).write_bytes(b"edge")

    fake_edge = ModuleType("edge_tts")
    fake_edge.Communicate = DummyCommunicate

    with patch.dict(sys.modules, {"edge_tts": fake_edge}):
        out = engine._generate_edge("hello", tmp_path / "edge.mp3")

    assert out.exists()
