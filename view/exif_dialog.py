from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

class ExifDialog(QDialog):
    # Ключевые поля, требуемые ТЗ (не менее 5 пунктов) — показываем первыми.
    PRIORITY_TAGS = [
        "Make",
        "Model",
        "DateTimeOriginal",
        "DateTime",
        "ExposureTime",
        "FNumber",
        "ISOSpeedRatings",
        "PhotographicSensitivity",
        "FocalLength",
        "ImageWidth",
        "ImageLength",
        "ExifImageWidth",
        "ExifImageHeight",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("EXIF Information")
        self.setMinimumSize(420, 500)

        self.form_layout = QFormLayout()

        content_widget = QWidget()
        content_widget.setLayout(self.form_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def set_exif_data(self, exif_data: dict[str, str]):
        self.clear_fields()

        if not exif_data:
            self.form_layout.addRow(
                QLabel("EXIF:"),
                QLabel("No EXIF data available for this file")
            )
            self.form_layout.addRow(
                QLabel("Hint:"),
                QLabel("Try a JPEG photo from a camera/phone (PNG/BMP usually have no EXIF)")
            )
            return

        ordered = {}
        for tag in self.PRIORITY_TAGS:
            if tag in exif_data:
                ordered[tag] = exif_data[tag]
        for name, value in exif_data.items():
            if name not in ordered:
                ordered[name] = value

        count_label = QLabel(f"Found {len(ordered)} tags (top: {min(len(ordered), len(self.PRIORITY_TAGS))} key tags first):")
        count_label.setWordWrap(True)
        self.form_layout.addRow(count_label)

        for name, value in ordered.items():
            name_label = QLabel(f"{name}:")
            value_label = QLabel(value)
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            self.form_layout.addRow(name_label, value_label)

    def clear_fields(self):
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)
