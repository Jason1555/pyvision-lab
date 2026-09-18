from model.image_model import ImageModel
from model.histogram import Histogram
from view.main_window import MainWindow
from controller.image_controller import ImageController

class HistogramController:
    def __init__(
        self,
        model: ImageModel,
        view: MainWindow,
        image_controller: ImageController,
    ):
        self.model = model
        self.view = view
        self.image_controller = image_controller

        self.histogram_panel = self.view.histogram_panel

        self._connect_signals()

    def _connect_signals(self):
        self.image_controller.image_loaded.connect(
            self.update
        )

        self.image_controller.histogram_changed.connect(
            self.update
        )

    def update(self):
        if self.model.get_image() is None:
            self.histogram_panel.clear()
            return

        before_image = self.model.get_preview_image()
        after_image = self.model.process_image()

        before_histogram = Histogram.calculate(
            before_image
        )

        after_histogram = Histogram.calculate(
            after_image
        )

        self.histogram_panel.set_histograms(
            before_histogram,
            after_histogram,
        )

    def clear(self):
        self.histogram_panel.clear()
