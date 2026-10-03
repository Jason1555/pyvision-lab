import numpy as np
from PIL import Image


class Histogram:
    # Больше этого числа пикселей — считаем гистограмму
    # по уменьшенной копии (достаточно для кривой 256 бинов).
    MAX_PIXELS = 600_000

    @staticmethod
    def _downscale(image: Image.Image) -> Image.Image:
        width, height = image.size
        total = width * height
        if total <= Histogram.MAX_PIXELS or total == 0:
            return image
        scale = (Histogram.MAX_PIXELS / total) ** 0.5
        new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
        try:
            return image.resize(new_size, Image.Resampling.BILINEAR)
        except Exception:
            return image

    @staticmethod
    def calculate(image: Image.Image) -> dict[str, np.ndarray]:
        # Уменьшаем ДО всех convert/asarray — меньше копий больших массивов.
        small = Histogram._downscale(image)

        # ЧБ: одна кривая яркости вместо трёх одинаковых R=G=B.
        if small.mode == "L":
            gray = np.asarray(small).ravel()
            hist = np.bincount(gray, minlength=256)
            return {"L": hist}

        rgba_image = small.convert("RGBA") if small.mode != "RGBA" else small
        array = np.asarray(rgba_image)

        alpha = array[:, :, 3]

        mask = alpha > 0
        # Полностью прозрачное изображение: пустые гистограммы,
        # чтобы не было bincount по пустому массиву без маски.
        if not mask.any():
            empty = np.zeros(256, dtype=np.int64)
            gray_empty = np.zeros(256, dtype=np.int64)
            return {"R": empty, "G": empty, "B": empty, "L": gray_empty}

        red = array[:, :, 0][mask]
        green = array[:, :, 1][mask]
        blue = array[:, :, 2][mask]

        # Яркость из уже замаскированных каналов — без второго
        # convert("L") и без копирования всего изображения.
        gray = (
            (0.299 * red.astype(np.float32))
            + (0.587 * green.astype(np.float32))
            + (0.114 * blue.astype(np.float32))
        ).astype(np.uint8)
        gray_hist = np.bincount(gray, minlength=256)

        return {
            "R": np.bincount(
                red,
                minlength=256,
            ),
            "G": np.bincount(
                green,
                minlength=256,
            ),
            "B": np.bincount(
                blue,
                minlength=256,
            ),
            "L": gray_hist,
        }

    @staticmethod
    def stats(
        image: Image.Image,
        hist: dict[str, np.ndarray] | None = None,
    ) -> dict[str, float]:
        """Краткая статистика для подписи под гистограммой.

        Принимает уже посчитанную гистограмму — mean/median/std
        выводятся из 256 бинов, без сортировки миллионов пикселей.
        Пустое или полностью прозрачное изображение -> нули.
        """
        try:
            if hist is None:
                hist = Histogram.calculate(image)

            def _mean(keys: tuple[str, ...]) -> float:
                merged = None
                for key in keys:
                    if key in hist:
                        merged = hist[key] if merged is None else merged + hist[key]
                if merged is None:
                    return 0.0
                total = float(merged.sum())
                if total <= 0:
                    return 0.0
                bins = np.arange(256, dtype=np.float64)
                return float((merged * bins).sum() / total)

            def _median_std(key: str) -> tuple[float, float]:
                data = hist.get(key)
                if data is None:
                    return 0.0, 0.0
                total = float(data.sum())
                if total <= 0:
                    return 0.0, 0.0
                bins = np.arange(256, dtype=np.float64)
                cumsum = np.cumsum(data)
                median = float(np.searchsorted(cumsum, total / 2.0))
                mean = float((data * bins).sum() / total)
                var = float(((bins - mean) ** 2 * data).sum() / total)
                return median, float(var ** 0.5)

            gray_key = "L" if "L" in hist else None
            if gray_key is None:
                return {
                    "mean": 0.0, "median": 0.0, "std": 0.0,
                    "mean_r": 0.0, "mean_g": 0.0, "mean_b": 0.0,
                    "black_pct": 0.0, "white_pct": 0.0, "total": 0.0,
                }

            total = float(hist[gray_key].sum())
            median, std = _median_std(gray_key)
            black_pct = float(hist[gray_key][0] * 100.0 / total) if total else 0.0
            white_pct = float(hist[gray_key][255] * 100.0 / total) if total else 0.0

            return {
                "mean": _mean((gray_key,)),
                "median": median,
                "std": std,
                "mean_r": _mean(("R",)) if "R" in hist else _mean((gray_key,)),
                "mean_g": _mean(("G",)) if "G" in hist else _mean((gray_key,)),
                "mean_b": _mean(("B",)) if "B" in hist else _mean((gray_key,)),
                "black_pct": black_pct,
                "white_pct": white_pct,
                "total": total,
            }
        except Exception:
            return {
                "mean": 0.0, "median": 0.0, "std": 0.0,
                "mean_r": 0.0, "mean_g": 0.0, "mean_b": 0.0,
                "black_pct": 0.0, "white_pct": 0.0, "total": 0.0,
            }
