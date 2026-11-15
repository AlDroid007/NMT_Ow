"""Smoke test: headless core/storage self-test plus a short GUI run on an in-memory store.

usage: python tests/smoke_test.py [--real-keystore] [--no-gui]
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nmt_tutor.selftest import main as selftest_main  # noqa: E402


def gui_smoke():
    """Opens the main window, starts a session, steps hints and finishes it; returns callback errors."""
    try:
        import tkinter as tk
        root = tk.Tk()
    except Exception as exc:
        print(f"SKIP  gui ({exc})")
        return 0
    from tkinter import messagebox

    from nmt_tutor.storage import open_memory_repository
    from nmt_tutor.ui_tk.app import NmtTutorApp

    for name in ("showinfo", "showwarning", "showerror"):
        setattr(messagebox, name, lambda *a, **k: None)
    setattr(messagebox, "askyesno", lambda *a, **k: True)
    errors = []
    root.report_callback_exception = lambda *exc: errors.append(exc)
    app = NmtTutorApp(root, open_memory_repository())
    root.update()
    app._apply_preset(["ukrmova", "math"])
    app._start_session()
    root.update()
    for _ in range(3):
        app._step_next_hint()
        root.update()
    for _ in range(400):
        root.update()
    root.destroy()
    print(f"{'OK  ' if not errors else 'FAIL'}  gui ({len(errors)} callback errors)")
    for exc in errors:
        print(exc)
    return len(errors)


if __name__ == "__main__":
    code = selftest_main(sys.argv)
    if "--no-gui" not in sys.argv:
        code = code or (1 if gui_smoke() else 0)
    sys.exit(code)
