import math

from pathlib import Path
from PIL import ExifTags, Image, ImageEnhance

from model.image_settings import ImageSettings

class ImageModel:
    def __init__(self):
        # Оригинальное изображение.
        # Никогда не изменяется.
        self.image: Image.Image | None = None

        # Уменьшенная копия оригинала для быстрой обработки.
        self.preview_image: Image.Image | None = None

        self.file_path: Path | None = None

        # Параметры обработки изображения.
        self.image_settings = ImageSettings()

    def load_image(self, file_path: str) -> Image.Image:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        image = Image.open(path)
        image.load()

        # Сохраняем оригинал.
        self.image = image

        # Сохраняем путь.
        self.file_path = path

        # Для нового изображения начинаем
        # с чистых настроек.
        self.image_settings = ImageSettings()

        # Создаём preview.
        self._update_preview()

        return self.image

    def _update_preview(self):
        if self.image is None:
            self.preview_image = None
            return

        self.preview_image = self.image.copy()

        self.preview_image.thumbnail(
            (1600, 1600),
            Image.Resampling.LANCZOS,
        )

    def get_image(self) -> Image.Image | None:
        return self.image

    def get_preview_image(self) -> Image.Image:
        if self.preview_image is None:
            raise RuntimeError("No image loaded")

        return self.preview_image

    def get_file_name(self) -> str:
        if self.file_path is None:
            return ""

        return self.file_path.name

    def get_file_size(self) -> int | None:
        if self.file_path is None:
            return None

        return self.file_path.stat().st_size

    def get_resolution(self) -> tuple[int, int] | None:
        if self.image is None:
            return None

        return self.image.size

    def get_color_depth(self) -> int | None:
        if self.image is None:
            return None

        mode_depth = {
            "1": 1,
            "L": 8,
            "P": 8,
            "RGB": 24,
            "RGBA": 32,
            "CMYK": 32,
            "YCbCr": 24,
            "LAB": 24,
            "HSV": 24,
            "I": 32,
            "F": 32,
        }

        return mode_depth.get(
            self.image.mode,
            "Unknown",
        )

    def get_format(self) -> str | None:
        if self.image is None:
            return None

        return self.image.format

    def get_color_model(self) -> str:
        if self.image is None:
            raise RuntimeError("No image loaded")

        return self.image.mode

    def get_exif(self) -> dict[str, str]:
        if self.image is None:
            return {}

        exif = self.image.getexif()

        exif_data = {}

        for tag_id, value in exif.items():
            tag_name = ExifTags.TAGS.get(
                tag_id,
                str(tag_id),
            )

            exif_data[tag_name] = str(value)

        return exif_data

    def process_image(self, preview=True):
        if self.image is None: return None

        result = self.preview_image.copy() if preview else self.image.copy()

        if self.image_settings.grayscale:
            result = result.convert("L")

        if self.image_settings.linear_correction:
            result = self._apply_linear_correction(result)

        if self.image_settings.gamma != 1.0:
            result = self._apply_gamma_correction(result)

        if self.image_settings.brightness != 0:
            factor = 1 + self.image_settings.brightness / 100
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(factor)

        if self.image_settings.contrast != 0:
            factor = 1 + self.image_settings.contrast / 100
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(factor)

        if self.image_settings.saturation != 0 and result.mode != "L":
            factor = 1 + self.image_settings.saturation / 100
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(factor)

        if self.image_settings.rotation != 0:
            result = result.rotate(
                self.image_settings.rotation,
                expand=True,
                resample=Image.Resampling.BICUBIC
            )

        return result

    def set_grayscale(self, enabled: bool):
        self.image_settings.grayscale = enabled

    def set_brightness(self, value: int):
        self.image_settings.brightness = value

    def set_contrast(self, value: int):
        self.image_settings.contrast = value

    def set_saturation(self, value: int):
        self.image_settings.saturation = value

    def set_rotation(self, value: float):
        self.image_settings.rotation = value

    def set_linear_correction(self, enabled: bool):
        self.image_settings.linear_correction = enabled

    def set_gamma(self, value: float):
        self.image_settings.gamma = value

    def rotate_by(self, angle: float):
        rotation = self.image_settings.rotation + angle

        if rotation > 180:
            rotation -= 360
        elif rotation < -180:
            rotation += 360

        self.image_settings.rotation = rotation

    def get_processed_size(self):
        if self.image is None:
            return None

        width, height = self.image.size
        angle = self.image_settings.rotation

        if angle % 360 == 0:
            return width, height

        radians = math.radians(angle)

        cos_value = abs(math.cos(radians))
        sin_value = abs(math.sin(radians))

        rotated_width = math.ceil(width * cos_value + height * sin_value)
        rotated_height = math.ceil(width * sin_value + height * cos_value)

        return rotated_width, rotated_height

    def _apply_linear_correction(self, image: Image.Image) -> Image.Image:
        grayscale = image.convert("L")

        min_value, max_value = grayscale.getextrema()

        if min_value == max_value:
            return grayscale

        return grayscale.point(
            lambda pixel: int(
                (pixel - min_value) * 255 / (max_value - min_value)
            )
        )

    def _apply_gamma_correction(self, image: Image.Image) -> Image.Image:
        gamma = self.image_settings.gamma

        if gamma == 1.0:
            return image

        return image.point(
            lambda pixel: int(
                255 * ((pixel / 255) ** gamma)
            )
        )
