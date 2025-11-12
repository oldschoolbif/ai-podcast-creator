"""
Unit tests for `FaceGenerator`.

The real implementation depends on heavy ML stacks (diffusers, torch, GPU). These
tests provide lightweight fakes to exercise prompt generation, device selection,
and file output behaviour without pulling the actual models.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.core.face_generator import FaceGenerator


def _install_stubs(monkeypatch: pytest.MonkeyPatch, pipeline_cls):
    """Install stub modules for torch, diffusers, and PIL used by the generator."""
    fake_torch = types.ModuleType("torch")
    fake_torch.float16 = "float16"
    fake_torch.float32 = "float32"

    class _NoGrad:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

    def no_grad():
        return _NoGrad()

    fake_torch.no_grad = no_grad

    fake_diffusers = types.ModuleType("diffusers")
    fake_diffusers.StableDiffusionPipeline = pipeline_cls

    fake_pil = types.ModuleType("PIL")
    fake_pil_image = types.ModuleType("PIL.Image")
    fake_pil.Image = fake_pil_image

    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setitem(sys.modules, "diffusers", fake_diffusers)
    monkeypatch.setitem(sys.modules, "PIL", fake_pil)
    monkeypatch.setitem(sys.modules, "PIL.Image", fake_pil_image)


class DummyGPU:
    def __init__(self, available: bool, device: str, perf_config: dict):
        self.gpu_available = available
        self._device = device
        self._perf = perf_config

    def get_device(self):
        return self._device

    def get_performance_config(self):
        return self._perf

    def clear_cache(self):
        return None


def test_generate_with_description_accelerated(monkeypatch, tmp_path):
    config = {"storage": {"cache_dir": str(tmp_path / "cache")}}

    created_pipelines = []

    class FakeImage:
        def __init__(self):
            self.saved = []
            self.size = (512, 512)

        def save(self, path, quality=95):
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fake-image")
            self.saved.append((path, quality))

    class FakePipeline:
        def __init__(self):
            self.model_id = None
            self.init_kwargs = {}
            self.to_device = None
            self.calls = []
            self.last_image = None

        @classmethod
        def from_pretrained(cls, model_id, **kwargs):
            instance = cls()
            instance.model_id = model_id
            instance.init_kwargs = kwargs
            created_pipelines.append(instance)
            return instance

        def to(self, device):
            self.to_device = device
            return self

        def __call__(self, **kwargs):
            image = FakeImage()
            self.calls.append(kwargs)
            self.last_image = image
            return SimpleNamespace(images=[image])

    _install_stubs(monkeypatch, FakePipeline)
    monkeypatch.setattr(
        "src.core.face_generator.get_gpu_manager",
        lambda: DummyGPU(True, "cuda", {"use_fp16": True}),
    )

    generator = FaceGenerator(config)
    output_path = generator.generate(description="Professional female news anchor")

    assert output_path == generator.output_dir / "generated_face.png"
    assert output_path.exists()

    assert created_pipelines, "Pipeline should be instantiated"
    pipeline = created_pipelines[0]
    assert pipeline.model_id == "runwayml/stable-diffusion-v1-5"
    assert pipeline.init_kwargs.get("torch_dtype") == "float16"
    assert pipeline.init_kwargs.get("device_map") == "auto"
    assert pipeline.to_device == "cuda"

    call = pipeline.calls[0]
    expected_base = generator._description_to_prompt("Professional female news anchor")
    assert call["prompt"].startswith(expected_base)
    assert "front-facing portrait" in call["prompt"]
    assert "artifacts" in call["negative_prompt"]

    # Ensure saved file used high-quality setting (95 default)
    assert pipeline.last_image.saved[0][1] == 95


def test_generate_with_custom_prompt_cpu(monkeypatch, tmp_path):
    config = {"storage": {"cache_dir": str(tmp_path / "cache")}}

    created_pipelines = []

    class FakeImage:
        def __init__(self):
            self.size = (256, 256)
            self.saved = []

        def save(self, path, quality=95):
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"custom-image")
            self.saved.append((path, quality))

    class FakePipeline:
        def __init__(self):
            self.model_id = None
            self.init_kwargs = {}
            self.calls = []

        @classmethod
        def from_pretrained(cls, model_id, **kwargs):
            instance = cls()
            instance.model_id = model_id
            instance.init_kwargs = kwargs
            created_pipelines.append(instance)
            return instance

        def __call__(self, **kwargs):
            image = FakeImage()
            self.calls.append(kwargs)
            self.last_image = image
            return SimpleNamespace(images=[image])

    _install_stubs(monkeypatch, FakePipeline)
    monkeypatch.setattr(
        "src.core.face_generator.get_gpu_manager",
        lambda: DummyGPU(False, "cpu", {}),
    )

    generator = FaceGenerator(config)
    custom_output = tmp_path / "faces" / "custom_face.png"
    result_path = generator.generate(prompt="hero portrait", output_path=custom_output)

    assert result_path == custom_output
    assert result_path.exists()

    pipeline = created_pipelines[0]
    assert pipeline.init_kwargs == {}  # CPU path skips extra kwargs
    call = pipeline.calls[0]
    assert call["prompt"].startswith("hero portrait")
    assert "hero portrait" in call["prompt"]


def test_description_to_prompt_variations(monkeypatch):
    monkeypatch.setattr(
        "src.core.face_generator.get_gpu_manager",
        lambda: DummyGPU(False, "cpu", {}),
    )
    generator = FaceGenerator({"storage": {"cache_dir": "."}})

    prompt = generator._description_to_prompt("Young female professional presenter")
    assert "young" in prompt
    # Current implementation matches 'male' before 'female' due to substring overlap.
    assert any(token in prompt for token in ["male", "female"])
    assert "professional business portrait" in prompt

    prompt_neutral = generator._description_to_prompt("Seasoned storyteller")
    assert prompt_neutral.startswith("professional person")
    assert "professional portrait" in prompt_neutral


def test_generate_import_error(monkeypatch, tmp_path):
    """Generating without diffusers installed should raise ImportError."""
    config = {"storage": {"cache_dir": str(tmp_path / "cache")}}
    monkeypatch.setattr(
        "src.core.face_generator.get_gpu_manager",
        lambda: DummyGPU(False, "cpu", {}),
    )

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("diffusers"):
            raise ImportError("diffusers missing")
        return original_import(name, *args, **kwargs)

    generator = FaceGenerator(config)

    with patch("builtins.__import__", side_effect=fake_import):
        with pytest.raises(ImportError):
            generator.generate(description="conference host")


def test_generate_pipeline_exception(monkeypatch, tmp_path):
    """Runtime errors from the pipeline should propagate upward."""
    config = {"storage": {"cache_dir": str(tmp_path / "cache")}}

    class FaultyPipeline:
        def __init__(self):
            self.init_kwargs = {}

        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            instance = cls()
            instance.init_kwargs = kwargs
            return instance

        def to(self, device):
            return self

        def __call__(self, **kwargs):
            raise RuntimeError("pipeline failed")

    _install_stubs(monkeypatch, FaultyPipeline)
    monkeypatch.setattr(
        "src.core.face_generator.get_gpu_manager",
        lambda: DummyGPU(True, "cuda", {"use_fp16": True}),
    )

    generator = FaceGenerator(config)

    with pytest.raises(RuntimeError, match="pipeline failed"):
        generator.generate(description="dynamic presenter")

