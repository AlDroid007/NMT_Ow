"""Entry point: Tkinter GUI when available, console mode otherwise (or with --cli)."""

import sys

from . import storage
from .cli import run_cli


def _set_windows_process_options():
    try:
        from ctypes import windll
        try:
            windll.shell32.SetCurrentProcessExplicitAppUserModelID("NMT.SovaTutor.Windows.3.2")
        except Exception:
            pass
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                windll.user32.SetProcessDPIAware()
            except Exception:
                pass
    except Exception:
        pass


def _open_storage(root, messagebox):
    """Opens the encrypted user data store; asks before continuing without saving."""
    try:
        return storage.get_repository()
    except Exception:
        pass
    # Hide the empty main window only while the question is shown.
    root.withdraw()
    try:
        return _ask_without_storage(messagebox)
    finally:
        try:
            root.deiconify()
        except Exception:
            pass


def _ask_without_storage(messagebox):
    try:
        return storage.get_repository()
    except storage.CryptoUnavailableError as exc:
        go_on = messagebox.askyesno(
            "Потрібен пакет «cryptography»",
            f"{exc}\n\nПродовжити без збереження результатів і власних банків?",
            icon="warning",
        )
    except Exception as exc:
        go_on = messagebox.askyesno(
            "Сховище даних недоступне",
            f"Не вдалося відкрити зашифроване сховище даних:\n{exc}\n\n"
            "Продовжити без збереження результатів і власних банків?",
            icon="warning",
        )
    if not go_on:
        return None
    repo = storage.open_memory_repository()
    storage.set_repository(repo)
    return repo


def main(argv=None):
    argv = sys.argv if argv is None else argv
    if "--cli" in argv:
        run_cli()
        return

    try:
        import tkinter as tk
        from tkinter import messagebox
    except Exception:
        run_cli()
        return

    if sys.platform.startswith("win"):
        _set_windows_process_options()

    try:
        root = tk.Tk()
        repo = _open_storage(root, messagebox)
        if repo is None:
            root.destroy()
            return
        from .ui_tk.app import NmtTutorApp

        NmtTutorApp(root, repo)
        root.mainloop()
    except Exception as exc:
        print(f"Не вдалося запустити графічний інтерфейс ({exc}). Перемикаюся на консольний режим...")
        run_cli()
