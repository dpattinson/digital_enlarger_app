import sys
import os

# Add the app directory to sys.path for both bundled and unbundled execution
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    # noinspection PyUnresolvedReferences
    base_path = sys._MEIPASS
else:
    # Running in a regular Python environment
    base_path = os.path.dirname(__file__)

sys.path.insert(0, os.path.abspath(base_path))


from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow
from app.controller import Controller

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    controller = Controller(main_window) # Instantiate controller
    main_window.show()
    sys.exit(app.exec())

