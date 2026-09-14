from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

class ExifDialog(QDialog):
    def __init__(self, exif_data=None, parent=None):
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
                QLabel("Exif data:"),
                QLabel("No Exif data avaliable")
            )
            return

        for name, value in exif_data.items():
            self.form_layout.addRow(
                QLabel(f"{name}:"),
                QLabel(value)
            )

    def clear_fields(self):
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)
