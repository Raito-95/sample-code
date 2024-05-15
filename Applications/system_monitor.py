import os
import sys
import psutil
import GPUtil
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar, QDesktopWidget, QPushButton, QStyle
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QTimer, Qt, QPoint


class SystemMonitor(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.label_network = None
        self.label_cpu = None
        self.label_gpu = None
        self.label_mem = None
        self.label_disk = []

        self.progress_bar_network = None
        self.progress_bar_cpu = None
        self.progress_bar_gpu = None
        self.progress_bar_mem = None
        self.progress_bar_disk = []
        self.progress_bar_upload = None
        self.progress_bar_download = None

        network_usage = psutil.net_io_counters()
        self.last_upload = network_usage.bytes_sent / 1024
        self.last_download = network_usage.bytes_recv / 1024
        self.max_upload_rate = 1
        self.max_download_rate = 1

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
        self.setWindowFlags(Qt.WindowStaysOnTopHint |  Qt.FramelessWindowHint | Qt.Tool)
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

        self.progress_bar_upload = QProgressBar(self.central_widget)
        self.progress_bar_download = QProgressBar(self.central_widget)

        self.progress_bar_upload.setFormat("")
        self.progress_bar_upload.setStyleSheet("""
            QProgressBar {
                border: 1px solid gray;
                border-radius: 3px;
                background-color: transparent;
                height: 10px;
            }

            QProgressBar::chunk {
                background-color: rgba(255, 120, 50, 255);
                margin: 0px;
            }
        """)

        self.progress_bar_download.setFormat("")
        self.progress_bar_download.setStyleSheet("""
            QProgressBar {
                border: 1px solid gray;
                border-radius: 3px;
                background-color: transparent;
                height: 10px;
            }

            QProgressBar::chunk {
                background-color: rgba(150, 50, 200, 255);
                margin: 0px;
            }
        """)

        self.layout.addWidget(self.progress_bar_upload)
        self.layout.addWidget(self.progress_bar_download)

    def init_cpu_widget(self):
        self.label_cpu, self.progress_bar_cpu = self.create_label_progress_bar()
        self.layout.addWidget(self.label_cpu)
        self.layout.addWidget(self.progress_bar_cpu)

    def init_gpu_widget(self):
        self.label_gpu, self.progress_bar_gpu = self.create_label_progress_bar()
        self.layout.addWidget(self.label_gpu)
        self.layout.addWidget(self.progress_bar_gpu)

    def init_memory_widget(self):
        self.label_mem, self.progress_bar_mem = self.create_label_progress_bar()
        self.layout.addWidget(self.label_mem)
        self.layout.addWidget(self.progress_bar_mem)

    def init_disk_widgets(self):
        for label in self.label_disk:
            self.layout.removeWidget(label)
            label.deleteLater()
        for bar in self.progress_bar_disk:
            self.layout.removeWidget(bar)
            bar.deleteLater()

        self.label_disk.clear()
        self.progress_bar_disk.clear()

        accessible_partitions = [p for p in psutil.disk_partitions() if os.path.exists(p.mountpoint) and os.access(p.mountpoint, os.R_OK)]
        for _ in accessible_partitions:
            label, progress_bar = self.create_label_progress_bar()
            self.label_disk.append(label)
            self.progress_bar_disk.append(progress_bar)
            self.layout.addWidget(label)
            self.layout.addWidget(progress_bar)

    def create_label_progress_bar(self):
        label = self.create_label()
        progress_bar = QProgressBar(self.central_widget)
        progress_bar.setRange(0, 100)
        progress_bar.setFormat("")
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid gray;
                border-radius: 3px;
                background-color: transparent;
            }

            QProgressBar::chunk {
                background-color: #05B8CC;
                margin: 0px;
            }
        """)
        return label, progress_bar

    def create_label(self):
        label = QLabel(self.central_widget)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setStyleSheet("color: white; background-color: transparent;")
        return label

    def update_network_info(self):
        try:
            network = psutil.net_io_counters()
            upload = (network.bytes_sent / 1024) - self.last_upload
            download = (network.bytes_recv / 1024) - self.last_download

            self.last_upload = network.bytes_sent / 1024
            self.last_download = network.bytes_recv / 1024

            self.max_upload_rate = max(self.max_upload_rate, upload)
            self.max_download_rate = max(self.max_download_rate, download)

            upload_percentage = int(upload / self.max_upload_rate * 100) if self.max_upload_rate > 0 else 0
            download_percentage = int(download / self.max_download_rate * 100) if self.max_download_rate > 0 else 0

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
            self.progress_bar_upload.setValue(upload_percentage)
            self.progress_bar_download.setValue(download_percentage)
        except Exception as e:
            self.label_network.setText("Network monitoring error")
            print(f"Error monitoring network: {e}")

    def update_cpu_info(self):
        try:
            cpu_usage = psutil.cpu_percent()
            self.label_cpu.setText(f"CPU: {cpu_usage:.1f}%")
            self.progress_bar_cpu.setValue(int(cpu_usage))
        except Exception as e:
            self.label_cpu.setText("CPU monitoring error")
            print(f"Error monitoring CPU: {e}")

    def update_gpu_info(self):
        try:
            gpu_info = GPUtil.getGPUs()[0] if GPUtil.getGPUs() else None
            if gpu_info:
                gpu_usage = gpu_info.load * 100
                gpu_temp = gpu_info.temperature
                self.label_gpu.setText(f"GPU: {gpu_usage:.1f}% - Temp: {gpu_temp}°C")
                self.progress_bar_gpu.setValue(int(gpu_usage))
            else:
                self.label_gpu.setText("No GPU detected")
        except Exception as e:
            self.label_gpu.setText("GPU monitoring error")
            print(f"Error monitoring GPU: {e}")

    def update_memory_info(self):
        try:
            mem = psutil.virtual_memory()
            mem_usage = mem.percent
            mem_used_gb = mem.used / 1024 / 1024 / 1024
            mem_total_gb = mem.total / 1024 / 1024 / 1024
            self.label_mem.setText(f"Mem: {mem_usage:.1f}% - {mem_used_gb:.1f}GB / {mem_total_gb:.1f}GB")
            self.progress_bar_mem.setValue(int(mem_usage))
        except Exception as e:
            self.label_mem.setText("Memory monitoring error")
            print(f"Error monitoring memory: {e}")

    def update_disk_info(self):
        accessible_partitions = [p for p in psutil.disk_partitions() if os.path.exists(p.mountpoint) and os.access(p.mountpoint, os.R_OK)]

        try:
            for index, partition in enumerate(accessible_partitions):
                disk_usage = psutil.disk_usage(partition.mountpoint)
                disk_usage_percent = disk_usage.percent
                disk_total_gb = disk_usage.total / (1024 ** 3)
                disk_used_gb = disk_usage.used / (1024 ** 3)
                self.label_disk[index].setText(f"Disk {index + 1}: {disk_usage_percent:.1f}% - {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB")
                self.progress_bar_disk[index].setValue(int(disk_usage_percent))
        except Exception as e:
            print(f"Error monitoring disk: {e}")

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
