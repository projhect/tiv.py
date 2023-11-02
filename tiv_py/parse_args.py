# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0

import os
import argparse
from is_url import is_url

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert images to colored block characters for terminal or HTML display. Provide a local path, URL, or use --stdin to read from standard input.")
    
    # Create a mutually exclusive group
    source_group = parser.add_mutually_exclusive_group(required=True)
    
    # Image source: local path or URL
    source_group.add_argument("image_source", nargs="?", help="Path to the image file or a URL")
    
    # Image source: standard input
    source_group.add_argument("--stdin", action="store_true", help="Read image path or URL from the standard input.")

    # Output mode: either 256-color mode or 24-bit mode
    parser.add_argument('--mode', choices=['256', '24bit'], default='256', help='ANSI color mode. Either 256-color mode or 24-bit mode. Default is 256-color mode.')

    # HTML mode
    parser.add_argument('--html', action='store_true', help='Generate output in HTML format instead of ANSI.')

    # Max width and height for resizing
    parser.add_argument('--max_width', type=int, default=80, help='Maximum width for the output. Default is 80.')
    parser.add_argument('--max_height', type=int, default=24, help='Maximum height for the output. Default is 24.')

    # Grayscale
    parser.add_argument('--grayscale', action='store_true', help='Convert the image to grayscale before processing.')

    # Parsing and validation
    args = parser.parse_args()
    if not args.stdin and not is_url(args.image_source) and not os.path.isfile(args.image_source):
        parser.error("Invalid image_source")

    return args
