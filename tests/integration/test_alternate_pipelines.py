"""
Smoke coverage for alternate orchestration paths that skip the avatar-heavy
waveform flow. These tests ensure we keep exercising the branches that power
audio-only, visualization-only, and SadTalker fallback experiences.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from tests.conftest import create_valid_mp3_file


class _StubGPU:
    """Minimal GPU manager replacement for deterministic tests."""

    gpu_available = False
    gpu_name = "Stub GPU"
    gpu_memory = 0.0
    device_id = 0

    def get_device(self) -> str:
        return "cpu"

    def clear_cache(self):
        return None

    def get_performance_config(self):
        return {"use_fp16": False}


@pytest.mark.integration
def test_audio_only_minimal_pipeline(monkeypatch, test_config, temp_dir):
    """Default pipeline should create the minimal black-frame video when no extras are requested."""
    from src.core.video_composer import VideoComposer

    config = copy.deepcopy(test_config)
    outputs_dir = Path(config["storage"]["outputs_dir"])
    outputs_dir.mkdir(parents=True, exist_ok=True)

    audio_path = create_valid_mp3_file(temp_dir / "audio_only.mp3", duration_seconds=1.0)

    monkeypatch.setattr(
        "src.core.video_composer.VideoComposer._validate_audio_file",
        lambda self, path: (True, ""),
    )

    call_args = {}

    def fake_minimal(self, audio_arg, output_path, quality=None):
        call_args["values"] = (audio_arg, output_path, quality)
        output_path.write_bytes(b"minimal-video")
        return output_path

    monkeypatch.setattr(
        "src.core.video_composer.VideoComposer._compose_minimal_video",
        fake_minimal,
    )

    composer = VideoComposer(config)
    result = composer.compose(audio_path)

    assert result.read_bytes() == b"minimal-video"
    assert call_args["values"][0] == audio_path
    assert call_args["values"][1] == result


@pytest.mark.integration
def test_visualization_only_pipeline_without_avatar(monkeypatch, test_config, temp_dir):
    """Visualization flag should drive the visualization-only branch when no avatar/background is requested."""
    from src.core.video_composer import VideoComposer

    config = copy.deepcopy(test_config)
    outputs_dir = Path(config["storage"]["outputs_dir"])
    outputs_dir.mkdir(parents=True, exist_ok=True)

    audio_path = create_valid_mp3_file(temp_dir / "visual_only.mp3", duration_seconds=1.0)

    monkeypatch.setattr(
        "src.core.video_composer.VideoComposer._validate_audio_file",
        lambda self, path: (True, ""),
    )

    call_args = {}

    def fake_visualization_only(self, audio_arg, output_path, quality=None):
        call_args["values"] = (audio_arg, output_path, quality)
        output_path.write_bytes(b"viz-video")
        return output_path

    monkeypatch.setattr(
        "src.core.video_composer.VideoComposer._compose_visualization_only",
        fake_visualization_only,
    )

    composer = VideoComposer(config)
    result = composer.compose(audio_path, use_visualization=True)

    assert result.read_bytes() == b"viz-video"
    assert call_args["values"][0] == audio_path
    assert call_args["values"][1] == result


@pytest.mark.integration
def test_sadtalker_fallback_pipeline(monkeypatch, test_config, temp_dir):
    """
    When SadTalker is requested but unavailable, the generator should fall back to the static video
    path and the composer should still produce a final output.
    """
    from src.core.avatar_generator import AvatarGenerator
    from src.core.video_composer import VideoComposer

    config = copy.deepcopy(test_config)
    config["avatar"]["engine"] = "sadtalker"
    config["avatar"]["enabled"] = True

    source_image = temp_dir / "avatar.png"
    source_image.write_bytes(b"fake-image-bytes")
    config["avatar"]["source_image"] = str(source_image)

    audio_path = create_valid_mp3_file(temp_dir / "narration.mp3", duration_seconds=1.0)

    # Use stub GPU manager across generator/composer
    monkeypatch.setattr("src.utils.gpu_utils.get_gpu_manager", lambda: _StubGPU())

    fallback_calls = {}

    def fake_fallback(self, audio_arg, output_path):
        fallback_calls["values"] = (audio_arg, output_path)
        output_path.write_bytes(b"fallback-avatar")
        return output_path

    monkeypatch.setattr(
        "src.core.avatar_generator.AvatarGenerator._create_fallback_video",
        fake_fallback,
    )
    monkeypatch.setattr(
        "src.core.avatar_generator.AvatarGenerator._generate_sadtalker",
        lambda self, audio_arg, output_path: self._create_fallback_video(audio_arg, output_path),
    )

    avatar_generator = AvatarGenerator(config)
    avatar_video = avatar_generator.generate(audio_path)

    assert avatar_video.read_bytes() == b"fallback-avatar"
    assert fallback_calls["values"][0] == audio_path

    outputs_dir = Path(config["storage"]["outputs_dir"])
    outputs_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        "src.core.video_composer.VideoComposer._validate_audio_file",
        lambda self, path: (True, ""),
    )
    monkeypatch.setattr(
        "src.core.video_composer.VideoComposer._get_audio_duration_ffmpeg",
        lambda self, path: 1.0,
    )

    compose_calls = {}

    def fake_avatar_with_background(self, avatar_arg, audio_arg, bg_path, output_path, quality=None):
        compose_calls["values"] = (avatar_arg, audio_arg, bg_path, output_path, quality)
        output_path.write_bytes(b"final-video")
        return output_path

    monkeypatch.setattr(
        "src.core.video_composer.VideoComposer._compose_avatar_with_background",
        fake_avatar_with_background,
    )

    composer = VideoComposer(config)
    final_output = composer.compose(audio_path, avatar_video=avatar_video, use_background=True)

    assert final_output.read_bytes() == b"final-video"
    assert compose_calls["values"][0] == avatar_video
    assert compose_calls["values"][1] == audio_path
    assert compose_calls["values"][3] == final_output


@pytest.mark.integration
def test_music_generator_cache_reuse(monkeypatch, test_config, temp_dir):
    """Music generator should skip regeneration when a cached asset already exists."""
    from src.core.music_generator import MusicGenerator

    config = copy.deepcopy(test_config)
    config["music"]["engine"] = "musicgen"
    config["storage"]["cache_dir"] = str(temp_dir / "cache")
    Path(config["storage"]["cache_dir"]).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        "src.core.music_generator.get_gpu_manager",
        lambda: _StubGPU(),
    )
    monkeypatch.setattr(
        "src.core.music_generator.MusicGenerator._init_musicgen",
        lambda self: None,
    )

    generation_calls = {"count": 0}

    def fake_generate_musicgen(self, description, output_path):
        generation_calls["count"] += 1
        output_path.write_bytes(f"music-{generation_calls['count']}".encode())
        return output_path

    monkeypatch.setattr(
        "src.core.music_generator.MusicGenerator._generate_musicgen",
        fake_generate_musicgen,
    )

    generator = MusicGenerator(config)

    first_path = generator.generate("uplifting background")
    second_path = generator.generate("uplifting background")

    assert first_path == second_path
    assert first_path.read_bytes() == b"music-1"
    assert generation_calls["count"] == 1

