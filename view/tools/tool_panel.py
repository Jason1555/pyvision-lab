from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

from view.tools.grayscale_tool import GrayscaleTool
from view.tools.brightness_tool import BrightnessTool
from view.tools.contrast_tool import ContrastTool
from view.tools.saturation_tool import SaturationTool

class ToolPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("toolPanel")

        self.grayscale_tool = GrayscaleTool()
        self.brightness_tool = BrightnessTool()
        self.contrast_tool = ContrastTool()
        self.saturation_tool = SaturationTool()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(self.grayscale_tool)
        layout.addWidget(self.brightness_tool)
        layout.addWidget(self.contrast_tool)
        layout.addWidget(self.saturation_tool)

        layout.addStretch()

        self.setLayout(layout)

    def set_tools_enabled(self, enabled:bool):
        self.grayscale_tool.setEnabled(enabled)
        self.brightness_tool.setEnabled(enabled)

    def reset(self):
        self.grayscale_tool.blockSignals(True)
        self.brightness_tool.blockSignals(True)
        self.contrast_tool.blockSignals(True)
        self.saturation_tool.blockSignals(True)

        self.grayscale_tool.setChecked(False)
        self.brightness_tool.reset()
        self.contrast_tool.reset()
        self.saturation_tool.reset()

        self.grayscale_tool.blockSignals(False)
        self.brightness_tool.blockSignals(False)
        self.contrast_tool.blockSignals(False)
        self.saturation_tool.blockSignals(False)
