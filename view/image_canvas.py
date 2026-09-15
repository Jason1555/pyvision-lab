from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class ImageCanvas(QGraphicsView):
    zoom_changed = pyqtSignal(int)

    MIN_ZOOM = 0.1
    MAX_ZOOM = 8.0
    ZOOM_STEP = 1.15

    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmap_item: QGraphicsPixmapItem | None = None

        self.zoom = 1.0

        # Логический размер изображения.
        # Это размер оригинала, а не preview.
        self.image_size: tuple[int, int] | None = None

        self.is_panning = False
        self.last_mouse_position = None

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def set_pixmap(self, pixmap: QPixmap, preserve_zoom: bool = False, original_size: tuple[int, int] | None = None):
        # Если original_size передан — запоминаем его.
        if original_size is not None: self.image_size = original_size

        # Если размер ещё неизвестен, используем размер pixmap.
        if self.image_size is None:
            self.image_size = (
                pixmap.width(),
                pixmap.height(),
            )

        current_zoom = self.zoom

        # Сохраняем положение скроллов.
        old_horizontal = self.horizontalScrollBar().value()
        old_vertical = self.verticalScrollBar().value()

        self.scene.clear()

        self.pixmap_item = self.scene.addPixmap(pixmap)

        original_width, original_height = self.image_size

        # Preview превращаем в изображение с логическим
        # размером оригинала.
        if pixmap.width() > 0 and pixmap.height() > 0:
            scale_x = original_width / pixmap.width()
            scale_y = original_height / pixmap.height()

            transform = QTransform()
            transform.scale(scale_x, scale_y)

            self.pixmap_item.setTransform(transform)

        # КРИТИЧЕСКИ ВАЖНО:
        # scene всегда имеет размер оригинального изображения.
        self.scene.setSceneRect(
            0,
            0,
            original_width,
            original_height,
        )

        if preserve_zoom:
            # Восстанавливаем именно коэффициент zoom.
            self.set_zoom(
                current_zoom,
                emit_signal=False,
            )

            # Восстанавливаем положение просмотра.
            self.horizontalScrollBar().setValue(old_horizontal)
            self.verticalScrollBar().setValue(old_vertical)

            self.zoom_changed.emit(self.get_zoom_percent())

        else:
            self.fit_image()

    def fit_image(self):
        if self.pixmap_item is None:
            return

        if self.image_size is None:
            return

        original_width, original_height = self.image_size

        viewport_rect = self.viewport().rect()

        if original_width <= 0 or original_height <= 0:
            return

        available_width = viewport_rect.width()
        available_height = viewport_rect.height()

        scale_x = available_width / original_width
        scale_y = available_height / original_height

        fit_zoom = min(
            scale_x,
            scale_y,
        )

        fit_zoom = max(
            self.MIN_ZOOM,
            min(self.MAX_ZOOM, fit_zoom),
        )

        self.zoom = fit_zoom

        self.setTransform(self._transform_for_zoom(self.zoom))

        self.centerOn(self.pixmap_item)

        self.zoom_changed.emit(self.get_zoom_percent())

    def reset_zoom(self):
        if self.pixmap_item is None:
            return

        self.set_zoom(1.0)

    def zoom_in(self):
        self.set_zoom(self.zoom * self.ZOOM_STEP)

    def zoom_out(self):
        self.set_zoom(self.zoom / self.ZOOM_STEP)

    def set_zoom(self, value: float, emit_signal: bool = True):
        if self.pixmap_item is None: return

        new_zoom = max(
            self.MIN_ZOOM,
            min(self.MAX_ZOOM, value),
        )

        self.zoom = new_zoom

        self.setTransform(self._transform_for_zoom(self.zoom))

        if emit_signal:
            self.zoom_changed.emit(self.get_zoom_percent())

    def get_zoom_percent(self) -> int:
        return round(self.zoom * 100)

    def _transform_for_zoom(self, zoom: float):
        transform = QTransform()
        transform.scale(
            zoom,
            zoom,
        )

        return transform

    def wheelEvent(self, event: QWheelEvent):
        if self.pixmap_item is None:
            return

        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = True
            self.last_mouse_position = event.position()

            self.setCursor(Qt.CursorShape.ClosedHandCursor)

            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if (
            self.is_panning
            and self.last_mouse_position is not None
        ):
            delta = (event.position() - self.last_mouse_position)

            self.last_mouse_position = event.position()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value()
                - int(delta.x())
            )

            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value()
                - int(delta.y())
            )

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = False
            self.last_mouse_position = None

            self.setCursor(Qt.CursorShape.ArrowCursor)

            event.accept()
            return

        super().mouseReleaseEvent(event)
