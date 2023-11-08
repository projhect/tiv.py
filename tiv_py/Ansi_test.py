import unittest
from tiv_py.Ansi import Ansi

class TestAnsiClass(unittest.TestCase):

    def test_best_index(self):
        self.assertEqual(Ansi.best_index(0, Ansi.COLOR_STEPS), 0)
        self.assertEqual(Ansi.best_index(127, Ansi.COLOR_STEPS), 2)
        self.assertEqual(Ansi.best_index(255, Ansi.GRAYSCALE), 23)

    def test_sqr(self):
        self.assertEqual(Ansi.sqr(10), 100)
        self.assertEqual(Ansi.sqr(-5), 25)

    def test_clamp(self):
        self.assertEqual(Ansi.clamp(256, 0, 255), 255)
        self.assertEqual(Ansi.clamp(-1, 0, 255), 0)
        self.assertEqual(Ansi.clamp(127, 0, 255), 127)

    def test_color_256_mode(self):
        # Test 256-color mode
        self.assertEqual(Ansi.color(Ansi.MODE_256, 0, 0, 0), "\u001B[38;5;16m")
        self.assertEqual(Ansi.color(Ansi.MODE_256 | Ansi.BG, 255, 0, 0), "\u001B[48;5;196m")

    def test_color_24bit_mode(self):
        # Test true color mode
        self.assertEqual(Ansi.color(0, 255, 0, 0), "\u001b[38;2;255;0;0m")
        self.assertEqual(Ansi.color(Ansi.BG, 0, 0, 255), "\u001b[48;2;0;0;255m")

if __name__ == '__main__':
    unittest.main()
