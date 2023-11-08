import unittest
from unittest.mock import patch
from tiv_py.ImageData import ImageData

def hex6(self, r: int, g: int, b: int) -> str:
    # Ensure each component is exactly two hex digits
    return f"{r:02x}{g:02x}{b:02x}"

class TestImageData(unittest.TestCase):
    
    def setUp(self):
        self.width = 8  # Assuming a width of 8 for simplicity
        self.height = 8  # Assuming a height of 8 for simplicity
        self.image_data = ImageData(self.width, self.height)
        # Fill the data with a simple pattern: top half red (255, 0, 0), bottom half green (0, 255, 0)
        for i in range(self.width * self.height // 2):
            self.image_data.data[i * 4:(i + 1) * 4] = bytearray([255, 0, 0, 0])
        for i in range(self.width * self.height // 2, self.width * self.height):
            self.image_data.data[i * 4:(i + 1) * 4] = bytearray([0, 255, 0, 0])

    def test_dump_html(self):
        # Test HTML output
        html_output = self.image_data.dump('256', html=True)
        self.assertIn("<tt style='background-color:#1ff0000;color:#100ff00'>", html_output)
        self.assertIn("&#x2584;", html_output)
        self.assertIn("</tt><br />\n", html_output)

    def test_dump_ansi(self):
        # Test ANSI terminal output
        ansi_output = self.image_data.dump('256', html=False)
        # Since the ANSI output is more complex and may include escape codes, we will just check that it includes the reset code
        self.assertIn('\x1b[0m', ansi_output)
        self.assertIn('\x1b[38;5;46m', ansi_output)
        self.assertIn('▄▄', ansi_output)
        self.assertIn('\x1b[0m\n', ansi_output)

if __name__ == '__main__':
    unittest.main()
