from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import *

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class HistogramPanel(QWidget):
    channels_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("histogramPanel")

        self.title_label = QLabel("HISTOGRAM")

        self.red_checkbox = QCheckBox("R")
        self.green_checkbox = QCheckBox("G")
        self.blue_checkbox = QCheckBox("B")

        self.red_checkbox.setChecked(True)
        self.green_checkbox.setChecked(True)
        self.blue_checkbox.setChecked(True)

        self.figure = Figure(
            figsize=(4, 3),
            dpi=100,
        )

        self.canvas = FigureCanvasQTAgg(self.figure)

        self.axis = self.figure.add_subplot(111)

        self._before = None
        self._after = None

        channels_layout = QHBoxLayout()
        channels_layout.setContentsMargins(0, 0, 0, 0)

        channels_layout.addWidget(self.red_checkbox)
        channels_layout.addWidget(self.green_checkbox)
        channels_layout.addWidget(self.blue_checkbox)
        channels_layout.addStretch()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.title_label)
        layout.addLayout(channels_layout)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.red_checkbox.toggled.connect(
            self._channels_changed
        )

        self.green_checkbox.toggled.connect(
            self._channels_changed
        )

        self.blue_checkbox.toggled.connect(
            self._channels_changed
        )

    def set_histograms(self, before, after):
        self._before = before
        self._after = after

        self._redraw()

    def _channels_changed(self):
        self.channels_changed.emit()
        self._redraw()

    def _redraw(self):
        if self._before is None or self._after is None:
            return

        self.axis.clear()

        channels = []

        if self.red_checkbox.isChecked():
            channels.append(("R", "red"))

        if self.green_checkbox.isChecked():
            channels.append(("G", "green"))

        if self.blue_checkbox.isChecked():
            channels.append(("B", "blue"))

        x = range(256)

        for channel, color in channels:
            self.axis.plot(
                x,
                self._before[channel],
                color=color,
                alpha=0.3,
                linewidth=1,
            )

            self.axis.plot(
                x,
                self._after[channel],
                color=color,
                alpha=1.0,
                linewidth=1.2,
            )

        self.axis.set_xlim(0, 255)
        self.axis.set_xlabel("Value")
        self.axis.set_ylabel("Pixels")

        self.axis.grid(
            True,
            alpha=0.15,
        )

        self.axis.plot(
            [],
            [],
            color="black",
            alpha=0.3,
            label="Before",
        )

        self.axis.plot(
            [],
            [],
            color="black",
            alpha=1.0,
            label="After",
        )

        self.axis.legend(
            loc="upper right",
            frameon=False,
        )

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def clear(self):
        self._before = None
        self._after = None

        self.axis.clear()
        self.canvas.draw_idle()
