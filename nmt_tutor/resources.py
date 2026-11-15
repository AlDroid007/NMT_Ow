"""Locations of files shipped next to the package (icons, launcher script)."""

import os

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(PACKAGE_DIR)
LAUNCHER_NAME = "nmt_tutor_mac.py"


def app_file(name):
    """Absolute path of a file that lives in the app folder (next to the launcher)."""
    return os.path.join(APP_ROOT, name)


def launcher_path():
    return app_file(LAUNCHER_NAME)
