from PyQt6.QtCore import pyqtSignal
from view.tools.adjustment_tool import AdjustmentTool


class ContrastTool(AdjustmentTool):
    contrast_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__("Contrast", parent)

        self.value_changed.connect(
            self.contrast_changed.emit
        )