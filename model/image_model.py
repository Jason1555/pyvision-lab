import datetime
import math

from pathlib import Path
from PIL import ExifTags, Image, ImageEnhance, ImageOps

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
            raise FileNotFoundError(f"Файл не найден: {path}")

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
            raise RuntimeError("Изображение не загружено")

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

    def get_color_depth(self) -> int | str | None:
        if self.image is None:
            return None

        mode_depth = {
            "1": 1,
            "L": 8,
            "P": 8,
            "LA": 16,
            "PA": 16,
            "RGB": 24,
            "RGBA": 32,
            "RGBa": 32,
            "CMYK": 32,
            "YCbCr": 24,
            "LAB": 24,
            "HSV": 24,
            "I": 32,
            "I;16": 16,
            "I;16B": 16,
            "I;16L": 16,
            "F": 32,
        }

        if self.image.mode in mode_depth:
            return mode_depth[self.image.mode]

        # Fallback: число каналов * 8 бит.
        try:
            return len(self.image.getbands()) * 8
        except Exception:
            return "Неизвестно"

    def get_format(self) -> str | None:
        if self.image is None:
            return None

        if self.image.format:
            return self.image.format

        # Fallback для изображений без установленного format.
        if self.file_path is not None and self.file_path.suffix:
            return self.file_path.suffix.lstrip(".").upper()

        return "Неизвестно"

    def get_color_model(self) -> str:
        if self.image is None:
            raise RuntimeError("Изображение не загружено")

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

            exif_data[tag_name] = self._format_exif_value(value)

        return exif_data

    @staticmethod
    def _format_exif_value(value) -> str:
        # IFDRational (например ExposureTime) -> читаемая дробь/число.
        try:
            from PIL.TiffImagePlugin import IFDRational

            if isinstance(value, IFDRational):
                try:
                    as_float = float(value)
                except Exception:
                    as_float = None
                if as_float is not None:
                    if value.denominator in (0, 1) or as_float >= 1:
                        return f"{as_float:.3g}"
                    return f"{value.numerator}/{value.denominator} ({as_float:.4g})"
                return f"{value.numerator}/{value.denominator}"
        except ImportError:
            pass

        if isinstance(value, bytes):
            try:
                text = value.decode("utf-8", errors="replace").strip().strip("\x00")
                return text if text else repr(value)
            except Exception:
                return repr(value)

        if isinstance(value, tuple):
            return ", ".join(ImageModel._format_exif_value(v) for v in value)

        text = str(value).strip()
        # Обрезаем слишком длинные сырые дампы.
        if len(text) > 300:
            text = text[:300] + "…"
        return text

    def get_extra_info(self) -> dict[str, str]:
        """Другая полезная информация для панели (пункт ТЗ)."""
        if self.image is None:
            return {}

        width, height = self.image.size
        bands = self.image.getbands()
        channels = len(bands)
        megapixels = width * height / 1_000_000
        memory_bytes = width * height * channels

        # Соотношение сторон.
        gcd = math.gcd(width, height) or 1
        aspect = f"{width // gcd}:{height // gcd}"

        if width > height:
            orientation = "Альбомная"
        elif height > width:
            orientation = "Портретная"
        else:
            orientation = "Квадратная"

        dpi = self.image.info.get("dpi", None)
        try:
            if isinstance(dpi, tuple) and len(dpi) == 2:
                dpi_text = f"{float(dpi[0]):.0f} x {float(dpi[1]):.0f}"
            elif dpi is not None:
                dpi_text = str(dpi)
            else:
                dpi_text = "—"
        except Exception:
            dpi_text = str(dpi)

        mtime_text = "—"
        if self.file_path is not None:
            try:
                ts = self.file_path.stat().st_mtime
                mtime_text = datetime.datetime.fromtimestamp(ts).strftime(
                    "%Y-%m-%d %H:%M"
                )
            except OSError:
                pass

        return {
            "Мегапиксели": f"{megapixels:.2f} Мп",
            "Пропорции": f"{aspect} ({orientation})",
            "Каналы": f"{channels} ({'/'.join(bands)})",
            "В памяти": self._format_bytes(memory_bytes),
            "DPI": dpi_text,
            "Изменён": mtime_text,
        }

    @staticmethod
    def _format_bytes(size: int) -> str:
        if size < 1024:
            return f"{size} B"
        if size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"
        if size < 1024 ** 3:
            return f"{size / 1024 ** 2:.2f} MB"
        return f"{size / 1024 ** 3:.2f} GB"

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
            result = self._apply_rotation(result)

        return result

    def save_processed_image(self, file_path: str):
        if self.image is None:
            raise RuntimeError("Изображение не загружено")

        result = self.process_image(preview=False)

        if result is None:
            raise RuntimeError("Не удалось обработать изображение")

        path = Path(file_path)

        if not path.suffix:
            raise ValueError(
                "Укажите расширение файла изображения."
            )

        suffix = path.suffix.lower()

        save_kwargs = {}
        # Пробрасываем EXIF, чтобы не терять метаданные (JPEG/TIFF).
        try:
            original_exif = self.image.getexif()
            if len(original_exif):
                # После поворота размеры/ориентация из оригинала врут,
                # поэтому чистим зависимые от геометрии теги.
                if self.image_settings.rotation % 360 != 0:
                    for tag_id in (274, 256, 257, 40962, 40963):
                        try:
                            if tag_id in original_exif:
                                del original_exif[tag_id]
                        except Exception:
                            pass
                if len(original_exif):
                    save_kwargs["exif"] = original_exif
        except Exception:
            pass

        if suffix in {".jpg", ".jpeg"}:
            if result.mode in {"RGBA", "LA", "PA", "P"}:
                # Белый фон вместо чёрного для прозрачных областей.
                background = Image.new("RGB", result.size, (255, 255, 255))
                alpha = None
                try:
                    alpha = result.split()[-1]
                except Exception:
                    alpha = None
                if alpha is not None:
                    background.paste(result.convert("RGB"), mask=alpha)
                    result = background
                else:
                    result = result.convert("RGB")
            elif result.mode != "RGB":
                result = result.convert("RGB")

            result.save(
                path,
                format="JPEG",
                quality=95,
                **save_kwargs,
            )
            return

        if suffix in {".tif", ".tiff"} and result.mode == "P":
            result = result.convert("RGB")

        # PNG не всегда принимает EXIF от JPEG — пробуем с EXIF,
        # при ошибке сохраняем без метаданных.
        try:
            result.save(path, **save_kwargs)
        except Exception:
            result.save(path)

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

    # Процент выбросов, отрезаемых с каждого края при линейной
    # коррекции. Старый min/max ломался от 1 битого пикселя
    # (0 или 255) — растяжка превращалась в тождество.
    LINEAR_CUT = 2.0

    def _apply_linear_correction(self, image: Image.Image) -> Image.Image:
        # Линейная растяжка с отсечкой выбросов (перцентили).
        # 2% самых тёмных становится 0, 2% самых светлых — 255,
        # остальное линейно. Работает строго для ЧБ (mode "L"):
        # для цветного кнопка заблокирована в ToolPanel (вариант А).
        # Цветной вход (если флаг выставили напрямую) сначала
        # переводим в яркость L, чтобы не уводить баланс белого.
        if image.mode != "L":
            image = image.convert("L")

        if self._is_flat(image):
            return image

        return ImageOps.autocontrast(
            image, cutoff=self.LINEAR_CUT, preserve_tone=False,
        )

    @staticmethod
    def _is_flat(band: Image.Image) -> bool:
        """Однотонный канал: растягивать нечего."""
        try:
            lo, hi = band.getextrema()
            return lo == hi
        except Exception:
            return True

    def _apply_gamma_correction(self, image: Image.Image) -> Image.Image:
        gamma = self.image_settings.gamma

        if gamma == 1.0:
            return image

        # LUT быстрее и точнее, чем point(lambda) для каждого пикселя.
        lut_1ch = [
            max(0, min(255, round(255 * ((i / 255) ** gamma))))
            for i in range(256)
        ]
        bands = len(image.getbands())
        return image.point(lut_1ch * bands)

    def _apply_rotation(self, image: Image.Image) -> Image.Image:
        # Угол в модели — clockwise-положительный (вправо = плюс,
        # как показывает dial). Pillow крутит наоборот
        # (плюс = против часовой), поэтому инвертируем один раз здесь.
        pil_angle = -self.image_settings.rotation
        angle = pil_angle % 360

        # Точный поворот на кратные 90° без интерполяции и прозрачных полей.
        if angle % 90 == 0:
            steps = int(round(angle / 90)) % 4
            transpose_map = {
                1: Image.Transpose.ROTATE_90,
                2: Image.Transpose.ROTATE_180,
                3: Image.Transpose.ROTATE_270,
            }
            if steps in transpose_map:
                return image.transpose(transpose_map[steps])
            return image

        rgba_image = image.convert("RGBA")
        return rgba_image.rotate(
            pil_angle,
            expand=True,
            resample=Image.Resampling.BILINEAR,
            fillcolor=(0, 0, 0, 0),
        )
