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
        """Test D-ID with invalid API key falls back to static video (lines 378-380)."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "invalid_key"}
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("requests.post") as mock_post, patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            mock_response = MagicMock()
            mock_response.status_code = 400  # Not 201
            mock_response.text = "Bad Request"
            mock_post.return_value = mock_response

            generator = AvatarGenerator(test_config)
            source_image = temp_dir / "avatar.jpg"
            source_image.write_bytes(b"fake image")

            audio_path = temp_dir / "audio.wav"
            audio_path.write_bytes(b"fake audio")

            # Should fall back to static video on API failure
            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = temp_dir / "fallback.mp4"
                result = generator._generate_did(audio_path, temp_dir / "output.mp4")
                mock_fallback.assert_called_once()

    @patch("requests.get")
    @patch("requests.post")
    @patch("time.sleep")  # Speed up test by mocking sleep
    def test_did_successful_generation(self, mock_sleep, mock_post, mock_get, test_config, temp_dir):
        """Test successful D-ID generation with polling (lines 359-423)."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "test_api_key"}
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        # Create source image
        source_image = temp_dir / "avatar.jpg"
        source_image.write_bytes(b"fake image data")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            # Mock initial POST request (create talk)
            mock_post_response = MagicMock()
            mock_post_response.status_code = 201
            mock_post_response.json.return_value = {"id": "test_talk_id"}
            mock_post.return_value = mock_post_response

            # Mock GET requests (polling)
            mock_get_response1 = MagicMock()
            mock_get_response1.status_code = 200
            mock_get_response1.json.return_value = {"status": "processing"}

            mock_get_response2 = MagicMock()
            mock_get_response2.status_code = 200
            mock_get_response2.json.return_value = {
                "status": "done",
                "result_url": "https://example.com/video.mp4"
            }

            # Mock video download
            mock_video_response = MagicMock()
            mock_video_response.status_code = 200
            mock_video_response.content = b"fake video content"

            mock_get.side_effect = [mock_get_response1, mock_get_response2, mock_video_response]

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            output_path = temp_dir / "output.mp4"
            audio_path.write_bytes(b"fake audio data")

            result = generator._generate_did(audio_path, output_path)

            # Verify API calls
            assert mock_post.called
            assert mock_get.call_count >= 2  # Polling + video download
            assert result == output_path
            assert output_path.exists()

    @patch("requests.get")
    @patch("requests.post")
    @patch("time.sleep")
    def test_did_no_talk_id(self, mock_sleep, mock_post, mock_get, test_config, temp_dir):
        """Test D-ID when no talk ID is received (lines 385-387)."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "test_key"}
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        source_image = temp_dir / "avatar.jpg"
        source_image.write_bytes(b"fake image")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            # Mock POST with no ID
            mock_post_response = MagicMock()
            mock_post_response.status_code = 201
            mock_post_response.json.return_value = {}  # No ID
            mock_post.return_value = mock_post_response

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            audio_path.write_bytes(b"fake audio")

            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = temp_dir / "fallback.mp4"
                result = generator._generate_did(audio_path, temp_dir / "output.mp4")
                mock_fallback.assert_called_once()

    @patch("requests.get")
    @patch("requests.post")
    @patch("time.sleep")
    def test_did_status_check_fails(self, mock_sleep, mock_post, mock_get, test_config, temp_dir):
        """Test D-ID when status check fails (lines 403-405)."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "test_key"}
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        source_image = temp_dir / "avatar.jpg"
        source_image.write_bytes(b"fake image")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            # Mock POST success
            mock_post_response = MagicMock()
            mock_post_response.status_code = 201
            mock_post_response.json.return_value = {"id": "test_id"}
            mock_post.return_value = mock_post_response

            # Mock GET failure
            mock_get_response = MagicMock()
            mock_get_response.status_code = 500
            mock_get.return_value = mock_get_response

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            audio_path.write_bytes(b"fake audio")

            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = temp_dir / "fallback.mp4"
                result = generator._generate_did(audio_path, temp_dir / "output.mp4")
                # Should timeout after max attempts
                mock_fallback.assert_called_once()

    @patch("requests.get")
    @patch("requests.post")
    @patch("time.sleep")
    def test_did_status_error(self, mock_sleep, mock_post, mock_get, test_config, temp_dir):
        """Test D-ID when status is error/failed (lines 431-434)."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "test_key"}
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        source_image = temp_dir / "avatar.jpg"
        source_image.write_bytes(b"fake image")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            # Mock POST success
            mock_post_response = MagicMock()
            mock_post_response.status_code = 201
            mock_post_response.json.return_value = {"id": "test_id"}
            mock_post.return_value = mock_post_response

            # Mock GET with error status
            mock_get_response = MagicMock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = {
                "status": "error",
                "error": {"message": "Generation failed"}
            }
            mock_get.return_value = mock_get_response

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            audio_path.write_bytes(b"fake audio")

            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = temp_dir / "fallback.mp4"
                result = generator._generate_did(audio_path, temp_dir / "output.mp4")
                mock_fallback.assert_called_once()

    @patch("requests.get")
    @patch("requests.post")
    @patch("time.sleep")
    def test_did_no_result_url(self, mock_sleep, mock_post, mock_get, test_config, temp_dir):
        """Test D-ID when done but no result URL (lines 427-429)."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "test_key"}
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        source_image = temp_dir / "avatar.jpg"
        source_image.write_bytes(b"fake image")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            # Mock POST success
            mock_post_response = MagicMock()
            mock_post_response.status_code = 201
            mock_post_response.json.return_value = {"id": "test_id"}
            mock_post.return_value = mock_post_response

            # Mock GET with done but no URL
            mock_get_response = MagicMock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = {"status": "done"}  # No result_url
            mock_get.return_value = mock_get_response

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            audio_path.write_bytes(b"fake audio")

            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = temp_dir / "fallback.mp4"
                result = generator._generate_did(audio_path, temp_dir / "output.mp4")
                mock_fallback.assert_called_once()

    @patch("requests.get")
    @patch("requests.post")
    @patch("time.sleep")
    def test_did_video_download_fails(self, mock_sleep, mock_post, mock_get, test_config, temp_dir):
        """Test D-ID when video download fails (lines 424-426)."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "test_key"}
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        source_image = temp_dir / "avatar.jpg"
        source_image.write_bytes(b"fake image")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            # Mock POST success
            mock_post_response = MagicMock()
            mock_post_response.status_code = 201
            mock_post_response.json.return_value = {"id": "test_id"}
            mock_post.return_value = mock_post_response

            # Mock GET with done status and URL
            mock_get_response1 = MagicMock()
            mock_get_response1.status_code = 200
            mock_get_response1.json.return_value = {
                "status": "done",
                "result_url": "https://example.com/video.mp4"
            }

            # Mock video download failure
            mock_get_response2 = MagicMock()
            mock_get_response2.status_code = 404

            mock_get.side_effect = [mock_get_response1, mock_get_response2]

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            audio_path.write_bytes(b"fake audio")

            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = temp_dir / "fallback.mp4"
                result = generator._generate_did(audio_path, temp_dir / "output.mp4")
                mock_fallback.assert_called_once()

    @patch("requests.post")
    def test_did_exception_handling(self, mock_post, test_config, temp_dir):
        """Test D-ID exception handling (lines 440-443)."""
        test_config["avatar"]["engine"] = "did"
        test_config["avatar"]["did"] = {"api_key": "test_key"}
        test_config["avatar"]["source_image"] = str(temp_dir / "avatar.jpg")
        test_config["storage"]["cache_dir"] = str(temp_dir)

        source_image = temp_dir / "avatar.jpg"
        source_image.write_bytes(b"fake image")

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            # Mock exception during POST
            mock_post.side_effect = Exception("Network error")

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            audio_path.write_bytes(b"fake audio")

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


class TestAvatarGeneratorEdgeCases:
    """Test edge cases and error handling paths."""

    def test_init_sadtalker_import_error(self, test_config, temp_dir):
        """Test SadTalker initialization with ImportError (lines 96-97)."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": str(temp_dir)}

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("builtins.__import__", side_effect=ImportError("torch not found")),
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = AvatarGenerator(test_config)
            assert generator.engine_type == "sadtalker"

    def test_init_wav2lip_model_not_exists(self, test_config, temp_dir):
        """Test Wav2Lip initialization when model doesn't exist (line 107)."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["avatar"]["wav2lip"] = {}

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("pathlib.Path.exists", return_value=False),
            patch("src.core.avatar_generator.AvatarGenerator._download_wav2lip_model") as mock_download,
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = AvatarGenerator(test_config)
            # Should handle missing model
            assert generator.engine_type == "wav2lip"

    def test_init_wav2lip_model_download_fails(self, test_config, temp_dir):
        """Test Wav2Lip when model download fails (lines 116-122)."""
        test_config["avatar"]["engine"] = "wav2lip"

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("pathlib.Path.exists", return_value=False),
            patch("src.core.avatar_generator.AvatarGenerator._download_wav2lip_model"),
        ):
            mock_gpu.return_value.gpu_available = False

            generator = AvatarGenerator(test_config)
            # Should handle missing model gracefully
            assert generator.engine_type == "wav2lip"

    def test_init_wav2lip_import_error(self, test_config, temp_dir):
        """Test Wav2Lip initialization with ImportError (lines 119-122)."""
        test_config["avatar"]["engine"] = "wav2lip"

        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("builtins.__import__", side_effect=ImportError("torch not found")),
        ):
            mock_gpu.return_value.gpu_available = False

            generator = AvatarGenerator(test_config)
            assert generator.engine_type == "wav2lip"
            assert generator.wav2lip_model_path is None

    @patch("subprocess.run")
    @patch("src.core.avatar_generator.Path.exists")
    @patch("shutil.copy")
    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.unlink")
    @patch("pathlib.Path.rmdir")
    def test_generate_sadtalker_no_result_files(self, mock_rmdir, mock_unlink, mock_glob, mock_copy, mock_exists, mock_run, test_config, temp_dir):
        """Test SadTalker generation when no result files found (lines 272-275)."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": str(temp_dir)}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.device_id = 0
            mock_gpu.return_value.get_device.return_value = "cuda"

            # Mock subprocess success but no files
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
            mock_exists.return_value = True
            mock_glob.return_value = []  # No result files

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            output_path = temp_dir / "output.mp4"
            audio_path.write_bytes(b"fake audio")

            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = output_path
                result = generator._generate_sadtalker(audio_path, output_path)
                # Should fall back when no files found
                mock_fallback.assert_called_once()

    @patch("subprocess.run")
    @patch("src.core.avatar_generator.Path.exists")
    @patch("shutil.copy")
    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.unlink")
    @patch("pathlib.Path.rmdir")
    def test_generate_sadtalker_with_result_files(self, mock_rmdir, mock_unlink, mock_glob, mock_copy, mock_exists, mock_run, test_config, temp_dir):
        """Test SadTalker generation with result files (lines 259-271)."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": str(temp_dir)}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.device_id = 0
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.clear_cache = MagicMock()

            # Mock successful generation with result file
            result_file = temp_dir / "result.mp4"
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
            mock_exists.return_value = True
            mock_glob.return_value = [result_file]  # Has result file

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            output_path = temp_dir / "output.mp4"
            audio_path.write_bytes(b"fake audio")

            result = generator._generate_sadtalker(audio_path, output_path)

            # Should copy result file
            assert mock_copy.called
            # Should cleanup
            assert mock_unlink.called
            assert mock_rmdir.called
            # Should clear GPU cache
            mock_gpu.return_value.clear_cache.assert_called()

    @patch("subprocess.run")
    def test_generate_wav2lip_error(self, mock_run, test_config, temp_dir):
        """Test Wav2Lip generation with subprocess error (lines 329-331)."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            # Mock subprocess failure
            mock_run.return_value = MagicMock(returncode=1, stderr="Error occurred")

            generator = AvatarGenerator(test_config)
            generator.wav2lip_model_path = temp_dir / "model.pth"

            audio_path = temp_dir / "audio.wav"
            output_path = temp_dir / "output.mp4"
            audio_path.write_bytes(b"fake audio")

            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = output_path
                result = generator._generate_wav2lip(audio_path, output_path)
                # Should fall back on error
                mock_fallback.assert_called_once()

    @patch("subprocess.run")
    def test_generate_wav2lip_exception(self, mock_run, test_config, temp_dir):
        """Test Wav2Lip generation with exception (lines 336-338)."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            # Mock exception
            mock_run.side_effect = Exception("Subprocess error")

            generator = AvatarGenerator(test_config)
            generator.wav2lip_model_path = temp_dir / "model.pth"

            audio_path = temp_dir / "audio.wav"
            output_path = temp_dir / "output.mp4"
            audio_path.write_bytes(b"fake audio")

            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = output_path
                result = generator._generate_wav2lip(audio_path, output_path)
                # Should fall back on exception
                mock_fallback.assert_called_once()

    @patch("subprocess.run")
    def test_generate_sadtalker_exception(self, mock_run, test_config, temp_dir):
        """Test SadTalker generation with exception (lines 283-287)."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": str(temp_dir)}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.device_id = 0
            mock_gpu.return_value.get_device.return_value = "cuda"

            # Mock exception during subprocess
            mock_run.side_effect = Exception("Subprocess failed")

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            output_path = temp_dir / "output.mp4"
            audio_path.write_bytes(b"fake audio")

            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = output_path
                result = generator._generate_sadtalker(audio_path, output_path)
                # Should fall back on exception
                mock_fallback.assert_called_once()

    def test_create_wav2lip_inference_script(self, test_config, temp_dir):
        """Test Wav2Lip inference script creation (lines 521-534)."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            generator = AvatarGenerator(test_config)
            script_path = temp_dir / "wav2lip_script.py"

            generator._create_wav2lip_inference_script(script_path)

            assert script_path.exists()
            assert script_path.is_file()
            content = script_path.read_text()
            assert "Wav2Lip" in content

    def test_generate_sadtalker_path_not_exists(self, test_config, temp_dir):
        """Test SadTalker when path doesn't exist (lines 167-169)."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {"checkpoint_dir": str(temp_dir / "nonexistent")}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.device_id = 0
            mock_gpu.return_value.get_device.return_value = "cuda"

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            output_path = temp_dir / "output.mp4"
            audio_path.write_bytes(b"fake audio")

            with patch.object(generator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = output_path
                result = generator._generate_sadtalker(audio_path, output_path)
                # Should fall back when path doesn't exist
                mock_fallback.assert_called_once()

    @patch("subprocess.run")
    def test_generate_sadtalker_with_still_mode(self, mock_run, test_config, temp_dir):
        """Test SadTalker with still_mode enabled (line 222)."""
        test_config["avatar"]["engine"] = "sadtalker"
        test_config["avatar"]["sadtalker"] = {
            "checkpoint_dir": str(temp_dir),
            "still_mode": True
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.device_id = 0
            mock_gpu.return_value.get_device.return_value = "cuda"

            # Mock successful generation
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

            generator = AvatarGenerator(test_config)
            audio_path = temp_dir / "audio.wav"
            output_path = temp_dir / "output.mp4"
            audio_path.write_bytes(b"fake audio")

            # Create temp dir structure
            sadtalker_path = temp_dir / "sadtalker"
            sadtalker_path.mkdir()
            (sadtalker_path / "checkpoints").mkdir()

            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.glob", return_value=[temp_dir / "result.mp4"]):
                    with patch("shutil.copy") as mock_copy:
                        result = generator._generate_sadtalker(audio_path, output_path)
                        
                        # Verify still_mode was passed
                        call_args = mock_run.call_args[0][0]
                        assert "--still" in call_args

    def test_generate_wav2lip_creates_script(self, test_config, temp_dir):
        """Test Wav2Lip creates inference script when needed (line 305)."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            generator = AvatarGenerator(test_config)
            generator.wav2lip_model_path = temp_dir / "model.pth"

            audio_path = temp_dir / "audio.wav"
            output_path = temp_dir / "output.mp4"
            audio_path.write_bytes(b"fake audio")

            # The actual script path used by the code: scripts/wav2lip_inference.py
            # Need to mock Path.exists() for this specific path to return False
            from pathlib import Path as PathClass
            
            original_exists = PathClass.exists
            
            def mock_exists(self):
                # Return False for the wav2lip script path to trigger creation
                if "wav2lip_inference.py" in str(self):
                    return False
                return original_exists(self)

            with patch.object(generator, "_create_wav2lip_inference_script") as mock_create_script:
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    
                    # Mock Path.exists() for the script path check
                    with patch.object(PathClass, "exists", mock_exists):
                        # Mock the result file that would be created
                        result_dir = Path(temp_dir) / "results"
                        result_dir.mkdir(exist_ok=True)
                        result_file = result_dir / "result.mp4"
                        result_file.write_bytes(b"fake video")
                        
                        with patch("pathlib.Path.glob") as mock_glob:
                            mock_glob.return_value = [result_file]
                            with patch("shutil.copy"):
                                generator._generate_wav2lip(audio_path, output_path)
                                # Should create script when it doesn't exist
                                mock_create_script.assert_called()

    @patch("urllib.request.urlretrieve")
    def test_download_wav2lip_model_success(self, mock_urlretrieve, test_config, temp_dir):
        """Test Wav2Lip model download success (lines 462-468)."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            generator = AvatarGenerator(test_config)
            model_path = temp_dir / "wav2lip_gan.pth"

            # Mock successful download
            mock_urlretrieve.return_value = None
            generator._download_wav2lip_model(model_path)

            # Should attempt download
            assert mock_urlretrieve.called

    @patch("urllib.request.urlretrieve")
    def test_download_wav2lip_model_all_urls_fail(self, mock_urlretrieve, test_config, temp_dir):
        """Test Wav2Lip model download when all URLs fail (lines 473-478)."""
        test_config["avatar"]["engine"] = "wav2lip"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            generator = AvatarGenerator(test_config)
            model_path = temp_dir / "wav2lip_gan.pth"

            # Mock all downloads fail
            mock_urlretrieve.side_effect = Exception("Network error")
            generator._download_wav2lip_model(model_path)

            # Should try all URLs (3 attempts)
            assert mock_urlretrieve.call_count == 3

    # Note: _create_fallback_video tests removed due to complex moviepy mocking
    # These methods (lines 480-517) can be tested via integration tests with real moviepy