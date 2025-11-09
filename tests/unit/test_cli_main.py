"""Unit tests for the Typer-based CLI."""

import sys
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import app - main.py now handles missing sqlalchemy gracefully
from src.cli.main import app

runner = CliRunner()


def make_cli_config(base_dir: Path) -> dict:
    return {
        "app": {"name": "AI Podcast Creator", "version": "1.0.0"},
        "tts": {"engine": "gtts"},
        "music": {"engine": "library"},
        "video": {"resolution": [1920, 1080], "fps": 30, "codec": "libx264"},
        "storage": {
            "cache_dir": str(base_dir / "cache"),
            "output_dir": str(base_dir / "outputs"),
            "outputs_dir": str(base_dir / "outputs"),
        },
        "character": {"name": "QA Bot", "voice_type": "gtts"},
    }


def test_cli_create_missing_script(tmp_path):
    result = runner.invoke(app, ["create", str(tmp_path / "missing.txt")])

    assert result.exit_code == 1
    assert "Script file not found" in result.stdout


def test_cli_create_audio_only_success(tmp_path):
    script_path = tmp_path / "script.txt"
    script_path.write_text("# Title\nHello world", encoding="utf-8")
    config = make_cli_config(tmp_path)

    voice_path = tmp_path / "voice.mp3"
    voice_path.write_bytes(b"voice")
    mixed_path = tmp_path / "mixed.mp3"
    mixed_path.write_bytes(b"mixed")

    final_audio_path = tmp_path / "outputs" / "script.mp3"

    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    fake_gpu.gpu_name = "CPU"
    fake_gpu.gpu_memory = 0

    def ffmpeg_side_effect(cmd, check=True, capture_output=True, text=False):
        Path(cmd[-2]).write_bytes(b"mp3")
        return MagicMock(returncode=0, stdout="", stderr="")

    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.cli.main.ScriptParser") as mock_parser,
        patch("src.cli.main.TTSEngine") as mock_tts,
        patch("src.cli.main.AudioMixer") as mock_mixer,
        patch("subprocess.run", side_effect=ffmpeg_side_effect),
    ):

        mock_parser.return_value.parse.return_value = {"text": "Hello world", "music_cues": []}
        mock_tts_instance = MagicMock(generate=MagicMock(return_value=voice_path))
        mock_tts.return_value = mock_tts_instance
        mock_mixer.return_value.mix.return_value = mixed_path

        result = runner.invoke(
            app,
            [
                "create",
                str(script_path),
                "--audio-only",
                "--output",
                "script",
                "--skip-music",
            ],
        )

        assert result.exit_code == 0
        assert "Podcast audio created successfully" in result.stdout
        assert final_audio_path.exists()


def test_cli_create_waveform_overrides(tmp_path):
    script_path = tmp_path / "script.txt"
    script_path.write_text("hello", encoding="utf-8")
    config = make_cli_config(tmp_path)

    # Provide baseline visualization config to mutate
    config["visualization"] = {"waveform": {"num_lines": 1, "position": "bottom"}}

    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    fake_gpu.gpu_name = "CPU"
    fake_gpu.gpu_memory = 0

    voice_path = tmp_path / "voice.mp3"
    voice_path.write_bytes(b"voice")

    mixed_path = tmp_path / "mixed.mp3"
    mixed_path.write_bytes(b"mixed")

    final_audio_path = tmp_path / "outputs" / "script.mp3"

    def ffmpeg_side_effect(cmd, check=True, capture_output=True, text=False):
        Path(cmd[-2]).write_bytes(b"mp3")
        return MagicMock(returncode=0, stdout="", stderr="")

    apply_calls = []

    import src.cli.main as cli_main

    original_apply = cli_main._apply_waveform_cli_overrides

    def capture_overrides(
        cfg,
        position,
        num_lines,
        thickness,
        colors,
        style,
        opacity,
        randomize,
        height_percent,
        width_percent,
        left_spacing,
        right_spacing,
        render_scale,
        anti_alias,
        orientation_offset,
        rotation,
        amplitude_multiplier,
        num_instances,
        instances_offset,
        instances_intersect,
    ):
        apply_calls.append(
            SimpleNamespace(
                position=position,
                num_lines=num_lines,
                thickness=thickness,
                colors=colors,
                style=style,
                opacity=opacity,
                randomize=randomize,
                height_percent=height_percent,
                width_percent=width_percent,
                left_spacing=left_spacing,
                right_spacing=right_spacing,
                render_scale=render_scale,
                anti_alias=anti_alias,
                orientation_offset=orientation_offset,
                rotation=rotation,
                amplitude_multiplier=amplitude_multiplier,
                num_instances=num_instances,
                instances_offset=instances_offset,
                instances_intersect=instances_intersect,
            )
        )

        # Execute the real override logic to mutate config
        return original_apply(
            cfg,
            position,
            num_lines,
            thickness,
            colors,
            style,
            opacity,
            randomize,
            height_percent,
            width_percent,
            left_spacing,
            right_spacing,
            render_scale,
            anti_alias,
            orientation_offset,
            rotation,
            amplitude_multiplier,
            num_instances,
            instances_offset,
            instances_intersect,
        )

    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.cli.main.ScriptParser") as mock_parser,
        patch("src.cli.main.TTSEngine") as mock_tts,
        patch("src.cli.main.AudioMixer") as mock_mixer,
        patch("subprocess.run", side_effect=ffmpeg_side_effect),
        patch("src.cli.main._apply_waveform_cli_overrides", side_effect=capture_overrides),
    ):
        mock_parser.return_value.parse.return_value = {"text": "hello world", "music_cues": []}
        mock_tts.return_value.generate.return_value = voice_path
        mock_mixer.return_value.mix.return_value = mixed_path

        result = runner.invoke(
            app,
            [
                "create",
                str(script_path),
                "--audio-only",
                "--visualize",
                "--waveform-position",
                "top,bottom",
                "--waveform-lines",
                "3",
                "--waveform-thickness",
                "6,4,2",
                "--waveform-colors",
                "10,20,30:40,50,60",
                "--waveform-style",
                "bars",
                "--waveform-opacity",
                "0.5",
                "--waveform-randomize",
                "--waveform-height",
                "40",
                "--waveform-width",
                "30",
                "--waveform-left-spacing",
                "5",
                "--waveform-right-spacing",
                "7",
                "--waveform-render-scale",
                "2.5",
                "--waveform-anti-alias",
                "--waveform-orientation-offset",
                "80",
                "--waveform-rotation",
                "15",
                "--waveform-amplitude",
                "1.7",
                "--waveform-instances",
                "2",
                "--waveform-instances-offset",
                "12",
                "--waveform-instances-intersect",
                "--skip-music",
                "--output",
                "script",
            ],
        )

        assert result.exit_code == 0
        assert final_audio_path.exists()
        assert apply_calls
        recorded = apply_calls[0]
        assert recorded.position == "top,bottom"
        assert recorded.num_lines == 3
        assert recorded.thickness == "6,4,2"
        assert recorded.colors == "10,20,30:40,50,60"
        assert recorded.style == "bars"
        assert recorded.randomize is True

        waveform_config = config["visualization"]["waveform"]
        assert waveform_config["num_lines"] == 3
        assert waveform_config["position"] == "top,bottom"
        assert waveform_config["line_thickness"] == [6, 4, 2]
        assert waveform_config["line_colors"] == [[10, 20, 30], [40, 50, 60]]
        assert waveform_config["waveform_style"] == "bars"
        assert pytest.approx(waveform_config["opacity"], rel=1e-3) == 0.5
        assert waveform_config["randomize"] is True
        assert waveform_config["height_percent"] == 40
        assert waveform_config["width_percent"] == 30
        assert waveform_config["left_spacing"] == 5
        assert waveform_config["right_spacing"] == 7
        assert pytest.approx(waveform_config["render_scale"], rel=1e-3) == 2.5
        assert waveform_config["anti_alias"] is True
        assert pytest.approx(waveform_config["orientation_offset"], rel=1e-3) == 80.0
        assert pytest.approx(waveform_config["rotation"], rel=1e-3) == 15.0
        assert pytest.approx(waveform_config["amplitude_multiplier"], rel=1e-3) == 1.7
        assert waveform_config["num_instances"] == 2
        assert waveform_config["instances_offset"] == 12
        assert waveform_config["instances_intersect"] is True


def test_cli_create_handles_mixer_failure(tmp_path):
    script_path = tmp_path / "script.txt"
    script_path.write_text("# Title\nHello", encoding="utf-8")
    config = make_cli_config(tmp_path)

    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    fake_gpu.gpu_name = "CPU"
    fake_gpu.gpu_memory = 0

    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.cli.main.ScriptParser") as mock_parser,
        patch("src.cli.main.TTSEngine") as mock_tts,
        patch("src.cli.main.AudioMixer") as mock_mixer,
    ):

        mock_parser.return_value.parse.return_value = {"text": "hello", "music_cues": []}
        mock_tts.return_value.generate.return_value = tmp_path / "voice.mp3"
        mock_mixer.return_value.mix.side_effect = RuntimeError("mix failed")

        result = runner.invoke(app, ["create", str(script_path), "--skip-music"])

        assert result.exit_code == 1
        assert "Error" in result.stdout
