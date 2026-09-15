from PyQt6.QtCore import pyqtSignal
from view.tools.adjustment_tool import AdjustmentTool


class SaturationTool(AdjustmentTool):
    saturation_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__("Saturation", parent)

        self.value_changed.connect(
            self.saturation_changed.emit
        )