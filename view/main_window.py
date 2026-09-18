from pathlib import Path

from PIL import Image

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import *

from view.histogram_panel import HistogramPanel
from view.image_canvas import ImageCanvas
from view.zoom_controls import ZoomControls
from view.image_info_panel import ImageInfoPanel
from view.tools.tool_panel import ToolPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vision Lab")
        self.resize(1200, 800)

        self.current_pixmap: QPixmap | None = None

        self.open_button = QPushButton("Open image")
        self.open_button.setObjectName("openButton")

        self.save_button = QPushButton("Save image")
        self.save_button.setObjectName("saveButton")
        self.save_button.setEnabled(False)

        self.tool_panel = ToolPanel()
        self.tool_panel.setEnabled(False)

        self.image_canvas = ImageCanvas()
        self.image_canvas.setObjectName("imageCanvas")

        self.image_info_panel = ImageInfoPanel()
        self.histogram_panel = HistogramPanel()

        right_panel = QWidget()

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)

        right_layout.addWidget(self.image_info_panel)

        right_layout.addWidget(self.histogram_panel, stretch=1)

        right_panel.setLayout(right_layout)

        self.zoom_controls = ZoomControls()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        main_layout.addWidget(self.open_button)
        main_layout.addWidget(self.save_button)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        content_layout.addWidget(self.tool_panel)
        content_layout.addWidget(self.image_canvas, stretch=1)
        content_layout.addWidget(right_panel)

        main_layout.addLayout(content_layout, stretch=1)
        main_layout.addWidget(self.zoom_controls)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)

        #self.load_styles()

    def load_styles(self):
        style_path = (
            Path(__file__).parent
            / "styles"
            / "main.qss"
        )

        try:
            with open(style_path, "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())
        except OSError as error:
            print(f"Could not load stylesheet: {error}")

    def ask_open_file(self) -> str:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open image",
            "",
            (
                "Images (*.jpg *.jpeg *.png *.bmp *.webp);;"
                "JPEG (*.jpg *.jpeg);;"
                "PNG (*.png);;"
                "BMP (*.bmp);;"
                "WEBP (*.webp);;"
                "All files (*)"
            ),
        )

        return file_path

    def ask_save_file(self, default_name: str = "") -> str:
        filters = (
            "PNG Image (*.png);;"
            "JPEG Image (*.jpg *.jpeg);;"
            "WebP Image (*.webp);;"
            "BMP Image (*.bmp);;"
            "TIFF Image (*.tif *.tiff);;"
            "All files (*.*)"
        )

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save image",
            default_name,
            filters,
        )

        if not file_path:
            return ""

        path = Path(file_path)

        if selected_filter.startswith("PNG"):
            extension = ".png"

        elif selected_filter.startswith("JPEG"):
            extension = ".jpg"

        elif selected_filter.startswith("WebP"):
            extension = ".webp"

        elif selected_filter.startswith("BMP"):
            extension = ".bmp"

        elif selected_filter.startswith("TIFF"):
            extension = ".tiff"

        else:
            return file_path

        # Если пользователь уже ввёл правильное расширение,
        # ничего менять не нужно.
        if path.suffix.lower() != extension:
            path = path.with_suffix(extension)

        return str(path)

    def show_image(self, pixmap: QPixmap, preserve_zoom: bool = False, original_size: tuple[int, int] | None = None):
        self.image_canvas.set_pixmap(pixmap, preserve_zoom=preserve_zoom, original_size = original_size)

    def show_image_info(self, file_name: str, width: int, height: int):
        self.setWindowTitle(
            f"Vision Lab — {file_name} — {width} × {height}"
        )

    def show_error(self, message: str) -> None:
        QMessageBox.critical(
            self,
            "Unable to open image",
            message,
        )

    def update_zoom_label(self):
        self.zoom_controls.set_zoom(self.image_canvas.get_zoom_percent())
