import sys
from pathlib import Path

import psutil
from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import (
    QAction,
    QColor,
    QGuiApplication,
    QIcon,
    QMouseEvent,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

try:
    from pynvml import (
        NVMLError,
        NVML_TEMPERATURE_GPU,
        nvmlDeviceGetCount,
        nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetMemoryInfo,
        nvmlDeviceGetName,
        nvmlDeviceGetTemperature,
        nvmlDeviceGetUtilizationRates,
        nvmlInit,
        nvmlShutdown,
    )

    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False
    NVMLError = Exception  # type: ignore[assignment]


class MetricRow(QFrame):
    def __init__(
        self,
        parent: QWidget,
        initial_text: str,
        _color: QColor,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("metricRow")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 5, 6, 5)
        layout.setSpacing(0)

        self.label = QLabel(initial_text, self)
        self.label.setObjectName("metricLabel")

        layout.addWidget(self.label)

    def set_text(self, text: str) -> None:
        self.label.setText(text)


class SystemMonitor(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("System Resource Monitor")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._movable = True
        self._drag_origin: QPoint | None = None
        self._gpu_handle = None
        self._nvml_initialized = False
        self._disk_mounts = self._discover_disk_mounts()

        root = QWidget(self)
        root.setObjectName("root")
        self.setCentralWidget(root)

        self._metrics_layout = QHBoxLayout(root)
        self._metrics_layout.setContentsMargins(6, 6, 6, 6)
        self._metrics_layout.setSpacing(4)

        self.cpu = MetricRow(root, "CPU: --%", QColor(255, 173, 110))
        self.mem = MetricRow(root, "Memory: --%", QColor(116, 224, 122))
        self.gpu = MetricRow(root, "GPU: --", QColor(102, 202, 238))
        self.gpu.label.setWordWrap(True)
        self.disk_rows: list[tuple[str, MetricRow]] = []
        for mount in self._disk_mounts:
            row = MetricRow(root, f"Disk {self._short_mount_label(mount)}: --%", QColor(133, 174, 255))
            self.disk_rows.append((mount, row))

        self._metrics_layout.addWidget(self.cpu)
        self._metrics_layout.addWidget(self.mem)
        for _mount, row in self.disk_rows:
            self._metrics_layout.addWidget(row)
        self._metrics_layout.addWidget(self.gpu)
        self._freeze_metric_widths()

        root.setStyleSheet(
            """
            QWidget#root {
                background-color: rgba(15, 20, 29, 230);
                border: 1px solid rgba(255, 255, 255, 42);
                border-radius: 12px;
            }
            QFrame#metricRow {
                background-color: rgba(255, 255, 255, 10);
                border: 1px solid rgba(255, 255, 255, 16);
                border-radius: 8px;
            }
            QLabel#metricLabel {
                color: #eef2ff;
                font-size: 12px;
                font-weight: 600;
            }
            """
        )

        self._init_gpu()
        self._apply_gpu_visibility()
        self._init_timers()
        self._init_tray()
        self.resize(760, 64)
        self._adjust_compact_width()
        QTimer.singleShot(100, self._move_to_bottom_right)

    def _init_tray(self) -> None:
        self.tray = QSystemTrayIcon(self)
        icon = QIcon.fromTheme("utilities-system-monitor")
        if icon.isNull():
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(133, 174, 255))
            icon = QIcon(pixmap)
        self.tray.setIcon(icon)

        self.action_toggle = QAction("Show/Hide", self)
        self.action_pin = QAction("", self)
        self.action_reset = QAction("Move to Bottom Right", self)
        self.action_exit = QAction("Exit", self)

        self.action_toggle.triggered.connect(self.toggle_visibility)
        self.action_pin.triggered.connect(self.toggle_movable)
        self.action_reset.triggered.connect(self._move_to_bottom_right)
        self.action_exit.triggered.connect(self.close)

        self._refresh_action_labels()
        self.tray.setContextMenu(self._create_context_menu())
        self.tray.activated.connect(self._on_tray_clicked)
        self.tray.show()

    def _create_context_menu(self) -> QMenu:
        menu = QMenu(self)
        menu.addAction(self.action_toggle)
        menu.addAction(self.action_pin)
        menu.addAction(self.action_reset)
        menu.addSeparator()
        menu.addAction(self.action_exit)
        return menu

    def _refresh_action_labels(self) -> None:
        self.action_pin.setText("Pin Window" if self._movable else "Unpin Window")

    def toggle_movable(self) -> None:
        self._movable = not self._movable
        self._refresh_action_labels()

    def toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()

    def _adjust_compact_width(self) -> None:
        rows = [self.cpu, self.mem] + [row for _m, row in self.disk_rows]
        if not self.gpu.isHidden():
            rows.append(self.gpu)
        if not rows:
            return

        margins = self._metrics_layout.contentsMargins()
        spacing = self._metrics_layout.spacing() * max(0, len(rows) - 1)
        target_width = sum(row.width() for row in rows) + spacing + margins.left() + margins.right()
        target_height = max(52, max(row.sizeHint().height() for row in rows) + margins.top() + margins.bottom())

        if abs(self.width() - target_width) > 2 or abs(self.height() - target_height) > 2:
            self.resize(target_width, target_height)

    def _freeze_metric_widths(self) -> None:
        self._set_row_width(self.cpu, ["CPU: 100%"])
        self._set_row_width(self.mem, ["Memory: 100% (999.9/999.9 GB)"])
        for mount, row in self.disk_rows:
            sample = f"Disk {self._short_mount_label(mount)}: 100% (9999/9999 GB)"
            self._set_row_width(row, [sample])
        self._set_row_width(
            self.gpu,
            [
                "GPU: 100% | NVIDIA GeForce RTX 4090",
                "Temp: 99C | VRAM: 24576/24576 MB",
            ],
        )

    @staticmethod
    def _set_row_width(row: MetricRow, samples: list[str]) -> None:
        max_width = 0
        for sample in samples:
            max_width = max(max_width, row.label.fontMetrics().horizontalAdvance(sample))
        row.setFixedWidth(max(112, max_width + 20))

    def _on_tray_clicked(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.toggle_visibility()

    def _init_timers(self) -> None:
        self.cpu_timer = QTimer(self)
        self.cpu_timer.setInterval(1000)
        self.cpu_timer.timeout.connect(self._update_cpu)
        self.cpu_timer.start()

        self.mem_timer = QTimer(self)
        self.mem_timer.setInterval(2000)
        self.mem_timer.timeout.connect(self._update_memory)
        self.mem_timer.start()

        self.disk_timer = QTimer(self)
        self.disk_timer.setInterval(15000)
        self.disk_timer.timeout.connect(self._update_disk)
        self.disk_timer.start()

        self.gpu_timer = QTimer(self)
        self.gpu_timer.setInterval(2000)
        self.gpu_timer.timeout.connect(self._update_gpu)
        if not self.gpu.isHidden():
            self.gpu_timer.start()

        self.gpu_retry_timer = QTimer(self)
        self.gpu_retry_timer.setInterval(10000)
        self.gpu_retry_timer.timeout.connect(self._retry_gpu_detection)
        self.gpu_retry_timer.start()

    def _init_gpu(self) -> None:
        if not NVML_AVAILABLE:
            return
        try:
            if not self._nvml_initialized:
                nvmlInit()
                self._nvml_initialized = True
            if nvmlDeviceGetCount() > 0:
                self._gpu_handle = nvmlDeviceGetHandleByIndex(0)
        except NVMLError:
            self._gpu_handle = None

    def _retry_gpu_detection(self) -> None:
        if self._gpu_handle is not None:
            return
        self._init_gpu()
        if self._gpu_handle is None:
            return
        self._apply_gpu_visibility()
        if not self.gpu_timer.isActive():
            self.gpu_timer.start()
        self._update_gpu()
        self.adjustSize()

    def _apply_gpu_visibility(self) -> None:
        has_gpu = self._gpu_handle is not None
        self.gpu.setVisible(has_gpu)

    @staticmethod
    def _format_gpu_name(raw_name: str) -> str:
        cleaned = " ".join(raw_name.split())
        for prefix in ("NVIDIA GeForce", "NVIDIA", "AMD Radeon", "Intel(R)"):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return cleaned or raw_name

    @staticmethod
    def _short_mount_label(mount: str) -> str:
        if sys.platform.startswith("win"):
            return mount.rstrip("\\").rstrip(":") + ":"
        return mount

    def _discover_disk_mounts(self) -> list[str]:
        mounts: list[str] = []
        seen: set[str] = set()
        for part in psutil.disk_partitions(all=False):
            mount = part.mountpoint
            if not mount or mount in seen:
                continue
            # Skip non-physical mounts when possible.
            if "cdrom" in (part.opts or "").lower():
                continue
            try:
                if not Path(mount).exists():
                    continue
                psutil.disk_usage(mount)
            except Exception:
                continue
            seen.add(mount)
            mounts.append(mount)
        if not mounts:
            mounts.append(str(Path("/")))
        return mounts

    def _update_cpu(self) -> None:
        usage = psutil.cpu_percent()
        self.cpu.set_text(f"CPU: {usage:.0f}%")
        self._adjust_compact_width()

    def _update_memory(self) -> None:
        mem = psutil.virtual_memory()
        self.mem.set_text(f"Memory: {mem.percent:.0f}% ({mem.used / 1024**3:.1f}/{mem.total / 1024**3:.1f} GB)")
        self._adjust_compact_width()

    def _update_disk(self) -> None:
        for mount, row in self.disk_rows:
            try:
                disk = psutil.disk_usage(mount)
                row.set_text(
                    f"Disk {self._short_mount_label(mount)}: {disk.percent:.0f}% "
                    f"({disk.used / 1024**3:.0f}/{disk.total / 1024**3:.0f} GB)"
                )
            except Exception:
                row.set_text(f"Disk {self._short_mount_label(mount)}: unavailable")
        self._adjust_compact_width()

    def _update_gpu(self) -> None:
        if not self._gpu_handle:
            self.gpu.set_text("GPU: unavailable")
            self._adjust_compact_width()
            return

        try:
            util = nvmlDeviceGetUtilizationRates(self._gpu_handle)
            temp = nvmlDeviceGetTemperature(self._gpu_handle, NVML_TEMPERATURE_GPU)
            mem = nvmlDeviceGetMemoryInfo(self._gpu_handle)
            name = nvmlDeviceGetName(self._gpu_handle)
            if isinstance(name, bytes):
                name = name.decode("utf-8", errors="ignore")
            pretty_name = self._format_gpu_name(str(name))
            self.gpu.set_text(
                f"GPU: {util.gpu:.0f}% | {pretty_name}\n"
                f"Temp: {temp}C | VRAM: {mem.used / 1024**2:.0f}/{mem.total / 1024**2:.0f} MB"
            )
            self._adjust_compact_width()
        except NVMLError:
            self.gpu.set_text("GPU: read error")
            self._adjust_compact_width()
        except Exception:
            self.gpu.set_text("GPU: read error")
            self._adjust_compact_width()

    def _move_to_bottom_right(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
        area = screen.availableGeometry()
        self.move(area.right() - self.width(), area.bottom() - self.height())

    def contextMenuEvent(self, event) -> None:  # type: ignore[override]
        self._refresh_action_labels()
        menu = self._create_context_menu()
        menu.exec(event.globalPos())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._movable and event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._movable and self._drag_origin and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_origin
            self.move(self.pos() + delta)
            self._drag_origin = event.globalPosition().toPoint()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if NVML_AVAILABLE and self._nvml_initialized:
            try:
                nvmlShutdown()
                self._nvml_initialized = False
            except NVMLError:
                pass
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    monitor = SystemMonitor()
    monitor.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
