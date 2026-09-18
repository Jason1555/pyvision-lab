from PyQt6.QtCore import pyqtSignal
from view.tools.adjustment_tool import AdjustmentTool

class GammaTool(AdjustmentTool):
    gamma_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(
            "Gamma",
            parent,
            minimum=10,
            maximum=300,
            default_value=100,
            scale=100,
            decimals=2,
        )

        self.value_changed.connect(
            self._on_gamma_changed
        )

    def _on_gamma_changed(self, value: int):
        self.gamma_changed.emit(value / self.scale)
