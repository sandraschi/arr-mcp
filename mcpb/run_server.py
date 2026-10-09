"""Entry point for PyInstaller-bundled server."""

import _strptime  # noqa: F401
import sys

sys.path.insert(0, ".")

from arr_mcp.server import main

if __name__ == "__main__":
    main()
