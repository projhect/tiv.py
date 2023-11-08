import unittest
from unittest.mock import Mock, patch
from io import StringIO
import sys
from PIL import Image
from tiv_py.dump import dump

class TestDumpFunction(unittest.TestCase):

    def setUp(self):
        # Create a test image
        self.image = Mock(spec=Image.Image)
        self.image.size = (2, 2)  # Example size
        self.image.convert.return_value.getpixel.return_value = (255, 0, 0)  # Every pixel is red for simplicity

        # Mock ImageData
        self.image_data_mock = Mock()
        self.image_data_mock.data = [0] * (2 * 2 * 4)  # Example data buffer for 2x2 image with RGB values
        
        # Patch the print function to capture output
        self.capturedOutput = StringIO()
        sys.stdout = self.capturedOutput

    def test_dump_with_ansi(self):
        # Test the dump function with ANSI output mode
        with patch('tiv_py.dump.ImageData', return_value=self.image_data_mock):
            # Configure the mock to return the expected ANSI string
            self.image_data_mock.dump.return_value = "\x1b[48;2;255;0;0m \x1b[0m\n" * 2  # Assuming a 2x2 image produces 2 blocks of red
    
            dump(self.image, mode='256', html=False)
            expected_output = self.image_data_mock.dump.return_value
    
            self.assertEqual(self.capturedOutput.getvalue().strip(), expected_output.strip())

    def test_dump_with_html(self):
        # Test the dump function with HTML output mode
        with patch('tiv_py.dump.ImageData', return_value=self.image_data_mock):
            # Configure the mock to return the expected HTML string
            self.image_data_mock.dump.return_value = '<span style="background-color: #ff0000;"> </span>\n' * 2  # Assuming a 2x2 image produces 4 spans

            dump(self.image, mode='256', html=True)
            expected_output = self.image_data_mock.dump.return_value  # Expected output string

            # Assert that the expected HTML output is in the captured output
            self.assertEqual(self.capturedOutput.getvalue().strip(), expected_output.strip())

    def tearDown(self):
        # Restore stdout
        sys.stdout = sys.__stdout__

if __name__ == '__main__':
    unittest.main()
    