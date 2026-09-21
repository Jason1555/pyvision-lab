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

        self.minimum = minimum
        self.maximum = maximum
        self.scale = scale
        self.decimals = decimals
        self.default_value = default_value

        # -------------------------------------------------
        # Label
        # -------------------------------------------------

        self.label = QLabel(name)
        self.label.setObjectName("toolLabel")
        self.label.setFixedWidth(78)

        # -------------------------------------------------
        # Slider
        # -------------------------------------------------

        self.slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.slider.setObjectName("toolSlider")

        self.slider.setRange(
            minimum,
            maximum
        )

        self.slider.setValue(
            default_value
        )

        # -------------------------------------------------
        # Value input
        # -------------------------------------------------

        self.value_input = QLineEdit()
        self.value_input.setObjectName(
            "toolValueInput"
        )

        self.value_input.setFixedWidth(44)

        self.value_input.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        # -------------------------------------------------
        # Reset button
        # -------------------------------------------------

        self.reset_button = QPushButton("↺")
        self.reset_button.setObjectName(
            "toolResetButton"
        )

        self.reset_button.setFixedSize(
            24,
            24
        )

        self.reset_button.setToolTip(
            f"Сбросить {name}"
        )

        # -------------------------------------------------
        # Layout
        # -------------------------------------------------

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(6)

        layout.addWidget(
            self.label
        )

        layout.addWidget(
            self.slider,
            stretch=1
        )

        layout.addWidget(
            self.value_input
        )

        layout.addWidget(
            self.reset_button
        )

        # -------------------------------------------------
        # Signals
        # -------------------------------------------------

        self.slider.valueChanged.connect(
            self._on_slider_changed
        )

        self.value_input.editingFinished.connect(
            self._on_input_finished
        )

        self.reset_button.clicked.connect(
            self.reset
        )

        # Initial value
        self._update_input(
            self.slider.value()
        )

    # =====================================================
    # Slider
    # =====================================================

    def _on_slider_changed(self, value: int):
        self._update_input(value)
        self.value_changed.emit(value)

    # =====================================================
    # Input
    # =====================================================

    def _on_input_finished(self):
        text = self.value_input.text().strip()

        try:
            actual_value = float(text)
        except ValueError:
            self._update_input(
                self.slider.value()
            )
            return

        slider_value = round(
            actual_value * self.scale
        )

        slider_value = max(
            self.minimum,
            min(
                self.maximum,
                slider_value
            )
        )

        self.slider.setValue(
            slider_value
        )

    # =====================================================
    # Formatting
    # =====================================================

    def _format_value(self, value: int) -> str:
        actual_value = value / self.scale

        if self.decimals == 0:
            return str(
                int(actual_value)
            )

        return (
            f"{actual_value:.{self.decimals}f}"
        )

    def _update_input(self, value: int):
        self.value_input.blockSignals(True)

        self.value_input.setText(
            self._format_value(value)
        )

        self.value_input.blockSignals(False)

    # =====================================================
    # Reset
    # =====================================================

    def reset(self):
        self.slider.setValue(
            self.default_value
        )
