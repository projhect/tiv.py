# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0

from PIL import Image
import requests
from io import BytesIO

def load_image(name: str) -> Image.Image:
    """
    Loads an image from a local file or a URL.
    """

    # Check if the given string is a URL
    if name.startswith("http://") or name.startswith("https://"):
        response = requests.get(name)
        return Image.open(BytesIO(response.content))
    return Image.open(name)