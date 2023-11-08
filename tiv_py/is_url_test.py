import unittest
from tiv_py.is_url import is_url

class TestIsUrl(unittest.TestCase):

    def test_is_url_with_http(self):
        self.assertTrue(is_url("http://example.com"))

    def test_is_url_with_https(self):
        self.assertTrue(is_url("https://example.com"))

    def test_is_url_without_http_or_https(self):
        self.assertFalse(is_url("ftp://example.com"))

    def test_is_url_with_none(self):
        self.assertFalse(is_url(None))

    def test_is_url_with_empty_string(self):
        self.assertFalse(is_url(""))

    def test_is_url_with_whitespace(self):
        self.assertFalse(is_url(" http://example.com"))

    def test_is_url_with_mixed_case(self):
        self.assertFalse(is_url("HtTp://example.com"))
        self.assertFalse(is_url("HtTpS://example.com"))

    # Add more tests as necessary to cover edge cases and other protocols if needed.

if __name__ == '__main__':
    unittest.main()
