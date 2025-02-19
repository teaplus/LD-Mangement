from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                            QLineEdit, QSpinBox, QPushButton, QHBoxLayout)

class CreateInstanceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Create New Instance')
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        form_layout.addRow('Name:', self.name_edit)

        self.cpu_spin = QSpinBox()
        self.cpu_spin.setRange(1, 4)
        self.cpu_spin.setValue(2)
        form_layout.addRow('CPU Cores:', self.cpu_spin)

        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(1024, 4096)
        self.memory_spin.setSingleStep(1024)
        self.memory_spin.setValue(2048)
        form_layout.addRow('Memory (MB):', self.memory_spin)

        layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        
        ok_button = QPushButton('Create')
        ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)

    def get_data(self):
        name = self.name_edit.text()
        properties = {
            'cpu': self.cpu_spin.value(),
            'memory': self.memory_spin.value()
        }
        return name, properties  # Return tuple of name and properties
    
    def show_create_dialog(self):
        dialog = CreateInstanceDialog(self)
        if dialog.exec():
            try:
                name, properties = dialog.get_data()  # Unpack the tuple
                if name:  # Check if name is not empty
                    self.ld_manager.create_instance(name, properties)
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, 'Warning', 'Please enter a name for the instance')
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))