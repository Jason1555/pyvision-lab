from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QPushButton

class GrayscaleTool(QPushButton):
    grayscale_clicked = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__("Grayscale", parent)

        self.setObjectName("grayscaleTool")
        self.setCheckable(True)

        self.clicked.connect(
            self.grayscale_clicked.emit
        )