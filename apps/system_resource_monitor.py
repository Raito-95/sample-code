import json
import subprocess
import sys
from pathlib import Path

import psutil
from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QAction, QColor, QGuiApplication, QIcon, QMouseEvent, QPixmap
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

LOW_COLOR = "#d2dbec"
MID_COLOR = "#f6c177"
HIGH_COLOR = "#ff6b6b"


class MetricRow(QFrame):
    def __init__(self, parent: QWidget, title: str, value: str = "--", detail: str = "--") -> None:
        super().__init__(parent)
        self.setObjectName("metricRow")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(6)

        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("metricTitle")
        self.title_label.setFixedWidth(44)

        self.value_label = QLabel(value, self)
        self.value_label.setObjectName("metricValue")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.value_label.setFixedWidth(42)

        self.detail_label = QLabel(detail, self)
        self.detail_label.setObjectName("metricDetail")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.detail_label.setMinimumWidth(80)

        self.label = QLabel(self)
        self.label.hide()

        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.value_label)
        layout.addWidget(self.detail_label)
        self._sync_label()

    def set_metric(self, value: str, detail: str, tone: str) -> None:
        self.value_label.setText(value)
        self.value_label.setStyleSheet(f"color: {tone};")
        self.detail_label.setText(detail)
        self._sync_label()

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)
        self._sync_label()

    def set_tooltip(self, text: str) -> None:
        self.setToolTip(text)
        self.title_label.setToolTip(text)
        self.detail_label.setToolTip(text)
        self.value_label.setToolTip(text)

    def set_detail(self, detail: str) -> None:
        self.set_metric(detail, "", LOW_COLOR)

    def _sync_label(self) -> None:
        parts = [self.title_label.text().rstrip(":"), self.value_label.text(), self.detail_label.text()]
        self.label.setText(" ".join(part for part in parts if part))


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
        self._disk_types = self._detect_disk_types()

        root = QWidget(self)
        root.setObjectName("root")
        self.setCentralWidget(root)

        self._metrics_layout = QVBoxLayout(root)
        self._metrics_layout.setContentsMargins(6, 6, 6, 6)
        self._metrics_layout.setSpacing(4)

        self.cpu = MetricRow(root, "CPU", "--%", "--")
        self.mem = MetricRow(root, "RAM", "--%", "--")
        self.gpu = MetricRow(root, "GPU", "--", "--")
        self._gpu_base_title = "GPU"
        self.disk_rows: list[tuple[str, MetricRow]] = []
        for mount in self._disk_mounts:
            short = self._short_mount_label(mount)
            kind = self._disk_types.get(short, "")
            title = short if not kind else f"{short} {kind}"
            row = MetricRow(root, title, "--%", "--")
            self.disk_rows.append((mount, row))

        self._metrics_layout.addWidget(self.cpu)
        self._metrics_layout.addWidget(self.mem)
        for _mount, row in self.disk_rows:
            self._metrics_layout.addWidget(row)
        self._metrics_layout.addWidget(self.gpu)

        root.setStyleSheet(
            """
            QWidget#root {
                background-color: rgba(15, 20, 29, 182);
                border: 1px solid rgba(255, 255, 255, 42);
                border-radius: 14px;
            }
            QFrame#metricRow {
                background-color: rgba(255, 255, 255, 4);
                border: 1px solid rgba(255, 255, 255, 16);
                border-radius: 8px;
            }
            QLabel#metricTitle {
                color: #eef2ff;
                font-size: 11px;
                font-weight: 800;
            }
            QLabel#metricValue {
                color: #d2dbec;
                font-size: 12px;
                font-weight: 800;
                min-width: 42px;
            }
            QLabel#metricDetail {
                color: #9fb0cc;
                font-size: 10px;
                font-weight: 700;
                min-width: 80px;
            }
            """
        )

        self._init_gpu()
        self._apply_gpu_visibility()
        self._init_timers()
        self._init_tray()
        self.resize(220, 220)
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
        target_width = min(280, max(200, max(row.sizeHint().width() for row in rows) + margins.left() + margins.right()))
        target_height = (
            sum(row.sizeHint().height() for row in rows)
            + spacing
            + margins.top()
            + margins.bottom()
        )

        if abs(self.width() - target_width) > 2 or abs(self.height() - target_height) > 2:
            self.resize(target_width, target_height)

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
        self.gpu.setVisible(self._gpu_handle is not None)

    @staticmethod
    def _format_gpu_name(raw_name: str) -> str:
        cleaned = " ".join(raw_name.split())
        for prefix in ("NVIDIA GeForce", "NVIDIA", "AMD Radeon", "Intel(R)"):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return cleaned or raw_name

    @staticmethod
    def _usage_color(percent: float) -> str:
        if percent >= 85:
            return HIGH_COLOR
        if percent >= 60:
            return MID_COLOR
        return LOW_COLOR

    @staticmethod
    def _short_mount_label(mount: str) -> str:
        if sys.platform.startswith("win"):
            return mount.rstrip("\\").rstrip(":") + ":"
        return mount

    def _detect_disk_types(self) -> dict[str, str]:
        if not sys.platform.startswith("win"):
            return {}

        command = (
            "$result=@{}; "
            "Get-Volume | Where-Object {$_.DriveLetter} | ForEach-Object { "
            "$dl=$_.DriveLetter; $kind=''; "
            "try { "
            "$pd=Get-Partition -DriveLetter $dl -ErrorAction Stop | "
            "Get-Disk -ErrorAction Stop | "
            "Get-PhysicalDisk -ErrorAction Stop | Select-Object -First 1; "
            "if($pd -and $pd.MediaType){$kind=$pd.MediaType.ToString()} "
            "} catch {} "
            "$result[($dl+':')]=$kind "
            "}; $result | ConvertTo-Json -Compress"
        )
        try:
            output = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", command],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=3,
            ).strip()
            raw = json.loads(output) if output else {}
            if not isinstance(raw, dict):
                return {}

            normalized: dict[str, str] = {}
            for drive, kind in raw.items():
                value = str(kind).upper()
                if "SSD" in value:
                    normalized[str(drive)] = "SSD"
                elif "HDD" in value:
                    normalized[str(drive)] = "HDD"
                else:
                    normalized[str(drive)] = ""
            return normalized
        except Exception:
            return {}

    def _discover_disk_mounts(self) -> list[str]:
        mounts: list[str] = []
        seen: set[str] = set()
        for part in psutil.disk_partitions(all=False):
            mount = part.mountpoint
            if not mount or mount in seen:
                continue
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
        freq = psutil.cpu_freq()
        freq_text = f"{freq.current / 1000:.2f}GHz" if freq else "N/A"
        self.cpu.set_metric(f"{usage:.0f}%", freq_text, self._usage_color(usage))
        self._adjust_compact_width()

    def _update_memory(self) -> None:
        mem = psutil.virtual_memory()
        detail = f"{mem.used / 1024**3:.1f}/{mem.total / 1024**3:.1f}GB"
        self.mem.set_metric(f"{mem.percent:.0f}%", detail, self._usage_color(mem.percent))
        self._adjust_compact_width()

    def _update_disk(self) -> None:
        for mount, row in self.disk_rows:
            try:
                disk = psutil.disk_usage(mount)
                detail = f"{disk.used / 1024**3:.0f}/{disk.total / 1024**3:.0f}GB"
                row.set_metric(f"{disk.percent:.0f}%", detail, self._usage_color(disk.percent))
            except Exception:
                row.set_metric("--", "unavailable", HIGH_COLOR)
        self._adjust_compact_width()

    def _update_gpu(self) -> None:
        if not self._gpu_handle:
            self.gpu.set_title(self._gpu_base_title)
            self.gpu.set_tooltip("")
            self.gpu.set_metric("--", "unavailable", HIGH_COLOR)
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
            self.gpu.set_title(self._gpu_base_title)
            self.gpu.set_tooltip(pretty_name)
            detail = f"{temp}C {mem.used / 1024**3:.1f}/{mem.total / 1024**3:.1f}GB"
            self.gpu.set_metric(f"{util.gpu:.0f}%", detail, self._usage_color(float(util.gpu)))
            self._adjust_compact_width()
        except NVMLError:
            self.gpu.set_title(self._gpu_base_title)
            self.gpu.set_tooltip("")
            self.gpu.set_metric("--", "read error", HIGH_COLOR)
            self._adjust_compact_width()
        except Exception:
            self.gpu.set_title(self._gpu_base_title)
            self.gpu.set_tooltip("")
            self.gpu.set_metric("--", "read error", HIGH_COLOR)
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
