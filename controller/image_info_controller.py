from model.image_model import ImageModel
from view.exif_dialog import ExifDialog
from view.main_window import MainWindow


class ImageInfoController:
    def __init__(self, model: ImageModel, view: MainWindow):
        self.model = model
        self.view = view

        self.exif_dialog = ExifDialog(self.view)
        self.view.image_info_panel.exif_clicked.connect(self.show_exif)

    def update_image_info(self) -> None:
        file_size = self.model.get_file_size()
        resolution = self.model.get_resolution()
        color_depth = self.model.get_color_depth()
        file_format = self.model.get_format()
        color_model = self.model.get_color_model()

        if (
            file_size is None
            or resolution is None
            or color_depth is None
            or file_format is None
            or color_model is None
        ):
            self.view.image_info_panel.clear()
            return

        self.view.image_info_panel.set_image_info(
            file_size,
            resolution,
            color_depth,
            file_format,
            color_model,
        )

    def show_exif(self) -> None:
        exif_data = self.model.get_exif()

        self.exif_dialog.set_exif_data(exif_data)
        self.exif_dialog.exec()
