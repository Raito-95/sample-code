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
        self.initTimers()
        self.setGeometryToBottom()

    def initUI(self):
        self.setWindowTitle("System Monitor")
        self.setGeometry(0, 0, 200, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")

    def initSystemTray(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_path, 'test.png')
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icon_path))

        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Quit", self)
        
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(app.quit)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def initWidgets(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.initNetworkWidget()
        self.initCPUWidget()
        self.initGPUWidget()
        self.initMemoryWidget()
        self.initDiskWidgets()

    def initNetworkWidget(self):
        self.label_network = self.createLabel()
        self.layout.addWidget(self.label_network)

    def initCPUWidget(self):
        self.label_cpu, self.progress_bar_cpu = self.createLabelProgressBar()
        self.layout.addWidget(self.label_cpu)
        self.layout.addWidget(self.progress_bar_cpu)

    def initGPUWidget(self):
        self.label_gpu, self.progress_bar_gpu = self.createLabelProgressBar()
        self.layout.addWidget(self.label_gpu)
        self.layout.addWidget(self.progress_bar_gpu)

    def initMemoryWidget(self):
        self.label_mem, self.progress_bar_mem = self.createLabelProgressBar()
        self.layout.addWidget(self.label_mem)
        self.layout.addWidget(self.progress_bar_mem)

    def initDiskWidgets(self):
        self.disk_labels = []
        self.disk_progress_bars = []
        for partition in psutil.disk_partitions():
            if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                label, progress_bar = self.createLabelProgressBar()
                self.disk_labels.append(label)
                self.disk_progress_bars.append(progress_bar)
                self.layout.addWidget(label)
                self.layout.addWidget(progress_bar)

    def createLabel(self):
        label = QLabel(self.central_widget)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setStyleSheet("color: white; background-color: transparent;")
        return label

    def createLabelProgressBar(self):
        label = QLabel(self.central_widget)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setStyleSheet("color: white; background-color: transparent;")

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
                margin: 0px; /* Ensure chunk fills the entire progress bar */
            }
        """)
        return label, progress_bar

    def initTimers(self):
        self.network_timer = QTimer(self)
        self.network_timer.timeout.connect(self.updateNetworkInfo)
        self.network_timer.start(3000)

        self.cpu_timer = QTimer(self)
        self.cpu_timer.timeout.connect(self.updateCPUInfo)
        self.cpu_timer.start(1000)

        self.gpu_timer = QTimer(self)
        self.gpu_timer.timeout.connect(self.updateGPUInfo)
        self.gpu_timer.start(4000)

        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self.updateMemoryInfo)
        self.memory_timer.start(2000)

        self.disk_timer = QTimer(self)
        self.disk_timer.timeout.connect(self.updateDiskInfo)
        self.disk_timer.start(5000)

    def updateNetworkInfo(self):
        try:
            network = psutil.net_io_counters()
            upload = network.bytes_sent / 1024 / 1024
            download = network.bytes_recv / 1024 / 1024
            self.label_network.setText(f"Net: ↑ {upload:.2f}MB/s ↓ {download:.2f}MB/s")
        except Exception as e:
            self.label_network.setText("Network information unavailable")
            # print(f"Error updating network info: {e}")

    def updateCPUInfo(self):
        try:
            cpu_usage = psutil.cpu_percent()
            self.label_cpu.setText(f"CPU: {cpu_usage:.1f}%")
            self.progress_bar_cpu.setValue(int(cpu_usage))
        except Exception as e:
            self.label_cpu.setText("CPU information unavailable")
            # print(f"Error updating CPU info: {e}")

    def updateGPUInfo(self):
        try:
            gpu_info = GPUtil.getGPUs()[0] if GPUtil.getGPUs() else None
            if gpu_info:
                gpu_usage = gpu_info.load * 100
                gpu_temp = gpu_info.temperature
                self.label_gpu.setText(f"GPU: {gpu_usage:.1f}% - Temp: {gpu_temp}°C")
                self.progress_bar_gpu.setValue(int(gpu_usage))
            else:
                self.label_gpu.setText("GPU information unavailable")
        except Exception as e:
            self.label_gpu.setText("GPU information unavailable")
            # print(f"Error updating GPU info: {e}")

    def updateMemoryInfo(self):
        try:
            mem = psutil.virtual_memory()
            mem_usage = mem.percent
            mem_used_gb = mem.used / 1024 / 1024 / 1024
            mem_total_gb = mem.total / 1024 / 1024 / 1024
            self.label_mem.setText(f"Mem: {mem_usage:.1f}% - {mem_used_gb:.1f}GB / {mem_total_gb:.1f}GB")
            self.progress_bar_mem.setValue(int(mem_usage))
        except Exception as e:
            self.label_mem.setText("Memory information unavailable")
            # print(f"Error updating memory info: {e}")

    def updateDiskInfo(self):
        try:
            for index, partition in enumerate(psutil.disk_partitions()):
                if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.R_OK):
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage_percent = disk_usage.percent
                    disk_total_gb = disk_usage.total / (1024 ** 3)
                    disk_used_gb = disk_usage.used / (1024 ** 3)
                    self.disk_labels[index].setText(f"Disk {index + 1}: {disk_usage_percent:.1f}% - {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB")
                    self.disk_progress_bars[index].setValue(int(disk_usage_percent))
        except Exception as e:
            for label in self.disk_labels:
                label.setText("Disk information unavailable")
            # print(f"Error updating disk info: {e}")

    def setGeometryToBottom(self):
        desktop = QDesktopWidget()
        screen = desktop.availableGeometry(self)
        window_height = self.height()
        self.setGeometry(screen.width() - self.width(), screen.height() - window_height, self.width(), window_height)

def main():
    global app
    app = QApplication(sys.argv)
    monitor = SystemMonitor()
    monitor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
