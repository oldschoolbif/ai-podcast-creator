"""
Comprehensive Unit Tests for Avatar Generator
Tests for src/core/avatar_generator.py - Aiming for 100% coverage
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.avatar_generator import AvatarGenerator

# Check if torch is available
try:
    import torch

    TORCH_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    TORCH_AVAILABLE = False

# Check if gfpgan is available
try:
    import gfpgan

    GFPGAN_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    GFPGAN_AVAILABLE = False

skip_if_no_torch = pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not installed")

skip_if_no_gfpgan = pytest.mark.skipif(not GFPGAN_AVAILABLE, reason="gfpgan not installed")


class TestAvatarGeneratorInit:
    """Test AvatarGenerator initialization."""

    def test_init_with_sadtalker(self, test_config):
        """Test initialization with SadTalker engine."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": "checkpoints", "enhancer": "gfpgan"}

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = AvatarGenerator(test_config)
            assert generator.engine_type == "sadtalker"

    def test_init_with_wav2lip(self, test_config):
        """Test initialization with Wav2Lip engine."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["avatar"]["wav2lip"] = {"checkpoint_path": "checkpoints/wav2lip.pth"}

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            generator = AvatarGenerator(test_config)
            assert generator.engine_type == "wav2lip"

    def test_init_with_did(self, test_config):
        """Test initialization with D-ID engine."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "test_key"}

        generator = AvatarGenerator(test_config)
        assert generator.engine_type == "did"


@skip_if_no_torch
class TestAvatarGeneratorSadTalker:
    """Test SadTalker generation."""

    @pytest.mark.gpu
    def test_generate_sadtalker_gpu(self, test_config, temp_dir, skip_if_no_gpu):
        """Test SadTalker generation with GPU."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {
            "checkpoint_dir": str(temp_dir),
            "enhancer": "gfpgan",
            "preprocess": "full",
            "still_mode": False,
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)

        image_path = temp_dir / "avatar.jpg"
        audio_path = temp_dir / "audio.wav"
        image_path.touch()
        audio_path.touch()

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("torch.load"),
            patch("torch.inference_mode"),
            patch("cv2.VideoWriter"),
        ):

            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.clear_cache = MagicMock()

            generator = AvatarGenerator(test_config)
            # generate() only takes audio_path, not image_path
            result = generator.generate(audio_path)

            assert result is not None

    def test_generate_sadtalker_cpu(self, test_config, temp_dir):
        """Test SadTalker generation with CPU."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": str(temp_dir)}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        image_path = temp_dir / "avatar.jpg"
        audio_path = temp_dir / "audio.wav"
        image_path.touch()
        audio_path.touch()

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("torch.load"),
            patch("torch.inference_mode"),
            patch("cv2.VideoWriter"),
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = AvatarGenerator(test_config)
            # _generate_sadtalker() takes only audio_path and output_path
            result = generator._generate_sadtalker(audio_path, temp_dir / "output.mp4")

            assert result is not None

    @skip_if_no_gfpgan
    def test_sadtalker_with_enhancer(self, test_config, temp_dir):
        """Test SadTalker with face enhancer."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": str(temp_dir), "enhancer": "gfpgan"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        image_path = temp_dir / "avatar.jpg"
        audio_path = temp_dir / "audio.wav"
        image_path.touch()
        audio_path.touch()

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("torch.load"),
            patch("torch.inference_mode"),
            patch("cv2.VideoWriter"),
            patch("gfpgan.GFPGANer"),
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = AvatarGenerator(test_config)
            # _generate_sadtalker() takes only audio_path and output_path
            result = generator._generate_sadtalker(audio_path, temp_dir / "output.mp4")

            assert result is not None


@skip_if_no_torch
class TestAvatarGeneratorWav2Lip:
    """Test Wav2Lip generation."""

    @pytest.mark.gpu
    def test_generate_wav2lip_gpu(self, test_config, temp_dir, skip_if_no_gpu):
        """Test Wav2Lip generation with GPU."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["avatar"]["wav2lip"] = {
            "checkpoint_path": str(temp_dir / "checkpoint.pth"),
            "face_det_batch_size": 16,
            "wav2lip_batch_size": 128,
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)

        video_path = temp_dir / "video.mp4"
        audio_path = temp_dir / "audio.wav"
        video_path.touch()
        audio_path.touch()

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("torch.load"),
            patch("torch.inference_mode"),
            patch("cv2.VideoCapture") as mock_cap,
            patch("cv2.VideoWriter"),
        ):

            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.clear_cache = MagicMock()

            mock_capture = MagicMock()
            mock_cap.return_value = mock_capture
            mock_capture.read.return_value = (False, None)  # End of video

            generator = AvatarGenerator(test_config)
            # _generate_wav2lip() takes only audio_path and output_path
            result = generator._generate_wav2lip(audio_path, temp_dir / "output.mp4")

            assert result is not None

    def test_generate_wav2lip_cpu(self, test_config, temp_dir):
        """Test Wav2Lip generation with CPU."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["avatar"]["wav2lip"] = {"checkpoint_path": str(temp_dir / "checkpoint.pth")}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        video_path = temp_dir / "video.mp4"
        audio_path = temp_dir / "audio.wav"
        video_path.touch()
        audio_path.touch()

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("torch.load"),
            patch("torch.inference_mode"),
            patch("cv2.VideoCapture") as mock_cap,
            patch("cv2.VideoWriter"),
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            mock_capture = MagicMock()
            mock_cap.return_value = mock_capture
            mock_capture.read.return_value = (False, None)

            generator = AvatarGenerator(test_config)
            # _generate_wav2lip() takes only audio_path and output_path
            result = generator._generate_wav2lip(audio_path, temp_dir / "output.mp4")

            assert result is not None


class TestAvatarGeneratorDID:
    """Test D-ID API generation."""

    @pytest.mark.network
    def test_generate_did(self, test_config, temp_dir):
        """Test D-ID generation."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {
            "api_key": "test_key",
            "presenter_id": "test_presenter",
            "voice_id": "test_voice",
        }
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("requests.post") as mock_post,
            patch("requests.get") as mock_get,
            patch("builtins.open", create=True),
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            # Mock create talk
            mock_create_response = MagicMock()
            mock_create_response.status_code = 201
            mock_create_response.json.return_value = {"id": "talk_123"}
            mock_post.return_value = mock_create_response

            # Mock status check
            mock_status_response = MagicMock()
            mock_status_response.status_code = 200
            mock_status_response.json.return_value = {"status": "done", "result_url": "https://example.com/video.mp4"}

            # Mock video download
            mock_video_response = MagicMock()
            mock_video_response.status_code = 200
            mock_video_response.content = b"fake video data"

            mock_get.side_effect = [mock_status_response, mock_video_response]

            generator = AvatarGenerator(test_config)
            image_path = temp_dir / "avatar.jpg"
            audio_path = temp_dir / "audio.wav"
            image_path.write_bytes(b"fake image")
            audio_path.write_bytes(b"fake audio")

            # _generate_did takes only audio_path and output_path
            result = generator._generate_did(audio_path, temp_dir / "output.mp4")

            assert result is not None

    def test_did_with_timeout(self, test_config, temp_dir):
        """Test D-ID with timeout/polling."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "test_key"}
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("requests.post") as mock_post,
            patch("requests.get") as mock_get,
            patch("time.sleep"),
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            # Mock successful creation
            mock_create_response = MagicMock()
            mock_create_response.status_code = 201
            mock_create_response.json.return_value = {"id": "talk_123"}
            mock_post.return_value = mock_create_response

            # Mock status checks - always pending (will timeout)
            mock_status_response = MagicMock()
            mock_status_response.status_code = 200
            mock_status_response.json.return_value = {"status": "pending"}
            mock_get.return_value = mock_status_response

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            audio_path.write_bytes(b"fake audio")

            # Should fall back after timeout
            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = temp_dir / "fallback.mp4"
                result = generator._generate_did(audio_path, temp_dir / "output.mp4")
                # Should eventually call fallback after max attempts
                # Note: The function will timeout and call fallback
                mock_fallback.assert_called_once()


class TestAvatarGeneratorCaching:
    """Test caching functionality - output directory management."""

    def test_output_directory_creation(self, test_config, temp_dir):
        """Test that output directory is created correctly."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": str(temp_dir)}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = AvatarGenerator(test_config)

            # Check output directory was created
            assert generator.output_dir.exists()
            assert generator.output_dir.is_dir()

    def test_models_directory_creation(self, test_config, temp_dir):
        """Test that models directory is created."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = AvatarGenerator(test_config)

            # Check models directory was created
            assert generator.models_dir.exists()
            assert generator.models_dir.is_dir()


class TestAvatarGeneratorFallback:
    """Test fallback video generation."""

    def test_create_fallback_video(self, test_config, temp_dir):
        """Test fallback video creation with static image."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        audio_path = temp_dir / "audio.wav"
        output_path = temp_dir / "output.mp4"

        # Create fake image
        image_path = temp_dir / "avatar.jpg"
        image_path.touch()
        audio_path.touch()

        # Mock moviepy classes before import
        mock_audio = MagicMock()
        mock_audio.duration = 5.0

        mock_video = MagicMock()
        mock_video.set_audio.return_value = mock_video
        mock_video.write_videofile = MagicMock()

        mock_moviepy = MagicMock()
        mock_moviepy.editor.ImageClip.return_value = mock_video
        mock_moviepy.editor.AudioFileClip.return_value = mock_audio

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}),
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = AvatarGenerator(test_config)
            result = generator._create_fallback_video(audio_path, output_path)

            assert result is not None

    def test_fallback_without_source_image(self, test_config, temp_dir):
        """Test fallback video creation when source image is missing."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["avatar"]["source_image"] = str(temp_dir / "nonexistent.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        audio_path = temp_dir / "audio.wav"
        output_path = temp_dir / "output.mp4"
        audio_path.touch()

        # Mock moviepy classes before import
        mock_audio = MagicMock()
        mock_audio.duration = 3.0

        mock_video = MagicMock()
        mock_video.set_audio.return_value = mock_video
        mock_video.write_videofile = MagicMock()

        mock_moviepy = MagicMock()
        mock_moviepy.editor.ImageClip.return_value = mock_video
        mock_moviepy.editor.AudioFileClip.return_value = mock_audio

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}),
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = AvatarGenerator(test_config)
            result = generator._create_fallback_video(audio_path, output_path)

            assert result is not None


class TestAvatarGeneratorErrorHandling:
    """Test error handling."""

    def test_generate_with_missing_source_image(self, test_config, temp_dir):
        """Test generation when configured source image is missing."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": str(temp_dir)}
        test_config["avatar"]["source_image"] = str(temp_dir / "nonexistent.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = AvatarGenerator(test_config)

            # Source image path should be set but file doesn't exist
            assert not generator.source_image.exists()

    def test_generate_with_missing_audio(self, test_config, temp_dir):
        """Test generation with missing audio file."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": str(temp_dir)}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu, patch("subprocess.run") as mock_run:

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            # Mock subprocess to simulate failure
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Audio file not found"

            generator = AvatarGenerator(test_config)

            missing_audio = temp_dir / "nonexistent.wav"

            # Should attempt to create fallback when generation fails
            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = temp_dir / "fallback.mp4"
                result = generator.generate(missing_audio)
                mock_fallback.assert_called_once()

    def test_did_with_invalid_api_key(self, test_config, temp_dir):
        """Test D-ID with invalid API key falls back to static video."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "invalid_key"}
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("requests.post") as mock_post, patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response

            generator = AvatarGenerator(test_config)

            audio_path = temp_dir / "audio.wav"
            audio_path.write_bytes(b"fake audio")

            # Should fall back to static video on API failure
            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = temp_dir / "fallback.mp4"
                result = generator._generate_did(audio_path, temp_dir / "output.mp4")
                mock_fallback.assert_called_once()


@pytest.mark.parametrize("engine", ["sadtalker", "wav2lip"])
def test_multiple_engines(test_config, temp_dir, engine):
    """Test initialization with different engines."""
    test_config["avatar"]["engine"] = engine
    test_config["avatar"][engine] = {
        "checkpoint_dir": str(temp_dir) if engine == "sadtalker" else None,
        "checkpoint_path": str(temp_dir / "model.pth") if engine == "wav2lip" else None,
    }

    with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
        mock_gpu.return_value.gpu_available = False

        generator = AvatarGenerator(test_config)
        assert generator.engine_type == engine
