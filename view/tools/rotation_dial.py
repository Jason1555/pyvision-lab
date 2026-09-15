from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import *

class RotationDial(QWidget):
    rotation_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dial = QDial()
        self.dial.setRange(-180, 180)
        self.dial.setValue(0)

        self.dial.setSingleStep(1)
        self.dial.setPageStep(15)
        self.dial.setNotchesVisible(True)

        self.value_label = QLabel("0°")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        layout.addWidget(self.dial)
        layout.addWidget(self.value_label)

        self.dial.valueChanged.connect(self._on_value_changed)

    def _on_value_changed(self, value: int):
        self.value_label.setText(f"{value}°")
        self.rotation_changed.emit(float(value))

    def reset(self):
        self.dial.setValue(0)

    def set_enabled(self, enabled: bool):
        self.dial.setEnabled(enabled)

    def set_rotation(self, value: float):
        value = int(value)

        self.dial.blockSignals(True)
        self.dial.setValue(value)
        self.dial.blockSignals(False)

        self.value_label.setText(f"{value}°")
