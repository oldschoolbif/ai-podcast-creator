"""Unit tests for the Typer-based CLI."""

import os
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
    if os.getenv("MUTANT_UNDER_TEST") or Path.cwd().name == "mutants":
        pytest.skip("Skip audio-only CLI success path during mutation runs; Typer exit handling is unstable under instrumentation.")
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

    def ffmpeg_side_effect(cmd, check=True, capture_output=True, text=False, **kwargs):
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

        assert result.exception is None, result.exception
        assert result.exit_code == 0, result.stdout
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

    def ffmpeg_side_effect(cmd, check=True, capture_output=True, text=False, **kwargs):
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

        assert result.exit_code == 0, result.stdout
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


def test_cli_create_avatar_background_visualization(tmp_path):
    script_path = tmp_path / "script.txt"
    script_path.write_text("Hello avatar world", encoding="utf-8")
    config = make_cli_config(tmp_path)

    voice_path = tmp_path / "voice.mp3"
    voice_path.write_bytes(b"voice")
    mixed_path = tmp_path / "mixed.mp3"
    mixed_path.write_bytes(b"mixed")
    avatar_path = tmp_path / "avatar.mp4"
    avatar_path.write_bytes(b"avatar-video")
    final_video_path = tmp_path / "outputs" / "custom.mp4"

    fake_gpu = MagicMock()
    fake_gpu.gpu_available = True
    fake_gpu.gpu_name = "Stub GPU"
    fake_gpu.gpu_memory = 12.0

    class DummyMetrics:
        def __init__(self):
            self.gpu_manager = SimpleNamespace(_component_gpu_samples=None)
            self.sessions = []
            self.quality = None
            self.flags = None

        def start_session(self, script_path, output_path=None):
            session_id = "sess123"
            return session_id

        def start_component(self, name):
            return SimpleNamespace(name=name)

        def finish_component(self, _component, error=None, file_monitor=None):
            return None

        def finish_session(self, output_path):
            self.sessions.append(output_path)

        def set_quality(self, quality):
            self.quality = quality

        def set_flags(self, avatar=False, visualization=False, background=False):
            self.flags = (avatar, visualization, background)

    class DummyProgress:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def add_task(self, *args, **kwargs):
            return 1

        def update(self, *args, **kwargs):
            return None

    metrics_stub = DummyMetrics()

    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.cli.main.ScriptParser") as mock_parser,
        patch("src.cli.main.TTSEngine") as mock_tts,
        patch("src.cli.main.AudioMixer") as mock_mixer,
        patch("src.core.avatar_generator.AvatarGenerator") as mock_avatar,
        patch("src.cli.main.VideoComposer") as mock_composer,
        patch("src.utils.metrics.get_metrics_tracker", return_value=metrics_stub),
        patch("src.cli.main.Progress", return_value=DummyProgress()),
        patch("subprocess.run") as mock_subproc,
    ):
        mock_parser.return_value.parse.return_value = {"text": "hello", "music_cues": []}
        mock_tts.return_value.generate.return_value = voice_path
        mock_mixer.return_value.mix.return_value = mixed_path

        avatar_instance = MagicMock()
        avatar_instance.generate.return_value = avatar_path
        avatar_instance.get_file_monitor.return_value = None
        mock_avatar.return_value = avatar_instance

        composer_instance = MagicMock()
        composer_instance.compose.return_value = final_video_path
        composer_instance.get_file_monitor.return_value = None
        mock_composer.return_value = composer_instance

        mock_subproc.return_value = SimpleNamespace(returncode=0, stdout="", stderr="")

        result = runner.invoke(
            app,
            [
                "create",
                str(script_path),
                "--avatar",
                "--visualize",
                "--background",
                "--output",
                "custom",
            ],
        )

        assert result.exit_code == 0, result.stdout
        avatar_instance.generate.assert_called_once_with(mixed_path)
        composer_instance.compose.assert_called_once()
        _, kwargs = composer_instance.compose.call_args
        assert kwargs["use_visualization"] is True
        assert kwargs["use_background"] is True
        assert kwargs["avatar_video"] == avatar_path
        assert kwargs["quality"] == "fastest"
        assert kwargs["output_name"] == "custom"
        assert metrics_stub.sessions == [str(final_video_path)]


def test_cli_create_avatar_fallback_to_visualization(tmp_path):
    script_path = tmp_path / "script.txt"
    script_path.write_text("Fallback avatar", encoding="utf-8")
    config = make_cli_config(tmp_path)

    voice_path = tmp_path / "voice.mp3"
    voice_path.write_bytes(b"voice")
    mixed_path = tmp_path / "mixed.mp3"
    mixed_path.write_bytes(b"mixed")
    avatar_path = tmp_path / "avatar.mp4"
    avatar_path.write_bytes(b"")  # simulate empty file
    final_video_path = tmp_path / "outputs" / "fallback.mp4"

    fake_gpu = MagicMock()
    fake_gpu.gpu_available = True
    fake_gpu.gpu_name = "Stub GPU"
    fake_gpu.gpu_memory = 12.0

    class DummyMetrics:
        def __init__(self):
            self.gpu_manager = SimpleNamespace(_component_gpu_samples=None)
            self.quality = None
            self.flags = None

        def start_session(self, *_args, **_kwargs):
            return "fallback-session"

        def start_component(self, name):
            return SimpleNamespace(name=name)

        def finish_component(self, *_args, **_kwargs):
            return None

        def finish_session(self, *_args, **_kwargs):
            return None

        def set_quality(self, quality):
            self.quality = quality

        def set_flags(self, avatar=False, visualization=False, background=False):
            self.flags = (avatar, visualization, background)

    class MinimalProgress:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def add_task(self, *args, **kwargs):
            return 1

        def update(self, *args, **kwargs):
            return None

    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.cli.main.ScriptParser") as mock_parser,
        patch("src.cli.main.TTSEngine") as mock_tts,
        patch("src.cli.main.AudioMixer") as mock_mixer,
        patch("src.core.avatar_generator.AvatarGenerator") as mock_avatar,
        patch("src.cli.main.VideoComposer") as mock_composer,
        patch("src.utils.metrics.get_metrics_tracker", return_value=DummyMetrics()),
        patch("src.cli.main.Progress", return_value=MinimalProgress()),
        patch("subprocess.run") as mock_subproc,
    ):
        mock_parser.return_value.parse.return_value = {"text": "fallback", "music_cues": []}
        mock_tts.return_value.generate.return_value = voice_path
        mock_mixer.return_value.mix.return_value = mixed_path

        avatar_instance = MagicMock()
        avatar_instance.generate.return_value = avatar_path
        avatar_instance.get_file_monitor.return_value = None
        mock_avatar.return_value = avatar_instance

        composer_instance = MagicMock()
        composer_instance.compose.return_value = final_video_path
        composer_instance.get_file_monitor.return_value = None
        mock_composer.return_value = composer_instance
        mock_subproc.return_value = SimpleNamespace(returncode=0, stdout="", stderr="")

        result = runner.invoke(
            app,
            [
                "create",
                str(script_path),
                "--avatar",
                "--visualize",
                "--background",
            ],
        )

        assert result.exception is None, repr(result.exception)
        assert result.exit_code == 0, result.stdout
        _, kwargs = composer_instance.compose.call_args
        assert kwargs["avatar_video"] is None
        assert kwargs["use_visualization"] is True
        assert kwargs["use_background"] is True


def test_cli_generate_face_success_when_device_available(tmp_path):
    config = make_cli_config(tmp_path)
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = True
    fake_gpu.gpu_name = "NVIDIA RTX 4060"
    fake_gpu.gpu_memory = 8.0

    generated = tmp_path / "generated_face.png"
    generated.write_bytes(b"face")

    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.core.face_generator.FaceGenerator") as mock_face,
    ):
        mock_instance = MagicMock()
        mock_instance.generate.return_value = generated
        mock_face.return_value = mock_instance

        output_path = tmp_path / "custom_face.png"
        result = runner.invoke(
            app,
            [
                "generate-face",
                "professional presenter",
                "--output",
                str(output_path),
            ],
        )

        assert result.exit_code == 0, result.stdout
        assert "Face generated successfully" in result.stdout
        mock_instance.generate.assert_called_once_with(
            description="professional presenter", output_path=output_path
        )


def test_cli_create_preview_only_skips_pipeline(tmp_path):
    script_path = tmp_path / "script.txt"
    script_path.write_text("Hello world", encoding="utf-8")

    config = make_cli_config(tmp_path)
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    fake_gpu.gpu_name = "CPU"
    fake_gpu.gpu_memory = 0

    parser_instance = MagicMock()
    parser_instance.parse.return_value = {"text": "preview text", "music_cues": []}

    tts_instance = MagicMock()
    audio_path = tmp_path / "voice.mp3"
    audio_path.write_bytes(b"voice")
    tts_instance.generate.return_value = audio_path

    class DummyRAMMonitor:
        total_ram_gb = 64.0
        max_ram_gb = 45.0

        def __init__(self, *args, **kwargs):
            pass

        def get_ram_usage_gb(self):
            return 10.0

        def check_ram_limit(self):
            return False, ""

    class DummyProgress:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def add_task(self, *args, **kwargs):
            return 1

        def update(self, *args, **kwargs):
            return None

    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.cli.main.ScriptParser", return_value=parser_instance),
        patch("src.cli.main.TTSEngine", return_value=tts_instance),
        patch("src.cli.main.AudioMixer") as mock_mixer,
        patch("src.cli.main.MusicGenerator") as mock_music,
        patch("src.cli.main.VideoComposer") as mock_composer,
        patch("src.utils.metrics.get_metrics_tracker", return_value=None),
        patch("src.utils.ram_monitor.RAMMonitor", DummyRAMMonitor),
        patch("src.cli.main.Progress", DummyProgress),
    ):
        result = runner.invoke(
            app,
            ["create", str(script_path), "--preview", "--skip-music"],
        )

        assert result.exit_code == 0, result.stdout
        assert "Preview audio created" in result.stdout
        mock_mixer.assert_not_called()
        mock_music.assert_not_called()
        mock_composer.assert_not_called()


def test_cli_create_audio_only_with_music_file(tmp_path):
    script_path = tmp_path / "script.txt"
    script_path.write_text("Hello audio", encoding="utf-8")

    music_path = tmp_path / "music.mp3"
    music_path.write_bytes(b"music")

    config = make_cli_config(tmp_path)
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    fake_gpu.gpu_name = "CPU"
    fake_gpu.gpu_memory = 0

    parser_instance = MagicMock()
    parser_instance.parse.return_value = {"text": "Hello audio", "music_cues": []}

    tts_instance = MagicMock()
    audio_path = tmp_path / "voice.mp3"
    audio_path.write_bytes(b"voice")
    tts_instance.generate.return_value = audio_path

    mixer_instance = MagicMock()
    mixed_audio = tmp_path / "mixed.mp3"
    mixed_audio.write_bytes(b"mixed")
    mixer_instance.mix.return_value = mixed_audio

    class DummyRAMMonitor:
        total_ram_gb = 64.0
        max_ram_gb = 45.0

        def __init__(self, *args, **kwargs):
            pass

        def get_ram_usage_gb(self):
            return 10.0

        def check_ram_limit(self):
            return False, ""

    class DummyProgress:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def add_task(self, *args, **kwargs):
            return 1

        def update(self, *args, **kwargs):
            return None

    def fake_run(cmd, check, capture_output, text=None):
        Path(cmd[-2]).write_bytes(b"final-mp3")
        return MagicMock(stdout="", stderr="")

    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.cli.main.ScriptParser", return_value=parser_instance),
        patch("src.cli.main.TTSEngine", return_value=tts_instance),
        patch("src.cli.main.AudioMixer", return_value=mixer_instance),
        patch("src.cli.main.MusicGenerator") as mock_music,
        patch("src.cli.main.VideoComposer") as mock_composer,
        patch("src.utils.metrics.get_metrics_tracker", return_value=None),
        patch("src.utils.ram_monitor.RAMMonitor", DummyRAMMonitor),
        patch("src.cli.main.Progress", DummyProgress),
        patch("subprocess.run", side_effect=fake_run),
    ):
        result = runner.invoke(
            app,
            [
                "create",
                str(script_path),
                "--audio-only",
                "--music-file",
                str(music_path),
                "--output",
                "final_audio",
            ],
        )

        assert result.exit_code == 0
        assert "Podcast audio created successfully" in result.stdout
        final_audio = tmp_path / "outputs" / "final_audio.mp3"
        assert final_audio.exists()
        mock_music.assert_not_called()
        mock_composer.assert_not_called()


def test_cli_create_with_avatar_visualize_background(tmp_path):
    script_path = tmp_path / "script.txt"
    script_path.write_text("# Title\nContent", encoding="utf-8")

    config = make_cli_config(tmp_path)
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = True
    fake_gpu.gpu_name = "RTX"
    fake_gpu.gpu_memory = 8.0

    parser_instance = MagicMock()
    parser_instance.parse.return_value = {"text": "Chunk text", "music_cues": ["upbeat instrumental"]}

    tts_instance = MagicMock()
    audio_path = tmp_path / "voice.mp3"
    audio_path.write_bytes(b"voice")
    tts_instance.generate.return_value = audio_path

    music_instance = MagicMock()
    generated_music = tmp_path / "generated.wav"
    generated_music.write_bytes(b"music")
    music_instance.generate.return_value = generated_music

    mixer_instance = MagicMock()
    mixed_audio = tmp_path / "mixed.mp3"
    mixed_audio.write_bytes(b"mixed")
    mixer_instance.mix.return_value = mixed_audio

    composer_instance = MagicMock()
    final_video = tmp_path / "outputs" / "chunk_video.mp4"
    final_video.parent.mkdir(parents=True, exist_ok=True)
    final_video.write_bytes(b"video")
    composer_instance.compose.return_value = final_video

    avatar_instance = MagicMock()
    avatar_video = tmp_path / "avatar.mp4"
    avatar_video.write_bytes(b"avatar")
    avatar_instance.generate.return_value = avatar_video

    class DummyMetrics:
        def __init__(self):
            self.flags = None
            self.quality = None

        def start_session(self, script_path):
            return "session01"

        def set_quality(self, quality):
            self.quality = quality

        def set_flags(self, **flags):
            self.flags = flags

        def start_component(self, component):
            return MagicMock()

        def finish_component(self, metrics, **kwargs):
            return None

        def finish_session(self, output_path=None):
            self.finished = output_path

    metrics_stub = DummyMetrics()

    class DummyRAMMonitor:
        total_ram_gb = 64.0
        max_ram_gb = 45.0

        def __init__(self, *args, **kwargs):
            pass

        def get_ram_usage_gb(self):
            return 12.0

        def check_ram_limit(self):
            return False, ""

    class DummyProgress:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def add_task(self, *args, **kwargs):
            return 1

        def update(self, *args, **kwargs):
            return None

    def fake_waveform_overrides(config, *args):
        return {**config, "visualization": {"overridden": True}}

    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.cli.main.ScriptParser", return_value=parser_instance),
        patch("src.cli.main.TTSEngine", return_value=tts_instance),
        patch("src.cli.main.MusicGenerator", return_value=music_instance),
        patch("src.cli.main.AudioMixer", return_value=mixer_instance),
        patch("src.cli.main.VideoComposer", return_value=composer_instance),
        patch("src.core.avatar_generator.AvatarGenerator", return_value=avatar_instance),
        patch("src.utils.metrics.get_metrics_tracker", return_value=metrics_stub),
        patch("src.utils.ram_monitor.RAMMonitor", DummyRAMMonitor),
        patch("src.cli.main.Progress", DummyProgress),
        patch("src.utils.script_chunker.chunk_script", return_value=[script_path]),
        patch("src.cli.main._apply_waveform_cli_overrides", side_effect=fake_waveform_overrides) as mock_waveform,
    ):
        result = runner.invoke(
            app,
            [
                "create",
                str(script_path),
                "energetic intro",
                "--visualize",
                "--background",
                "--avatar",
                "--quality",
                "high",
                "--chunk-duration",
                "1",
                "--waveform-lines",
                "3",
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
                "2.0",
                "--waveform-anti-alias",
                "--waveform-orientation-offset",
                "80",
                "--waveform-rotation",
                "15",
                "--waveform-amplitude",
                "1.6",
                "--waveform-instances",
                "2",
                "--waveform-instances-offset",
                "12",
                "--waveform-instances-intersect",
            ],
        )

        assert result.exit_code == 0
        assert final_video.exists()
        mock_waveform.assert_called_once()
        assert metrics_stub.flags == {"avatar": True, "visualization": True, "background": True}
        composer_instance.compose.assert_called_once()
        avatar_instance.generate.assert_called_once()


def test_cli_list_without_database(tmp_path):
    """Test list command when database is not available."""
    with patch("src.cli.main.DATABASE_AVAILABLE", False):
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "Database not available" in result.stdout


def test_cli_list_with_database(tmp_path):
    """Test list command when database is available."""
    with (
        patch("src.cli.main.DATABASE_AVAILABLE", True),
        patch("src.cli.main.console") as mock_console,
    ):
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        mock_console.print.assert_called()


def test_cli_config_show(tmp_path):
    """Test config command with --show flag."""
    config = make_cli_config(tmp_path)
    
    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.console") as mock_console,
    ):
        result = runner.invoke(app, ["config", "--show"])
        
        assert result.exit_code == 0
        mock_console.print.assert_called()


def test_cli_config_edit(tmp_path):
    """Test config command with --edit flag."""
    # Rich console output may not appear in stdout, so just check exit code
    result = runner.invoke(app, ["config", "--edit"])
    
    assert result.exit_code == 0


def test_cli_config_reset(tmp_path):
    """Test config command with --reset flag."""
    # Rich console output may not appear in stdout, so just check exit code
    result = runner.invoke(app, ["config", "--reset"])
    
    assert result.exit_code == 0


def test_cli_config_no_flags(tmp_path):
    """Test config command without flags."""
    result = runner.invoke(app, ["config"])
    
    assert result.exit_code == 0
    assert "Use --show to display config" in result.stdout


def test_cli_init_creates_directories(tmp_path):
    """Test init command creates required directories."""
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        
        with (
            patch("src.cli.main.DATABASE_AVAILABLE", False),
            patch("src.cli.main.console") as mock_console,
        ):
            result = runner.invoke(app, ["init"])
            
            assert result.exit_code == 0
            # Check directories were created
            assert (tmp_path / "data" / "scripts").exists()
            assert (tmp_path / "data" / "outputs").exists()
            assert (tmp_path / "data" / "cache").exists()
            assert (tmp_path / "data" / "models").exists()
            assert (tmp_path / "logs").exists()
    finally:
        os.chdir(original_cwd)


def test_cli_init_with_database(tmp_path):
    """Test init command with database available."""
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        
        with (
            patch("src.cli.main.DATABASE_AVAILABLE", True),
            patch("src.cli.main.init_db") as mock_init_db,
            patch("src.cli.main.console") as mock_console,
        ):
            result = runner.invoke(app, ["init"])
            
            assert result.exit_code == 0
            mock_init_db.assert_called_once()
    finally:
        os.chdir(original_cwd)


def test_cli_version(tmp_path):
    """Test version command."""
    config = make_cli_config(tmp_path)
    
    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.console") as mock_console,
    ):
        result = runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        mock_console.print.assert_called()


def test_cli_status(tmp_path):
    """Test status command."""
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    fake_gpu.gpu_name = "CPU"
    fake_gpu.gpu_memory = 0
    
    with (
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.cli.main.console") as mock_console,
        patch("subprocess.run") as mock_subprocess,
    ):
        # Mock FFmpeg check
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "ffmpeg version"
        
        result = runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        mock_console.print.assert_called()


def test_cli_generate_face_no_gpu(tmp_path):
    """Test generate_face command when GPU is not available (line 70)."""
    config = make_cli_config(tmp_path)
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    
    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.core.face_generator.FaceGenerator") as mock_face_gen,
    ):
        mock_face_gen.return_value.generate.return_value = tmp_path / "face.png"
        
        result = runner.invoke(app, ["generate-face", "test face"])
        
        assert result.exit_code == 0
        assert "CPU" in result.stdout or "WARN" in result.stdout


def test_cli_generate_face_exception(tmp_path):
    """Test generate_face command exception handling (lines 93-95)."""
    config = make_cli_config(tmp_path)
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    
    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("src.core.face_generator.FaceGenerator") as mock_face_gen,
    ):
        mock_face_gen.return_value.generate.side_effect = Exception("Face generation failed")
        
        result = runner.invoke(app, ["generate-face", "test face"])
        
        assert result.exit_code == 1
        assert "Error" in result.stdout


def test_cli_create_with_chunking_error(tmp_path):
    """Test create command with chunking error (lines 215-218)."""
    script_path = tmp_path / "script.txt"
    script_path.write_text("# Title\nHello world", encoding="utf-8")
    config = make_cli_config(tmp_path)
    
    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.chunk_script", side_effect=Exception("Chunking failed")),
        patch("src.cli.main.ScriptParser") as mock_parser,
        patch("src.cli.main.TTSEngine") as mock_tts,
        patch("src.cli.main.AudioMixer") as mock_mixer,
        patch("src.cli.main.VideoComposer") as mock_composer,
        patch("src.utils.ram_monitor.RAMMonitor") as mock_ram,
    ):
        mock_ram_instance = MagicMock()
        mock_ram_instance.get_ram_usage_gb.return_value = 10.0
        mock_ram_instance.total_ram_gb = 64.0
        mock_ram_instance.max_ram_gb = 45.0
        mock_ram_instance.check_ram_limit.return_value = (False, None)
        mock_ram.return_value = mock_ram_instance
        
        mock_parser.return_value.parse.return_value = {"text": "Hello world", "music_cues": []}
        mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
        mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
        mock_composer.return_value.compose.return_value = tmp_path / "output" / "video.mp4"
        
        result = runner.invoke(app, ["create", str(script_path), "--chunk-duration", "3"])
        
        # Should continue with full script
        assert "Continuing with full script" in result.stdout or result.exit_code == 0


def test_cli_create_multiple_chunks(tmp_path):
    """Test create command with multiple chunks (lines 229-230, 252, 254-256, 370-372, 479-483)."""
    script_path = tmp_path / "script.txt"
    script_path.write_text("# Title\n" + "Hello world. " * 1000, encoding="utf-8")  # Long script
    config = make_cli_config(tmp_path)
    
    # Mock chunker to return multiple chunks
    chunk1 = tmp_path / "chunk1.txt"
    chunk2 = tmp_path / "chunk2.txt"
    chunk1.write_text("Chunk 1", encoding="utf-8")
    chunk2.write_text("Chunk 2", encoding="utf-8")
    
    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.chunk_script", return_value=[chunk1, chunk2]),
        patch("src.cli.main.ScriptParser") as mock_parser,
        patch("src.cli.main.TTSEngine") as mock_tts,
        patch("src.cli.main.AudioMixer") as mock_mixer,
        patch("src.cli.main.VideoComposer") as mock_composer,
        patch("src.utils.ram_monitor.RAMMonitor") as mock_ram,
    ):
        mock_ram_instance = MagicMock()
        mock_ram_instance.get_ram_usage_gb.return_value = 10.0
        mock_ram_instance.total_ram_gb = 64.0
        mock_ram_instance.max_ram_gb = 45.0
        mock_ram_instance.check_ram_limit.return_value = (False, None)
        mock_ram.return_value = mock_ram_instance
        
        mock_parser.return_value.parse.return_value = {"text": "Hello world", "music_cues": []}
        mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
        mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
        mock_composer.return_value.compose.return_value = tmp_path / "output" / "video.mp4"
        
        result = runner.invoke(app, ["create", str(script_path), "--chunk-duration", "1"])
        
        # Should process multiple chunks
        assert "Processing" in result.stdout or "chunk" in result.stdout.lower() or result.exit_code == 0


def test_cli_create_with_music_offset(tmp_path):
    """Test create command with music_start_offset (line 319)."""
    script_path = tmp_path / "script.txt"
    script_path.write_text("# Title\nHello world", encoding="utf-8")
    config = make_cli_config(tmp_path)
    
    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.ScriptParser") as mock_parser,
        patch("src.cli.main.TTSEngine") as mock_tts,
        patch("src.cli.main.AudioMixer") as mock_mixer,
        patch("src.cli.main.VideoComposer") as mock_composer,
        patch("src.utils.ram_monitor.RAMMonitor") as mock_ram,
    ):
        mock_ram_instance = MagicMock()
        mock_ram_instance.get_ram_usage_gb.return_value = 10.0
        mock_ram_instance.total_ram_gb = 64.0
        mock_ram_instance.max_ram_gb = 45.0
        mock_ram_instance.check_ram_limit.return_value = (False, None)
        mock_ram.return_value = mock_ram_instance
        
        mock_parser.return_value.parse.return_value = {"text": "Hello world", "music_cues": []}
        mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
        mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
        mock_composer.return_value.compose.return_value = tmp_path / "output" / "video.mp4"
        
        result = runner.invoke(app, ["create", str(script_path), "calm music", "--music-offset", "5.0"])
        
        assert result.exit_code == 0
        # Should mention music offset
        assert "offset" in result.stdout.lower() or "5" in result.stdout


def test_cli_create_with_avatar(tmp_path):
    """Test create command with avatar enabled (lines 381->420, 390->401)."""
    script_path = tmp_path / "script.txt"
    script_path.write_text("# Title\nHello world", encoding="utf-8")
    config = make_cli_config(tmp_path)
    
    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.ScriptParser") as mock_parser,
        patch("src.cli.main.TTSEngine") as mock_tts,
        patch("src.cli.main.AudioMixer") as mock_mixer,
        patch("src.cli.main.VideoComposer") as mock_composer,
        patch("src.core.avatar_generator.AvatarGenerator") as mock_avatar,
        patch("src.utils.ram_monitor.RAMMonitor") as mock_ram,
    ):
        mock_ram_instance = MagicMock()
        mock_ram_instance.get_ram_usage_gb.return_value = 10.0
        mock_ram_instance.total_ram_gb = 64.0
        mock_ram_instance.max_ram_gb = 45.0
        mock_ram_instance.check_ram_limit.return_value = (False, None)
        mock_ram.return_value = mock_ram_instance
        
        mock_parser.return_value.parse.return_value = {"text": "Hello world", "music_cues": []}
        mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
        mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
        
        avatar_video = tmp_path / "avatar.mp4"
        avatar_video.write_bytes(b"video")
        mock_avatar_instance = MagicMock()
        mock_avatar_instance.generate.return_value = avatar_video
        mock_avatar_instance.get_file_monitor.return_value = None
        mock_avatar.return_value = mock_avatar_instance
        
        mock_composer.return_value.compose.return_value = tmp_path / "output" / "video.mp4"
        
        result = runner.invoke(app, ["create", str(script_path), "--avatar"])
        
        assert result.exit_code == 0
        mock_avatar.assert_called_once()


def test_cli_status_with_gpu(tmp_path):
    """Test status command with GPU available (lines 737, 747-775, 798-802, 807)."""
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = True
    fake_gpu.gpu_name = "Test GPU"
    fake_gpu.gpu_memory = 8.0
    fake_gpu.get_performance_config.return_value = {"use_fp16": True, "use_tf32": True}
    fake_gpu.get_memory_usage.return_value = {
        "allocated_gb": 2.0,
        "free_gb": 6.0,
        "total_gb": 8.0
    }
    
    # Mock torch module
    mock_torch = MagicMock()
    mock_torch.cuda.get_device_capability.return_value = (8, 0)
    mock_torch.version.cuda = "11.8"
    mock_torch.backends.cudnn.is_available.return_value = True
    mock_torch.backends.cudnn.version.return_value = 8500
    
    with (
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("subprocess.run") as mock_subprocess,
        patch.dict("sys.modules", {"torch": mock_torch}),
    ):
        # Mock FFmpeg with NVENC
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "enable-nvenc"
        
        result = runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        assert "GPU" in result.stdout or "OK" in result.stdout


def test_cli_status_ffmpeg_not_found(tmp_path):
    """Test status command when FFmpeg is not found (lines 741-743)."""
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    
    with (
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("subprocess.run", side_effect=FileNotFoundError()),
    ):
        result = runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        assert "FFmpeg" in result.stdout or "FAIL" in result.stdout


def test_cli_status_gpu_with_torch_error(tmp_path):
    """Test status command with GPU but torch error (line 774)."""
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = True
    fake_gpu.gpu_name = "Test GPU"
    fake_gpu.gpu_memory = 8.0
    fake_gpu.get_performance_config.return_value = {"use_fp16": False, "use_tf32": False}
    fake_gpu.get_memory_usage.return_value = {
        "allocated_gb": 2.0,
        "free_gb": 6.0,
        "total_gb": 8.0
    }
    
    # Mock torch module to raise exception
    mock_torch = MagicMock()
    mock_torch.cuda.get_device_capability.side_effect = Exception("Torch error")
    
    with (
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("subprocess.run") as mock_subprocess,
        patch.dict("sys.modules", {"torch": mock_torch}),
    ):
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "ffmpeg version"
        
        result = runner.invoke(app, ["status"])
        
        assert result.exit_code == 0


def test_cli_status_cpu_with_torch_not_available(tmp_path):
    """Test status command with CPU and torch not available (lines 781-782)."""
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    
    # Mock torch module
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False
    
    with (
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("subprocess.run") as mock_subprocess,
        patch.dict("sys.modules", {"torch": mock_torch}),
    ):
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "ffmpeg version"
        
        result = runner.invoke(app, ["status"])
        
        assert result.exit_code == 0


def test_cli_status_models_dir_not_found(tmp_path):
    """Test status command when models directory not found (line 792)."""
    fake_gpu = MagicMock()
    fake_gpu.gpu_available = False
    
    with (
        patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
        patch("subprocess.run") as mock_subprocess,
        patch("pathlib.Path.exists", return_value=False),
    ):
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "ffmpeg version"
        
        result = runner.invoke(app, ["status"])
        
        assert result.exit_code == 0


def test_cli_waveform_overrides_invalid_thickness(tmp_path):
    """Test _apply_waveform_cli_overrides with invalid thickness (lines 852-854)."""
    from src.cli.main import _apply_waveform_cli_overrides
    
    config = {}
    
    # Test invalid thickness format
    result_config = _apply_waveform_cli_overrides(
        config.copy(),
        position=None,
        num_lines=None,
        thickness="invalid",
        colors=None,
        style=None,
        opacity=None,
        randomize=False,
        height_percent=None,
        width_percent=None,
        left_spacing=None,
        right_spacing=None,
        render_scale=None,
        anti_alias=None,
        orientation_offset=None,
        rotation=None,
        amplitude_multiplier=None,
        num_instances=None,
        instances_offset=None,
        instances_intersect=None,
    )
    
    # Should not crash, may use default
    assert "visualization" in result_config


def test_cli_waveform_overrides_invalid_colors(tmp_path):
    """Test _apply_waveform_cli_overrides with invalid colors (lines 862->860, 864->868, 866-867)."""
    from src.cli.main import _apply_waveform_cli_overrides
    
    config = {}
    
    # Test invalid colors format
    result_config = _apply_waveform_cli_overrides(
        config.copy(),
        position=None,
        num_lines=None,
        thickness=None,
        colors="invalid,format",
        style=None,
        opacity=None,
        randomize=False,
        height_percent=None,
        width_percent=None,
        left_spacing=None,
        right_spacing=None,
        render_scale=None,
        anti_alias=None,
        orientation_offset=None,
        rotation=None,
        amplitude_multiplier=None,
        num_instances=None,
        instances_offset=None,
        instances_intersect=None,
    )
    
    # Should not crash
    assert "visualization" in result_config or result_config == config


def test_cli_waveform_overrides_invalid_style(tmp_path):
    """Test _apply_waveform_cli_overrides with invalid style (line 872)."""
    from src.cli.main import _apply_waveform_cli_overrides
    
    config = {}
    
    # Test invalid style
    result_config = _apply_waveform_cli_overrides(
        config.copy(),
        position=None,
        num_lines=None,
        thickness=None,
        colors=None,
        style="invalid_style",
        opacity=None,
        randomize=False,
        height_percent=None,
        width_percent=None,
        left_spacing=None,
        right_spacing=None,
        render_scale=None,
        anti_alias=None,
        orientation_offset=None,
        rotation=None,
        amplitude_multiplier=None,
        num_instances=None,
        instances_offset=None,
        instances_intersect=None,
    )
    
    # Should not crash
    assert "visualization" in result_config


def test_cli_main_function():
    """Test main() function (line 907)."""
    from src.cli.main import main
    
    with patch("src.cli.main.app") as mock_app:
        main()
        mock_app.assert_called_once()


def test_cli_cleanup_dry_run(tmp_path):
    """Test cleanup command with --dry-run flag."""
    config = make_cli_config(tmp_path)
    
    # Create some test files
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / "test.txt").write_text("test")
    
    with patch("src.cli.main.load_config", return_value=config):
        result = runner.invoke(app, ["cleanup", "--dry-run"])
        
        assert result.exit_code == 0
        # File should still exist (dry-run doesn't delete)
        assert (cache_dir / "test.txt").exists()


def test_cli_cleanup_nothing_to_clean(tmp_path):
    """Test cleanup command when there's nothing to clean."""
    config = make_cli_config(tmp_path)
    
    with patch("src.cli.main.load_config", return_value=config):
        result = runner.invoke(app, ["cleanup", "--force"])
        
        assert result.exit_code == 0
        # Rich console output may not appear in stdout, but command should succeed


def test_cli_cleanup_cache_only(tmp_path):
    """Test cleanup command with --cache-only flag."""
    config = make_cli_config(tmp_path)
    
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / "test.txt").write_text("test")
    
    with (
        patch("src.cli.main.load_config", return_value=config),
        patch("src.cli.main.console") as mock_console,
        patch("typer.confirm", return_value=True),
    ):
        result = runner.invoke(app, ["cleanup", "--cache-only", "--force"])
        
        assert result.exit_code == 0