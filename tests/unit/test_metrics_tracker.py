import builtins
import json
import time
from pathlib import Path

import pytest

from src.utils import metrics
from src.utils.metrics import ComponentMetrics, MetricsTracker, get_metrics_tracker


class StubGPU:
    gpu_available = True
    gpu_name = "Stub GPU"
    gpu_memory = 12.0

    def get_memory_usage(self):
        return {"allocated_gb": 1.25}

    def get_utilization(self):
        return {"gpu_percent": 25.0}


@pytest.fixture(autouse=True)
def patch_cpu_ram(monkeypatch, request):
    if request.node.get_closest_marker("no_cpu_patch"):
        # Allow tests to exercise the real implementation
        yield
        return

    sample = {"cpu_percent": 10.0, "ram_used_gb": 4.0, "ram_total_gb": 16.0, "ram_percent": 25.0}
    monkeypatch.setattr(metrics, "_get_cpu_ram_usage", lambda: sample.copy())
    yield


def make_config(tmp_path: Path) -> dict:
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return {"storage": {"cache_dir": str(cache_dir)}}


def test_metrics_tracker_session_and_component(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    monkeypatch.setattr(metrics.MetricsTracker, "_print_summary", lambda self: None, raising=False)
    tracker = MetricsTracker(config)
    tracker.gpu_manager = StubGPU()

    session_id = tracker.start_session("script.txt", output_path="podcast.mp4")
    assert len(session_id) == 8
    assert tracker.current_session.gpu_name == "Stub GPU"

    tracker.set_quality("fast")
    tracker.set_flags(avatar=True, visualization=False, background=True)

    component = tracker.start_component("tts")
    assert isinstance(component, ComponentMetrics)
    assert tracker.current_session.components == [component]

    tracker.gpu_manager._component_gpu_samples = [40.0, 60.0]

    output_file = tmp_path / "tts_output.wav"
    output_file.write_bytes(b"\x00" * 1024)

    class DummyMonitor:
        def __init__(self, path):
            self.file_path = path

        def get_metrics_summary(self):
            return {
                "final_size_mb": 1.0,
                "average_growth_rate_mb_per_sec": 0.5,
                "file_creation_time_sec": 2.0,
                "growth_samples_count": 3,
            }

    tracker.finish_component(component, file_monitor=DummyMonitor(output_file))

    assert component.duration is not None
    assert component.gpu_utilization_avg == pytest.approx(60.0)
    assert component.output_file_path == str(output_file)
    assert component.output_file_size_mb == pytest.approx(1.0)

    tracker.finish_session(output_path="final.mp4")

    metrics_files = list((tmp_path / "cache" / "metrics").glob("*.json"))
    assert metrics_files, "Metrics JSON file not written"
    data = json.loads(metrics_files[0].read_text())
    assert data["quality_preset"] == "fast"
    assert data["used_avatar"] is True
    assert data["used_background"] is True
    assert data["components"][0]["file_creation_time_sec"] == pytest.approx(2.0)


def test_get_metrics_tracker_global(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    monkeypatch.setattr(metrics, "_metrics_tracker", None)

    tracker = get_metrics_tracker(config)
    assert isinstance(tracker, MetricsTracker)

    tracker2 = get_metrics_tracker()
    assert tracker2 is tracker


def test_metrics_tracker_print_summary_formatting(tmp_path, capsys):
    config = make_config(tmp_path)
    tracker = MetricsTracker(config)

    # Build a synthetic session with two components to exercise summary formatting paths.
    session = metrics.GenerationMetrics(
        session_id="session1",
        script_path="script.txt",
        output_path="out.mp4",
    )
    session.total_duration = 42.5
    session.gpu_name = "RTX 9999"
    session.gpu_memory_gb = 24.0
    session.quality_preset = "ultra"

    error_comp = ComponentMetrics(component="avatar", start_time=0.0)
    error_comp.duration = 12.34
    error_comp.error = "face not detected"
    error_comp.gpu_utilization_avg = 75.0  # Triggers 🔥 branch
    error_comp.cpu_usage_avg = 55.0  # Triggers 🔥 branch for CPU
    error_comp.ram_usage_after = {"ram_used_gb": 12.0, "ram_total_gb": 16.0, "ram_percent": 75.0}
    error_comp.output_file_size_mb = 123.45
    error_comp.file_growth_rate_mb_per_sec = 6.7
    error_comp.file_creation_time_sec = 8.9
    error_comp.gpu_memory_before = {"allocated_gb": 1.0}
    error_comp.gpu_memory_after = {"allocated_gb": 2.5}

    ok_comp = ComponentMetrics(component="tts", start_time=0.0)
    ok_comp.duration = 3.21
    ok_comp.gpu_utilization_avg = 15.0  # ⚡ branch
    ok_comp.cpu_usage_avg = 5.0  # 💤 branch
    ok_comp.ram_usage_after = {"ram_used_gb": 4.0, "ram_total_gb": 16.0, "ram_percent": 25.0}

    session.components = [error_comp, ok_comp]
    tracker.current_session = session

    tracker._print_summary()
    output = capsys.readouterr().out
    lines = [line.rstrip() for line in output.strip().splitlines()]

    assert lines[0] == "=" * 60
    assert lines[1] == "📊 GENERATION METRICS"
    assert lines[2] == "=" * 60
    assert lines[3] == "Total Duration: 42.50s"
    assert lines[4] == "GPU: RTX 9999"
    assert lines[5] == "GPU Memory: 24.0 GB"
    assert lines[6] == "Quality: ultra"
    # Blank separator line
    assert lines[7] == ""
    assert lines[8] == "Component Breakdown:"
    assert lines[9].startswith("  ❌ avatar")
    assert "12.34s" in lines[9]
    assert "GPU Memory: +1.50 GB" in lines[10]
    assert "🔥 75.0%" in lines[11]
    assert "🔥 55.0%" in lines[12]
    assert "RAM Usage: 12.0/16.0 GB (75.0%)" in lines[13]
    assert "Output File: 123.45 MB" in lines[14]
    assert "Encoding Rate: 6.70 MB/s" in lines[15]
    assert "File Creation Time: 8.90s" in lines[16]
    assert lines[17].startswith("  ✅ tts")
    assert "3.21s" in lines[17]
    assert "⚡ 15.0%" in lines[18]
    assert "💤 5.0%" in lines[19]
    assert "RAM Usage: 4.0/16.0 GB (25.0%)" in lines[20]
    assert lines[-1] == "=" * 60


@pytest.mark.unit
def test_component_finish_uses_device_samples(monkeypatch):
    comp = ComponentMetrics(
        component="gpu_task",
        start_time=time.time() - 1.0,
        gpu_memory_before={"allocated_gb": 1.0},
        gpu_utilization_before={"gpu_percent": 5.0},
        cpu_usage_before={"cpu_percent": 10.0},
        ram_usage_before={"ram_used_gb": 3.0, "ram_total_gb": 16.0, "ram_percent": 18.75},
    )

    class DeviceStub:
        gpu_available = True

        def __init__(self):
            self.gpu_name = "RTX Stub"
            self.gpu_memory = 24.0
            self._component_gpu_samples = [15.0, 70.0]

        def get_memory_usage(self):
            return {"allocated_gb": 2.6}

        def get_utilization(self):
            return {"gpu_percent": 20.0}

    monkeypatch.setattr(
        metrics,
        "_get_cpu_ram_usage",
        lambda: {"cpu_percent": 50.0, "ram_used_gb": 6.0, "ram_total_gb": 16.0, "ram_percent": 37.5},
    )

    device = DeviceStub()
    comp.finish(device)

    assert comp.duration is not None
    assert comp.gpu_memory_after == {"allocated_gb": 2.6}
    assert comp.gpu_utilization_avg == pytest.approx(70.0)
    assert not hasattr(device, "_component_gpu_samples")
    assert comp.cpu_usage_avg == pytest.approx((10.0 + 50.0) / 2.0)
    assert comp.ram_usage_after["ram_percent"] == pytest.approx(37.5)


@pytest.mark.unit
def test_component_finish_without_device(monkeypatch):
    comp = ComponentMetrics(
        component="cpu_task",
        start_time=time.time() - 0.5,
        cpu_usage_before={"cpu_percent": 12.0},
        ram_usage_before={"ram_used_gb": 2.0, "ram_total_gb": 16.0, "ram_percent": 12.5},
    )

    class DeviceStub:
        gpu_available = False

    monkeypatch.setattr(
        metrics,
        "_get_cpu_ram_usage",
        lambda: {"cpu_percent": 20.0, "ram_used_gb": 5.0, "ram_total_gb": 16.0, "ram_percent": 31.25},
    )

    comp.finish(DeviceStub())

    assert comp.gpu_memory_after == {}
    assert comp.gpu_utilization_avg is None
    assert comp.cpu_usage_avg == pytest.approx(16.0)
    assert comp.ram_usage_after["ram_used_gb"] == pytest.approx(5.0)


@pytest.mark.unit
def test_metrics_summary_omits_small_memory_delta(tmp_path, capsys):
    config = make_config(tmp_path)
    tracker = MetricsTracker(config)

    session = metrics.GenerationMetrics(session_id="session2", script_path="script.txt")
    session.total_duration = 12.0
    session.gpu_name = None
    session.quality_preset = None

    comp = ComponentMetrics(component="video", start_time=0.0)
    comp.duration = 2.5
    comp.gpu_memory_before = {"allocated_gb": 1.0}
    comp.gpu_memory_after = {"allocated_gb": 1.005}  # below 0.01 GB delta threshold
    comp.cpu_usage_avg = 12.0
    comp.gpu_utilization_avg = 8.0
    comp.ram_usage_after = {"ram_used_gb": 3.5, "ram_total_gb": 16.0, "ram_percent": 21.9}

    session.components = [comp]
    tracker.current_session = session

    tracker._print_summary()
    output = capsys.readouterr().out

    assert "GPU: CPU" in output
    assert "GPU Memory:" not in output
    assert "GPU Utilization: 💤 8.0%" in output
    assert "CPU Usage: ⚡ 12.0%" in output


@pytest.mark.unit
@pytest.mark.no_cpu_patch
def test_get_cpu_ram_usage_fallback(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "psutil":
            raise ImportError("psutil missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = metrics._get_cpu_ram_usage()
    assert result == {"cpu_percent": 0.0, "ram_used_gb": 0.0, "ram_total_gb": 0.0, "ram_percent": 0.0}


def test_metrics_tracker_save_metrics_failure(tmp_path, monkeypatch, capsys):
    config = make_config(tmp_path)
    tracker = MetricsTracker(config)
    tracker.start_session("script.txt")
    tracker.current_session.total_duration = 0.5

    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(metrics.json, "dump", boom)
    tracker._save_metrics()
    captured = capsys.readouterr()
    assert "⚠ Could not save metrics" in captured.out
