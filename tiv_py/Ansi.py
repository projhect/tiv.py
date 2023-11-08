# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0

import bisect

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
    def best_index(v: int, options: int) -> int:
        index = bisect.bisect_left(options, v)
        if index == len(options) or (index > 0 and v - options[index - 1] < options[index] - v):
            index = index - 1
        return index

    @staticmethod
    def sqr(i: int) -> int:
        return i * i

    @staticmethod
    def clamp(value: int, min_val: int, max_val: int) -> int:
        return max(min(value, max_val), min_val)

    @staticmethod
    def color(flags: int, r: int, g: int, b: int) -> str:
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
