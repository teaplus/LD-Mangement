from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import QTimer
import psutil

class ResourceMonitor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update mỗi giây
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # CPU Usage
        self.cpu_label = QLabel('CPU Usage:')
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        
        # Memory Usage
        self.mem_label = QLabel('Memory Usage:')
        self.mem_bar = QProgressBar()
        self.mem_bar.setRange(0, 100)
        
        # Disk Usage
        self.disk_label = QLabel('Disk Usage:')
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        
        # Add widgets to layout
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)
        layout.addWidget(self.mem_label)
        layout.addWidget(self.mem_bar)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.disk_bar)
        
    def update_stats(self):
        # CPU
        cpu_percent = psutil.cpu_percent()
        self.cpu_label.setText(f'CPU Usage: {cpu_percent}%')
        self.cpu_bar.setValue(int(cpu_percent))
        
        # Memory
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        self.mem_label.setText(f'Memory Usage: {mem_percent}% ({self.format_bytes(mem.used)}/{self.format_bytes(mem.total)})')
        self.mem_bar.setValue(int(mem_percent))
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        self.disk_label.setText(f'Disk Usage: {disk_percent}% ({self.format_bytes(disk.used)}/{self.format_bytes(disk.total)})')
        self.disk_bar.setValue(int(disk_percent))
        
    def format_bytes(self, bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.1f}{unit}"
            bytes /= 1024