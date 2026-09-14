from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

from view.tools.grayscale_tool import GrayscaleTool
from view.tools.brightness_tool import BrightnessTool

class ToolPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("toolPanel")

        self.grayscale_tool = GrayscaleTool()
        self.brightness_tool = BrightnessTool()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(self.grayscale_tool)
        layout.addWidget(self.brightness_tool)

        layout.addStretch()

        self.setLayout(layout)

    def set_tools_enabled(self, enabled:bool):
        self.grayscale_tool.setEnabled(enabled)
        self.brightness_tool.setEnabled(enabled)