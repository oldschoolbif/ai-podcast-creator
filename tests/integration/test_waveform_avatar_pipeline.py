"""
Integration test that exercises the waveform → avatar → composer pipeline end to end.

The goal is to ensure the orchestration between `AvatarGenerator`, `AudioVisualizer`,
and `VideoComposer` stays wired together correctly without invoking heavyweight GPU
or FFmpeg operations.
"""

from __future__ import annotations

import copy
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.conftest import create_valid_mp3_file


@pytest.mark.integration
def test_waveform_avatar_pipeline(monkeypatch, test_config, temp_dir):
    """Full pipeline smoke test for waveform overlay on top of an avatar video."""
    from src.core.avatar_generator import AvatarGenerator
    from src.core.video_composer import VideoComposer

    config = copy.deepcopy(test_config)

    # Ensure storage/output locations are isolated per-test
    outputs_dir = Path(config["storage"]["outputs_dir"])
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Provide a deterministic avatar source image so AvatarGenerator init succeeds
    avatar_source = temp_dir / "avatar_source.jpg"
    avatar_source.write_bytes(b"avatar-src")
    config["avatar"]["engine"] = "none"
    config["avatar"]["enabled"] = True
    config["avatar"]["source_image"] = str(avatar_source)

    # Rich waveform configuration to verify options flow through AudioVisualizer
    config["visualization"] = {
        "style": "waveform",
        "waveform": {
            "num_lines": 3,
            "position": "top,bottom",
            "opacity": 0.65,
            "render_scale": 1.5,
            "line_thickness": [6, 4, 2],
            "line_colors": [[10, 20, 30], [40, 50, 60], [70, 80, 90]],
            "amplitude_multiplier": 1.8,
            "num_instances": 2,
            "instances_offset": 8,
        },
    }
    config["video"]["fps"] = 24
    config["video"]["resolution"] = [640, 360]

    audio_path = create_valid_mp3_file(temp_dir / "pipeline_input.mp3", duration_seconds=1.5)

    # --- Patch heavy dependencies -------------------------------------------------

    class DummyGPU:
        gpu_available = False
        gpu_name = "Stub GPU"
        gpu_memory = 0.0
        device_id = 0

        def get_device(self):
            return "cpu"

        def clear_cache(self):
            return None

        def get_performance_config(self):
            return {"use_fp16": False}

        def get_utilization(self):
            return {}

    monkeypatch.setattr("src.utils.gpu_utils.get_gpu_manager", lambda: DummyGPU())
    monkeypatch.setattr(
        "src.core.video_composer.VideoComposer._validate_audio_file",
        lambda self, path: (True, ""),
        raising=False,
    )
    monkeypatch.setattr(
        "src.core.video_composer.VideoComposer._get_audio_duration_ffmpeg",
        lambda self, path: 2.0,
        raising=False,
    )

    viz_calls = []

    def fake_generate_visualization(self, audio_path_arg, output_path):
        viz_calls.append(
            {
                "audio": audio_path_arg,
                "position": self.position,
                "num_lines": self.num_lines,
                "num_instances": self.num_instances,
                "opacity": self.opacity,
                "line_thickness": self.line_thickness,
            }
        )
        output_path.write_bytes(b"viz")
        return output_path

    monkeypatch.setattr(
        "src.core.audio_visualizer.AudioVisualizer.generate_visualization",
        fake_generate_visualization,
        raising=False,
    )

    avatar_calls = []
    avatar_video_path = temp_dir / "avatar_generated.mp4"

    def fake_avatar_generate(self, audio_path_arg, for_basic_mode=True):
        avatar_calls.append(audio_path_arg)
        avatar_video_path.write_bytes(b"avatar")
        return avatar_video_path

    monkeypatch.setattr(
        "src.core.avatar_generator.AvatarGenerator.generate",
        fake_avatar_generate,
        raising=False,
    )

    def fake_popen(cmd, *args, **kwargs):
        # The output path is the penultimate argument (before '-y')
        output_index = -2 if cmd[-1] == "-y" else -1
        Path(cmd[output_index]).write_bytes(b"final")

        class Proc:
            returncode = 0
            stdout = None
            stderr = None

            def communicate(self, timeout=None):
                return ("", "")

            def poll(self):
                return 0

        return Proc()

    monkeypatch.setattr("src.core.video_composer.subprocess.Popen", fake_popen)

    # ---------------------------------------------------------------------------

    avatar_generator = AvatarGenerator(config)
    generated_avatar = avatar_generator.generate(audio_path)

    composer = VideoComposer(config)
    final_output = composer.compose(
        audio_path,
        avatar_video=generated_avatar,
        use_visualization=True,
        quality="fastest",
    )

    assert avatar_calls == [audio_path]
    assert viz_calls and viz_calls[0]["audio"] == audio_path
    assert viz_calls[0]["position"] == "top,bottom"
    assert viz_calls[0]["num_lines"] == 3
    assert viz_calls[0]["num_instances"] == 2
    assert pytest.approx(viz_calls[0]["opacity"], rel=1e-3) == 0.65
    assert Path(viz_calls[0]["audio"]).exists()

    assert final_output.exists()
    assert final_output.read_bytes() == b"final"


