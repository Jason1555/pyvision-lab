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

        self.setObjectName("exifDialog")
        self.setWindowTitle("Информация EXIF")
        self.setMinimumSize(520, 560)
        self.resize(560, 620)

        self.title_label = QLabel("ДАННЫЕ EXIF")
        self.title_label.setObjectName("exifTitle")

        self.count_label = QLabel("")
        self.count_label.setObjectName("exifCount")
        self.count_label.setWordWrap(True)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.count_label)

        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
        )
        self.form_layout.setHorizontalSpacing(14)
        self.form_layout.setVerticalSpacing(3)

        content_widget = QWidget()
        content_widget.setObjectName("exifContent")
        content_widget.setLayout(self.form_layout)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("exifScroll")
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        # Кнопка "Копировать всё" — удобно для отчёта по лабе.
        copy_button = QPushButton("Копировать всё")
        copy_button.setObjectName("exifCopyButton")
        copy_button.clicked.connect(self._copy_to_clipboard)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.addWidget(copy_button)
        footer_layout.addStretch()
        footer_layout.addWidget(button_box)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addWidget(scroll_area, stretch=1)
        layout.addLayout(footer_layout)

        self.setLayout(layout)

        self._last_text = ""

    def set_exif_data(self, exif_data: dict[str, str]):
        self.clear_fields()

        if not exif_data:
            self.count_label.setText("В этом файле нет данных EXIF")
            empty_label = QLabel()
            empty_label.setObjectName("exifEmpty")
            empty_label.setWordWrap(True)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.form_layout.addRow(empty_label)
            self._last_text = "Нет данных EXIF"
            return

        ordered = {}
        for tag in self.PRIORITY_TAGS:
            if tag in exif_data:
                ordered[tag] = exif_data[tag]
        for name, value in exif_data.items():
            if name not in ordered:
                ordered[name] = value

        key_count = sum(1 for tag in self.PRIORITY_TAGS if tag in exif_data)
        self.count_label.setText(
            f"Найдено тегов: {len(ordered)} · ключевых: {key_count}"
        )

        lines = []
        # Разделитель «ключевые / остальные», чтобы ТЗ-пункты
        # были видны сразу, а не терялись в простыне тегов.
        key_names = [t for t in self.PRIORITY_TAGS if t in ordered]
        other_names = [n for n in ordered if n not in key_names]

        if key_names and other_names:
            self._add_section("КЛЮЧЕВЫЕ ТЕГИ")
            for name in key_names:
                lines.append(self._add_row(name, ordered[name]))
            self._add_section("ВСЕ ТЕГИ")
            for name in other_names:
                lines.append(self._add_row(name, ordered[name]))
        else:
            for name, value in ordered.items():
                lines.append(self._add_row(name, value))

        self._last_text = "\n".join(lines)

    def _add_section(self, text: str):
        section = QLabel(text)
        section.setObjectName("exifSection")
        self.form_layout.addRow(section)

    def _add_row(self, name: str, value: str) -> str:
        name_label = QLabel(f"{name}")
        name_label.setObjectName("exifKey")

        value_label = QLabel(value)
        value_label.setObjectName(
            "exifValueKey" if name in self.PRIORITY_TAGS else "exifValue"
        )
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.form_layout.addRow(name_label, value_label)
        return f"{name}: {value}"

    def _copy_to_clipboard(self):
        QApplication.clipboard().setText(self._last_text)

    def clear_fields(self):
        self.count_label.setText("")
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)
