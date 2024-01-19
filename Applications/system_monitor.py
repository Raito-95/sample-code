import sys
import os
import psutil
import GPUtil
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar, QSystemTrayIcon, QMenu, QAction, QDesktopWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt

class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.initSystemTray()
        self.initWidgets()
        self.initTimer()
        self.setGeometryToBottom()

    def initUI(self):
        self.setWindowTitle("System Monitor")
        self.setGeometry(0, 0, 200, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")

    def initSystemTray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("C:/Users/User/Github/sample-code/Applications/test.png"))

        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Quit", self)
        
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(app.quit)  # Use app.quit() to correctly close the application
        
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def initWidgets(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # Network
        self.label_network = QLabel(self.central_widget)
        self.label_network.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_network.setStyleSheet("color: white;")
        layout.addWidget(self.label_network)

        # CPU
        self.label_cpu = QLabel(self.central_widget)
        self.label_cpu.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_cpu.setStyleSheet("color: white;")
        layout.addWidget(self.label_cpu)

        self.progress_bar_cpu = QProgressBar(self.central_widget)
        self.progress_bar_cpu.setRange(0, 100)
        self.progress_bar_cpu.setTextVisible(True)  # Show text
        layout.addWidget(self.progress_bar_cpu)

        # GPU
        self.label_gpu = QLabel(self.central_widget)
        self.label_gpu.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_gpu.setStyleSheet("color: white;")
        layout.addWidget(self.label_gpu)

        self.progress_bar_gpu = QProgressBar(self.central_widget)
        self.progress_bar_gpu.setRange(0, 100)
        self.progress_bar_gpu.setTextVisible(True)  # Show text
        layout.addWidget(self.progress_bar_gpu)

        # Memory
        self.label_mem = QLabel(self.central_widget)
        self.label_mem.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_mem.setStyleSheet("color: white;")
        layout.addWidget(self.label_mem)

        self.progress_bar_mem = QProgressBar(self.central_widget)
        self.progress_bar_mem.setRange(0, 100)
        self.progress_bar_mem.setTextVisible(True)  # Show text
        layout.addWidget(self.progress_bar_mem)

        # Disk
        self.disk_labels = []
        self.disk_progress_bars = []

        for partition in psutil.disk_partitions():
            # Check if the disk exists and is readable
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                label = QLabel(self.central_widget)
                label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                label.setStyleSheet("color: white;")
                self.disk_labels.append(label)
                layout.addWidget(label)

                progress_bar = QProgressBar(self.central_widget)
                progress_bar.setRange(0, 100)
                progress_bar.setTextVisible(True)  # Show text
                layout.addWidget(progress_bar)
                self.disk_progress_bars.append(progress_bar)

    def initTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateSystemInfo)
        self.timer.start(1000)

    def updateSystemInfo(self):
        # Network upload and download data
        network = psutil.net_io_counters()
        upload = network.bytes_sent / 1024 / 1024  # MB
        download = network.bytes_recv / 1024 / 1024  # MB
        self.label_network.setText(f"Net: ↑ {upload:.2f}MB/s ↓ {download:.2f}MB/s")

        # CPU usage
        cpu_usage = psutil.cpu_percent()
        self.label_cpu.setText(f"CPU: {cpu_usage:.1f}%")
        self.progress_bar_cpu.setValue(int(cpu_usage))

        # Set the progress bar width to match the label background width
        label_width = self.label_cpu.width()
        self.progress_bar_cpu.setFixedWidth(label_width)

        # GPU usage and temperature
        gpu_info = GPUtil.getGPUs()[0]
        gpu_usage = gpu_info.load * 100
        gpu_temp = gpu_info.temperature
        self.label_gpu.setText(f"GPU: {gpu_usage:.1f}% - Temp: {gpu_temp}°C")
        self.progress_bar_gpu.setValue(int(gpu_usage))

        # Memory usage and used memory
        mem = psutil.virtual_memory()
        mem_usage = mem.percent
        mem_used_gb = mem.used / 1024 / 1024 / 1024  # GB
        mem_total_gb = mem.total / 1024 / 1024 / 1024  # GB
        self.label_mem.setText(f"Mem: {mem_usage:.1f}% - {mem_used_gb:.1f}GB / {mem_total_gb:.1f}GB")
        self.progress_bar_mem.setValue(int(mem_usage))

        # Update disk usage
        for index, partition in enumerate(psutil.disk_partitions()):
            # Check if the disk exists and is readable
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                disk_usage = psutil.disk_usage(partition.mountpoint)
                disk_usage_percent = disk_usage.percent
                disk_total_gb = disk_usage.total / (1024 ** 3)  # GB
                disk_used_gb = disk_usage.used / (1024 ** 3)  # GB
                self.disk_labels[index].setText(f"Disk {index + 1}: {disk_usage_percent:.1f}% - {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB")
                self.disk_progress_bars[index].setValue(int(disk_usage_percent))
                
    def setGeometryToBottom(self):
        desktop = QDesktopWidget()
        screen = desktop.availableGeometry(self)  # Use self as a parameter to ensure the window is not obscured by other windows
        window_height = self.height()
        self.setGeometry(screen.width() - self.width(), screen.height() - window_height, self.width(), window_height)

def main():
    global app  # Make app a global variable for access in quit_action
    app = QApplication(sys.argv)
    monitor = SystemMonitor()
    monitor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
