from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QWidget,
)


class AdjustmentTool(QWidget):
    value_changed = pyqtSignal(int)

    def __init__(
        self,
        name: str,
        parent=None,
    ):
        super().__init__(parent)

        self.setObjectName("adjustmentTool")

        self.label = QLabel(name)
        self.label.setFixedWidth(80)

        self.slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.slider.setRange(-100, 100)
        self.slider.setValue(0)

        self.value_label = QLabel("0")
        self.value_label.setFixedWidth(32)
        self.value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(self.label)
        layout.addWidget(
            self.slider,
            stretch=1,
        )
        layout.addWidget(self.value_label)

        self.setLayout(layout)

        self.slider.valueChanged.connect(
            self._on_value_changed
        )

    def _on_value_changed(self, value: int):
        self.value_label.setText(str(value))
        self.value_changed.emit(value)

    def reset(self):
        self.slider.setValue(0)