"""
Tests to cover missing lines in tts_engine.py for Codecov
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.tts_engine import TTSEngine, _ensure_project_root_on_path


class TestTTSEngineCoverageGaps:
    """Test uncovered lines in tts_engine.py"""

    def test_ensure_project_root_path_removal(self):
        """Test _ensure_project_root_on_path when PROJECT_ROOT is in sys.path but not at front."""
        # Save original sys.path
        original_path = sys.path.copy()
        
        try:
            # Import to get PROJECT_ROOT
            from src.core.tts_engine import PROJECT_ROOT
            
            # Remove PROJECT_ROOT if it's at front
            if sys.path and sys.path[0] == PROJECT_ROOT:
                sys.path.pop(0)
            
            # Add PROJECT_ROOT to middle of path if not already there
            if PROJECT_ROOT not in sys.path:
                sys.path.insert(2, PROJECT_ROOT)
            
            # Call the function - it should move PROJECT_ROOT to front
            _ensure_project_root_on_path()
            
            # Verify PROJECT_ROOT is now at front
            assert sys.path[0] == PROJECT_ROOT
        finally:
            # Restore original path
            sys.path[:] = original_path

    def test_init_piper_engine(self, test_config, temp_dir):
        """Test initialization with piper engine."""
        test_config["tts"] = {"engine": "piper"}
        test_config["storage"]["cache_dir"] = str(temp_dir)
        
        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"
        
        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu):
            engine = TTSEngine(test_config)
            assert engine.engine_type == "piper"

    def test_generate_piper(self, test_config, temp_dir):
        """Test piper TTS generation (creates empty file as placeholder)."""
        test_config["tts"] = {"engine": "piper"}
        test_config["storage"]["cache_dir"] = str(temp_dir)
        
        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False
        mock_gpu.get_device.return_value = "cpu"
        
        with patch("src.core.tts_engine.get_gpu_manager", return_value=mock_gpu):
            engine = TTSEngine(test_config)
            
            # Generate should create an empty file (uses cache, so check cache dir)
            result = engine.generate("test text for piper")
            
            assert result.exists()
            # File should be empty (placeholder implementation)
            assert result.stat().st_size == 0

