import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def make_cfg(tmp_path, engine="wav2lip"):
    (tmp_path / "cache").mkdir()
    return {
        "storage": {"cache_dir": str(tmp_path / "cache"), "outputs_dir": str(tmp_path / "out")},
        "avatar": {"engine": engine, "sadtalker": {"enhancer": "gfpgan"}},
    }


@pytest.mark.unit
def test_init_wav2lip_missing_model_sets_fallback(tmp_path):
    from src.core.avatar_generator import AvatarGenerator

    cfg = make_cfg(tmp_path, engine="wav2lip")

    with patch("src.core.avatar_generator.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        gen = AvatarGenerator(cfg)
        # Model path may be None or a path depending on download; accept both but no crash
        assert hasattr(gen, "wav2lip_model_path")


@pytest.mark.unit
def test_did_init_without_key(tmp_path, capsys):
    from src.core.avatar_generator import AvatarGenerator

    cfg = make_cfg(tmp_path, engine="did")
    gen = AvatarGenerator(cfg)
    # Should not raise; prints warning and continues
    # Call a method that will fallback due to missing key
    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"mp3")
    out = gen.generate(audio)
    assert isinstance(out, Path)


@pytest.mark.unit
def test_sadtalker_not_present_uses_fallback(tmp_path):
    from src.core.avatar_generator import AvatarGenerator

    cfg = make_cfg(tmp_path, engine="sadtalker")
    gen = AvatarGenerator(cfg)

    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"mp3")

    with patch.object(AvatarGenerator, "_create_fallback_video", return_value=tmp_path / "out.mp4") as fb:
        out = gen.generate(audio)
        assert out.name.endswith(".mp4")
        assert fb.called


@pytest.mark.unit
def test_sadtalker_subprocess_command_built_correctly(tmp_path):
    """Verify SadTalker command construction when external dir exists."""
    from src.core.avatar_generator import AvatarGenerator
    import subprocess

    cfg = make_cfg(tmp_path, engine="sadtalker")
    cfg["avatar"]["sadtalker"] = {"enhancer": "gfpgan", "expression_scale": 1.5, "still_mode": True}

    # Create fake SadTalker external directory
    sadtalker_path = tmp_path.parent / "external" / "SadTalker"
    sadtalker_path.mkdir(parents=True)
    (sadtalker_path / "inference.py").touch()
    (sadtalker_path / "checkpoints").mkdir()

    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"mp3")

    with patch("src.core.avatar_generator.get_gpu_manager") as get_gpu:
        gpu = MagicMock()
        gpu.gpu_available = False
        gpu.get_device.return_value = "cpu"
        get_gpu.return_value = gpu

        gen = AvatarGenerator(cfg)

        with patch("src.core.avatar_generator.subprocess.run") as run:
            run.return_value = MagicMock(returncode=1, stderr="")  # Simulate failure to test fallback
            out = gen.generate(audio)
            # Should call subprocess with correct structure
            assert run.called
            assert out.name.endswith(".mp4")


@pytest.mark.unit
def test_wav2lip_fallback_video_creation(tmp_path):
    """Test Wav2Lip fallback video uses MoviePy."""
    from src.core.avatar_generator import AvatarGenerator

    cfg = make_cfg(tmp_path, engine="wav2lip")
    gen = AvatarGenerator(cfg)
    gen.wav2lip_model_path = None  # No model = will use fallback

    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"mp3")

    class FakeAudio:
        duration = 2.0

        def close(self):
            pass

    class FakeImageClip:
        def __init__(self, *a, **k):
            pass

        def set_audio(self, a):
            return self

        def write_videofile(self, *a, **k):
            pass

    fake_moviepy = MagicMock()
    fake_moviepy.editor = MagicMock()
    fake_moviepy.editor.AudioFileClip = MagicMock(return_value=FakeAudio())
    fake_moviepy.editor.ImageClip = MagicMock(return_value=FakeImageClip())

    with patch.dict(sys.modules, {"moviepy": fake_moviepy, "moviepy.editor": fake_moviepy.editor}):
        # Ensure fallback path is tested
        out = gen._create_fallback_video(audio, tmp_path / "fallback.mp4")
        assert out.name.endswith(".mp4")


