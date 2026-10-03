from pathlib import Path

from PIL import Image

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

from model.image_model import ImageModel
from view.main_window import MainWindow


class ImageController(QObject):
    image_loaded = pyqtSignal()
    image_changed = pyqtSignal()
    histogram_changed = pyqtSignal()

    def __init__(self, model: ImageModel, view: MainWindow):
        super().__init__()

        self.model = model
        self.view = view

        self.rotation_timer = QTimer(self)
        self.rotation_timer.setSingleShot(True)
        self.rotation_timer.setInterval(30)
        self.rotation_timer.timeout.connect(self._apply_rotation)

        self._connect_signals()

    def _connect_signals(self):
        self.view.open_button.clicked.connect(self.open_image)
        self.view.save_button.clicked.connect(self.save_image)
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
        self.rotation_timer.stop()
        file_path = self.view.ask_open_file()

        if not file_path:
            return

        try:
            image = self.model.load_image(file_path)

            self.view.tool_panel.reset()

            qimage = self.pil_to_qimage(image)

            # Qt не смог создать изображение из загруженных данных.
            if qimage.isNull():
                raise RuntimeError(
                    "Не удалось создать изображение из загруженных данных."
                )

            pixmap = QPixmap.fromImage(qimage)

            if pixmap.isNull():
                raise RuntimeError(
                    "Не удалось отобразить изображение."
                )

            self.view.show_image(
                pixmap,
                preserve_zoom=False,
            )

            width, height = image.size

            self.view.show_image_info(
                self.model.get_file_name(),
                width,
                height,
            )

            self.view.tool_panel.setEnabled(True)
            self.view.save_button.setEnabled(True)

            self.image_loaded.emit()

        except Exception as error:
            self.view.show_error(
                f"Не удалось открыть изображение:\n\n{error}"
            )

    def save_image(self):
        if self.model.get_image() is None:
            return

        file_name = self.model.get_file_name()

        if file_name:
            path = Path(file_name)
            default_name = str(
                path.with_name(
                    f"{path.stem}_изм{path.suffix}"
                )
            )
        else:
            default_name = "изменённое_изображение.png"

        file_path = self.view.ask_save_file(default_name)

        if not file_path:
            return

        try:
            self.model.save_processed_image(file_path)
            self.view.show_info(f"Изображение сохранено:\n\n{file_path}")

        except Exception as error:
            self.view.show_error(
                f"Не удалось сохранить изображение:\n\n{error}",
                title="Не удалось сохранить изображение",
            )

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
            original_size=processed_size,
        )

        self.image_changed.emit()

    def convert_to_grayscale(self, enabled: bool):
        self.model.set_grayscale(enabled)
        if not enabled:
            # ЧБ выключили — сбрасываем и флаг линейной в модели,
            # иначе process_image продолжит тянуть цветное фото.
            self.model.set_linear_correction(False)
        self._refresh_image()
        self.histogram_changed.emit()

    def adjust_brightness(self, value: int):
        self.model.set_brightness(value)
        self._refresh_image()
        self.histogram_changed.emit()

    def adjust_contrast(self, value: int):
        self.model.set_contrast(value)
        self._refresh_image()
        self.histogram_changed.emit()

    def adjust_saturation(self, value: int):
        self.model.set_saturation(value)
        self._refresh_image()
        self.histogram_changed.emit()

    def adjust_rotation(self, value: float):
        self.model.set_rotation(value)
        self.rotation_timer.start()

    def _apply_rotation(self):
        self._refresh_image()
        self.histogram_changed.emit()

    def rotate_left(self):
        self.rotation_timer.stop()

        self.model.rotate_by(-90)
        self._sync_rotation_dial()
        self._refresh_image()
        self.histogram_changed.emit()

    def rotate_right(self):
        self.rotation_timer.stop()

        self.model.rotate_by(90)
        self._sync_rotation_dial()
        self._refresh_image()
        self.histogram_changed.emit()

    def adjust_linear_correction(self, enabled: bool):
        # Страховка: без ЧБ линейную не применяем даже напрямую.
        if enabled and not self.model.image_settings.grayscale:
            enabled = False
        self.model.set_linear_correction(enabled)
        self._refresh_image()
        self.histogram_changed.emit()

    def adjust_gamma(self, value: float):
        self.model.set_gamma(value)
        self._refresh_image()
        self.histogram_changed.emit()

    def reset_rotation(self):
        self.rotation_timer.stop()

        self.model.set_rotation(0)
        self._sync_rotation_dial()
        self._refresh_image()
        self.histogram_changed.emit()

    def _sync_rotation_dial(self):
        self.view.tool_panel.rotation_dial.set_rotation(self.model.image_settings.rotation)

    @staticmethod
    def pil_to_qimage(image: Image.Image) -> QImage:
        # Быстрые пути без промежуточного RGBA:
        # L -> Grayscale8 (1 байт/пиксель), RGB -> RGB888 (3 байта).
        if image.mode == "L":
            width, height = image.size
            data = image.tobytes("raw", "L")
            qimage = QImage(
                data,
                width,
                height,
                width,
                QImage.Format.Format_Grayscale8,
            )
            return qimage.copy()

        if image.mode == "RGB":
            width, height = image.size
            data = image.tobytes("raw", "RGB")
            qimage = QImage(
                data,
                width,
                height,
                width * 3,
                QImage.Format.Format_RGB888,
            )
            return qimage.copy()

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
