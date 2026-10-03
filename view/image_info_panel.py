from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import *

class ImageInfoPanel(QFrame):
    exif_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.title_label = QLabel("ИНФОРМАЦИЯ ОБ ИЗОБРАЖЕНИИ")
        self.file_size_label = QLabel("—")
        self.resolution_label = QLabel("—")
        self.color_depth_label = QLabel("—")
        self.format_label = QLabel("—")
        self.color_model_label = QLabel("—")
        self.extra_label = QLabel("—")
        self.extra_label.setWordWrap(True)

        self.exif_button = QPushButton("EXIF")

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        form_layout.addRow("Размер:", self.file_size_label)
        form_layout.addRow("Разрешение:", self.resolution_label)
        form_layout.addRow("Глубина цвета:", self.color_depth_label)
        form_layout.addRow("Формат:", self.format_label)
        form_layout.addRow("Цветовая модель:", self.color_model_label)
        form_layout.addRow("Дополнительно:", self.extra_label)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addLayout(form_layout)
        layout.addWidget(self.exif_button)
        layout.addStretch()

        self.setLayout(layout)

        self.exif_button.clicked.connect(self.exif_clicked.emit)

    def set_image_info(self, file_size: int, resolution: tuple[int, int], color_depth, file_format: str, color_model: str, extra_info: dict[str, str] | None = None):
        self.file_size_label.setText(self._format_file_size(file_size))

        width, height = resolution

        self.resolution_label.setText(f"{width} x {height} пкс")

        self.color_depth_label.setText(f"{color_depth} бит/пиксель")

        self.format_label.setText(str(file_format))

        self.color_model_label.setText(color_model)

        if extra_info:
            lines = [f"{key}: {value}" for key, value in extra_info.items()]
            self.extra_label.setText("\n".join(lines))
        else:
            self.extra_label.setText("—")

    def clear(self):
        self.file_size_label.setText("—")
        self.resolution_label.setText("—")
        self.color_depth_label.setText("—")
        self.format_label.setText("—")
        self.color_model_label.setText("—")
        self.extra_label.setText("—")

    @staticmethod
    def _format_file_size(size: int) -> str:
        if size < 1024:
            return f"{size} B"

        if size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"

        if size < 1024 ** 3:
            return f"{size / 1024 ** 2:.2f} MB"

        return f"{size / 1024 ** 3:.2f} GB"
