# Simple program to print images to the shell using 24 bit ANSI color codes and Unicode block graphics characters.
# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0


import bisect
from PIL import Image
import requests
from io import BytesIO
import sys
import os


class Ansi:
    """
    Provides methods for generating ANSI escape sequences for colored text.
    ANSI escape sequences are used to produce colored output in terminals.
    """

    RESET = "\u001b[0m"
    FG = 1
    BG = 2
    MODE_256 = 4
    MODE_24BIT = 8

    COLOR_STEPS = [0, 0x5f, 0x87, 0xaf, 0xd7, 0xff]
    GRAYSCALE = [0x08, 0x12, 0x1c, 0x26, 0x30, 0x3a, 0x44, 0x4e, 0x58, 0x62, 0x6c, 0x76,
                 0x80, 0x8a, 0x94, 0x9e, 0xa8, 0xb2, 0xbc, 0xc6, 0xd0, 0xda, 0xe4, 0xee]

    @staticmethod
    def best_index(v, options):
        index = bisect.bisect_left(options, v)
        if index == len(options) or (index > 0 and v - options[index - 1] < options[index] - v):
            index = index - 1
        return index

    @staticmethod
    def sqr(i):
        return i * i

    @staticmethod
    def clamp(value, min_val, max_val):
        return max(min(value, max_val), min_val)

    @staticmethod
    def color(flags, r, g, b):
        """
        Produces an ANSI sequence for setting foreground or background color in 256-color mode or true color (24-bit) mode.
        """
        r = Ansi.clamp(r, 0, 255)
        g = Ansi.clamp(g, 0, 255)
        b = Ansi.clamp(b, 0, 255)

        bg = (flags & Ansi.BG) != 0

        if (flags & Ansi.MODE_256) == 0:
            return (f"\u001b[48;2;{r};{g};{b}m" if bg else f"\u001b[38;2;{r};{g};{b}m")
        
        r_idx = Ansi.best_index(r, Ansi.COLOR_STEPS)
        g_idx = Ansi.best_index(g, Ansi.COLOR_STEPS)
        b_idx = Ansi.best_index(b, Ansi.COLOR_STEPS)

        r_q = Ansi.COLOR_STEPS[r_idx]
        g_q = Ansi.COLOR_STEPS[g_idx]
        b_q = Ansi.COLOR_STEPS[b_idx]

        gray = round(r * 0.2989 + g * 0.5870 + b * 0.1140)

        gray_idx = Ansi.best_index(gray, Ansi.GRAYSCALE)
        gray_q = Ansi.GRAYSCALE[gray_idx]

        if 0.3 * Ansi.sqr(r_q-r) + 0.59 * Ansi.sqr(g_q-g) + 0.11 *Ansi.sqr(b_q-b) < \
           0.3 * Ansi.sqr(gray_q-r) + 0.59 * Ansi.sqr(gray_q-g) + 0.11 * Ansi.sqr(gray_q-b):
            color_index = 16 + 36 * r_idx + 6 * g_idx + b_idx
        else:
            color_index = 232 + gray_idx  # 1..24 -> 232..255

        return (f"\u001B[48;5;{color_index}m" if bg else f"\u001B[38;5;{color_index}m")


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
        self.bgColor = [0, 0, 0]
        self.fgColor = [0, 0, 0]
        self.character = ' '

    def bit_count(self, n):
        return bin(n).count("1")

    def load(self, data, p0, scanWidth):
        """
        Computes average colors for the foreground and background of the block, determines which channel (red, green, blue) has the greatest range of values, and generates a bitmap that represents which pixels are above/below the midpoint of that range.
        Then finds the block character from the BITMAPS list that best matches the computed bitmap. If no good match is found, it uses a shading character.
        """
        
        self.min = [255, 255, 255]
        self.max = [0, 0, 0]
        self.bgColor = [0, 0, 0]
        self.fgColor = [0, 0, 0]

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
            pos += scanWidth - 16

        # Determine the color channel with the most significant range
        splitIndex = 0
        bestSplit = 0
        for i in range(3):
            if self.max[i] - self.min[i] > bestSplit:
                bestSplit = self.max[i] - self.min[i]
                splitIndex = i
        splitValue = self.min[splitIndex] + bestSplit // 2

        # Compute a bitmap using the given split and sum the color values for both buckets
        bits = 0
        fgCount = 0
        bgCount = 0
        pos = p0
        for y in range(8):
            for x in range(4):
                bits <<= 1
                if (data[pos + splitIndex] & 255) > splitValue:
                    avg = self.fgColor
                    bits |= 1
                    fgCount += 1
                else:
                    avg = self.bgColor
                    bgCount += 1
                for i in range(3):
                    avg[i] += data[pos] & 255
                    pos += 1
                pos += 1  # Alpha
            pos += scanWidth - 16

        # Calculate the average color value for each bucket
        for i in range(3):
            if bgCount:
                self.bgColor[i] //= bgCount
            if fgCount:
                self.fgColor[i] //= fgCount

        # Find the best bitmap match
        bestDiff = float("inf")
        invert = False
        for i in range(0, len(BITMAPS), 2):
            diff = self.bit_count(BITMAPS[i] ^ bits)
            if diff < bestDiff:
                self.character = BITMAPS[i + 1]
                bestDiff = diff
                invert = False
            diff = self.bit_count(~BITMAPS[i] & 0xFFFFFFFF ^ bits)
            if diff < bestDiff:
                self.character = BITMAPS[i + 1]
                bestDiff = diff
                invert = True

        # Use a shade image if the match is not good
        if bestDiff > 10:
            invert = False
            shades = " \u2591\u2592\u2593\u2588"
            self.character = shades[min(4, fgCount * 5 // 32)]

        # Swap colors if we use an inverted character
        if invert:
            self.bgColor, self.fgColor = self.fgColor, self.bgColor


class ImageData:
    """
    Represents the entire image's data and provides the dump method, which converts the image data to colored block characters for terminal or HTML display.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = bytearray(width * height * 4)
        
    def hex6(self, r, g, b):
        return f"{(1 << 24) | ((r & 255) << 16) | ((g & 255) << 8) | (b & 255):06x}"
    
    def dump(self, mode, html):
        output = []
        block_char = BlockChar()
        
        y = 0
        while y < self.height - 7:
            pos = y * self.width * 4
            if html:
                last = ""
                x = 0
                while x < self.width - 3:
                    block_char.load(self.data, pos, self.width * 4)
                    fg = self.hex6(block_char.fgColor[0], block_char.fgColor[1], block_char.fgColor[2])
                    bg = self.hex6(block_char.bgColor[0], block_char.bgColor[1], block_char.bgColor[2])
                    style = f"background-color:#{bg};color:#{fg}"
                    if style != last:
                        if last:
                            output.append("</tt>")
                        output.append(f"<tt style='{style}'>")
                        last = style
                    output.append(f"&#x{(ord(block_char.character)):04x};")
                    pos += 16
                    x += 4
                output.append("</tt><br />\n")
            else:
                last_fg = ""
                last_bg = ""
                x = 0
                while x < self.width - 3:
                    block_char.load(self.data, pos, self.width * 4)
                    fg = Ansi.color(Ansi.FG | mode, block_char.fgColor[0], block_char.fgColor[1], block_char.fgColor[2])
                    bg = Ansi.color(Ansi.BG | mode, block_char.bgColor[0], block_char.bgColor[1], block_char.bgColor[2])
                    if fg != last_fg:
                        output.append(fg)
                        last_fg = fg
                    if bg != last_bg:
                        output.append(bg)
                        last_bg = bg
                    output.append(block_char.character)
                    pos += 16
                    x += 4
                output.append(Ansi.RESET + "\n")
            y += 8
        return ''.join(output)


def dump(image, mode, html):
    """
    Takes an image and generates a string representation of the image using block characters and ANSI color codes (or HTML).
    """

    w, h = image.size
    image_data = ImageData(w, h)
    data = image_data.data
    
    # Convert image to RGB
    image_rgb = image.convert("RGB")

    for y in range(h):
        for x in range(w):
            r, g, b = image_rgb.getpixel((x, y))
            pos = (y * w + x) * 4
            data[pos] = r
            data[pos + 1] = g
            data[pos + 2] = b

    print(image_data.dump(mode, html))


def load_image(name):
    """
    Loads an image from a local file or a URL.
    """

    # Check if the given string is a URL
    if name.startswith("http://") or name.startswith("https://"):
        response = requests.get(name)
        return Image.open(BytesIO(response.content))
    return Image.open(name)


def resize_image(original, maxWidth, maxHeight, grayscale):
    """
    Resize an image to fit within specified dimensions without cropping or distorting it.
    Optionally, converts the image to grayscale.

    :param original: PIL Image object representing the image to be resized.
    :param maxWidth: Maximum allowable width for the resized image.
    :param maxHeight: Maximum allowable height for the resized image.
    :param grayscale: Boolean value indicating if the output image should be in grayscale.
    :return: Resized (and optionally grayscaled) PIL Image object.
    """
    
    # Get the original dimensions of the image.
    originalWidth, originalHeight = original.size
    
    # Calculate the scaling factor. The image is scaled by the smallest of the two ratios 
    # (width and height) to ensure it fits within the provided dimensions.
    scale = min(maxWidth / originalWidth, maxHeight / originalHeight)
    
    # Calculate the new dimensions for the resized image.
    height = int(originalHeight * scale)
    width = int(originalWidth * scale)
    
    # Check if the image is already the correct size and not needing grayscaling.
    if originalWidth == width and not grayscale:
        # If it's already the correct size and doesn't need to be grayscaled, 
        # use the original image.
        image = original
    else:
        # If resizing or grayscaling is needed, process the image accordingly.
        
        # Check if grayscale mode is required.
        if grayscale:
            # Resize the image and convert to grayscale.
            image = original.resize((width, height), Image.LANCZOS).convert('L')
        else:
            # Only resize the image.
            image = original.resize((width, height), Image.LANCZOS)
        
    return image


def convert(name, maxWidth, maxHeight, mode, html, grayscale):
    """
    Resizes an image, if necessary, to fit within a given width and height, and then dumps its colored block character representation to the terminal or as HTML.
    """

    original = load_image(name)
    image = resize_image(original, maxWidth, maxHeight, grayscale)
    dump(image, mode, html)


def main(args):
    """
    Processes command-line arguments and drives the image conversion and display process.
    """

    grayscale = False
    mode = Ansi.MODE_24BIT
    html = False

    if not args:
        print(
            "Image file name required.\n\n"
            " - Use -w and -h to set the maximum width and height in characters (defaults: 80, 24).\n"
            " - Use -256 for 256 color mode, -grayscale for grayscale and -stdin to obtain file names from stdin.\n"
        )
        return

    start = 0
    maxWidth = 80
    maxHeight = 24
    stdin = False
    while start < len(args) and args[start].startswith("-"):
        option = args[start]
        if option == "-w" and start < len(args) - 1:
            start += 1
            maxWidth = int(args[start])
        elif option == "-h" and start < len(args) - 1:
            start += 1
            maxHeight = int(args[start])
        elif option == "-256":
            mode = (mode & ~Ansi.MODE_24BIT) | Ansi.MODE_256
        elif option == "-grayscale":
            grayscale = True
        elif option == "-html":
            html = True
        elif option == "-stdin":
            stdin = True
        start += 1

    maxWidth *= 4
    maxHeight *= 8

    if stdin:
        for line in sys.stdin:
            name = line.strip()
            if not name:
                break
            convert(name, maxWidth, maxHeight, mode, html, grayscale)
    elif start == len(args) - 1 and (is_url(args[start]) or not os.path.isdir(args[start])):
        convert(args[start], maxWidth, maxHeight, mode, html, grayscale)
    else:
        print("Too many arguments.")


def is_url(name):
    return name.startswith("http://") or name.startswith("https://")


if __name__ == "__main__":
    main(sys.argv[1:])
