"""
Additional unit coverage for `MusicGenerator` focusing on MusicGen code paths
without requiring the heavy Audiocraft/Torch stack at runtime.

These tests install lightweight stub modules into ``sys.modules`` so the real
implementation executes while we assert on the orchestration behaviour.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.core.music_generator import MusicGenerator


class _DummyContext:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class _FakeTensor:
    def __init__(self):
        self.cpu_calls = 0

    def cpu(self):
        self.cpu_calls += 1
        return self


class DummyGPU:
    def __init__(self, available: bool, *, device: str = "cuda", perf: dict | None = None):
        self.gpu_available = available
        self._device = device
        self._perf = perf or {"use_fp16": False}
        self.clear_count = 0

    def get_device(self):
        return self._device

    def get_performance_config(self):
        return self._perf

    def clear_cache(self):
        self.clear_count += 1


def _install_musicgen_stubs(monkeypatch: pytest.MonkeyPatch, *, version: str = "2.1.0"):
    """Inject stub `torch`, `torchaudio`, and `audiocraft` modules."""
    autocast_calls: list[bool] = []
    saved_files: list[Path] = []
    compile_calls: list[tuple] = []
    instances: list = []

    # Torch stub -------------------------------------------------------------
    fake_torch = types.ModuleType("torch")
    fake_torch.__version__ = version

    def inference_mode():
        return _DummyContext()

    fake_torch.inference_mode = inference_mode

    def compile_stub(model, mode=None):
        compile_calls.append((model, mode))
        return model

    if version >= "2.0.0":
        fake_torch.compile = compile_stub

    class _AMP:
        @staticmethod
        def autocast(enabled=True):
            autocast_calls.append(enabled)
            return _DummyContext()

    fake_torch.cuda = SimpleNamespace(amp=_AMP())
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    # Torchaudio stub --------------------------------------------------------
    fake_torchaudio = types.ModuleType("torchaudio")

    def save_stub(path, tensor, sample_rate):
        path = Path(path)
        path.write_bytes(b"fake-audio")
        saved_files.append((path, sample_rate))

    fake_torchaudio.save = save_stub
    monkeypatch.setitem(sys.modules, "torchaudio", fake_torchaudio)

    # Audiocraft stub --------------------------------------------------------
    class FakeMusicGen:
        def __init__(self):
            self.lm = MagicMock()
            self.sample_rate = 32000
            self.generate = MagicMock(return_value=[_FakeTensor()])
            self.set_generation_params = MagicMock()

        @classmethod
        def get_pretrained(cls, model_name, device):
            instance = cls()
            instance.model_name = model_name
            instance.device = device
            instances.append(instance)
            return instance

    fake_models = types.ModuleType("audiocraft.models")
    fake_models.MusicGen = FakeMusicGen
    fake_audiocraft = types.ModuleType("audiocraft")
    fake_audiocraft.models = fake_models
    monkeypatch.setitem(sys.modules, "audiocraft", fake_audiocraft)
    monkeypatch.setitem(sys.modules, "audiocraft.models", fake_models)

    return {
        "autocast_calls": autocast_calls,
        "saved_files": saved_files,
        "compile_calls": compile_calls,
        "instances": instances,
        "torch": fake_torch,
    }


def _base_config(tmp_path: Path, engine: str = "musicgen") -> dict:
    return {
        "storage": {"cache_dir": str(tmp_path / "cache"), "outputs_dir": str(tmp_path / "outputs")},
        "music": {engine: {"model": "facebook/musicgen-small", "duration": 6}, "engine": engine},
    }


def test_musicgen_accelerated_initialization_enables_compile_and_fp16(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    stubs = _install_musicgen_stubs(monkeypatch, version="2.1.0")
    gpu = DummyGPU(True, perf={"use_fp16": True})
    monkeypatch.setattr("src.core.music_generator.get_gpu_manager", lambda: gpu)

    config = _base_config(tmp_path)
    generator = MusicGenerator(config)

    # Model should be initialised once using GPU.
    instance = stubs["instances"][0]
    assert instance.device == "cuda"
    assert stubs["compile_calls"], "torch.compile should be invoked on GPU path"
    instance.lm.half.assert_called()  # FP16 optimisation

    # Trigger generation to exercise autocast + clear_cache behaviour.
    output = generator.generate("Energetic background music")
    assert output.exists()
    assert stubs["autocast_calls"], "autocast should run when GPU is enabled"
    assert gpu.clear_count == 2  # before and after generation
    saved_path, saved_rate = stubs["saved_files"][0]
    assert saved_path == output
    assert saved_rate == instance.sample_rate


def test_musicgen_cpu_path_skips_compile(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    stubs = _install_musicgen_stubs(monkeypatch, version="1.9.0")  # compile not available
    gpu = DummyGPU(False, device="cpu")
    monkeypatch.setattr("src.core.music_generator.get_gpu_manager", lambda: gpu)

    config = _base_config(tmp_path)
    generator = MusicGenerator(config)

    instance = stubs["instances"][0]
    assert instance.device == "cpu"
    assert not stubs["compile_calls"], "compile should not run on older torch versions"

    stubs["autocast_calls"].clear()
    output = generator.generate(["soft focus cue"])
    assert output.exists()
    assert not stubs["autocast_calls"], "autocast should not run when GPU unavailable"
    assert gpu.clear_count == 0  # CPU path does not touch cache


def test_musicgen_generate_handles_exception(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    stubs = _install_musicgen_stubs(monkeypatch, version="2.1.0")
    gpu = DummyGPU(True, perf={"use_fp16": False})
    monkeypatch.setattr("src.core.music_generator.get_gpu_manager", lambda: gpu)

    config = _base_config(tmp_path)
    generator = MusicGenerator(config)

    # Force the underlying model to raise so we hit the safety path.
    instance = stubs["instances"][0]
    instance.generate.side_effect = RuntimeError("boom")

    result = generator.generate("Calm ambience")
    assert result is None
    assert gpu.clear_count == 1  # Only the pre-generation clear executed


def test_mubert_and_library_engines_create_placeholder_files(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    _install_musicgen_stubs(monkeypatch)  # Needed because the module always imports torch/audiocraft
    gpu = DummyGPU(False, device="cpu")
    monkeypatch.setattr("src.core.music_generator.get_gpu_manager", lambda: gpu)

    cfg = _base_config(tmp_path, engine="mubert")
    generator = MusicGenerator(cfg)
    placeholder = generator.generate("calm focus loop")
    assert placeholder.exists()

    cfg_lib = _base_config(tmp_path, engine="library")
    generator_lib = MusicGenerator(cfg_lib)
    selection = generator_lib.generate("uplifting background")
    assert selection.exists()


def test_generate_returns_cached_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    stubs = _install_musicgen_stubs(monkeypatch)
    gpu = DummyGPU(False, device="cpu")
    monkeypatch.setattr("src.core.music_generator.get_gpu_manager", lambda: gpu)

    cfg = _base_config(tmp_path)
    generator = MusicGenerator(cfg)

    cached = generator.cache_dir / f"{generator._get_cache_key('repeat cue')}.wav"
    cached.write_bytes(b"cached")

    result = generator.generate("repeat cue")
    assert result == cached
    # No new files should be saved when cache hit occurs.
    assert not stubs["saved_files"]

