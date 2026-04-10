"""主窗口"""

from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("黑夜君临遗物助手 v0.1.0")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
