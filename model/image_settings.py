from dataclasses import dataclass

@dataclass
class ImageSettings:
    grayscale: bool = False
    brightness: int = 0
    contrast: int = 0
    saturation: int = 0
    rotation: float = 0.0
