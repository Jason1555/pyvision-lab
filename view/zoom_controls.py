from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import *

class ZoomControls(QWidget):
    zoom_in_clicked = pyqtSignal()
    zoom_out_clicked = pyqtSignal()
    fit_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("zoomControls")

        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.setObjectName("zoomOutButton")

        self.zoom_label = QPushButton("100%")
        self.zoom_label.setObjectName("zoomLabel")
        self.zoom_label.setCursor(Qt.CursorShape.PointingHandCursor)

        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setObjectName("zoomInButton")

        self.fit_button = QPushButton("Fit")
        self.fit_button.setObjectName("fitButton")

        layout = QHBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        layout.addWidget(self.zoom_out_button)
        layout.addWidget(self.zoom_label)
        layout.addWidget(self.zoom_in_button)
        layout.addWidget(self.fit_button)

        self.setLayout(layout)

        self.zoom_out_button.clicked.connect(self.zoom_out_clicked.emit)
        self.zoom_in_button.clicked.connect(self.zoom_in_clicked.emit)
        self.fit_button.clicked.connect(self.fit_clicked.emit)

    def set_zoom(self, percent: int) -> None:
        self.zoom_label.setText(f"{percent}%")
