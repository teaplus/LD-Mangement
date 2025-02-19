import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import logger

def main():
    try:
        app = QApplication(sys.argv)
        
        # Load styles
        with open('ui/resources/styles.qss', 'r') as f:
            app.setStyleSheet(f.read())
        
        window = MainWindow()
        window.show()
        
        return app.exec()

    except Exception as e:
        logger.error(f"Error in main: {e}")
        return 1

if __name__ == "__main__":
    exit(main())