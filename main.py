import sys
import os

# Ensure the root directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow
from app.controller import Controller

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    controller = Controller(main_window) # Instantiate controller
    main_window.show()
    sys.exit(app.exec())

