import sys

from PyQt6.QtWidgets import QApplication
from view.main_window import MainWindow
from model.image_model import ImageModel
from controller.image_controller import ImageController
from controller.image_info_controller import ImageInfoController
from controller.zoom_controller import ZoomController

def main():
    app = QApplication(sys.argv)

    model = ImageModel()
    view = MainWindow()

    image_controller = ImageController(model=model, view=view)
    image_info_controller = ImageInfoController(model=model, view=view)
    zoom_controller = ZoomController(view=view)
    
    app.controllers = [image_controller, image_info_controller, zoom_controller]

    view.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
