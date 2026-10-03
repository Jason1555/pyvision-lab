from model.histogram import Histogram

from PyQt6.QtCore import QObject, QTimer


class HistogramController(QObject):
    # Пауза после последнего движения слайдера перед тяжёлым
    # пересчётом по оригиналу. Быстрый отклик даёт preview,
    # точные цифры — отложенный полный пересчёт.
    FULL_DELAY_MS = 400

    def __init__(
        self,
        model,
        view,
        image_controller,
    ):
        super().__init__()

        self.model = model
        self.view = view
        self.image_controller = image_controller

        self.histogram_panel = self.view.histogram_panel

        self._full_timer = QTimer(self)
        self._full_timer.setSingleShot(True)
        self._full_timer.setInterval(self.FULL_DELAY_MS)
        self._full_timer.timeout.connect(self._update_full)

        self._connect_signals()

    def _connect_signals(self):
        self.image_controller.image_loaded.connect(
            self.on_image_loaded
        )

        self.image_controller.histogram_changed.connect(
            self.update
        )

    def update(self):
        if self.model.get_image() is None:
            self.histogram_panel.clear()
            return

        # Панель ДО статична: исходник не меняется от слайдеров,
        # поэтому её кривая и масштаб зафиксированы при загрузке
        # (on_image_loaded) и здесь не пересчитываются.
        # Здесь обновляется только ПОСЛЕ.
        after_image = self.model.process_image(preview=True)

        after_histogram = Histogram.calculate(
            after_image
        )

        after_stats = Histogram.stats(
            after_image, after_histogram
        )

        self.histogram_panel.set_histograms(
            self.histogram_panel.before_histogram,
            after_histogram,
            before_stats=self.histogram_panel.before_stats,
            after_stats=after_stats,
            is_grayscale=bool(
                self.model.image_settings.grayscale
                or after_image.mode == "L"
            ),
        )

        # 2. Точно: через паузу пересчитать по ОРИГИНАЛУ
        # (те же данные, что уйдут в сохранённый файл).
        # Каждый новый тик слайдера сбрасывает таймер.
        self._full_timer.start()

    def on_image_loaded(self):
        """Загружено новое изображение: зафиксировать панель ДО."""
        if self.model.get_image() is None:
            self.histogram_panel.clear()
            return

        before_image = self.model.get_preview_image()

        before_histogram = Histogram.calculate(
            before_image
        )
        before_stats = Histogram.stats(
            before_image, before_histogram
        )

        self.histogram_panel.freeze_before(
            before_histogram, before_stats
        )

        # Сразу показать и ПОСЛЕ (без обработки = копия ДО).
        self.update()
        # Точный ДО по оригиналу придёт с _update_full.

    def _update_full(self):
        """Точный пересчёт гистограммы по оригиналу (данные как в файле)."""
        if self.model.get_image() is None:
            return

        after_image = self.model.process_image(preview=False)

        after_histogram = Histogram.calculate(
            after_image
        )

        after_stats = Histogram.stats(
            after_image, after_histogram
        )

        self.histogram_panel.set_histograms(
            self.histogram_panel.before_histogram,
            after_histogram,
            before_stats=self.histogram_panel.before_stats,
            after_stats=after_stats,
            is_grayscale=bool(
                self.model.image_settings.grayscale
                or after_image.mode == "L"
            ),
        )

    def clear(self):
        self._full_timer.stop()
        self.histogram_panel.clear()
