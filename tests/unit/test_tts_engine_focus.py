import sys
from pathlib import Path
from types import SimpleNamespace
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
def test_tts_engine_module_adds_root_to_sys_path():
    from src.core import tts_engine

    expected = str(Path(tts_engine.__file__).parent.parent.parent)
    assert expected in sys.path


@pytest.mark.unit
def test_engine_defaults_to_gtts_and_sets_flag(tmp_path):
    from src.core.tts_engine import TTSEngine

    cache_dir = tmp_path / "cache"
    outputs_dir = tmp_path / "out"
    cfg = {"storage": {"cache_dir": str(cache_dir), "outputs_dir": str(outputs_dir)}}

    fake_gtts = SimpleNamespace(gTTS=lambda *a, **k: None)
    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu, patch.dict(sys.modules, {"gtts": fake_gtts}):
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        engine = TTSEngine(cfg)

        assert engine.engine_type == "gtts"
        assert getattr(engine, "gtts_available", False) is True

# ============================================================================
# Tests for error paths and edge cases
# ============================================================================

@pytest.mark.unit
def test_init_gtts_import_error(tmp_path):
    """Test _init_gtts raises ImportError when gTTS is not installed."""
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path)
    cfg["tts"]["engine"] = "gtts"

    with (
        patch("src.core.tts_engine.get_gpu_manager") as mock_gpu,
        patch.dict("sys.modules", {"gtts": None}),
    ):
        mock_gpu.return_value.gpu_available = False
        mock_gpu.return_value.get_device.return_value = "cpu"

        with pytest.raises(ImportError, match="gTTS not installed"):
            TTSEngine(cfg)


@pytest.mark.unit
def test_init_coqui_import_error(tmp_path):
    """Test _init_coqui raises ImportError when Coqui TTS is not installed."""
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path)
    cfg["tts"]["engine"] = "coqui"
    cfg["tts"]["coqui"] = {"model": "tts_models/en/ljspeech/tacotron2-DDC"}

    with (
        patch("src.core.tts_engine.get_gpu_manager") as mock_gpu,
        patch.dict("sys.modules", {"TTS": None, "torch": None}),
    ):
        mock_gpu.return_value.gpu_available = False
        mock_gpu.return_value.get_device.return_value = "cpu"

        with pytest.raises(ImportError, match="Coqui TTS not installed"):
            TTSEngine(cfg)


@pytest.mark.unit
def test_init_coqui_exception_handling(tmp_path):
    """Test _init_coqui handles exceptions during initialization."""
    from src.core.tts_engine import TTSEngine
    import sys

    cfg = make_config(tmp_path)
    cfg["tts"]["engine"] = "coqui"
    cfg["tts"]["coqui"] = {"model": "tts_models/en/ljspeech/tacotron2-DDC"}

    # Stub torch and TTS modules before patching
    stub_torch = MagicMock()
    stub_tts = MagicMock()
    stub_tts.api = MagicMock()
    stub_tts.api.TTS = MagicMock(side_effect=Exception("Model loading failed"))

    with (
        patch.dict("sys.modules", {"torch": stub_torch, "TTS": stub_tts, "TTS.api": stub_tts.api}),
        patch("src.core.tts_engine.get_gpu_manager") as mock_gpu,
        patch("builtins.print") as mock_print,  # Patch print to avoid Unicode encoding issues
    ):
        mock_gpu.return_value.gpu_available = False
        mock_gpu.return_value.get_device.return_value = "cpu"

        with pytest.raises(Exception, match="Model loading failed"):
            TTSEngine(cfg)


@pytest.mark.unit
def test_init_elevenlabs_import_error(tmp_path):
    """Test _init_elevenlabs raises ImportError when ElevenLabs is not installed."""
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path)
    cfg["tts"]["engine"] = "elevenlabs"
    cfg["tts"]["elevenlabs"] = {"api_key": "test_key"}

    with (
        patch("src.core.tts_engine.get_gpu_manager") as mock_gpu,
        patch.dict("sys.modules", {"elevenlabs": None}),
    ):
        mock_gpu.return_value.gpu_available = False
        mock_gpu.return_value.get_device.return_value = "cpu"

        with pytest.raises(ImportError, match="ElevenLabs not installed"):
            TTSEngine(cfg)


@pytest.mark.unit
def test_init_azure_import_error(tmp_path):
    """Test _init_azure raises ImportError when Azure Speech is not installed."""
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path)
    cfg["tts"]["engine"] = "azure"
    cfg["tts"]["azure"] = {"api_key": "test_key", "region": "eastus"}

    with (
        patch("src.core.tts_engine.get_gpu_manager") as mock_gpu,
        patch.dict("sys.modules", {"azure": None}),
    ):
        mock_gpu.return_value.gpu_available = False
        mock_gpu.return_value.get_device.return_value = "cpu"

        with pytest.raises(ImportError, match="Azure Speech not installed"):
            TTSEngine(cfg)


@pytest.mark.skip(reason="Complex elevenlabs module stubbing - tested via integration")
def test_generate_elevenlabs_missing_api_key(tmp_path):
    """Test _generate_elevenlabs raises ValueError when API key is missing."""
    # This requires complex stubbing of elevenlabs module imported locally
    # Better tested through integration tests
    pass


@pytest.mark.unit
def test_generate_gtts_retry_then_failure(tmp_path):
    """Test _generate_gtts retries and raises exception after max retries."""
    from src.core.tts_engine import TTSEngine

    cfg = make_config(tmp_path)
    cfg["tts"]["engine"] = "gtts"

    with (
        patch("src.core.tts_engine.get_gpu_manager") as mock_gpu,
        patch("gtts.gTTS") as mock_gtts,
    ):
        mock_gpu.return_value.gpu_available = False
        mock_gpu.return_value.get_device.return_value = "cpu"

        engine = TTSEngine(cfg)
        output_path = tmp_path / "output.mp3"

        # Mock gTTS to fail all retries
        mock_tts_instance = MagicMock()
        mock_tts_instance.save.side_effect = Exception("Network error")
        mock_gtts.return_value = mock_tts_instance

        with pytest.raises(Exception, match="gTTS failed after 3 attempts"):
            engine._generate_gtts("test text", output_path)


@pytest.mark.skip(reason="Complex TTS/torch module stubbing - tested via integration")
def test_generate_coqui_exception(tmp_path):
    """Test _generate_coqui raises exception on generation failure."""
    # This requires complex stubbing of TTS and torch modules imported locally
    # Better tested through integration tests
    pass


@pytest.mark.skip(reason="Complex pydub mocking - tested via integration")
def test_generate_pyttsx3_mp3_conversion_failure(tmp_path):
    """Test _generate_pyttsx3 falls back to WAV when MP3 conversion fails."""
    # This requires complex mocking of pydub which is imported locally
    # Better tested through integration tests
    pass


@pytest.mark.skip(reason="Complex asyncio event loop mocking - tested via integration")
def test_generate_edge_runtime_error_handling(tmp_path):
    """Test _generate_edge handles RuntimeError when event loop exists."""
    # This requires complex asyncio event loop mocking
    # Better tested through integration tests
    pass


@pytest.mark.unit
def test_engine_type_default_value_when_missing_from_config(tmp_path):
    """Test that engine_type defaults to 'gtts' when not in config (kills mutant 5)."""
    from src.core.tts_engine import TTSEngine

    cache_dir = tmp_path / "cache"
    outputs_dir = tmp_path / "out"
    # Config without 'tts' key or 'engine' key
    cfg = {"storage": {"cache_dir": str(cache_dir), "outputs_dir": str(outputs_dir)}}

    fake_gtts = SimpleNamespace(gTTS=lambda *a, **k: None)
    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu, patch.dict(sys.modules, {"gtts": fake_gtts}):
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        engine = TTSEngine(cfg)
        # Must default to "gtts" when config.get("tts", {}).get("engine", "gtts") is used
        assert engine.engine_type == "gtts"

@pytest.mark.unit
def test_gtts_branch_taken_when_engine_type_equals_gtts(tmp_path):
    """Test that gtts branch is taken when engine_type == 'gtts' (kills mutant 18)."""
    from src.core.tts_engine import TTSEngine

    cache_dir = tmp_path / "cache"
    outputs_dir = tmp_path / "out"
    cfg = {"storage": {"cache_dir": str(cache_dir), "outputs_dir": str(outputs_dir)}, "tts": {"engine": "gtts"}}

    fake_gtts = SimpleNamespace(gTTS=lambda *a, **k: None)
    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu, patch.dict(sys.modules, {"gtts": fake_gtts}):
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        init_gtts_called = {"value": False}

        original_init = TTSEngine._init_gtts

        def tracked_init(self):
            init_gtts_called["value"] = True
            return original_init(self)

        with patch.object(TTSEngine, "_init_gtts", new=tracked_init):
            engine = TTSEngine(cfg)
            # Must call _init_gtts when engine_type == "gtts"
            assert init_gtts_called["value"] is True
            assert engine.engine_type == "gtts"

@pytest.mark.unit
def test_coqui_branch_taken_when_engine_type_equals_coqui(tmp_path):
    """Test that coqui branch is taken when engine_type == 'coqui' (kills mutant 20)."""
    from src.core.tts_engine import TTSEngine

    cache_dir = tmp_path / "cache"
    outputs_dir = tmp_path / "out"
    cfg = {"storage": {"cache_dir": str(cache_dir), "outputs_dir": str(outputs_dir)}, "tts": {"engine": "coqui", "coqui": {"model": "dummy"}}}

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        init_coqui_called = {"value": False}

        def tracked_init(self):
            init_coqui_called["value"] = True
            # Don't call original - just mark as called

        with patch.object(TTSEngine, "_init_coqui", new=tracked_init), patch.object(TTSEngine, "_init_gtts", side_effect=AssertionError("gTTS should not be called")):
            engine = TTSEngine(cfg)
            # Must call _init_coqui when engine_type == "coqui"
            assert init_coqui_called["value"] is True
            assert engine.engine_type == "coqui"

@pytest.mark.unit
def test_piper_branch_taken_when_engine_type_equals_piper(tmp_path):
    """Test that piper branch is taken when engine_type == 'piper' (kills mutant 26)."""
    from src.core.tts_engine import TTSEngine

    cache_dir = tmp_path / "cache"
    outputs_dir = tmp_path / "out"
    cfg = {"storage": {"cache_dir": str(cache_dir), "outputs_dir": str(outputs_dir)}, "tts": {"engine": "piper"}}

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        init_piper_called = {"value": False}

        def tracked_init(self):
            init_piper_called["value"] = True
            # Don't call original - just mark as called

        with patch.object(TTSEngine, "_init_piper", new=tracked_init), patch.object(TTSEngine, "_init_gtts", side_effect=AssertionError("gTTS should not be called")):
            engine = TTSEngine(cfg)
            # Must call _init_piper when engine_type == "piper"
            assert init_piper_called["value"] is True
            assert engine.engine_type == "piper"

@pytest.mark.unit
def test_gtts_available_set_to_true_on_init(tmp_path):
    """Test that gtts_available is set to True in _init_gtts (kills mutant 29)."""
    from src.core.tts_engine import TTSEngine

    cache_dir = tmp_path / "cache"
    outputs_dir = tmp_path / "out"
    cfg = {"storage": {"cache_dir": str(cache_dir), "outputs_dir": str(outputs_dir)}}

    fake_gtts = SimpleNamespace(gTTS=lambda *a, **k: None)
    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu, patch.dict(sys.modules, {"gtts": fake_gtts}):
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        engine = TTSEngine(cfg)
        # Must set gtts_available = True in _init_gtts
        assert getattr(engine, "gtts_available", None) is True


@pytest.mark.unit
def test_unknown_engine_falls_back_to_gtts(tmp_path):
    from src.core.tts_engine import TTSEngine

    cfg = {
        "storage": {"cache_dir": str(tmp_path / "cache"), "outputs_dir": str(tmp_path / "out")},
        "tts": {"engine": "unknown"},
    }

    fake_gtts = SimpleNamespace(gTTS=lambda *a, **k: None)
    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu, patch.dict(sys.modules, {"gtts": fake_gtts}):
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        marker = {"called": False}

        original_init = TTSEngine._init_gtts

        def wrapped(self):
            marker["called"] = True
            return original_init(self)

        with patch.object(TTSEngine, "_init_gtts", new=wrapped):
            engine = TTSEngine(cfg)

        assert marker["called"] is True
        assert engine.engine_type == "unknown"
        assert getattr(engine, "gtts_available", False) is True


@pytest.mark.unit
def test_engine_branch_initializers_called(tmp_path):
    from src.core.tts_engine import TTSEngine

    base = {"storage": {"cache_dir": str(tmp_path / "cache"), "outputs_dir": str(tmp_path / "out")}}

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        with patch.object(TTSEngine, "_init_coqui") as init_coqui:
            TTSEngine({**base, "tts": {"engine": "coqui", "coqui": {"model": "dummy"}}})
            init_coqui.assert_called_once()

        with patch.object(TTSEngine, "_init_piper") as init_piper:
            TTSEngine({**base, "tts": {"engine": "piper"}})
            init_piper.assert_called_once()


@pytest.mark.unit
@pytest.mark.parametrize(
    "engine,config_extra,init_attr",
    [
        ("coqui", {"coqui": {"model": "dummy"}}, "_init_coqui"),
        ("piper", {}, "_init_piper"),
    ],
)
def test_non_gtts_engines_preserve_type_and_skip_gtts(tmp_path, engine, config_extra, init_attr):
    from src.core.tts_engine import TTSEngine

    base = {"storage": {"cache_dir": str(tmp_path / "cache"), "outputs_dir": str(tmp_path / "out")}}
    cfg = {**base, "tts": {"engine": engine, **config_extra}}

    with patch("src.core.tts_engine.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        with patch.object(TTSEngine, "_init_gtts", side_effect=AssertionError("gTTS branch should not run")), patch.object(
            TTSEngine, init_attr, return_value=None
        ) as init_mock:
            tts = TTSEngine(cfg)

    init_mock.assert_called_once()
    assert tts.engine_type == engine


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

            with patch.dict(
                sys.modules, {"pydub": MagicMock(AudioSegment=MagicMock(from_wav=MagicMock(return_value=fake_audio)))}
            ):
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
