import unittest
from unittest.mock import patch, Mock
from tiv_py.load_image import load_image

class TestLoadImage(unittest.TestCase):

    @patch('requests.get')
    @patch('PIL.Image.open')
    def test_load_image_from_url(self, mock_image_open, mock_requests_get):
        # Setup mock for requests.get
        mock_response = Mock()
        expected_image_data = b'image data'
        mock_response.content = expected_image_data
        mock_requests_get.return_value = mock_response

        # Setup mock for PIL.Image.open
        mock_image = Mock()
        mock_image_open.return_value = mock_image

        image = load_image('http://example.com/image.png')

        # Assert that the image was loaded correctly
        mock_requests_get.assert_called_once_with('http://example.com/image.png')
        mock_image_open.assert_called_once()
        self.assertEqual(image, mock_image)

    @patch('PIL.Image.open')
    def test_load_image_from_file(self, mock_image_open):
        # Setup mock for PIL.Image.open
        mock_image = Mock()
        mock_image_open.return_value = mock_image

        image = load_image('/path/to/local/image.png')

        # Assert that the image was loaded correctly
        mock_image_open.assert_called_once_with('/path/to/local/image.png')
        self.assertEqual(image, mock_image)

    @patch('requests.get')
    def test_load_image_from_invalid_url(self, mock_requests_get):
        # Setup mock to raise an exception when requests.get is called
        mock_requests_get.side_effect = Exception("Invalid URL")

        with self.assertRaises(Exception) as context:
            load_image('http://invalid_url/image.png')

        self.assertTrue('Invalid URL' in str(context.exception))

    @patch('PIL.Image.open')
    def test_load_image_from_invalid_file(self, mock_image_open):
        # Setup mock to raise an exception when PIL.Image.open is called
        mock_image_open.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError) as context:
            load_image('/path/to/nonexistent/image.png')

        self.assertTrue('File not found' in str(context.exception))

if __name__ == '__main__':
    unittest.main()
