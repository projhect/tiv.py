# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0

from PIL import Image
from ImageData import ImageData

def dump(image: Image.Image, mode: str, html: bool):
    """
    Takes an image and generates a string representation of the image using block characters and ANSI color codes (or HTML).
    """

    w, h = image.size
    image_data = ImageData(w, h)
    
    # Convert image to RGB
    image_rgb = image.convert("RGB")

    for y in range(h):
        for x in range(w):
            r, g, b = image_rgb.getpixel((x, y))
            pos = (y * w + x) * 4
            image_data.data[pos] = r
            image_data.data[pos + 1] = g
            image_data.data[pos + 2] = b

    print(image_data.dump(mode, html))
