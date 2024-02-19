import sys
import os
import psutil
import GPUtil
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QSystemTrayIcon, QMenu, QAction, QDesktopWidget, QPushButton, QStyle
from PyQt5.QtGui import QIcon, QMouseEvent, QPainter, QPen, QColor, QPainterPath
from PyQt5.QtCore import QTimer, Qt, QPoint

class LineGraphWidget(QWidget):
    def __init__(self, parent=None, line_color=QColor(5, 184, 204)):
        super(LineGraphWidget, self).__init__(parent)
        self.usage_data = [0] * 100  # Initialize with 100 data points
        self.line_color = line_color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Draw background
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 50))

        # Create a path for the line graph
        path = QPainterPath()
        if len(self.usage_data) > 1:
            step = w / (len(self.usage_data) - 1)
            path.moveTo(0, h - self.usage_data[0] * h / 100)
            for i in range(1, len(self.usage_data)):
                path.lineTo(int(i * step), int(h - self.usage_data[i] * h / 100))

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
        self.usage_data.pop(0)
        self.usage_data.append(usage)
        self.update()  # Trigger a repaint

class NetworkGraphWidget(QWidget):
    def __init__(self, parent=None):
        super(NetworkGraphWidget, self).__init__(parent)
        self.upload_data = [0] * 100
        self.download_data = [0] * 100
        self.upload_line_color = QColor(255, 120, 50)  # Orange for upload
        self.download_line_color = QColor(150, 50, 200)  # Purple for download

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Draw background
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 50))

        # Calculate the maximum value for upload and download
        max_value = max(*self.upload_data, *self.download_data)
        if max_value == 0:
            max_value = 1  # Avoid division by zero

        # Draw the upload graph (dashed line)
        if len(self.upload_data) > 1:
            step = w / (len(self.upload_data) - 1)
            pen = QPen(self.upload_line_color, 3)  # Increase the line width to 3
            pen.setStyle(Qt.CustomDashLine)
            pen.setDashPattern([6, 4])  # Increase the length of dashes and gaps
            painter.setPen(pen)
            for i in range(1, len(self.upload_data)):
                painter.drawLine(
                    int((i - 1) * step), int(h - self.upload_data[i - 1] * h / max_value),
                    int(i * step), int(h - self.upload_data[i] * h / max_value)
                )

        # Draw the download graph (solid line)
        if len(self.download_data) > 1:
            step = w / (len(self.download_data) - 1)
            painter.setPen(QPen(self.download_line_color, 2))
            for i in range(1, len(self.download_data)):
                painter.drawLine(
                    int((i - 1) * step), int(h - self.download_data[i - 1] * h / max_value),
                    int(i * step), int(h - self.download_data[i] * h / max_value)
                )

    def update_usage(self, upload_diff, download_diff):
        # Shift data to the right and insert new values at the beginning
        self.upload_data.pop()
        self.upload_data.insert(0, upload_diff)

        self.download_data.pop()
        self.download_data.insert(0, download_diff)

        self.update()  # Trigger a repaint

class SystemMonitor(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.is_movable = True
        self.old_pos = None
        network_usage = psutil.net_io_counters()
        self.last_upload = network_usage.bytes_sent / 1024
        self.last_download = network_usage.bytes_recv / 1024
        self.init_ui()
        self.init_system_tray()
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
        self.pin_button.setStyleSheet("background-color: green;" if self.is_movable else "background-color: red;")
        self.pin_button.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton if self.is_movable else QStyle.SP_DialogCancelButton))

    def mousePressEvent(self, event: QMouseEvent):
        if self.is_movable and event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_movable and self.old_pos is not None and event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def init_system_tray(self):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.png')
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        tray_menu = QMenu()
        tray_menu.addAction(QAction("Show", self, triggered=self.show))
        tray_menu.addAction(QAction("Hide", self, triggered=self.hide))
        tray_menu.addAction(QAction("Quit", self, triggered=self.app.quit))
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def init_widgets(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 40, 10, 10)

        # Network usage label
        self.label_network = QLabel(self.central_widget)
        self.label_network.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_network.setStyleSheet("color: white; background-color: transparent;")
        self.layout.addWidget(self.label_network)

        # Network usage graph
        self.network_graph = NetworkGraphWidget(self.central_widget)
        self.layout.addWidget(self.network_graph)

        # CPU usage line graph widget
        self.label_cpu = QLabel("CPU Usage", self.central_widget)
        self.label_cpu.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_cpu.setStyleSheet("color: white; background-color: transparent;")
        self.layout.addWidget(self.label_cpu)
        self.cpu_graph = LineGraphWidget(self.central_widget)
        self.layout.addWidget(self.cpu_graph)

        # GPU usage line graph widget
        self.label_gpu = QLabel("GPU Usage", self.central_widget)
        self.label_gpu.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_gpu.setStyleSheet("color: white; background-color: transparent;")
        self.layout.addWidget(self.label_gpu)
        self.gpu_graph = LineGraphWidget(self.central_widget)
        self.layout.addWidget(self.gpu_graph)

        # Memory usage line graph widget
        self.label_mem = QLabel("Memory Usage", self.central_widget)
        self.label_mem.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_mem.setStyleSheet("color: white; background-color: transparent;")
        self.layout.addWidget(self.label_mem)
        self.memory_graph = LineGraphWidget(self.central_widget)
        self.layout.addWidget(self.memory_graph)

        # Disk usage line graph widget
        self.disk_labels = []
        self.disk_graphs = []
        for partition in psutil.disk_partitions():
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint,os.R_OK):
                label = QLabel(f"Disk {len(self.disk_labels) + 1} Usage", self.central_widget)
                label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                label.setStyleSheet("color: white; background-color: transparent;")
                self.disk_labels.append(label)
                self.layout.addWidget(label)
                graph = LineGraphWidget(self.central_widget)
                self.disk_graphs.append(graph)
                self.layout.addWidget(graph)
        self.pin_button.raise_()

    def init_timers(self):
        # Update the network information
        self.network_timer = QTimer(self)
        self.network_timer.timeout.connect(self.update_network_info)
        self.network_timer.start(1000)

        # Update the CPU information
        self.cpu_timer = QTimer(self)
        self.cpu_timer.timeout.connect(self.update_cpu_info)
        self.cpu_timer.start(1000)

        # Update the GPU information
        self.gpu_timer = QTimer(self)
        self.gpu_timer.timeout.connect(self.update_gpu_info)
        self.gpu_timer.start(1000)

        # Update the memory information
        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self.update_memory_info)
        self.memory_timer.start(1000)

        # Update the disk information
        self.disk_timer = QTimer(self)
        self.disk_timer.timeout.connect(self.update_disk_info)
        self.disk_timer.start(1000)

    def update_network_info(self):
        network_usage = psutil.net_io_counters()
        upload = network_usage.bytes_sent / 1024
        download = network_usage.bytes_recv / 1024

        upload_diff = upload - self.last_upload
        download_diff = download - self.last_download

        self.last_upload = upload
        self.last_download = download

        self.label_network.setText(f"Net: ↑ {upload_diff:.2f} KB/s ↓ {download_diff:.2f} KB/s")
        self.network_graph.update_usage(upload_diff, download_diff)

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
        memory_usage = mem.percent
        mem_used_gb = mem.used / 1024 / 1024 / 1024
        mem_total_gb = mem.total / 1024 / 1024 / 1024
        self.label_mem.setText(f"Mem: {memory_usage:.1f}% - {mem_used_gb:.1f}GB / {mem_total_gb:.1f}GB")
        self.memory_graph.update_usage(memory_usage)

    def update_disk_info(self):
        for i, partition in enumerate(psutil.disk_partitions()):
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                disk_usage = psutil.disk_usage(partition.mountpoint)
                disk_usage_percent = disk_usage.percent
                disk_total_gb = disk_usage.total / (1024 ** 3)
                disk_used_gb = disk_usage.used / (1024 ** 3)
                self.disk_labels[i].setText(f"Disk {i + 1}: {disk_usage_percent:.1f}% - {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB")
                self.disk_graphs[i].update_usage(disk_usage_percent)

    def set_geometry_to_bottom(self):
        desktop = QDesktopWidget()
        screen = desktop.availableGeometry(self)
        window_height = self.height()
        self.setGeometry(screen.width() - self.width(), screen.height() - window_height, self.width(), window_height)

def main():
    app = QApplication(sys.argv)
    monitor = SystemMonitor(app)
    monitor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()