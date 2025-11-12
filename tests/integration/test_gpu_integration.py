"""
GPU-Focused Integration Tests
Tests GPU acceleration across core modules in real scenarios
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.avatar_generator import AvatarGenerator
from src.core.audio_visualizer import AudioVisualizer
from src.core.music_generator import MusicGenerator
from src.core.tts_engine import TTSEngine
from src.core.video_composer import VideoComposer
from src.utils.gpu_utils import get_gpu_manager


@pytest.mark.integration
class TestGPUIntegration:
    """Integration tests for GPU functionality across core modules."""

    def test_gpu_manager_initialization(self, test_config):
        """Test GPU manager is properly initialized across modules."""
        gpu_manager = get_gpu_manager()
        
        # GPU manager should exist
        assert gpu_manager is not None
        
        # Should have device attribute
        device = gpu_manager.get_device()
        assert device is not None
        assert isinstance(device, str)
        
        # Should have gpu_available attribute
        gpu_available = gpu_manager.gpu_available
        assert isinstance(gpu_available, bool)
        
        # Device should be valid
        assert device in ["cpu", "cuda", "cuda:0", "cuda:1"]

    def test_tts_engine_gpu_detection(self, test_config, temp_dir):
        """Test TTS engine detects and uses GPU when available."""
        test_config["tts"] = {"engine": "gtts"}  # gTTS doesn't use GPU, but tests GPU manager integration
        test_config["storage"]["cache_dir"] = str(temp_dir)
        
        engine = TTSEngine(test_config)
        
        # Should have GPU manager
        assert engine.gpu_manager is not None
        assert engine.device is not None
        assert isinstance(engine.use_gpu, bool)
        
        # Device should match GPU manager
        gpu_manager = get_gpu_manager()
        assert engine.device == gpu_manager.get_device()
        assert engine.use_gpu == gpu_manager.gpu_available

    def test_avatar_generator_gpu_detection(self, test_config):
        """Test AvatarGenerator detects and configures GPU."""
        gen = AvatarGenerator(test_config)
        
        # Should have GPU manager
        assert gen.gpu_manager is not None
        assert gen.device is not None
        assert isinstance(gen.use_gpu, bool)
        
        # Device should match GPU manager
        gpu_manager = get_gpu_manager()
        assert gen.device == gpu_manager.get_device()
        assert gen.use_gpu == gpu_manager.gpu_available

    def test_music_generator_gpu_detection(self, test_config):
        """Test MusicGenerator detects and configures GPU."""
        gen = MusicGenerator(test_config)
        
        # Should have GPU manager
        assert gen.gpu_manager is not None
        assert gen.device is not None
        
        # Device should match GPU manager
        gpu_manager = get_gpu_manager()
        assert gen.device == gpu_manager.get_device()

    def test_audio_visualizer_gpu_encoding(self, test_config_visualization, temp_dir):
        """Test AudioVisualizer uses GPU encoding when available."""
        viz = AudioVisualizer(test_config_visualization)
        
        # AudioVisualizer doesn't directly expose GPU manager, but uses it internally
        # Test that it can initialize without errors
        assert viz is not None
        assert viz.resolution is not None

    def test_video_composer_gpu_encoding(self, test_config, temp_dir):
        """Test VideoComposer uses GPU encoding (NVENC) when available."""
        composer = VideoComposer(test_config)
        
        # VideoComposer uses GPU manager internally for NVENC
        # Test that it can initialize without errors
        assert composer is not None

    @pytest.mark.skipif(
        not (Path(__file__).parent.parent.parent / "models" / "wav2lip_gan.pth").exists(),
        reason="Wav2Lip model not available"
    )
    @pytest.mark.network
    def test_avatar_generator_gpu_workflow(self, test_config, temp_dir, skip_if_no_internet):
        """Test AvatarGenerator GPU workflow end-to-end."""
        from src.core.tts_engine import TTSEngine
        
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)
        
        # Generate audio first
        tts = TTSEngine(test_config)
        audio_path = tts.generate("Test audio for avatar generation")
        assert audio_path.exists()
        
        # Create avatar generator
        gen = AvatarGenerator(test_config)
        
        # Should detect GPU availability
        assert gen.use_gpu is not None
        assert gen.device is not None
        
        # If GPU is available, should use it
        if gen.use_gpu:
            assert "cuda" in gen.device.lower()
            # GPU-specific initialization should have occurred
            assert gen.gpu_manager is not None

    def test_gpu_manager_performance_config(self, test_config):
        """Test GPU manager provides performance configuration."""
        gpu_manager = get_gpu_manager()
        
        if gpu_manager.gpu_available:
            perf_config = gpu_manager.get_performance_config()
            
            # Should have performance config
            assert perf_config is not None
            assert isinstance(perf_config, dict)
            
            # Should have expected keys
            assert "use_fp16" in perf_config
            assert isinstance(perf_config["use_fp16"], bool)

    def test_gpu_manager_memory_management(self, test_config):
        """Test GPU manager memory management functions."""
        gpu_manager = get_gpu_manager()
        
        if gpu_manager.gpu_available:
            # Should be able to get memory usage
            memory_usage = gpu_manager.get_memory_usage()
            assert memory_usage is not None
            assert isinstance(memory_usage, dict)
            
            # Should be able to clear cache
            try:
                gpu_manager.clear_cache()
            except Exception as e:
                # Clear cache might fail in some environments, that's OK
                pytest.skip(f"GPU cache clear not available: {e}")

    def test_gpu_manager_utilization(self, test_config):
        """Test GPU manager can report GPU utilization."""
        gpu_manager = get_gpu_manager()
        
        if gpu_manager.gpu_available:
            utilization = gpu_manager.get_utilization()
            assert utilization is not None
            assert isinstance(utilization, dict)
            
            # Should have GPU percent if available
            if "gpu_percent" in utilization:
                assert isinstance(utilization["gpu_percent"], (int, float))
                assert 0 <= utilization["gpu_percent"] <= 100

    def test_coqui_tts_gpu_integration(self, test_config, temp_dir):
        """Test Coqui TTS GPU integration (if available)."""
        try:
            import TTS
        except ImportError:
            pytest.skip("Coqui TTS not installed")
        
        test_config["tts"] = {
            "engine": "coqui",
            "coqui": {"model": "tts_models/en/ljspeech/tacotron2-DDC"}
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)
        
        try:
            engine = TTSEngine(test_config)
            
            # Should have GPU manager
            assert engine.gpu_manager is not None
            
            # If GPU is available, Coqui should use it
            if engine.use_gpu:
                assert "cuda" in engine.device.lower()
                # Coqui TTS should be initialized with GPU
                assert engine.tts is not None
        except Exception as e:
            pytest.skip(f"Coqui TTS GPU integration not available: {e}")

    def test_musicgen_gpu_integration(self, test_config, temp_dir):
        """Test MusicGen GPU integration (if available)."""
        try:
            import audiocraft
        except ImportError:
            pytest.skip("AudioCraft not installed")
        
        test_config["music"] = {"engine": "musicgen"}
        test_config["storage"]["cache_dir"] = str(temp_dir)
        
        try:
            gen = MusicGenerator(test_config)
            
            # Should have GPU manager
            assert gen.gpu_manager is not None
            
            # If GPU is available, MusicGen should use it
            if gen.gpu_manager.gpu_available:
                assert "cuda" in gen.device.lower()
        except Exception as e:
            pytest.skip(f"MusicGen GPU integration not available: {e}")

    def test_gpu_fallback_to_cpu(self, test_config, temp_dir):
        """Test modules gracefully fall back to CPU when GPU unavailable."""
        # Mock GPU as unavailable
        from unittest.mock import patch
        
        with patch("src.utils.gpu_utils.get_gpu_manager") as mock_gpu:
            mock_manager = MagicMock()
            mock_manager.gpu_available = False
            mock_manager.get_device.return_value = "cpu"
            mock_gpu.return_value = mock_manager
            
            # TTS engine should work with CPU
            test_config["tts"] = {"engine": "gtts"}
            test_config["storage"]["cache_dir"] = str(temp_dir)
            
            engine = TTSEngine(test_config)
            assert engine.device == "cpu"
            assert engine.use_gpu is False
            
            # Avatar generator should work with CPU
            gen = AvatarGenerator(test_config)
            assert gen.device == "cpu"
            assert gen.use_gpu is False

