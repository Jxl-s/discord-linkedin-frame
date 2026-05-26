from pathlib import Path
from PIL import Image
import numpy as np

ALPHA_PATH = Path(__file__).parent / "assets" / "alpha.png"


def apply_frame(image: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    """
    Composite a colored frame onto a square image using assets/alpha.png.

    The red channel of alpha.png is treated as the frame's alpha mask:
    255 = fully opaque frame color, 0 = fully transparent (shows original image).
    The image is resized to match alpha.png's dimensions if needed.
    Returns an RGBA image.
    """
    alpha_img = Image.open(ALPHA_PATH).convert("RGB")
    w, h = alpha_img.size

    base = image.convert("RGBA").resize((w, h), Image.LANCZOS)

    red_channel = np.array(alpha_img)[:, :, 0]  # shape (h, w), values 0-255

    # Build the frame layer: solid color with alpha = red channel
    r, g, b = color
    frame_arr = np.zeros((h, w, 4), dtype=np.uint8)
    frame_arr[:, :, 0] = r
    frame_arr[:, :, 1] = g
    frame_arr[:, :, 2] = b
    frame_arr[:, :, 3] = red_channel

    frame_layer = Image.fromarray(frame_arr, mode="RGBA")

    result = Image.alpha_composite(base, frame_layer)
    return result
