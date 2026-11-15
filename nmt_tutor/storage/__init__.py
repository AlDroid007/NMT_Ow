"""User data storage: the single entry point for UI and core code.

    repo = get_repository()          # encrypted local SQLite by default
    repo.save_result(...); repo.get_progress(); repo.load_custom_banks()

A different backend (cloud, iOS sandbox) is plugged in with set_repository()
and/or paths.set_data_dir() before the UI starts.
"""

from . import paths
from .base import KeyMismatchError, Repository, StorageError  # noqa: F401
from .crypto import CryptoUnavailableError, INSTALL_HINT  # noqa: F401

_repo = None


def open_repository(data_dir=None, keystore=None, import_legacy=True):
    """Opens the encrypted SQLite repository in `data_dir` (default: paths.data_dir())."""
    from .crypto import Cipher, require_cryptography
    from .keystore import default_keystore, get_or_create_key
    from .legacy_import import run_legacy_import
    from .sqlite_repo import SQLiteRepository

    require_cryptography()
    if data_dir is not None:
        paths.set_data_dir(data_dir)
    folder = paths.data_dir()
    store = keystore or default_keystore(paths.key_file_path())
    cipher = Cipher(get_or_create_key(store))
    db = paths.db_path()
    notices = []
    try:
        repo = SQLiteRepository(db, cipher)
    except KeyMismatchError:
        moved = paths.quarantine(db)
        repo = SQLiteRepository(db, cipher)
        notices.append(
            "Ключ шифрування не підходить до наявної бази даних (наприклад, після перенесення на інший комп’ютер "
            f"або видалення ключа зі Зв’язки ключів). Стару базу збережено як:\n{moved}\nСтворено нову порожню базу."
        )
    if import_legacy:
        run_legacy_import(repo, folder)
    repo.startup_notices = notices
    return repo


def open_memory_repository():
    """Store that lives only in memory; nothing survives a restart (no `cryptography` needed)."""
    from .memory_repo import MemoryRepository

    return MemoryRepository()


def get_repository():
    global _repo
    if _repo is None:
        _repo = open_repository()
    return _repo


def set_repository(repo):
    global _repo
    _repo = repo
