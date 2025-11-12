import time
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils.file_monitor import FileMonitor


def test_file_monitor_tracks_growth(tmp_path):
    file_path = tmp_path / "growing.bin"
    updates = []

    monitor = FileMonitor(
        file_path,
        update_callback=lambda size, rate, warning: updates.append((size, rate, warning)),
        check_interval=0.01,
    )

    monitor.start()
    # Give monitor loop time to start
    time.sleep(0.02)

    with file_path.open("wb") as f:
        f.write(b"\x00" * (512 * 1024))

    time.sleep(0.03)

    with file_path.open("ab") as f:
        f.write(b"\x00" * (256 * 1024))

    time.sleep(0.05)
    monitor.stop()

    summary = monitor.get_metrics_summary()
    assert summary["final_size_mb"] == pytest.approx(0.75, rel=0.2)
    assert summary["average_growth_rate_mb_per_sec"] >= 0
    assert summary["growth_samples_count"] >= 0
    # At least one callback should have triggered once file existed
    assert any(entry[0] >= 0 for entry in updates)


def test_file_monitor_helpers(tmp_path):
    file_path = tmp_path / "file.bin"
    file_path.write_bytes(b"\x00" * 128)

    monitor = FileMonitor(file_path)
    # Manually tweak internal counters
    monitor.stall_time = monitor.stall_threshold
    assert monitor.is_stalled()


# ============================================================================
# Additional error path tests
# ============================================================================

def test_file_monitor_stop_handles_oserror(tmp_path):
    """Test stop() handles OSError when getting file stats."""
    file_path = tmp_path / "file.bin"
    file_path.write_bytes(b"\x00" * 128)

    monitor = FileMonitor(file_path)
    monitor.start()
    time.sleep(0.02)
    
    # Mock Path.exists() and stat() to raise OSError
    with patch.object(Path, "exists", return_value=True), patch.object(Path, "stat", side_effect=OSError("Permission denied")):
        # Should not raise exception
        monitor.stop()


def test_file_monitor_stop_handles_file_not_found(tmp_path):
    """Test stop() handles FileNotFoundError when file doesn't exist."""
    file_path = tmp_path / "nonexistent.bin"

    monitor = FileMonitor(file_path)
    monitor.start()
    
    # File doesn't exist, should handle gracefully
    monitor.stop()
    
    # Should not raise exception
    assert monitor.final_size_mb is None


def test_file_monitor_get_current_size_handles_oserror(tmp_path):
    """Test get_current_size_mb() handles OSError."""
    file_path = tmp_path / "file.bin"
    file_path.write_bytes(b"\x00" * 128)

    monitor = FileMonitor(file_path)
    
    # Mock Path.exists() and stat() to raise OSError
    with patch.object(Path, "exists", return_value=True), patch.object(Path, "stat", side_effect=OSError("Permission denied")):
        size = monitor.get_current_size_mb()
        
        # Should return 0.0 on error
        assert size == 0.0


def test_file_monitor_get_current_size_handles_file_not_found(tmp_path):
    """Test get_current_size_mb() handles FileNotFoundError."""
    file_path = tmp_path / "nonexistent.bin"

    monitor = FileMonitor(file_path)
    size = monitor.get_current_size_mb()
    
    # Should return 0.0 when file doesn't exist
    assert size == 0.0


def test_file_monitor_loop_handles_oserror(tmp_path):
    """Test _monitor_loop handles OSError gracefully."""
    file_path = tmp_path / "file.bin"
    file_path.write_bytes(b"\x00" * 128)

    monitor = FileMonitor(file_path, check_interval=0.01)
    monitor.start()
    time.sleep(0.02)
    
    # Mock Path.exists() and stat() to raise OSError
    with patch.object(Path, "exists", return_value=True), patch.object(Path, "stat", side_effect=OSError("Permission denied")):
        time.sleep(0.05)
        monitor.stop()
    
    # Should not raise exception, monitoring should continue


def test_file_monitor_loop_handles_file_not_found(tmp_path):
    """Test _monitor_loop handles FileNotFoundError when file is deleted."""
    file_path = tmp_path / "file.bin"
    file_path.write_bytes(b"\x00" * 128)

    monitor = FileMonitor(file_path, check_interval=0.01)
    monitor.start()
    time.sleep(0.02)
    
    # Delete file while monitoring
    file_path.unlink()
    
    time.sleep(0.05)
    monitor.stop()
    
    # Should not raise exception, monitoring should handle deleted file


def test_file_monitor_get_average_growth_rate_no_samples(tmp_path):
    """Test get_average_growth_rate returns 0.0 when no samples."""
    file_path = tmp_path / "file.bin"
    file_path.write_bytes(b"\x00" * 128)

    monitor = FileMonitor(file_path)
    monitor.growth_samples = []  # No samples
    
    assert monitor.get_average_growth_rate() == 0.0


def test_file_monitor_get_file_creation_time_not_created(tmp_path):
    """Test get_file_creation_time_sec returns None when file not created."""
    file_path = tmp_path / "nonexistent.bin"

    monitor = FileMonitor(file_path, check_interval=0.01)
    monitor.start()
    time.sleep(0.05)  # Give it time to check
    monitor.stop()
    
    # File was never created
    assert monitor.get_file_creation_time_sec() is None

