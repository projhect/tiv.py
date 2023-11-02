# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0

# List of bit patterns corresponding to various block characters.
# For use in approximating parts of the image with ASCII characters.
BITMAPS = [    
    0x00000000, '\u00a0',

    # Block graphics
    # 0xffff0000, '\u2580',  # upper 1/2; redundant with inverse lower 1/2

    0x0000000f, '\u2581',  # lower 1/8
    0x000000ff, '\u2582',  # lower 1/4
    0x00000fff, '\u2583',
    0x0000ffff, '\u2584',  # lower 1/2
    0x000fffff, '\u2585',
    0x00ffffff, '\u2586',  # lower 3/4
    0x0fffffff, '\u2587',
    # 0xffffffff, '\u2588',  # full; redundant with inverse space

    0xeeeeeeee, '\u258a',  # left 3/4
    0xcccccccc, '\u258c',  # left 1/2
    0x88888888, '\u258e',  # left 1/4

    0x0000cccc, '\u2596',  # quadrant lower left
    0x00003333, '\u2597',  # quadrant lower right
    0xcccc0000, '\u2598',  # quadrant upper left
    # 0xccccffff, '\u2599',  # 3/4 redundant with inverse 1/4
    0xcccc3333, '\u259a',  # diagonal 1/2
    # 0xffffcccc, '\u259b',  # 3/4 redundant
    # 0xffff3333, '\u259c',  # 3/4 redundant
    0x33330000, '\u259d',  # quadrant upper right
    # 0x3333cccc, '\u259e',  # 3/4 redundant
    # 0x3333ffff, '\u259f',  # 3/4 redundant

    # Line drawing subset: no double lines, no complex light lines
    # Simple light lines duplicated because there is no center pixel int the 4x8 matrix

    0x000ff000, '\u2501',  # Heavy horizontal
    0x66666666, '\u2503',  # Heavy vertical

    0x00077666, '\u250f',  # Heavy down and right
    0x000ee666, '\u2513',  # Heavy down and left
    0x66677000, '\u2517',  # Heavy up and right
    0x666ee000, '\u251b',  # Heavy up and left

    0x66677666, '\u2523',  # Heavy vertical and right
    0x666ee666, '\u252b',  # Heavy vertical and left
    0x000ff666, '\u2533',  # Heavy down and horizontal
    0x666ff000, '\u253b',  # Heavy up and horizontal
    0x666ff666, '\u254b',  # Heavy cross

    0x000cc000, '\u2578',  # Bold horizontal left
    0x00066000, '\u2579',  # Bold horizontal up
    0x00033000, '\u257a',  # Bold horizontal right
    0x00066000, '\u257b',  # Bold horizontal down

    0x06600660, '\u254f',  # Heavy double dash vertical

    0x000f0000, '\u2500',  # Light horizontal
    0x0000f000, '\u2500',  
    0x44444444, '\u2502',  # Light vertical
    0x22222222, '\u2502',

    0x000e0000, '\u2574',  # light left
    0x0000e000, '\u2574',  # light left
    0x44440000, '\u2575',  # light up
    0x22220000, '\u2575',  # light up
    0x00030000, '\u2576',  # light right
    0x00003000, '\u2576',  # light right
    0x00004444, '\u2575',  # light down
    0x00002222, '\u2575',  # light down

    # Misc technical

    0x44444444, '\u23a2',  # [ extension
    0x22222222, '\u23a5',  # ] extension

    #12345678
    0x0f000000, '\u23ba',  # Horizontal scanline 1
    0x00f00000, '\u23bb',  # Horizontal scanline 3
    0x00000f00, '\u23bc',  # Horizontal scanline 7
    0x000000f0, '\u23bd',  # Horizontal scanline 9

    # Geometrical shapes. Tricky because some of them are too wide.

    # 0x00ffff00, '\u25fe',  # Black medium small square
    0x00066000, '\u25aa',  # Black small square

    # 0x11224488, '\u2571',  # diagonals
    # 0x88442211, '\u2572',
    # 0x99666699, '\u2573',

    # 0x000137f0, '\u25e2',  # Triangles
    # 0x0008cef0, '\u25e3',
    # 0x000fec80, '\u25e4',
    # 0x000f7310, '\u25e5'
]

class BlockChar:
    """
    Processes 4x8 pixel blocks of an image and finds the best matching block character and its foreground and background colors.
    """

    def __init__(self):
        self.min = [255, 255, 255]
        self.max = [0, 0, 0]
        self.bg_color = [0, 0, 0]
        self.fg_color = [0, 0, 0]
        self.character = ' '

    def bit_count(self, n: int):
        return bin(n).count("1")

    def load(self, data: bytearray, p0: int, scan_width: int):
        """
        Computes average colors for the foreground and background of the block, determines which channel (red, green, blue) has the greatest range of values, and generates a bitmap that represents which pixels are above/below the midpoint of that range.
        Then finds the block character from the BITMAPS list that best matches the computed bitmap. If no good match is found, it uses a shading character.
        """
        
        self.min = [255, 255, 255]
        self.max = [0, 0, 0]
        self.bg_color = [0, 0, 0]
        self.fg_color = [0, 0, 0]

        # Determine the min and max values for each color channel
        pos = p0
        for y in range(8):
            for x in range(4):
                for i in range(3):
                    d = data[pos] & 255
                    self.min[i] = min(self.min[i], d)
                    self.max[i] = max(self.max[i], d)
                    pos += 1
                pos += 1  # Alpha
            pos += scan_width - 16

        # Determine the color channel with the most significant range
        splitIndex = 0
        best_split = 0
        for i in range(3):
            if self.max[i] - self.min[i] > best_split:
                best_split = self.max[i] - self.min[i]
                splitIndex = i
        split_value = self.min[splitIndex] + best_split // 2

        # Compute a bitmap using the given split and sum the color values for both buckets
        bits = 0
        fg_count = 0
        bg_count = 0
        pos = p0
        for y in range(8):
            for x in range(4):
                bits <<= 1
                if (data[pos + splitIndex] & 255) > split_value:
                    avg = self.fg_color
                    bits |= 1
                    fg_count += 1
                else:
                    avg = self.bg_color
                    bg_count += 1
                for i in range(3):
                    avg[i] += data[pos] & 255
                    pos += 1
                pos += 1  # Alpha
            pos += scan_width - 16

        # Calculate the average color value for each bucket
        for i in range(3):
            if bg_count:
                self.bg_color[i] //= bg_count
            if fg_count:
                self.fg_color[i] //= fg_count

        # Find the best bitmap match
        best_diff = float("inf")
        invert = False
        for i in range(0, len(BITMAPS), 2):
            diff = self.bit_count(BITMAPS[i] ^ bits)
            if diff < best_diff:
                self.character = BITMAPS[i + 1]
                best_diff = diff
                invert = False
            diff = self.bit_count(~BITMAPS[i] & 0xFFFFFFFF ^ bits)
            if diff < best_diff:
                self.character = BITMAPS[i + 1]
                best_diff = diff
                invert = True

        # Use a shade image if the match is not good
        if best_diff > 10:
            invert = False
            shades = " \u2591\u2592\u2593\u2588"
            self.character = shades[min(4, fg_count * 5 // 32)]

        # Swap colors if we use an inverted character
        if invert:
            self.bg_color, self.fg_color = self.fg_color, self.bg_color