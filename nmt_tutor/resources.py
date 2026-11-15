"""Locations of files shipped next to the package (icons, launcher script).

In a PyInstaller build the package and these files live in the bundle folder (sys._MEIPASS),
so the same relative layout works for both the script and the packaged app.
"""

import os
import sys

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(PACKAGE_DIR)
LAUNCHER_NAME = "nmt_tutor_mac.py"


def app_file(name):
    """Absolute path of a file that lives in the app folder (next to the launcher)."""
    return os.path.join(APP_ROOT, name)


def launcher_path():
    return app_file(LAUNCHER_NAME)


def is_frozen():
    """True when running as a packaged executable (PyInstaller)."""
    return bool(getattr(sys, "frozen", False))
