"""Unit tests for the Typer-based CLI."""

import sys
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
