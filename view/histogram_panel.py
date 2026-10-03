from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import *

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

# Цвета кривых и тёмной темы — в одном месте.
CHANNEL_COLORS = {
    "R": "#ef4444",
    "G": "#22c55e",
    "B": "#3b82f6",
}
GRAY_BEFORE = "#9ca3af"
GRAY_AFTER = "#f3f4f6"
FIGURE_FACE = "#1f2024"
AXES_FACE = "#24262b"
TEXT_COLOR = "#d5d8df"
GRID_COLOR = "#3a3d45"
CLIP_COLOR = "#f87171"


def _format_count(value: float, _pos=None) -> str:
    """Подпись оси Y: абсолютное число пикселей (тыс./млн)."""
    value = int(round(value))
    if value >= 1_000_000:
        text = f"{value / 1_000_000:g} млн"
    elif value >= 1_000:
        text = f"{value / 1_000:g} тыс."
    else:
        text = str(value)
    return text


def _CountFormatter():
    return FuncFormatter(_format_count)


def _hist_peak(hist) -> float:
    """Пик видимых кривых — для единого масштаба панелей ДО/ПОСЛЕ."""
    peak = 0.0
    if not hist:
        return peak
    for data in hist.values():
        try:
            value = float(np.asarray(data).max(initial=0))
        except Exception:
            continue
        if value > peak:
            peak = value
    return peak


class HistogramPanel(QWidget):
    channels_changed = pyqtSignal()
    options_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("histogramPanel")

        self.title_label = QLabel("ГИСТОГРАММА")

        self.red_checkbox = QCheckBox("R")
        self.green_checkbox = QCheckBox("G")
        self.blue_checkbox = QCheckBox("B")

        self.red_checkbox.setChecked(True)
        self.green_checkbox.setChecked(True)
        self.blue_checkbox.setChecked(True)

        self.fill_checkbox = QCheckBox("Заливка")
        self.fill_checkbox.setObjectName("histFillCheck")
        self.fill_checkbox.setChecked(True)
        self.fill_checkbox.setToolTip(
            "Заливка площади под кривой — так проще сравнивать до/после"
        )

        self.figure = Figure(
            figsize=(5.2, 3.2),
            dpi=100,
            facecolor=FIGURE_FACE,
        )

        self.canvas = FigureCanvasQTAgg(self.figure)

        self.ax_before = self.figure.add_subplot(1, 2, 1)
        self.ax_after = self.figure.add_subplot(1, 2, 2)

        for ax in (self.ax_before, self.ax_after):
            ax.set_facecolor(AXES_FACE)

        self._before = None
        self._after = None
        self._before_stats = None
        self._after_stats = None
        self._is_grayscale = False
        # Зафиксированный потолок Y панели ДО: исходник не меняется,
        # поэтому масштаб "до" запоминаем один раз при загрузке.
        self._before_y_max = 0.0

        channels_layout = QHBoxLayout()
        channels_layout.setContentsMargins(0, 0, 0, 0)
        channels_layout.setSpacing(8)

        channels_layout.addWidget(self.red_checkbox)
        channels_layout.addWidget(self.green_checkbox)
        channels_layout.addWidget(self.blue_checkbox)
        channels_layout.addStretch()
        channels_layout.addWidget(self.fill_checkbox)

        self.stats_label = QLabel("—")
        self.stats_label.setObjectName("histStatsLabel")
        self.stats_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.title_label)
        layout.addLayout(channels_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(self.stats_label)

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

        self.fill_checkbox.toggled.connect(self._options_changed)

    @property
    def before_histogram(self):
        return self._before

    @property
    def before_stats(self):
        return self._before_stats

    def set_histograms(
        self,
        before,
        after,
        before_stats=None,
        after_stats=None,
        is_grayscale: bool = False,
        freeze_before: bool = False,
    ):
        """freeze_before=True — новая картинка: запомнить масштаб ДО.

        Панель ДО статична: её данные и потолок Y фиксируются один раз
        при загрузке и больше не трогаются слайдерами.
        """
        if freeze_before or self._before is None:
            self._before = before
            self._before_stats = before_stats
            self._before_y_max = max(_hist_peak(before), 1.0)
        self._after = after
        self._after_stats = after_stats
        self._is_grayscale = is_grayscale

        self._redraw()

    def _channels_changed(self):
        self.channels_changed.emit()
        self._redraw()

    def _options_changed(self):
        self.options_changed.emit()
        self._redraw()

    def _is_gray_mode(self) -> bool:
        if self._before is None or self._after is None:
            return self._is_grayscale
        return self._is_grayscale or (
            "L" in self._before
            and "L" in self._after
            and "R" not in self._after
        )

    def _active_channels(self) -> list:
        channels = []
        if self.red_checkbox.isChecked():
            channels.append(("R", CHANNEL_COLORS["R"]))
        if self.green_checkbox.isChecked():
            channels.append(("G", CHANNEL_COLORS["G"]))
        if self.blue_checkbox.isChecked():
            channels.append(("B", CHANNEL_COLORS["B"]))
        return channels

    def _draw_single(self, ax, hist, stats, title: str, y_max: float = 0):
        ax.clear()
        ax.set_facecolor(AXES_FACE)

        x = range(256)
        fill = self.fill_checkbox.isChecked()

        if self._is_gray_mode():
            data = hist.get("L") if hist else None
            if data is not None:
                if fill:
                    ax.fill_between(
                        x, data, alpha=0.35,
                        color=GRAY_BEFORE, step="mid",
                    )
                ax.plot(x, data, color=GRAY_AFTER, linewidth=1.4)
        else:
            for channel, color in self._active_channels():
                if hist is None or channel not in hist:
                    continue
                data = hist[channel]
                if fill:
                    ax.fill_between(
                        x, data, alpha=0.22, color=color, step="mid",
                    )
                ax.plot(x, data, color=color, alpha=0.95, linewidth=1.2)

        if stats is not None:
            for value, pct in (
                (0, stats.get("black_pct", 0.0)),
                (255, stats.get("white_pct", 0.0)),
            ):
                if pct > 0.5:
                    ax.axvline(
                        value, color=CLIP_COLOR, linestyle="--",
                        linewidth=1.0, alpha=0.8,
                    )

        ax.set_xlim(0, 255)
        # Единый масштаб Y для панелей ДО/ПОСЛЕ: сравнение честное,
        # подпись — абсолютное число пикселей, а не проценты.
        if y_max > 0:
            ax.set_ylim(0, y_max * 1.08)
            ax.yaxis.set_major_formatter(_CountFormatter())
        ax.set_title(title, color=TEXT_COLOR, fontsize=9, pad=4)
        ax.tick_params(colors=TEXT_COLOR, labelsize=7)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)

        ax.grid(True, alpha=0.18, color=GRID_COLOR, linewidth=0.6)

    def _redraw(self):
        if self._before is None or self._after is None:
            return

        # ДО — статична (масштаб зафиксирован при загрузке).
        # ПОСЛЕ — в том же масштабе, чтобы сравнение было честным:
        # кривая может стать ниже/шире, но ось не "подстраивается".
        before_max = self._before_y_max or max(
            _hist_peak(self._before), 1.0
        )

        self._draw_single(
            self.ax_before, self._before, self._before_stats, "ДО",
            y_max=before_max,
        )
        self._draw_single(
            self.ax_after, self._after, self._after_stats, "ПОСЛЕ",
            y_max=before_max,
        )

        self.ax_before.set_ylabel("Пиксели", color=TEXT_COLOR, fontsize=8)
        self.ax_after.set_ylabel("")
        self.ax_after.tick_params(labelleft=False)
        for ax in (self.ax_before, self.ax_after):
            ax.set_xlabel("Яркость", color=TEXT_COLOR, fontsize=8)

        self._update_stats_text()

        self.figure.tight_layout(pad=1.2, w_pad=2.0)
        self.canvas.draw_idle()

    def _update_stats_text(self):
        before = self._before_stats
        after = self._after_stats

        if before is None or after is None:
            self.stats_label.setText("—")
            return

        if self._is_gray_mode():
            mean_line = (
                f"Среднее {before['mean']:.1f} → {after['mean']:.1f} "
                f"({after['mean'] - before['mean']:+.1f})  |  "
                f"Медиана {before['median']:.0f} → {after['median']:.0f}"
            )
        else:
            mean_line = (
                f"Среднее {before['mean']:.1f} → {after['mean']:.1f} "
                f"({after['mean'] - before['mean']:+.1f})  |  "
                f"R {before['mean_r']:.0f}→{after['mean_r']:.0f}  "
                f"G {before['mean_g']:.0f}→{after['mean_g']:.0f}  "
                f"B {before['mean_b']:.0f}→{after['mean_b']:.0f}"
            )

        clip_line = (
            f"Отсечка: тени {before['black_pct']:.1f}% → "
            f"{after['black_pct']:.1f}%,  "
            f"света {before['white_pct']:.1f}% → {after['white_pct']:.1f}%"
        )

        self.stats_label.setText(f"{mean_line}\n{clip_line}")

    def freeze_before(self, before, before_stats):
        """Зафиксировать панель ДО (вызывается один раз при загрузке)."""
        self._before = before
        self._before_stats = before_stats
        self._before_y_max = max(_hist_peak(before), 1.0)

    def clear(self):
        self._before = None
        self._after = None
        self._before_stats = None
        self._after_stats = None
        self._is_grayscale = False
        self._before_y_max = 0.0

        for ax in (self.ax_before, self.ax_after):
            ax.clear()
            ax.set_facecolor(AXES_FACE)
        self.stats_label.setText("—")
        self.canvas.draw_idle()
