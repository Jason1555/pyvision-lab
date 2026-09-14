from view.main_window import MainWindow

class ZoomController:
    def __init__(self, view: MainWindow):
        self.view = view

        self.zoom_controls = self.view.zoom_controls
        self.image_canvas = self.view.image_canvas

        self.zoom_controls.zoom_in_clicked.connect(self.image_canvas.zoom_in)
        self.zoom_controls.zoom_out_clicked.connect(self.image_canvas.zoom_out)
        self.zoom_controls.fit_clicked.connect(self.image_canvas.fit_image)
        self.zoom_controls.zoom_label.clicked.connect(self.image_canvas.reset_zoom)
        self.image_canvas.zoom_changed.connect(self.zoom_controls.set_zoom)
