import os
import sys
import psutil
import GPUtil
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QDesktopWidget, QPushButton, QStyle
from PyQt5.QtGui import QMouseEvent, QPainter, QPen, QColor, QPainterPath
from PyQt5.QtCore import QTimer, Qt, QPoint


class LineGraphWidget(QWidget):
    def __init__(self, parent=None, line_color=QColor(5, 184, 204), dynamic_max=False):
        super(LineGraphWidget, self).__init__(parent)
        self.usage_data = []  # Initialize as an empty list
        self.line_color = line_color
        self.dynamic_max = dynamic_max  # Set whether to use dynamic max value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Draw background
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 50))

        # Determine the max value based on dynamic_max flag
        if not self.usage_data:
            return
        max_value = max(self.usage_data) if self.dynamic_max else 100

        # Function to scale the height relative to the max value
        def scaled_height(value):
            return h - (value * h / max_value)

        # Create a path for the line graph
        path = QPainterPath()
        step = w / max(len(self.usage_data) - 1, 1)
        path.moveTo(0, scaled_height(self.usage_data[0]))
        for i in range(1, len(self.usage_data)):
            path.lineTo(int(i * step), scaled_height(self.usage_data[i]))

        # Draw the filled area under the line
        fill_path = QPainterPath(path)
        fill_path.lineTo(w, h)
        fill_path.lineTo(0, h)
        fill_path.closeSubpath()
        painter.fillPath(fill_path, QColor(self.line_color.red(), self.line_color.green(), self.line_color.blue(), 50))

        # Draw the line graph
        painter.setPen(QPen(self.line_color, 2))
        painter.drawPath(path)

    def update_usage(self, usage):
        self.usage_data.append(usage)
        if len(self.usage_data) > 100:
            self.usage_data.pop(0)
        self.update()  # Trigger a repaint


class SystemMonitor(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.label_network = None
        self.label_cpu = None
        self.label_gpu = None
        self.label_mem = None
        self.label_disk = []

        self.upload_graph = None
        self.download_graph = None
        self.cpu_graph = None
        self.gpu_graph = None
        self.memory_graph = None
        self.disk_graphs = []

        network_usage = psutil.net_io_counters()
        self.last_upload = network_usage.bytes_sent / 1024
        self.last_download = network_usage.bytes_recv / 1024

        self.app = app
        self.is_movable = True
        self.old_pos = None
        self.init_ui()
        self.init_widgets()
        self.init_timers()
        self.set_geometry_to_bottom()

    def init_ui(self):
        self.setWindowTitle("System Monitor")
        self.setGeometry(0, 0, 220, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.pin_button = QPushButton(self)
        self.pin_button.setCheckable(True)
        self.pin_button.setChecked(True)
        self.pin_button.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.pin_button.setStyleSheet("background-color: green;")
        self.pin_button.clicked.connect(self.toggle_movable)
        self.pin_button.setGeometry(190, 10, 20, 20)

    def toggle_movable(self):
        self.is_movable = not self.is_movable
        if self.is_movable:
            self.pin_button.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
            self.pin_button.setStyleSheet("background-color: green;")
        else:
            self.pin_button.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
            self.pin_button.setStyleSheet("background-color: red;")

    def mousePressEvent(self, event: QMouseEvent):
        if self.is_movable and event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_movable and self.old_pos is not None and event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def init_widgets(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 40, 10, 10)

        self.init_network_widget()
        self.init_cpu_widget()
        self.init_gpu_widget()
        self.init_memory_widget()
        self.init_disk_widgets()
        self.pin_button.raise_()

    def init_timers(self):
        self.network_timer = QTimer(self)
        self.network_timer.timeout.connect(self.update_network_info)
        self.network_timer.start(1000)

        self.cpu_timer = QTimer(self)
        self.cpu_timer.timeout.connect(self.update_cpu_info)
        self.cpu_timer.start(3000)

        self.gpu_timer = QTimer(self)
        self.gpu_timer.timeout.connect(self.update_gpu_info)
        self.gpu_timer.start(4000)

        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self.update_memory_info)
        self.memory_timer.start(5000)

        self.disk_timer = QTimer(self)
        self.disk_timer.timeout.connect(self.update_disk_info)
        self.disk_timer.start(10000)

    def init_network_widget(self):
        self.label_network = self.create_label()
        self.layout.addWidget(self.label_network)

        self.upload_graph = LineGraphWidget(self.central_widget, line_color=QColor(255, 120, 50), dynamic_max=True)  # Orange for upload
        self.download_graph = LineGraphWidget(self.central_widget, line_color=QColor(150, 50, 200), dynamic_max=True)  # Purple for download
        self.layout.addWidget(self.upload_graph)
        self.layout.addWidget(self.download_graph)

    def init_cpu_widget(self):
        self.label_cpu = self.create_label()
        self.layout.addWidget(self.label_cpu)
        self.cpu_graph = LineGraphWidget(self.central_widget)
        self.layout.addWidget(self.cpu_graph)

    def init_gpu_widget(self):
        self.label_gpu = self.create_label()
        self.layout.addWidget(self.label_gpu)
        self.gpu_graph = LineGraphWidget(self.central_widget)
        self.layout.addWidget(self.gpu_graph)

    def init_memory_widget(self):
        self.label_mem = self.create_label()
        self.layout.addWidget(self.label_mem)
        self.memory_graph = LineGraphWidget(self.central_widget)
        self.layout.addWidget(self.memory_graph)

    def init_disk_widgets(self):
        self.label_disk = []
        self.disk_graphs = []
        for partition in psutil.disk_partitions():
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                label = self.create_label()
                self.label_disk.append(label)
                self.layout.addWidget(label)
                graph = LineGraphWidget(self.central_widget)
                self.disk_graphs.append(graph)
                self.layout.addWidget(graph)

    def create_label(self):
        label = QLabel(self.central_widget)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setStyleSheet("color: white; background-color: transparent;")
        return label

    def update_network_info(self):
        network = psutil.net_io_counters()
        if not hasattr(self, 'last_upload'):
            self.last_upload = network.bytes_sent / 1024
            self.last_download = network.bytes_recv / 1024
        upload = (network.bytes_sent / 1024) - self.last_upload
        download = (network.bytes_recv / 1024) - self.last_download

        self.last_upload = network.bytes_sent / 1024
        self.last_download = network.bytes_recv / 1024

        if upload > 1024:
            upload /= 1024
            upload_unit = "MB/s"
        else:
            upload_unit = "KB/s"

        if download > 1024:
            download /= 1024
            download_unit = "MB/s"
        else:
            download_unit = "KB/s"

        self.label_network.setText(f"Net: ↑ {upload:.2f} {upload_unit} ↓ {download:.2f} {download_unit}")
        self.upload_graph.update_usage(upload)
        self.download_graph.update_usage(download)

    def update_cpu_info(self):
        cpu_usage = psutil.cpu_percent()
        self.label_cpu.setText(f"CPU: {cpu_usage:.1f}%")
        self.cpu_graph.update_usage(cpu_usage)

    def update_gpu_info(self):
        gpu_info = GPUtil.getGPUs()[0] if GPUtil.getGPUs() else None
        if gpu_info:
            gpu_usage = gpu_info.load * 100
            gpu_temp = gpu_info.temperature
            self.label_gpu.setText(f"GPU: {gpu_usage:.1f}% - Temp: {gpu_temp}°C")
            self.gpu_graph.update_usage(gpu_usage)

    def update_memory_info(self):
        mem = psutil.virtual_memory()
        mem_usage = mem.percent
        mem_used_gb = mem.used / 1024 / 1024 / 1024
        mem_total_gb = mem.total / 1024 / 1024 / 1024
        self.label_mem.setText(f"Mem: {mem_usage:.1f}% - {mem_used_gb:.1f}GB / {mem_total_gb:.1f}GB")
        self.memory_graph.update_usage(mem_usage)

    def update_disk_info(self):
        for index, partition in enumerate(psutil.disk_partitions()):
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                disk_usage = psutil.disk_usage(partition.mountpoint)
                disk_usage_percent = disk_usage.percent
                disk_total_gb = disk_usage.total / (1024 ** 3)
                disk_used_gb = disk_usage.used / (1024 ** 3)
                self.label_disk[index].setText(f"Disk {index + 1}: {disk_usage_percent:.1f}% - {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB")
                self.disk_graphs[index].update_usage(disk_usage_percent)

    def set_geometry_to_bottom(self):
        desktop = QDesktopWidget()
        screen = desktop.availableGeometry(self)
        self.setGeometry(screen.width() - self.width(), screen.height() - self.height(), self.width(), self.height())


def main():
    app = QApplication(sys.argv)
    monitor = SystemMonitor(app)
    monitor.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
