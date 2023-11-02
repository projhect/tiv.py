# Derived from Stefan Haustein's TerminalImageViewer.java, available at:
# https://github.com/stefanhaustein/TerminalImageViewer
# License: Apache 2.0

from typing import Optional

def is_url(name: Optional[str]) -> bool:
    return name is not None and (name.startswith("http://") or name.startswith("https://"))
