from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import *

class AdjustmentTool(QWidget):
    value_changed = pyqtSignal(int)

    def __init__(
        self,
        name: str,
        parent=None,
        minimum: int = -100,
        maximum: int = 100,
        default_value: int = 0,
        scale: float = 1.0,
        decimals: int = 0,
    ):
        super().__init__(parent)

        self.setObjectName("adjustmentTool")

        self.scale = scale
        self.decimals = decimals
        self.default_value = default_value

        self.label = QLabel(name)
        self.label.setFixedWidth(80)

        self.slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(default_value)

        self.value_label = QLabel()
        self.value_label.setFixedWidth(40)
        self.value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(self.label)
        layout.addWidget(self.slider, stretch=1)
        layout.addWidget(self.value_label)

        self.setLayout(layout)

        self.slider.valueChanged.connect(
            self._on_value_changed
        )

        self._on_value_changed(self.slider.value())

    def _on_value_changed(self, value: int):
        actual_value = value / self.scale

        if self.decimals == 0:
            self.value_label.setText(str(int(actual_value)))
        else:
            self.value_label.setText(
                f"{actual_value:.{self.decimals}f}"
            )

        self.value_changed.emit(value)

    def reset(self):
        self.slider.setValue(self.default_value)