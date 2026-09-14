from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import *

class ImageInfoPanel(QFrame):
    exif_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.title_label = QLabel("IMAGE INFO")
        self.file_size_label = QLabel("—")
        self.resolution_label = QLabel("—")
        self.color_depth_label = QLabel("—")
        self.format_label = QLabel("—")
        self.color_model_label = QLabel("—")

        self.exif_button = QPushButton("EXIF")

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        form_layout.addRow("Size:", self.file_size_label)
        form_layout.addRow("Resolution:", self.resolution_label)
        form_layout.addRow("Color depth:", self.color_depth_label)
        form_layout.addRow("Format:", self.format_label)
        form_layout.addRow("Color model:", self.color_model_label)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addLayout(form_layout)
        layout.addWidget(self.exif_button)
        layout.addStretch()

        self.setLayout(layout)

        self.exif_button.clicked.connect(self.exif_clicked.emit)

    def set_image_info(self, file_size: int, resolution: tuple[int, int], color_depth: int, file_format: str, color_model: str):
        self.file_size_label.setText(self._format_file_size(file_size))

        width, height = resolution

        self.resolution_label.setText(f"{width} x {height} px")

        self.color_depth_label.setText(f"{color_depth} bit/pixel")

        self.format_label.setText(file_format)

        self.color_model_label.setText(color_model)

    def clear(self):
        self.file_size_label.setText("—")
        self.resolution_label.setText("—")
        self.color_depth_label.setText("—")
        self.format_label.setText("—")
        self.color_model_label.setText("—")

    @staticmethod
    def _format_file_size(size: int) -> str:
        if size < 1024:
            return f"{size} B"

        if size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"

        if size < 1024 ** 3:
            return f"{size / 1024 ** 2:.2f} MB"

        return f"{size / 1024 ** 3:.2f} GB"
