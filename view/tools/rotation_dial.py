from math import cos, radians, sin

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class RotationDialWidget(QDial):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setRange(-180, 180)
        self.setValue(0)

        self.setSingleStep(1)
        self.setPageStep(15)

        self.setNotchesVisible(False)

        self.setMinimumSize(108, 108)
        self.setMaximumSize(108, 108)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(
            6,
            6,
            self.width() - 12,
            self.height() - 12,
        )

        center = rect.center()

        radius = min(
            rect.width(),
            rect.height()
        ) / 2

        # ---------------------------------------------
        # Background
        # ---------------------------------------------

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(QColor("#151619")))

        painter.drawEllipse(rect)

        # ---------------------------------------------
        # Outer ring
        # ---------------------------------------------

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.setPen(QPen(QColor("#30333b"), 2))

        painter.drawEllipse(rect.adjusted(1, 1, -1, -1))

        # ---------------------------------------------
        # Zero marker
        # ---------------------------------------------

        marker_radius = radius - 7

        painter.setPen(
            QPen(
                QColor("#4a4e59"),
                1,
            )
        )

        for angle in (-135, -90, -45, 0, 45, 90, 135, 180):
            angle_rad = radians(angle - 90)

            outer_x = (
                center.x()
                + cos(angle_rad)
                * marker_radius
            )

            outer_y = (
                center.y()
                + sin(angle_rad)
                * marker_radius
            )

            inner_x = (
                center.x()
                + cos(angle_rad)
                * (marker_radius - 4)
            )

            inner_y = (
                center.y()
                + sin(angle_rad)
                * (marker_radius - 4)
            )

            painter.drawLine(
                int(inner_x),
                int(inner_y),
                int(outer_x),
                int(outer_y),
            )

        # ---------------------------------------------
        # Rotation arc
        # ---------------------------------------------

        value = self.value()

        if value != 0:
            arc_rect = rect.adjusted(
                5,
                5,
                -5,
                -5,
            )

            painter.setPen(
                QPen(
                    QColor("#3b82f6"),
                    3,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )

            # QPainter angles use 1/16 degree.
            #
            # 0° is at the top.
            start_angle = 90 * 16
            span_angle = -value * 16

            painter.drawArc(
                arc_rect,
                start_angle,
                span_angle,
            )

        # ---------------------------------------------
        # Pointer
        # ---------------------------------------------

        pointer_angle = radians(
            value - 90
        )

        pointer_length = radius - 19

        pointer_x = (
            center.x()
            + cos(pointer_angle)
            * pointer_length
        )

        pointer_y = (
            center.y()
            + sin(pointer_angle)
            * pointer_length
        )

        painter.setPen(
            QPen(
                QColor("#dbeafe"),
                2,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )

        painter.drawLine(
            center,
            QPointF(pointer_x, pointer_y),
        )

        # ---------------------------------------------
        # Center point
        # ---------------------------------------------

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            QBrush(
                QColor("#3b82f6")
            )
        )

        painter.drawEllipse(
            center,
            4,
            4,
        )

        painter.end()

class RotationDial(QWidget):
    rotation_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName(
            "rotationControl"
        )

        # -------------------------------------------------
        # Custom dial
        # -------------------------------------------------

        self.dial = RotationDialWidget()

        self.dial.setObjectName(
            "rotationDialWidget"
        )

        # -------------------------------------------------
        # Value input
        # -------------------------------------------------

        self.value_input = QLineEdit()
        self.value_input.setObjectName(
            "rotationValueInput"
        )

        self.value_input.setFixedWidth(58)
        self.value_input.setFixedHeight(26)

        self.value_input.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # -------------------------------------------------
        # Degree label
        # -------------------------------------------------

        self.degree_label = QLabel("°")
        self.degree_label.setObjectName(
            "rotationDegreeLabel"
        )

        # -------------------------------------------------
        # Value row
        # -------------------------------------------------

        value_layout = QHBoxLayout()
        value_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        value_layout.setSpacing(3)

        value_layout.addStretch()

        value_layout.addWidget(
            self.value_input
        )

        value_layout.addWidget(
            self.degree_label
        )

        value_layout.addStretch()

        # -------------------------------------------------
        # Main layout
        # -------------------------------------------------

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(6)

        layout.addWidget(
            self.dial,
            alignment=Qt.AlignmentFlag.AlignHCenter,
        )

        layout.addLayout(
            value_layout
        )

        # -------------------------------------------------
        # Signals
        # -------------------------------------------------

        self.dial.valueChanged.connect(
            self._on_dial_changed
        )

        self.value_input.editingFinished.connect(
            self._on_input_finished
        )

        self._update_input(
            self.dial.value()
        )

    # =====================================================
    # Dial
    # =====================================================

    def _on_dial_changed(self, value: int):
        self._update_input(value)

        self.rotation_changed.emit(
            float(value)
        )

        self.dial.update()

    # =====================================================
    # Input
    # =====================================================

    def _on_input_finished(self):
        text = self.value_input.text().strip()

        if not text:
            self._update_input(
                self.dial.value()
            )
            return

        try:
            value = float(text)
        except ValueError:
            self._update_input(
                self.dial.value()
            )
            return

        value = round(value)

        value = max(
            -180,
            min(
                180,
                value,
            ),
        )

        self.dial.setValue(value)

    # =====================================================
    # Formatting
    # =====================================================

    def _update_input(self, value: int):
        self.value_input.blockSignals(True)

        self.value_input.setText(
            str(value)
        )

        self.value_input.blockSignals(False)

    # =====================================================
    # Public API
    # =====================================================

    def reset(self):
        self.dial.setValue(0)

    def set_enabled(self, enabled: bool):
        self.dial.setEnabled(enabled)
        self.value_input.setEnabled(enabled)

    def set_rotation(self, value: float):
        value = max(
            -180,
            min(
                180,
                int(value),
            ),
        )

        self.dial.blockSignals(True)

        self.dial.setValue(value)

        self.dial.blockSignals(False)

        self._update_input(value)

        self.dial.update()
