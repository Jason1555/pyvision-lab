from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QPushButton

class GrayscaleTool(QPushButton):
    grayscale_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Grayscale", parent)

        self.setObjectName("grayscaleTool")

        self.clicked.connect(self.grayscale_clicked.emit)
