import unittest
from PIL import Image
from tiv_py.resize_image import resize_image

class TestResizeImage(unittest.TestCase):

    def setUp(self):
        # Create a test image
        self.original = Image.new('RGB', (800, 600), color = 'red')

    def test_resize_downscale(self):
        # Test that the image is downscaled correctly
        max_width, max_height = 400, 300
        resized = resize_image(self.original, max_width, max_height, False)
        self.assertEqual(resized.size, (400, 300))

    def test_resize_no_change(self):
        # Test that the image is unchanged if it's already within the max dimensions
        max_width, max_height = 800, 600
        resized = resize_image(self.original, max_width, max_height, False)
        self.assertEqual(resized.size, (800, 600))

    def test_resize_grayscale(self):
        # Test that the image is converted to grayscale
        max_width, max_height = 800, 600
        resized = resize_image(self.original, max_width, max_height, True)
        self.assertEqual(resized.mode, 'L')
        self.assertEqual(resized.size, (800, 600))

    def test_resize_aspect_ratio_maintained(self):
        # Test that the aspect ratio is maintained during resize
        max_width, max_height = 200, 600
        resized = resize_image(self.original, max_width, max_height, False)
        self.assertEqual(resized.size, (200, 150))

    def test_resize_larger_dimensions(self):
        # Test that the image is upscaled if the max dimensions are larger than the image
        max_width, max_height = 1000, 1000
        resized = resize_image(self.original, max_width, max_height, False)
        self.assertEqual(resized.size, (1000, 750))

if __name__ == '__main__':
    unittest.main()
