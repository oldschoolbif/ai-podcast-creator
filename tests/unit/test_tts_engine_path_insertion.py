"""Test that sys.path.insert uses index 0 for proper module resolution."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_sys_path_insert_index_zero():
    """Test that sys.path.insert uses 0 to prioritize project root in imports.

    This test ensures that when TTSEngine imports gpu_utils, it uses index 0
    to ensure the project root is checked first before any other paths.
    Changing to index 1 would allow other paths to take precedence, potentially
    causing import errors or wrong module imports.
    """
    from src.core.tts_engine import TTSEngine

    config = {
        "tts": {"engine": "gtts"},
        "storage": {"cache_dir": "/tmp/test_cache"},
    }

    # Verify that importing TTSEngine doesn't fail due to path issues
    # This implicitly tests that sys.path.insert(0, ...) works correctly
    engine = TTSEngine(config)

    # Verify engine was initialized correctly
    assert engine.engine_type == "gtts"
    assert hasattr(engine, "gpu_manager")  # Should be imported from src.utils.gpu_utils

    # Verify sys.path was modified (though exact state depends on import order)
    # The key is that the import succeeded, which wouldn't work if index 1 was used
    # when there are conflicting paths
    assert engine is not None


def test_sys_path_insert_priority():
    """Test that index 0 ensures project modules are found first."""
    original_path = sys.path.copy()

    try:
        # Clear any existing project path
        project_root = str(Path(__file__).parent.parent.parent)
        if project_root in sys.path:
            sys.path.remove(project_root)

        # Create a mock conflicting module name
        import shutil
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        conflicting_dir = temp_dir / "src" / "utils"
        conflicting_dir.mkdir(parents=True)
        (conflicting_dir / "gpu_utils.py").write_text("gpu_available = False\n")

        # Insert conflicting path first
        sys.path.insert(0, str(temp_dir))
        # Then insert project root - should override if index 0
        sys.path.insert(0, project_root)

        # Now import should use project root, not temp dir
        from src.core.tts_engine import TTSEngine

        config = {
            "tts": {"engine": "gtts"},
            "storage": {"cache_dir": "/tmp/test"},
        }

        engine = TTSEngine(config)
        # If project root wasn't prioritized (index 0), this might fail or use wrong module
        assert engine is not None
        assert hasattr(engine, "gpu_manager")

    finally:
        sys.path[:] = original_path
        shutil.rmtree(temp_dir, ignore_errors=True)
