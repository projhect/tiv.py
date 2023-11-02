# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0

from PIL import Image

def resize_image(original: Image.Image, max_width: int, max_height: int, grayscale: bool) -> Image.Image:
    """
    Resize an image to fit within specified dimensions without cropping or distorting it.
    Optionally, converts the image to grayscale.

    :param original: PIL Image object representing the image to be resized.
    :param max_width: Maximum allowable width for the resized image.
    :param max_height: Maximum allowable height for the resized image.
    :param grayscale: Boolean value indicating if the output image should be in grayscale.
    :return: Resized (and optionally grayscaled) PIL Image object.
    """
    
    # Get the original dimensions of the image.
    original_width, original_height = original.size
    
    # Calculate the scaling factor. The image is scaled by the smallest of the two ratios 
    # (width and height) to ensure it fits within the provided dimensions.
    scale = min(max_width / original_width, max_height / original_height)
    
    # Calculate the new dimensions for the resized image.
    height = int(original_height * scale)
    width = int(original_width * scale)
    
    # Check if the image is already the correct size and not needing grayscaling.
    if original_width == width and not grayscale:
        # If it's already the correct size and doesn't need to be grayscaled, 
        # use the original image.
        image = original
    else:
        # If resizing or grayscaling is needed, process the image accordingly.
        
        # Check if grayscale mode is required.
        if grayscale:
            # Resize the image and convert to grayscale.
            image = original.resize((width, height), Image.LANCZOS).convert('L')
        else:
            # Only resize the image.
            image = original.resize((width, height), Image.LANCZOS)
        
    return image