"""
This module provides a system monitor application using PyQt5
that displays real-time information about CPU, GPU, memory, and disk usage.
"""

import sys
import os
import psutil
import GPUtil
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar, QSystemTrayIcon, QMenu, QAction, QDesktopWidget, QPushButton, QStyle
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtCore import QTimer, Qt, QPoint

class SystemMonitor(QMainWindow):
    """Main window class for the system monitor application."""
    def __init__(self, app):
        super().__init__()
        # Initialize attributes
        self.label_network = None
        self.label_cpu = None
        self.progress_bar_cpu = None
        self.label_gpu = None
        self.progress_bar_gpu = None
        self.label_mem = None
        self.progress_bar_mem = None
        self.disk_labels = []
        self.disk_progress_bars = []

        # Initialize UI and functionality
        self.app = app
        self.is_movable = True
        self.old_pos = None
        self.init_ui()
        self.init_system_tray()
        self.init_widgets()
        self.init_timers()
        self.set_geometry_to_bottom()

    def init_ui(self):
        """Initialize the main window UI."""
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
        """Toggle the movability of the window."""
        self.is_movable = not self.is_movable
        if self.is_movable:
            self.pin_button.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
            self.pin_button.setStyleSheet("background-color: green;")
        else:
            self.pin_button.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
            self.pin_button.setStyleSheet("background-color: red;")

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events to enable window movement."""
        if self.is_movable:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events to move the window."""
        if self.is_movable and self.old_pos is not None:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def init_system_tray(self):
        """Initialize the system tray icon and menu."""
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.png')
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)

        tray_menu = QMenu()
        tray_menu.addAction(QAction("Show", self, triggered=self.show))
        tray_menu.addAction(QAction("Hide", self, triggered=self.hide))
        tray_menu.addAction(QAction("Quit", self, triggered=self.app.quit))

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def init_widgets(self):
        """Initialize the widgets for displaying system information."""
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

    def init_network_widget(self):
        """Initialize the network information widget."""
        self.label_network = self.create_label()
        self.layout.addWidget(self.label_network)

    def init_cpu_widget(self):
        """Initialize the CPU information widget."""
        self.label_cpu, self.progress_bar_cpu = self.create_label_progress_bar()
        self.layout.addWidget(self.label_cpu)
        self.layout.addWidget(self.progress_bar_cpu)

    def init_gpu_widget(self):
        """Initialize the GPU information widget."""
        self.label_gpu, self.progress_bar_gpu = self.create_label_progress_bar()
        self.layout.addWidget(self.label_gpu)
        self.layout.addWidget(self.progress_bar_gpu)

    def init_memory_widget(self):
        """Initialize the memory information widget."""
        self.label_mem, self.progress_bar_mem = self.create_label_progress_bar()
        self.layout.addWidget(self.label_mem)
        self.layout.addWidget(self.progress_bar_mem)

    def init_disk_widgets(self):
        """Initialize the disk information widgets."""
        self.disk_labels = []
        self.disk_progress_bars = []
        for partition in psutil.disk_partitions():
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                label, progress_bar = self.create_label_progress_bar()
                self.disk_labels.append(label)
                self.disk_progress_bars.append(progress_bar)
                self.layout.addWidget(label)
                self.layout.addWidget(progress_bar)

    def create_label(self):
        """Create and return a QLabel with predefined styles."""
        label = QLabel(self.central_widget)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setStyleSheet("color: white; background-color: transparent;")
        return label

    def create_label_progress_bar(self):
        """Create and return a QLabel and QProgressBar with predefined styles."""
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

    def init_timers(self):
        """Initialize timers for updating system information."""
        self.network_timer = QTimer(self)
        self.network_timer.timeout.connect(self.update_network_info)
        self.network_timer.start(3000)

        self.cpu_timer = QTimer(self)
        self.cpu_timer.timeout.connect(self.update_cpu_info)
        self.cpu_timer.start(1000)

        self.gpu_timer = QTimer(self)
        self.gpu_timer.timeout.connect(self.update_gpu_info)
        self.gpu_timer.start(4000)

        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self.update_memory_info)
        self.memory_timer.start(2000)

        self.disk_timer = QTimer(self)
        self.disk_timer.timeout.connect(self.update_disk_info)
        self.disk_timer.start(5000)

    def update_network_info(self):
        """Update the network information widget."""
        network = psutil.net_io_counters()
        upload = network.bytes_sent / 1024 / 1024
        download = network.bytes_recv / 1024 / 1024
        self.label_network.setText(f"Net: ↑ {upload:.2f}MB/s ↓ {download:.2f}MB/s")

    def update_cpu_info(self):
        """Update the CPU information widget."""
        cpu_usage = psutil.cpu_percent()
        self.label_cpu.setText(f"CPU: {cpu_usage:.1f}%")
        self.progress_bar_cpu.setValue(int(cpu_usage))

    def update_gpu_info(self):
        """Update the GPU information widget."""
        gpu_info = GPUtil.getGPUs()[0] if GPUtil.getGPUs() else None
        if gpu_info:
            gpu_usage = gpu_info.load * 100
            gpu_temp = gpu_info.temperature
            self.label_gpu.setText(f"GPU: {gpu_usage:.1f}% - Temp: {gpu_temp}°C")
            self.progress_bar_gpu.setValue(int(gpu_usage))

    def update_memory_info(self):
        """Update the memory information widget."""
        mem = psutil.virtual_memory()
        mem_usage = mem.percent
        mem_used_gb = mem.used / 1024 / 1024 / 1024
        mem_total_gb = mem.total / 1024 / 1024 / 1024
        self.label_mem.setText(f"Mem: {mem_usage:.1f}% - {mem_used_gb:.1f}GB / {mem_total_gb:.1f}GB")
        self.progress_bar_mem.setValue(int(mem_usage))

    def update_disk_info(self):
        """Update the disk information widgets."""
        for index, partition in enumerate(psutil.disk_partitions()):
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                disk_usage = psutil.disk_usage(partition.mountpoint)
                disk_usage_percent = disk_usage.percent
                disk_total_gb = disk_usage.total / (1024 ** 3)
                disk_used_gb = disk_usage.used / (1024 ** 3)
                self.disk_labels[index].setText(f"Disk {index + 1}: {disk_usage_percent:.1f}% - {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB")
                self.disk_progress_bars[index].setValue(int(disk_usage_percent))

    def set_geometry_to_bottom(self):
        """Set the window geometry to the bottom right corner of the screen."""
        desktop = QDesktopWidget()
        screen = desktop.availableGeometry(self)
        window_height = self.height()
        self.setGeometry(screen.width() - self.width(), screen.height() - window_height, self.width(), window_height)

def main():
    """Main function to start the application."""
    app = QApplication(sys.argv)
    monitor = SystemMonitor(app)
    monitor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
