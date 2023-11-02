# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0

import sys
from parse_args import parse_args
from Ansi import Ansi
from convert import convert

def main():
    """
    Simple program to print images to the shell using 24 bit ANSI color codes and Unicode block graphics characters.
    """

    args = parse_args()
    mode = Ansi.MODE_256 if args.mode == "256" else Ansi.MODE_24BIT
    max_width = args.max_width*4
    max_height = args.max_height*8

    if args.stdin:
        for line in sys.stdin:
            name = line.strip()
            if not name:
                break
            convert(name, max_width, max_height, mode, args.html, args.grayscale)
    else:
        convert(args.image_source, max_width, max_height, mode, args.html, args.grayscale)

if __name__ == "__main__":
    main()
