"""Smoke test: headless core/storage self-test plus a short GUI run on an in-memory store.

usage: python tests/smoke_test.py [--real-keystore] [--no-gui]
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nmt_tutor.selftest import main as selftest_main  # noqa: E402


def wrong_answer(q):
    """An answer that is certainly wrong (None when the type makes that awkward)."""
    if q["qtype"] == "single":
        others = [lbl for lbl in q.get("labels", []) if str(lbl).upper() != str(q["answer"]).upper()]
        return others[0] if others else None
    if q["qtype"] == "short":
        return "-98765"
    return None


def answer_all(app, root, wrong_every=2):
    """Answers every question of the current plan through the UI handlers (some wrong) and finishes."""
    i = 0
    while True:
        block = app.plan[app.current_block_idx]
        q = block["questions"][app.current_q_idx]
        ans = wrong_answer(q) if i % wrong_every == 1 else None
        app.active_answer_getter = (lambda a=ans if ans is not None else q["answer"]: a)
        app._submit_question()
        root.update()
        i += 1
        last_block = app.current_block_idx + 1 >= len(app.plan)
        if last_block and app.current_q_idx + 1 >= len(block["questions"]):
            break
        app._next_question()
        root.update()
    app._finish_session()
    root.update()


def gui_smoke():
    """Opens the main window, enters a profile, runs and finishes a session, opens the cabinet; returns errors."""
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
    from nmt_tutor.profiles import new_profile

    store = open_memory_repository()
    app = NmtTutorApp(root, store)  # no profiles yet: opens the "create profile" form
    root.update()
    profile = new_profile("Smoke", subjects=["ukrmova", "math"], targets={"math": 180})
    store.save_profile(profile)
    app.enter_profile(profile)
    root.update()
    app._apply_preset(["ukrmova", "math"])
    app._start_session()
    root.update()
    for _ in range(3):
        app._step_next_hint()
        root.update()
    answer_all(app, root)
    app.show_cabinet()
    root.update()
    if not store.for_profile(profile["id"]).list_results():
        errors.append(("session result was not stored for the profile",))

    # Answers chosen but never checked with «Перевірити» still count when leaving with «Далі →».
    app.show_setup()
    root.update()
    app._apply_preset(["german"])
    app._start_session()
    root.update()
    while True:
        q = app.plan[app.current_block_idx]["questions"][app.current_q_idx]
        app.active_answer_getter = (lambda a=q["answer"]: a)
        last = app.current_q_idx + 1 >= len(app.plan[app.current_block_idx]["questions"])
        app._next_question()
        root.update()
        if last:
            break
    if len(store.for_profile(profile["id"]).list_results()) != 2:
        errors.append(("answers left with «Далі →» were not stored",))
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
