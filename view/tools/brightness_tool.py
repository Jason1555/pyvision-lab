from PyQt6.QtCore import pyqtSignal
from view.tools.adjustment_tool import AdjustmentTool

class BrightnessTool(AdjustmentTool):
    brightness_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__("Яркость", parent)

        self.value_changed.connect(
            self.brightness_changed.emit
        )