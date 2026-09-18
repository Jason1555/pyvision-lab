from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal

from view.tools.grayscale_tool import GrayscaleTool
from view.tools.brightness_tool import BrightnessTool
from view.tools.contrast_tool import ContrastTool
from view.tools.saturation_tool import SaturationTool
from view.tools.gamma_tool import GammaTool
from view.tools.rotation_dial import RotationDial


class ToolPanel(QWidget):
    rotate_left_clicked = pyqtSignal()
    rotate_right_clicked = pyqtSignal()
    rotate_reset_clicked = pyqtSignal()

    linear_correction_changed = pyqtSignal(bool)
    gamma_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("toolPanel")

        self.grayscale_tool = GrayscaleTool()
        self.brightness_tool = BrightnessTool()
        self.contrast_tool = ContrastTool()
        self.saturation_tool = SaturationTool()
        self.gamma_tool = GammaTool()
        self.rotation_dial = RotationDial()

        self.linear_correction_button = QPushButton(
            "Линейная коррекция"
        )
        self.linear_correction_button.setCheckable(True)

        self.rotate_left_button = QPushButton("↶")
        self.rotate_left_button.setToolTip(
            "Повернуть на 90° против часовой стрелки"
        )

        self.rotate_reset_button = QPushButton("0°")
        self.rotate_reset_button.setToolTip(
            "Сбросить поворот"
        )

        self.rotate_right_button = QPushButton("↷")
        self.rotate_right_button.setToolTip(
            "Повернуть на 90° по часовой стрелке"
        )

        # Rotation
        self.rotate_left_button.clicked.connect(
            self.rotate_left_clicked.emit
        )

        self.rotate_right_button.clicked.connect(
            self.rotate_right_clicked.emit
        )

        self.rotate_reset_button.clicked.connect(
            self.rotate_reset_clicked.emit
        )

        # Linear correction
        self.linear_correction_button.toggled.connect(
            self.linear_correction_changed.emit
        )

        # Gamma
        self.gamma_tool.gamma_changed.connect(
            self.gamma_changed.emit
        )

        rotation_buttons_layout = QHBoxLayout()
        rotation_buttons_layout.addWidget(
            self.rotate_left_button
        )
        rotation_buttons_layout.addWidget(
            self.rotate_reset_button
        )
        rotation_buttons_layout.addWidget(
            self.rotate_right_button
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(self.grayscale_tool)
        layout.addWidget(self.brightness_tool)
        layout.addWidget(self.contrast_tool)
        layout.addWidget(self.saturation_tool)
        layout.addWidget(self.gamma_tool)
        layout.addWidget(self.rotation_dial)
        layout.addLayout(rotation_buttons_layout)
        layout.addWidget(
            self.linear_correction_button
        )

        layout.addStretch()

        self.setLayout(layout)

    def set_tools_enabled(self, enabled: bool):
        self.grayscale_tool.setEnabled(enabled)
        self.brightness_tool.setEnabled(enabled)
        self.contrast_tool.setEnabled(enabled)
        self.saturation_tool.setEnabled(enabled)
        self.gamma_tool.setEnabled(enabled)
        self.rotation_dial.set_enabled(enabled)

        self.linear_correction_button.setEnabled(enabled)

        self.rotate_left_button.setEnabled(enabled)
        self.rotate_reset_button.setEnabled(enabled)
        self.rotate_right_button.setEnabled(enabled)

    def reset(self):
        self.grayscale_tool.blockSignals(True)
        self.brightness_tool.blockSignals(True)
        self.contrast_tool.blockSignals(True)
        self.saturation_tool.blockSignals(True)
        self.gamma_tool.blockSignals(True)
        self.rotation_dial.blockSignals(True)

        self.grayscale_tool.setChecked(False)
        self.brightness_tool.reset()
        self.contrast_tool.reset()
        self.saturation_tool.reset()
        self.gamma_tool.reset()
        self.rotation_dial.reset()

        self.grayscale_tool.blockSignals(False)
        self.brightness_tool.blockSignals(False)
        self.contrast_tool.blockSignals(False)
        self.saturation_tool.blockSignals(False)
        self.gamma_tool.blockSignals(False)
        self.rotation_dial.blockSignals(False)

        self.linear_correction_button.blockSignals(True)
        self.linear_correction_button.setChecked(False)
        self.linear_correction_button.blockSignals(False)
