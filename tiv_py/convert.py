# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0

from load_image import load_image
from resize_image import resize_image
from dump import dump

def convert(name: str, max_width: int, max_height: int, mode: str, html: bool, grayscale: bool):
    """
    Resizes an image, if necessary, to fit within a given width and height, and then dumps its colored block character representation to the terminal or as HTML.
    """

    original = load_image(name)
    image = resize_image(original, max_width, max_height, grayscale)
    dump(image, mode, html)
