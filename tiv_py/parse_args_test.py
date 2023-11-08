import unittest
from unittest.mock import patch
from tiv_py.parse_args import parse_args

class TestParseArgs(unittest.TestCase):

    @patch('tiv_py.parse_args.os.path.isfile', return_value=True)  # Mock os.path.isfile to always return True
    @patch('tiv_py.parse_args.is_url', return_value=False)  # Mock is_url to always return False
    def test_valid_local_image_source(self, mock_is_url, mock_isfile):
        test_args = ["local_image.png"]
        with patch('sys.argv', ['prog'] + test_args):
            args = parse_args()
            self.assertEqual(args.image_source, "local_image.png")
            self.assertFalse(args.stdin)
            self.assertEqual(args.mode, '256')
            self.assertEqual(args.max_width, 80)
            self.assertEqual(args.max_height, 24)
            self.assertFalse(args.grayscale)

    @patch('tiv_py.is_url', return_value=True)  # Mock is_url to always return True
    def test_valid_url_image_source(self, mock_is_url):
        test_args = ["http://example.com/image.png"]
        with patch('sys.argv', ['prog'] + test_args):
            args = parse_args()
            self.assertEqual(args.image_source, "http://example.com/image.png")
            self.assertFalse(args.stdin)

    def test_stdin_flag(self):
        test_args = ["--stdin"]
        with patch('sys.argv', ['prog'] + test_args):
            args = parse_args()
            self.assertTrue(args.stdin)

    @patch('tiv_py.parse_args.os.path.isfile', return_value=True)  # Mock os.path.isfile to always return True
    def test_html_flag(self, mock_isfile):
        test_args = ["local_image.png", "--html"]
        with patch('sys.argv', ['prog'] + test_args):
            args = parse_args()
            self.assertTrue(args.html)

    @patch('tiv_py.parse_args.os.path.isfile', return_value=True)
    @patch('tiv_py.parse_args.is_url', return_value=False)  # Assuming is_url is a function you've defined elsewhere
    def test_max_width_height(self, mock_isfile, mock_isurl):
        test_args = ["local_image.png", "--max_width", "100", "--max_height", "50"]
        with patch('sys.argv', ['prog'] + test_args):
            args = parse_args()
            self.assertEqual(args.max_width, 100)
            self.assertEqual(args.max_height, 50)

    @patch('tiv_py.parse_args.argparse.ArgumentParser.error')  # Mock the error method of ArgumentParser
    @patch('tiv_py.parse_args.os.path.isfile', return_value=False)  # Mock os.path.isfile to always return False
    @patch('tiv_py.parse_args.is_url', return_value=False)  # Mock is_url to always return False
    def test_invalid_image_source(self, mock_is_url, mock_isfile, mock_error):
        test_args = ["non_existent_image.png"]
        with patch('sys.argv', ['prog'] + test_args):
            parse_args()
            mock_error.assert_called_with("Invalid image_source")

if __name__ == '__main__':
    unittest.main()
