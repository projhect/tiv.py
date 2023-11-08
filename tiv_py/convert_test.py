import unittest
from unittest.mock import Mock
from unittest.mock import patch
from tiv_py.convert import convert

class TestConvertFunction(unittest.TestCase):

    @patch('tiv_py.convert.load_image')
    @patch('tiv_py.convert.resize_image')
    @patch('tiv_py.convert.dump')
    def test_convert(self, mock_dump, mock_resize_image, mock_load_image):
        # Arrange
        test_image_name = 'test_image.jpg'
        max_width = 80
        max_height = 60
        mode = '256'
        html = False
        grayscale = False

        # mock objects for the image
        original_image_mock = Mock()
        resized_image_mock = Mock()

        # Set the return values of the mocked functions
        mock_load_image.return_value = original_image_mock
        mock_resize_image.return_value = resized_image_mock

        # Act
        convert(test_image_name, max_width, max_height, mode, html, grayscale)

        # Assert
        # Check if load_image was called with the correct filename
        mock_load_image.assert_called_once_with(test_image_name)

        # Check if resize_image was called with the correct parameters
        mock_resize_image.assert_called_once_with(original_image_mock, max_width, max_height, grayscale)

        # Check if dump was called with the resized image and the correct parameters
        mock_dump.assert_called_once_with(resized_image_mock, mode, html)

if __name__ == '__main__':
    unittest.main()
