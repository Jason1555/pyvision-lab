import numpy as np
from PIL import Image


class Histogram:
    @staticmethod
    def calculate(image: Image.Image) -> dict[str, np.ndarray]:
        rgba_image = image.convert("RGBA")
        array = np.asarray(rgba_image)

        alpha = array[:, :, 3]

        mask = alpha > 0

        red = array[:, :, 0][mask]
        green = array[:, :, 1][mask]
        blue = array[:, :, 2][mask]

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
        }
