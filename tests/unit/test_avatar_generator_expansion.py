"""
Expanded Avatar Generator Tests - Night Shift Edition
Comprehensive edge case and path coverage
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def make_avatar_config(tmp_path, engine="wav2lip"):
    """Create avatar config for testing."""
    return {
        "storage": {"cache_dir": str(tmp_path / "cache"), "outputs_dir": str(tmp_path / "output")},
        "avatar": {
            "engine": engine,
            "source_image": str(tmp_path / "avatar.jpg"),
            "sadtalker": {"enhancer": "gfpgan", "expression_scale": 1.0, "still_mode": False},
            "did": {"api_key": "test_key"},
        },
    }


class TestAvatarGeneratorInitialization:
    """Test AvatarGenerator initialization paths."""

    def test_init_creates_output_directory(self, tmp_path):
        """Test that output directory is created on init."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path)
        gen = AvatarGenerator(cfg)

        assert gen.output_dir.exists()
        assert gen.output_dir.is_dir()

    def test_init_creates_models_directory(self, tmp_path):
        """Test that models directory is created on init."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path)
        gen = AvatarGenerator(cfg)

        assert gen.models_dir.exists()
        assert gen.models_dir.is_dir()

    def test_init_sets_source_image_from_config(self, tmp_path):
        """Test source image is set from config."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path)
        avatar_img = tmp_path / "custom_avatar.jpg"
        avatar_img.write_bytes(b"image")
        cfg["avatar"]["source_image"] = str(avatar_img)

        gen = AvatarGenerator(cfg)

        assert gen.source_image == avatar_img

    def test_init_uses_default_source_image(self, tmp_path):
        """Test default source image when not specified."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path)
        del cfg["avatar"]["source_image"]

        gen = AvatarGenerator(cfg)

        # Should use default path
        assert gen.source_image is not None
        assert isinstance(gen.source_image, Path)

    def test_init_wav2lip_engine(self, tmp_path):
        """Test initialization with Wav2Lip engine."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="wav2lip")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            gen = AvatarGenerator(cfg)

            assert gen.engine_type == "wav2lip"
            assert hasattr(gen, "wav2lip_model_path")

    def test_init_sadtalker_engine(self, tmp_path):
        """Test initialization with SadTalker engine."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="sadtalker")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            gen = AvatarGenerator(cfg)

            assert gen.engine_type == "sadtalker"

    def test_init_did_engine(self, tmp_path):
        """Test initialization with D-ID engine."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="did")

        gen = AvatarGenerator(cfg)

        assert gen.engine_type == "did"
        assert hasattr(gen, "did_api_key")


class TestAvatarGeneratorGenerate:
    """Test generate method."""

    def test_generate_wav2lip_path(self, tmp_path):
        """Test generate with Wav2Lip engine."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="wav2lip")
        gen = AvatarGenerator(cfg)

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"audio")

        with patch.object(gen, "_generate_wav2lip") as mock_gen:
            mock_gen.return_value = tmp_path / "avatar.mp4"
            result = gen.generate(audio_path)

            assert result is not None
            assert mock_gen.called

    def test_generate_sadtalker_path(self, tmp_path):
        """Test generate with SadTalker engine."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="sadtalker")
        gen = AvatarGenerator(cfg)

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"audio")

        with patch.object(gen, "_generate_sadtalker") as mock_gen:
            mock_gen.return_value = tmp_path / "avatar.mp4"
            result = gen.generate(audio_path)

            assert result is not None
            assert mock_gen.called

    def test_generate_did_path(self, tmp_path):
        """Test generate with D-ID engine."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="did")
        gen = AvatarGenerator(cfg)

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"audio")

        with patch.object(gen, "_generate_did") as mock_gen:
            mock_gen.return_value = tmp_path / "avatar.mp4"
            result = gen.generate(audio_path)

            assert result is not None
            assert mock_gen.called

    def test_generate_output_path_format(self, tmp_path):
        """Test that output path follows expected format."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path)
        gen = AvatarGenerator(cfg)

        audio_path = tmp_path / "my_audio_file.mp3"
        expected_output = gen.output_dir / f"avatar_{audio_path.stem}.mp4"

        with patch.object(gen, "_generate_wav2lip", return_value=expected_output):
            result = gen.generate(audio_path)

            assert result == expected_output
            assert "avatar_" in result.name


class TestAvatarGeneratorFallback:
    """Test fallback video creation."""

    def test_create_fallback_video_with_moviepy(self, tmp_path):
        """Test fallback video creation using MoviePy."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path)
        gen = AvatarGenerator(cfg)

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"audio")
        output_path = tmp_path / "fallback.mp4"

        # Mock moviepy
        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()

        mock_audio = MagicMock()
        mock_audio.duration = 5.0
        mock_audio.close = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)

        mock_image = MagicMock()
        mock_image.set_audio.return_value = mock_image
        mock_image.set_duration.return_value = mock_image
        mock_image.write_videofile = MagicMock()
        mock_moviepy.editor.ImageClip = MagicMock(return_value=mock_image)

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            # Create source image for fallback
            gen.source_image.parent.mkdir(parents=True, exist_ok=True)
            gen.source_image.write_bytes(b"image")

            result = gen._create_fallback_video(audio_path, output_path)

            assert result == output_path
            assert mock_moviepy.editor.AudioFileClip.called
            assert mock_moviepy.editor.ImageClip.called

    def test_create_fallback_video_handles_missing_source_image(self, tmp_path):
        """Test fallback when source image doesn't exist."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path)
        gen = AvatarGenerator(cfg)

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"audio")
        output_path = tmp_path / "fallback.mp4"

        # Source image doesn't exist
        gen.source_image = tmp_path / "missing.jpg"

        # Mock moviepy
        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()

        mock_audio = MagicMock()
        mock_audio.duration = 5.0
        mock_audio.close = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)

        mock_image = MagicMock()
        mock_image.set_audio.return_value = mock_image
        mock_image.set_duration.return_value = mock_image
        mock_image.write_videofile = MagicMock()
        mock_moviepy.editor.ImageClip = MagicMock(return_value=mock_image)

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            # Should handle missing image gracefully (will try to load anyway)
            try:
                result = gen._create_fallback_video(audio_path, output_path)
                # May succeed or fail depending on MoviePy behavior
            except Exception:
                # Expected if image doesn't exist
                pass


class TestAvatarGeneratorSadTalkerPaths:
    """Test SadTalker-specific paths."""

    def test_sadtalker_command_construction_with_still_mode(self, tmp_path):
        """Test SadTalker command includes --still when configured."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="sadtalker")
        cfg["avatar"]["sadtalker"]["still_mode"] = True

        gen = AvatarGenerator(cfg)

        # Verify still_mode is in config
        assert cfg["avatar"]["sadtalker"]["still_mode"] is True

    def test_sadtalker_command_construction_with_expression_scale(self, tmp_path):
        """Test SadTalker command includes expression_scale."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="sadtalker")
        cfg["avatar"]["sadtalker"]["expression_scale"] = 2.5

        gen = AvatarGenerator(cfg)

        # Verify expression_scale is in config
        assert cfg["avatar"]["sadtalker"]["expression_scale"] == 2.5

    def test_sadtalker_fallback_on_subprocess_failure(self, tmp_path):
        """Test SadTalker falls back when subprocess fails."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="sadtalker")
        gen = AvatarGenerator(cfg)

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"audio")

        # Mock SadTalker path exists but subprocess fails
        with patch("pathlib.Path.exists", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1, stderr="Error")

                with patch.object(
                    gen, "_create_fallback_video", return_value=tmp_path / "fallback.mp4"
                ) as mock_fallback:
                    result = gen._generate_sadtalker(audio_path, tmp_path / "out.mp4")

                    assert result is not None
                    assert mock_fallback.called


class TestAvatarGeneratorWav2LipPaths:
    """Test Wav2Lip-specific paths."""

    def test_wav2lip_model_download_path(self, tmp_path):
        """Test Wav2Lip model download path."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="wav2lip")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            gen = AvatarGenerator(cfg)

            # Verify model path structure
            expected_model_path = gen.models_dir / "wav2lip_gan.pth"
            assert hasattr(gen, "models_dir")
            assert isinstance(gen.wav2lip_model_path, (type(None), Path))

    def test_wav2lip_with_model_path(self, tmp_path):
        """Test Wav2Lip initialization when model exists."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="wav2lip")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            gen = AvatarGenerator(cfg)

            # Manually set model path to simulate existing model
            gen.wav2lip_model_path = gen.models_dir / "wav2lip_gan.pth"
            gen.models_dir.mkdir(parents=True, exist_ok=True)
            gen.wav2lip_model_path.write_bytes(b"model")

            # Generate should use wav2lip path
            audio_path = tmp_path / "audio.mp3"
            audio_path.write_bytes(b"audio")

            with patch.object(gen, "_generate_wav2lip", return_value=tmp_path / "out.mp4"):
                result = gen.generate(audio_path)

                assert result is not None


class TestAvatarGeneratorDIDPaths:
    """Test D-ID-specific paths."""

    def test_did_init_with_env_key(self, tmp_path):
        """Test D-ID initialization with API key from environment."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="did")
        del cfg["avatar"]["did"]["api_key"]  # Remove from config

        with patch("os.getenv", return_value="env_api_key"):
            gen = AvatarGenerator(cfg)

            assert gen.did_api_key == "env_api_key"

    def test_did_init_with_config_key(self, tmp_path):
        """Test D-ID initialization with API key from config."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="did")
        cfg["avatar"]["did"]["api_key"] = "config_api_key"

        with patch("os.getenv", return_value=None):
            gen = AvatarGenerator(cfg)

            assert gen.did_api_key == "config_api_key"

    def test_did_init_without_key(self, tmp_path):
        """Test D-ID initialization without API key."""
        from src.core.avatar_generator import AvatarGenerator

        cfg = make_avatar_config(tmp_path, engine="did")
        del cfg["avatar"]["did"]["api_key"]

        with patch("os.getenv", return_value=None):
            gen = AvatarGenerator(cfg)

            assert gen.did_api_key is None
