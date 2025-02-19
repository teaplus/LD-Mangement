from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
import pyqtgraph as pg
from collections import deque
import numpy as np

class ResourceGraph(QWidget):
    def __init__(self, title, max_points=100, parent=None):
        super().__init__(parent)
        self.max_points = max_points
        self.data = deque(maxlen=max_points)
        self.time_data = deque(maxlen=max_points)
        self.init_ui(title)

    def init_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tạo plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle(title)
        self.plot_widget.showGrid(x=True, y=True)
        
        # Thiết lập style cho plot
        self.plot_widget.getAxis('left').setTextPen('k')
        self.plot_widget.getAxis('bottom').setTextPen('k')
        self.plot_widget.setLabel('left', 'Usage', units='%')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        
        # Tạo line plot
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='b', width=2))
        
        layout.addWidget(self.plot_widget)

    def update_data(self, value):
        self.data.append(value)
        self.time_data.append(len(self.time_data))
        
        # Cập nhật plot
        self.curve.setData(
            x=list(self.time_data), 
            y=list(self.data)
        )