"""Where user data lives. The only module that decides storage locations.

Resolution order: set_data_dir() (e.g. the app sandbox on iOS) -> the
NMT_TUTOR_DATA_DIR environment variable -> ~/Documents/NMT_Tutor (v3.5 location).
"""

import os
from datetime import datetime

ENV_VAR = "NMT_TUTOR_DATA_DIR"
DB_FILENAME = "nmt_tutor_data.sqlite3"
KEY_FILENAME = ".nmt_tutor_key"

_override = None


def set_data_dir(path):
    """Overrides the data folder (call before the repository is opened)."""
    global _override
    _override = path


def default_data_dir():
    return os.path.join(os.path.expanduser("~"), "Documents", "NMT_Tutor")


def data_dir():
    base = _override or os.environ.get(ENV_VAR) or default_data_dir()
    try:
        os.makedirs(base, exist_ok=True)
    except OSError:
        base = os.path.expanduser("~")
    return base


def db_path():
    return os.path.join(data_dir(), DB_FILENAME)


def key_file_path():
    return os.path.join(data_dir(), KEY_FILENAME)


def quarantine(path):
    """Renames an unreadable file aside (never deletes it) and returns the new path."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = f"{path}.unreadable-{stamp}"
    os.replace(path, target)
    for suffix in ("-wal", "-shm", "-journal"):
        if os.path.exists(path + suffix):
            os.replace(path + suffix, target + suffix)
    return target
