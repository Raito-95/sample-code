import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from apps import system_resource_monitor as srm


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


def test_format_gpu_name_strips_known_vendor_prefix():
    assert srm.SystemMonitor._format_gpu_name("NVIDIA GeForce RTX 4060") == "RTX 4060"
    assert srm.SystemMonitor._format_gpu_name("AMD Radeon RX 7800 XT") == "RX 7800 XT"


def test_update_cpu_shows_usage_only(monkeypatch, qapp):
    monkeypatch.setattr(srm.SystemMonitor, "_init_timers", lambda self: None)
    monkeypatch.setattr(srm.SystemMonitor, "_init_gpu", lambda self: None)
    monkeypatch.setattr(srm.SystemMonitor, "_discover_disk_mounts", lambda self: ["/disk1"])
    monkeypatch.setattr(srm.QTimer, "singleShot", staticmethod(lambda *_args, **_kwargs: None))
    monkeypatch.setattr(srm.psutil, "cpu_percent", lambda: 37.0)

    monitor = srm.SystemMonitor()
    monitor._update_cpu()

    assert monitor.cpu.label.text() == "CPU: 37%"


def test_update_disk_updates_disk_card(monkeypatch, qapp):
    monkeypatch.setattr(srm.SystemMonitor, "_init_timers", lambda self: None)
    monkeypatch.setattr(srm.SystemMonitor, "_init_gpu", lambda self: None)
    monkeypatch.setattr(srm.QTimer, "singleShot", staticmethod(lambda *_args, **_kwargs: None))
    monkeypatch.setattr(srm.SystemMonitor, "_discover_disk_mounts", lambda self: ["/disk1", "/disk2"])
    monkeypatch.setattr(
        srm.psutil,
        "disk_usage",
        lambda path: SimpleNamespace(
            percent=61.0 if path == "/disk1" else 42.0,
            used=200 * 1024**3 if path == "/disk1" else 100 * 1024**3,
            total=500 * 1024**3 if path == "/disk1" else 300 * 1024**3,
        ),
    )

    monitor = srm.SystemMonitor()
    monitor._update_disk()

    assert len(monitor.disk_rows) == 2
    first = monitor.disk_rows[0][1]
    second = monitor.disk_rows[1][1]
    assert "Disk" in first.label.text()
    assert "61%" in first.label.text()
    assert "42%" in second.label.text()


def test_tray_menu_has_no_trend_toggle(monkeypatch, qapp):
    monkeypatch.setattr(srm.SystemMonitor, "_init_timers", lambda self: None)
    monkeypatch.setattr(srm.SystemMonitor, "_init_gpu", lambda self: None)
    monkeypatch.setattr(srm.SystemMonitor, "_discover_disk_mounts", lambda self: ["/disk1", "/disk2"])
    monkeypatch.setattr(srm.QTimer, "singleShot", staticmethod(lambda *_args, **_kwargs: None))

    monitor = srm.SystemMonitor()
    assert not hasattr(monitor, "action_trend")
