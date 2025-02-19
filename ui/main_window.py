from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QTableWidget, QTableWidgetItem, QMessageBox)
from PySide6.QtCore import Qt
from core.ld_manager import LDPlayerManager
from .dialogs.create_instance import CreateInstanceDialog
from utils.logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ld_manager = LDPlayerManager()
        self.init_ui()

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

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Name', 'Status', 'CPU', 'Memory', 'Actions'])
        layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(0)
        for device in self.ld_manager.devices.values():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(device.name))
            self.table.setItem(row, 1, QTableWidgetItem(device.status))
            self.table.setItem(row, 2, QTableWidgetItem(str(device.properties.get('cpu', '-'))))
            self.table.setItem(row, 3, QTableWidgetItem(str(device.properties.get('memory', '-'))))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            
            start_btn = QPushButton('▶')
            start_btn.clicked.connect(lambda checked, name=device.name: self.start_instance(name))
            
            stop_btn = QPushButton('⏹')
            stop_btn.clicked.connect(lambda checked, name=device.name: self.stop_instance(name))
            
            actions_layout.addWidget(start_btn)
            actions_layout.addWidget(stop_btn)
            
            self.table.setCellWidget(row, 4, actions_widget)

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