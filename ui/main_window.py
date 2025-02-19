from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                            QProgressBar)
from PySide6.QtCore import Qt, QTimer
from core.ld_manager import LDPlayerManager
from .dialogs.create_instance import CreateInstanceDialog
from utils.logger import logger
from .widgets.resource_monitor import ResourceMonitor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ld_manager = LDPlayerManager()
        self.init_ui()
        
        # Timer để cập nhật tài nguyên
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_resources)
        self.update_timer.start(2000)  # Cập nhật mỗi 2 giây

    def init_ui(self):
        self.setWindowTitle('LDPlayer Manager')
        self.setMinimumSize(800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_btn = QPushButton('Create Instance')
        self.create_btn.clicked.connect(self.show_create_dialog)
        
        self.start_btn = QPushButton('Start')
        self.start_btn.clicked.connect(self.start_selected)
        
        self.stop_btn = QPushButton('Stop')
        self.stop_btn.clicked.connect(self.stop_selected)
        
        self.install_btn = QPushButton('Install App')
        self.install_btn.clicked.connect(self.install_app)

        for btn in [self.create_btn, self.start_btn, self.stop_btn, self.install_btn]:
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # Add resource monitor
        self.resource_monitor = ResourceMonitor()
        layout.addWidget(self.resource_monitor)
        
        # Add stretch to push resource monitor to top
        layout.addStretch()

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # Thêm cột cho CPU, Memory, Threads
        self.table.setHorizontalHeaderLabels([
            'Name', 'Status', 'CPU %', 'Memory (MB)', 
            'Threads', 'Actions', 'Resource Graph'
        ])
        layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(0)
        for device in self.ld_manager.devices.values():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Basic info
            self.table.setItem(row, 0, QTableWidgetItem(device.name))
            self.table.setItem(row, 1, QTableWidgetItem(device.status))
            
            # Resource columns
            for i in range(2, 5):
                self.table.setItem(row, i, QTableWidgetItem('0'))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            
            start_btn = QPushButton('▶')
            start_btn.clicked.connect(lambda checked, name=device.name: self.start_instance(name))
            
            stop_btn = QPushButton('⏹')
            stop_btn.clicked.connect(lambda checked, name=device.name: self.stop_instance(name))
            
            actions_layout.addWidget(start_btn)
            actions_layout.addWidget(stop_btn)
            
            self.table.setCellWidget(row, 5, actions_widget)
            
            # Resource graph
            graph_widget = QWidget()
            graph_layout = QVBoxLayout(graph_widget)
            
            cpu_bar = QProgressBar()
            cpu_bar.setRange(0, 100)
            cpu_bar.setTextVisible(True)
            
            mem_bar = QProgressBar()
            mem_bar.setRange(0, 1024)  # Max 1GB
            mem_bar.setTextVisible(True)
            
            graph_layout.addWidget(cpu_bar)
            graph_layout.addWidget(mem_bar)
            
            self.table.setCellWidget(row, 6, graph_widget)

    def show_create_dialog(self):
        dialog = CreateInstanceDialog(self)
        if dialog.exec():
            name, properties = dialog.get_data()
            try:
                self.ld_manager.create_instance(name, properties)
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def start_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        name = self.table.item(row, 0).text()
        try:
            self.ld_manager.start_instance(name)
            self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def stop_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        name = self.table.item(row, 0).text()
        try:
            self.ld_manager.stop_instance(name)
            self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def install_app(self):
        from PyQt6.QtWidgets import QFileDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select APK",
            "",
            "Android Package (*.apk)"
        )
        
        if file_name:
            selected = self.table.selectedItems()
            if not selected:
                return
                
            row = selected[0].row()
            name = self.table.item(row, 0).text()
            try:
                self.ld_manager.install_app(name, file_name)
                QMessageBox.information(self, 'Success', 'App installed successfully')
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def update_resources(self):
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            resources = self.ld_manager.get_instance_resources(name)
            
            # Update text values
            self.table.item(row, 2).setText(f"{resources['cpu']:.1f}")
            self.table.item(row, 3).setText(f"{resources['memory']:.1f}")
            self.table.item(row, 4).setText(str(resources['threads']))
            
            # Update progress bars
            graph_widget = self.table.cellWidget(row, 6)
            if graph_widget:
                cpu_bar = graph_widget.layout().itemAt(0).widget()
                mem_bar = graph_widget.layout().itemAt(1).widget()
                
                cpu_bar.setValue(int(resources['cpu']))
                cpu_bar.setFormat(f"{resources['cpu']:.1f}%")
                
                mem_bar.setValue(int(resources['memory']))
                mem_bar.setFormat(f"{resources['memory']:.1f} MB")