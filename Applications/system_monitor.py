import os
import sys
import psutil
import GPUtil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QDesktopWidget, QMenu
)
from PyQt5.QtGui import QMouseEvent, QPainter, QPen, QColor, QPainterPath
from PyQt5.QtCore import QTimer, Qt, QPoint


class LineGraphWidget(QWidget):
    def __init__(self, parent=None, line_color=QColor(5, 184, 204), dynamic_max=False):
        super().__init__(parent)
        self.usage_data = []
        self.line_color = line_color
        self.dynamic_max = dynamic_max

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 20))

        if not self.usage_data:
            return

        max_value = max(self.usage_data) if self.dynamic_max else 100

        def scaled_height(value):
            return h - (value * h / max_value)

        path = QPainterPath()
        step = w / max(len(self.usage_data) - 1, 1)
        path.moveTo(0, scaled_height(self.usage_data[0]))
        for i in range(1, len(self.usage_data)):
            path.lineTo(int(i * step), scaled_height(self.usage_data[i]))

        fill_path = QPainterPath(path)
        fill_path.lineTo(w, h)
        fill_path.lineTo(0, h)
        fill_path.closeSubpath()

        fill_color = QColor(self.line_color)
        fill_color.setAlpha(25)
        painter.fillPath(fill_path, fill_color)

        line_color = QColor(self.line_color)
        line_color.setAlpha(180)
        painter.setPen(QPen(line_color, 2))
        painter.drawPath(path)

    def update_usage(self, usage):
        self.usage_data.append(usage)
        if len(self.usage_data) > 100:
            self.usage_data.pop(0)
        self.update()


class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Monitor")
        self.setGeometry(0, 0, 220, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 80);")

        self.is_movable = True
        self.old_pos = None
        self.disk_labels = []
        self.disk_graphs = []

        self.setup_ui()
        self.setup_timers()
        self.set_geometry_to_bottom()

    def setup_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # CPU
        self.label_cpu = QLabel("CPU: --%", self)
        self.label_cpu.setStyleSheet("color: white; background-color: transparent;")
        self.layout.addWidget(self.label_cpu)
        self.cpu_graph = LineGraphWidget(self.central_widget, QColor(255, 128, 0))
        self.layout.addWidget(self.cpu_graph)

        # Memory
        self.label_mem = QLabel("Memory: --%", self)
        self.label_mem.setStyleSheet("color: white; background-color: transparent;")
        self.layout.addWidget(self.label_mem)
        self.mem_graph = LineGraphWidget(self.central_widget, QColor(0, 200, 0))
        self.layout.addWidget(self.mem_graph)

        # Network
        self.label_net = QLabel("Net: ↑ 0 KB/s ↓ 0 KB/s", self)
        self.label_net.setStyleSheet("color: white; background-color: transparent;")
        self.layout.addWidget(self.label_net)
        self.upload_graph = LineGraphWidget(self.central_widget, QColor(255, 50, 50), True)
        self.download_graph = LineGraphWidget(self.central_widget, QColor(150, 50, 200), True)
        self.layout.addWidget(self.upload_graph)
        self.layout.addWidget(self.download_graph)

        # Disk
        disk_colors = [QColor(180 - i*30, 180 - i*30, 180 - i*30) for i in range(10)]
        for i, partition in enumerate(psutil.disk_partitions()):
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                label = QLabel(f"Disk {i+1}: --%", self)
                label.setStyleSheet("color: white; background-color: transparent;")
                self.layout.addWidget(label)
                graph = LineGraphWidget(self.central_widget, disk_colors[i % len(disk_colors)])
                self.layout.addWidget(graph)
                self.disk_labels.append(label)
                self.disk_graphs.append(graph)

        # GPU
        self.label_gpu = QLabel("GPU: --%", self)
        self.label_gpu.setStyleSheet("color: white; background-color: transparent;")
        self.layout.addWidget(self.label_gpu)
        self.gpu_graph = LineGraphWidget(self.central_widget, QColor(0, 170, 255))
        self.layout.addWidget(self.gpu_graph)

    def toggle_movable(self):
        self.is_movable = not self.is_movable

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(30, 30, 30, 220);
                color: white;
                border: 1px solid gray;
            }
            QMenu::item:selected {
                background-color: rgba(80, 80, 80, 180);
            }
        """)

        pin_action = menu.addAction("Unpin window" if not self.is_movable else "Pin window")
        exit_action = menu.addAction("Exit")

        selected_action = menu.exec_(self.mapToGlobal(event.pos()))

        if selected_action == pin_action:
            self.toggle_movable()
        elif selected_action == exit_action:
            self.close()

    def mousePressEvent(self, event: QMouseEvent):
        if self.is_movable and event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_movable and self.old_pos and event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def setup_timers(self):
        self.cpu_timer = QTimer(self)
        self.cpu_timer.timeout.connect(self.update_cpu)
        self.cpu_timer.start(1000)

        self.mem_timer = QTimer(self)
        self.mem_timer.timeout.connect(self.update_mem)
        self.mem_timer.start(5000)

        self.net_timer = QTimer(self)
        self.net_timer.timeout.connect(self.update_net)
        self.net_timer.start(1000)

        net = psutil.net_io_counters()
        self.last_upload = net.bytes_sent / 1024
        self.last_download = net.bytes_recv / 1024

        self.gpu_timer = QTimer(self)
        self.gpu_timer.timeout.connect(self.update_gpu)
        self.gpu_timer.start(5000)

        self.disk_timer = QTimer(self)
        self.disk_timer.timeout.connect(self.update_disks)
        self.disk_timer.start(10000)

    def update_cpu(self):
        cpu = psutil.cpu_percent()
        self.label_cpu.setText(f"CPU: {cpu:.1f}%")
        self.cpu_graph.update_usage(cpu)

    def update_mem(self):
        mem = psutil.virtual_memory()
        usage = mem.percent
        used = mem.used / 1024**3
        total = mem.total / 1024**3
        self.label_mem.setText(f"Mem: {usage:.1f}% - {used:.1f}GB / {total:.1f}GB")
        self.mem_graph.update_usage(usage)

    def update_net(self):
        net = psutil.net_io_counters()
        up = net.bytes_sent / 1024
        down = net.bytes_recv / 1024
        upload = up - self.last_upload
        download = down - self.last_download
        self.last_upload = up
        self.last_download = down

        up_unit = "KB/s" if upload < 1024 else "MB/s"
        down_unit = "KB/s" if download < 1024 else "MB/s"
        if upload >= 1024:
            upload /= 1024
        if download >= 1024:
            download /= 1024

        self.label_net.setText(f"Net: ↑ {upload:.2f} {up_unit} ↓ {download:.2f} {down_unit}")
        self.upload_graph.update_usage(upload)
        self.download_graph.update_usage(download)

    def update_disks(self):
        for i, partition in enumerate(psutil.disk_partitions()):
            if i >= len(self.disk_graphs):
                break
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                usage = psutil.disk_usage(partition.mountpoint)
                percent = usage.percent
                used = usage.used / 1024**3
                total = usage.total / 1024**3
                self.disk_labels[i].setText(
                    f"Disk {i+1}: {percent:.1f}% - {used:.1f}GB / {total:.1f}GB"
                )
                self.disk_graphs[i].update_usage(percent)

    def update_gpu(self):
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                usage = gpu.load * 100
                temp = gpu.temperature
                name = gpu.name
                vram_used = gpu.memoryUsed
                vram_total = gpu.memoryTotal

                self.label_gpu.setText(
                    f"{name}\nGPU: {usage:.1f}% | Temp: {temp}°C\n"
                    f"VRAM: {vram_used:.1f}MB / {vram_total:.1f}MB"
                )
                self.gpu_graph.update_usage(usage)
            else:
                self.label_gpu.setText("No GPU detected")
                self.gpu_graph.update_usage(0)
        except Exception as e:
            self.label_gpu.setText("GPU error")
            self.gpu_graph.update_usage(0)
            print(f"[GPU] Error: {e}")

    def set_geometry_to_bottom(self):
        desktop = QDesktopWidget()
        screen = desktop.availableGeometry(self)
        self.setGeometry(
            screen.width() - self.width(),
            screen.height() - self.height(),
            self.width(),
            self.height()
        )


def main():
    app = QApplication(sys.argv)
    window = SystemMonitor()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
