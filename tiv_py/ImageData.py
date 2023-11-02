# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0

from Ansi import Ansi
from BlockChar import BlockChar

class ImageData:
    """
    Represents the entire image's data and provides the dump method, which converts the image data to colored block characters for terminal or HTML display.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.data = bytearray(width * height * 4)
        
    def hex6(self, r: int, g: int, b: int) -> int:
        return f"{(1 << 24) | ((r & 255) << 16) | ((g & 255) << 8) | (b & 255):06x}"
    
    def dump(self, mode: str, html: bool):
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
                    fg = self.hex6(block_char.fg_color[0], block_char.fg_color[1], block_char.fg_color[2])
                    bg = self.hex6(block_char.bg_color[0], block_char.bg_color[1], block_char.bg_color[2])
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
                    fg = Ansi.color(Ansi.FG | mode, block_char.fg_color[0], block_char.fg_color[1], block_char.fg_color[2])
                    bg = Ansi.color(Ansi.BG | mode, block_char.bg_color[0], block_char.bg_color[1], block_char.bg_color[2])
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
