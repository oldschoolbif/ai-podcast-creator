import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def make_cfg(tmp_path):
    (tmp_path / "out").mkdir()
    (tmp_path / "cache").mkdir()
    return {
        "storage": {"outputs_dir": str(tmp_path / "out"), "cache_dir": str(tmp_path / "cache")},
        "video": {"fps": 24, "codec": "libx264"},
        "character": {"name": "QA Bot"},
    }


@pytest.mark.unit
def test_visualization_flow(tmp_path):
    from src.core.video_composer import VideoComposer

    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"mp3")

    cfg = make_cfg(tmp_path)
    expected = Path(cfg["storage"]["outputs_dir"]) / "podcast_0000.mp4"

    class FakeViz:
        def __init__(self, _):
            pass

        def generate_visualization(self, a, o):
            o.write_bytes(b"mp4")
            return o

    with patch("src.core.video_composer.datetime") as dt:
        dt.now.return_value.strftime.return_value = "0000"
        with patch.dict(sys.modules, {"src.core.audio_visualizer": MagicMock(AudioVisualizer=FakeViz)}):
            comp = VideoComposer(cfg)
            out = comp.compose(audio, use_visualization=True)
            assert out == expected
            assert out.exists()


@pytest.mark.unit
def test_text_overlay_path(tmp_path):
    """Ensure text overlay branch executes without MoviePy export."""
    from src.core.video_composer import VideoComposer

    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"mp3")

    cfg = make_cfg(tmp_path)

    class FakeClip:
        def __init__(self, *a, **k):
            pass

        def set_duration(self, d):
            return self

        def set_audio(self, a):
            return self

        def close(self):
            return None

        def write_videofile(self, *a, **k):
            return None

    class FakeAudio:
        duration = 1.0

        def close(self):
            pass

    # Patch moviepy.editor classes used
    fake_editor = MagicMock()
    fake_editor.AudioFileClip = MagicMock(return_value=FakeAudio())
    fake_editor.ImageClip = MagicMock(return_value=FakeClip())
    fake_editor.ColorClip = MagicMock(return_value=FakeClip())
    fake_editor.CompositeVideoClip = MagicMock(return_value=FakeClip())

    with patch.dict(sys.modules, {"moviepy": MagicMock(editor=fake_editor), "moviepy.editor": fake_editor}):
        with patch("src.core.video_composer.VideoComposer._create_text_image", return_value=str(tmp_path / "t.png")):
            comp = VideoComposer(cfg)
            out = comp.compose(audio)
            assert isinstance(out, Path)


@pytest.mark.unit
def test_ffmpeg_fallback_on_import_error(tmp_path):
    from src.core.video_composer import VideoComposer

    audio = tmp_path / "a.mp3"
    img = tmp_path / "bg.jpg"
    audio.write_bytes(b"mp3")
    img.write_bytes(b"jpg")

    cfg = make_cfg(tmp_path)
    cfg["video"]["background_path"] = str(img)

    with patch("src.core.video_composer.subprocess.run") as run:
        run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Force ImportError when importing moviepy.editor
        import builtins

        orig_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name.startswith("moviepy"):
                raise ImportError("no moviepy")
            return orig_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            comp = VideoComposer(cfg)
            out = comp.compose(audio)
            assert isinstance(out, Path)
            assert run.called


@pytest.mark.unit
def test_create_default_background(tmp_path):
    """Ensure default background generation works when missing."""
    from src.core.video_composer import VideoComposer

    cfg = make_cfg(tmp_path)
    # Remove background_path to force default generation
    cfg["video"]["background_path"] = str(tmp_path / "missing.jpg")

    comp = VideoComposer(cfg)
    bg = comp._create_default_background()
    assert bg.exists()
    assert bg.suffix == ".jpg"


@pytest.mark.unit
def test_overlay_visualization_on_avatar_success(tmp_path):
    """Test avatar overlay with visualization success path."""
    from src.core.video_composer import VideoComposer

    audio = tmp_path / "a.mp3"
    avatar = tmp_path / "avatar.mp4"
    audio.write_bytes(b"mp3")
    avatar.write_bytes(b"mp4")

    cfg = make_cfg(tmp_path)
    output = tmp_path / "out" / "final.mp4"

    class FakeViz:
        def __init__(self, _):
            pass

        def generate_visualization(self, a, o):
            o.write_bytes(b"viz")
            return o

    with patch("src.core.video_composer.subprocess.run") as run:
        run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        with patch.dict(sys.modules, {"src.core.audio_visualizer": MagicMock(AudioVisualizer=FakeViz)}):
            comp = VideoComposer(cfg)
            out = comp._overlay_visualization_on_avatar(avatar, audio, output)
            assert out == output
            assert run.called


@pytest.mark.unit
def test_overlay_visualization_ffmpeg_failure_uses_viz_fallback(tmp_path):
    """Test overlay fallback when FFmpeg fails."""
    from src.core.video_composer import VideoComposer

    audio = tmp_path / "a.mp3"
    avatar = tmp_path / "avatar.mp4"
    audio.write_bytes(b"mp3")
    avatar.write_bytes(b"mp4")

    cfg = make_cfg(tmp_path)
    output = tmp_path / "out" / "final.mp4"

    class FakeViz:
        def __init__(self, _):
            pass

        def generate_visualization(self, a, o):
            o.write_bytes(b"viz")
            return o

    # FFmpeg fails
    with patch("src.core.video_composer.subprocess.run") as run:
        run.return_value = MagicMock(returncode=1, stderr="ffmpeg error")
        with patch.dict(sys.modules, {"src.core.audio_visualizer": MagicMock(AudioVisualizer=FakeViz)}):
            comp = VideoComposer(cfg)
            out = comp._overlay_visualization_on_avatar(avatar, audio, output)
            # Should fall back to visualization copy
            assert out == output


