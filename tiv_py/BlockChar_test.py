import unittest
from unittest.mock import patch
from tiv_py.BlockChar import BlockChar, BITMAPS 

class TestBlockChar(unittest.TestCase):

    def setUp(self):
        self.block_char = BlockChar()

    def test_bit_count(self):
        self.assertEqual(self.block_char.bit_count(0b101010), 3)
        self.assertEqual(self.block_char.bit_count(0b11111111), 8)
        self.assertEqual(self.block_char.bit_count(0), 0)

    @patch('tiv_py.BlockChar.BITMAPS', [0b1111, 'X', ~0b1111 & 0xFFFFFFFF, 'X'])
    def test_load(self):
        data = bytearray([255, 0, 0, 255] * 32)  # 4x8 block of red pixels
        self.block_char.load(data, 0, 16)
        self.assertEqual(self.block_char.bg_color, [255, 0, 0])
        self.assertEqual(self.block_char.fg_color, [0, 0, 0])
        self.assertEqual(self.block_char.character, 'X')

        data = bytearray([0, 0, 255, 255] * 32)  # 4x8 block of blue pixels
        self.block_char.load(data, 0, 16)
        self.assertEqual(self.block_char.bg_color, [0, 0, 255])
        self.assertEqual(self.block_char.fg_color, [0, 0, 0])
        self.assertEqual(self.block_char.character, 'X')

if __name__ == '__main__':
    unittest.main()
