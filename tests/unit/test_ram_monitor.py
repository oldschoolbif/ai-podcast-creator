from types import SimpleNamespace

import pytest

from src.utils.ram_monitor import RAMMonitor


def make_virtual_memory(used_gb, total_gb=16.0):
    used = int(used_gb * 1024**3)
    total = int(total_gb * 1024**3)
    available = total - used
    percent = (used / total) * 100
    return SimpleNamespace(
        total=total,
        used=used,
        available=available,
        percent=percent,
    )


def test_ram_monitor_thresholds(monkeypatch):
    state = {"used": 4.0}

    def fake_virtual_memory():
        return make_virtual_memory(state["used"])

    monkeypatch.setattr("src.utils.ram_monitor.psutil.virtual_memory", fake_virtual_memory)

    monitor = RAMMonitor(max_ram_gb=8.0, warning_threshold_gb=6.0)

    over, message = monitor.check_ram_limit()
    assert (over, message) == (False, "")

    state["used"] = 6.5
    over, message = monitor.check_ram_limit()
    assert over is False
    assert "WARNING" in message

    # Warning should not repeat once issued
    over, message = monitor.check_ram_limit()
    assert (over, message) == (False, "")

    state["used"] = 9.0
    over, message = monitor.check_ram_limit()
    assert over is True
    assert "CRITICAL" in message


def test_ram_monitor_status(monkeypatch):
    monkeypatch.setattr(
        "src.utils.ram_monitor.psutil.virtual_memory",
        lambda: make_virtual_memory(5.0, total_gb=20.0),
    )

    monitor = RAMMonitor(max_ram_gb=10.0, warning_threshold_gb=8.0)
    status = monitor.get_status()

    assert status["used_gb"] == 5.0
    assert status["available_gb"] == 15.0
    assert status["total_gb"] == monitor.total_ram_gb
    assert status["limit_gb"] == 10.0
    assert status["warning_gb"] == 8.0
    assert status["over_limit"] is False
    assert status["near_limit"] is False


def test_ram_monitor_usage_helpers(monkeypatch):
    sample = make_virtual_memory(7.5, total_gb=30.0)
    monkeypatch.setattr("src.utils.ram_monitor.psutil.virtual_memory", lambda: sample)

    monitor = RAMMonitor(max_ram_gb=20.0, warning_threshold_gb=10.0)

    assert monitor.get_ram_usage_gb() == pytest.approx(7.5)
    assert monitor.get_ram_percent() == pytest.approx((7.5 / 30.0) * 100)

