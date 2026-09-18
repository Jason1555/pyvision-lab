from PIL import Image
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import *

from model.image_model import ImageModel
from view.main_window import MainWindow

class ImageController(QObject):
    image_loaded = pyqtSignal()
    def __init__(self, model: ImageModel, view: MainWindow):
        super().__init__()

        self.model = model
        self.view = view

        self.view.open_button.clicked.connect(self.open_image)
        self.view.tool_panel.grayscale_tool.grayscale_clicked.connect(self.convert_to_grayscale)
        self.view.tool_panel.brightness_tool.brightness_changed.connect(self.adjust_brightness)
        self.view.tool_panel.contrast_tool.contrast_changed.connect(self.adjust_contrast)
        self.view.tool_panel.saturation_tool.saturation_changed.connect(self.adjust_saturation)
        self.view.tool_panel.rotation_dial.rotation_changed.connect(self.adjust_rotation)
        self.view.tool_panel.rotate_left_clicked.connect(self.rotate_left)
        self.view.tool_panel.rotate_right_clicked.connect(self.rotate_right)
        self.view.tool_panel.rotate_reset_clicked.connect(self.reset_rotation)
        self.view.tool_panel.linear_correction_changed.connect(self.adjust_linear_correction)
        self.view.tool_panel.gamma_changed.connect(self.adjust_gamma)

    def open_image(self):
        file_path = self.view.ask_open_file()

        if not file_path: return

        try:
            image = self.model.load_image(file_path)

            self.view.tool_panel.reset()

            file_size = self.model.get_file_size()
            resolution = self.model.get_resolution()
            color_depth = self.model.get_color_depth()
            file_format = self.model.get_format()
            color_model = self.model.get_color_model()

            self.view.image_info_panel.set_image_info(
                file_size,
                resolution,
                color_depth,
                file_format,
                color_model,
            )

            qimage = self.pil_to_qimage(image)

            if qimage.isNull():
                raise RuntimeError(
                    "Qt could not create an image from the loaded data."
                )

            pixmap = QPixmap.fromImage(qimage)

            if pixmap.isNull():
                raise RuntimeError(
                    "Qt could not create a pixmap from the image."
                )

            self.view.show_image(pixmap, preserve_zoom=False)

            width, height = image.size

            self.view.show_image_info(
                self.model.get_file_name(),
                width,
                height,
            )

            self.view.tool_panel.setEnabled(True)

        except Exception as error:
            self.view.show_error(f"Failed to open image:\n\n{error}")

    def _refresh_image(self):
        image = self.model.process_image()

        if image is None:
            return

        qimage = self.pil_to_qimage(image)
        pixmap = QPixmap.fromImage(qimage)

        processed_size = self.model.get_processed_size()

        self.view.show_image(
            pixmap,
            preserve_zoom=True,
            original_size=processed_size
        )

    def convert_to_grayscale(self, enabled):
        self.model.set_grayscale(enabled)
        self._refresh_image()

    def adjust_brightness(self, value):
        self.model.set_brightness(value)
        self._refresh_image()

    def adjust_contrast(self, value):
        self.model.set_contrast(value)
        self._refresh_image()

    def adjust_saturation(self, value):
        self.model.set_saturation(value)
        self._refresh_image()

    def adjust_rotation(self, value: float):
        self.model.set_rotation(value)
        self._refresh_image()

    def rotate_left(self):
        self.model.rotate_by(-90)
        self._sync_rotation_dial()
        self._refresh_image()

    def rotate_right(self):
        self.model.rotate_by(90)
        self._sync_rotation_dial()
        self._refresh_image()

    def adjust_linear_correction(self, enabled: bool):
        self.model.set_linear_correction(enabled)
        self._refresh_image()

    def adjust_gamma(self, value: float):
        self.model.set_gamma(value)
        self._refresh_image()

    def reset_rotation(self):
        self.model.set_rotation(0)
        self._sync_rotation_dial()
        self._refresh_image()

    def _sync_rotation_dial(self):
        self.view.tool_panel.rotation_dial.set_rotation(self.model.image_settings.rotation)

    @staticmethod
    def pil_to_qimage(image: Image.Image) -> QImage:
        rgba_image = image.convert("RGBA")

        width = rgba_image.width
        height = rgba_image.height

        data = rgba_image.tobytes("raw", "RGBA")

        qimage = QImage(
            data,
            width,
            height,
            width * 4,
            QImage.Format.Format_RGBA8888,
        )

        return qimage.copy()
