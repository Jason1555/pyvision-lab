from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSignal

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

        # -------------------------------------------------
        # Tools
        # -------------------------------------------------

        self.grayscale_tool = GrayscaleTool()
        self.grayscale_tool.setObjectName("grayscaleTool")

        self.brightness_tool = BrightnessTool()
        self.brightness_tool.setObjectName("brightnessTool")

        self.contrast_tool = ContrastTool()
        self.contrast_tool.setObjectName("contrastTool")

        self.saturation_tool = SaturationTool()
        self.saturation_tool.setObjectName("saturationTool")

        self.gamma_tool = GammaTool()
        self.gamma_tool.setObjectName("gammaTool")
        self.gamma_tool.setToolTip("Нелинейная (гамма) коррекция")

        self.rotation_dial = RotationDial()
        self.rotation_dial.setObjectName("rotationDial")

        # -------------------------------------------------
        # Linear correction
        # -------------------------------------------------

        self.linear_correction_button = QPushButton(
            "Linear correction (B/W)"
        )
        self.linear_correction_button.setObjectName(
            "linearCorrectionButton"
        )
        self.linear_correction_button.setCheckable(True)

        # -------------------------------------------------
        # Rotation buttons
        # -------------------------------------------------

        self.rotate_left_button = QPushButton("↶")
        self.rotate_left_button.setObjectName(
            "rotateLeftButton"
        )
        self.rotate_left_button.setToolTip(
            "Повернуть на 90° против часовой стрелки"
        )

        self.rotate_reset_button = QPushButton("0°")
        self.rotate_reset_button.setObjectName(
            "rotateResetButton"
        )
        self.rotate_reset_button.setToolTip(
            "Сбросить поворот"
        )

        self.rotate_right_button = QPushButton("↷")
        self.rotate_right_button.setObjectName(
            "rotateRightButton"
        )
        self.rotate_right_button.setToolTip(
            "Повернуть на 90° по часовой стрелке"
        )

        # -------------------------------------------------
        # Signals
        # -------------------------------------------------

        self.rotate_left_button.clicked.connect(
            self.rotate_left_clicked.emit
        )

        self.rotate_right_button.clicked.connect(
            self.rotate_right_clicked.emit
        )

        self.rotate_reset_button.clicked.connect(
            self.rotate_reset_clicked.emit
        )

        self.linear_correction_button.toggled.connect(
            self.linear_correction_changed.emit
        )

        self.gamma_tool.gamma_changed.connect(
            self.gamma_changed.emit
        )

        # -------------------------------------------------
        # Rotation controls
        # -------------------------------------------------

        rotation_buttons_layout = QHBoxLayout()
        rotation_buttons_layout.setContentsMargins(
            0, 0, 0, 0
        )
        rotation_buttons_layout.setSpacing(4)

        rotation_buttons_layout.addWidget(
            self.rotate_left_button
        )
        rotation_buttons_layout.addWidget(
            self.rotate_reset_button
        )
        rotation_buttons_layout.addWidget(
            self.rotate_right_button
        )

        # -------------------------------------------------
        # Main layout
        # -------------------------------------------------

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            12, 12, 12, 12
        )
        layout.setSpacing(0)

        # =================================================
        # Adjustments
        # =================================================

        adjustments_title = QLabel("ADJUSTMENTS")
        adjustments_title.setObjectName("sectionTitle")

        layout.addWidget(adjustments_title)
        layout.addSpacing(8)

        layout.addWidget(self.grayscale_tool)
        layout.addSpacing(6)

        layout.addWidget(self.brightness_tool)
        layout.addSpacing(6)

        layout.addWidget(self.contrast_tool)
        layout.addSpacing(6)

        layout.addWidget(self.saturation_tool)
        layout.addSpacing(6)

        layout.addWidget(self.gamma_tool)

        # =================================================
        # Transform
        # =================================================

        layout.addSpacing(18)

        transform_title = QLabel("TRANSFORM")
        transform_title.setObjectName("sectionTitle")

        layout.addWidget(transform_title)
        layout.addSpacing(8)

        rotation_container = QWidget()
        rotation_container.setObjectName(
            "rotationContainer"
        )

        rotation_layout = QVBoxLayout(
            rotation_container
        )
        rotation_layout.setContentsMargins(
            0, 0, 0, 0
        )
        rotation_layout.setSpacing(6)

        rotation_layout.addWidget(
            self.rotation_dial,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        rotation_layout.addLayout(
            rotation_buttons_layout
        )

        layout.addWidget(rotation_container)

        # =================================================
        # Correction
        # =================================================

        layout.addSpacing(18)

        correction_title = QLabel("CORRECTION")
        correction_title.setObjectName("sectionTitle")

        layout.addWidget(correction_title)
        layout.addSpacing(8)

        layout.addWidget(
            self.linear_correction_button
        )

        # Push everything to the top
        layout.addStretch()

    def set_tools_enabled(self, enabled: bool):
        self.grayscale_tool.setEnabled(enabled)
        self.brightness_tool.setEnabled(enabled)
        self.contrast_tool.setEnabled(enabled)
        self.saturation_tool.setEnabled(enabled)
        self.gamma_tool.setEnabled(enabled)

        self.rotation_dial.set_enabled(enabled)

        self.linear_correction_button.setEnabled(
            enabled
        )

        self.rotate_left_button.setEnabled(
            enabled
        )
        self.rotate_reset_button.setEnabled(
            enabled
        )
        self.rotate_right_button.setEnabled(
            enabled
        )

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

        self.linear_correction_button.blockSignals(
            True
        )
        self.linear_correction_button.setChecked(
            False
        )
        self.linear_correction_button.blockSignals(
            False
        )