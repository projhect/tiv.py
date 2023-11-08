import unittest
from unittest.mock import patch, mock_open
from tiv_py.__main__ import main
from tiv_py.Ansi import Ansi

class TestMainFunction(unittest.TestCase):

    @patch('tiv_py.__main__.parse_args')
    @patch('tiv_py.__main__.convert')
    def test_main_with_filename(self, mock_convert, mock_parse_args):
        mock_args = mock_parse_args.return_value
        mock_args.mode = "24bit"
        mock_args.max_width = 20
        mock_args.max_height = 10
        mock_args.stdin = False
        mock_args.html = False
        mock_args.grayscale = False
        mock_args.image_source = "image.png"
        
        main()
        
        mock_convert.assert_called_once_with(
            "image.png", 80, 80, Ansi.MODE_24BIT, False, False
        )

@patch('tiv_py.parse_args')
@patch('sys.stdin', new_callable=mock_open, read_data="image.png\n\n")
@patch('tiv_py.__main__.convert')
def test_main_with_stdin(self, mock_convert, mock_stdin, mock_parse_args):
    mock_args = mock_parse_args.return_value
    mock_args.mode = "256"
    mock_args.max_width = 20
    mock_args.max_height = 10
    mock_args.stdin = True
    mock_args.html = False
    mock_args.grayscale = False
    mock_args.image_source = None
    
    with self.assertRaises(SystemExit) as cm:
        main()
    self.assertEqual(cm.exception.code, 2)
    
    # If the above passes, meaning the SystemExit occurred with the expected code,
    # now ensure convert was called with the correct parameters. However, if the
    # SystemExit is expected due to incorrect arguments, the below assertion should
    # be removed and the cause of the SystemExit should be corrected instead.
    mock_convert.assert_called_once_with(
        "image.png", 80, 80, Ansi.MODE_256, False, False
    )

if __name__ == '__main__':
    unittest.main()
