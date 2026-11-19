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


def cancel_pending(root):
    """Drops pending Tk timers (owl animation etc.) so destroying the window stays quiet."""
    try:
        for after_id in root.tk.splitlist(root.tk.call("after", "info")):
            root.tk.call("after", "cancel", after_id)
    except Exception:
        pass


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
    cancel_pending(root)
    root.destroy()
    print(f"{'OK  ' if not errors else 'FAIL'}  gui ({len(errors)} callback errors)")
    for exc in errors:
        print(exc)
    return len(errors)


def pump(root, until, seconds=10):
    """Runs the Tk loop until `until()` is true (background work finishes on the Tk thread)."""
    import time

    end = time.time() + seconds
    while time.time() < end:
        root.update()
        if until():
            return True
        time.sleep(0.02)
    return False


def fill_cloud_dialog(app, root, email, code):
    """Types into the real «sign in with e-mail» dialog: e-mail -> Enter -> code -> Enter."""
    import tkinter as tk

    win = app._cloud_dialog
    entry = next(w for w in win.winfo_children()[0].winfo_children()[0].winfo_children() if isinstance(w, tk.Entry))
    entry.delete(0, "end")
    entry.insert(0, email)
    entry.event_generate("<Return>")
    pump(root, lambda: "Ми надіслали код" in "".join(
        w.cget("text") for w in entry.master.winfo_children() if isinstance(w, tk.Label)))
    entry.delete(0, "end")
    entry.insert(0, code)
    entry.event_generate("<Return>")
    pump(root, lambda: not win.winfo_exists())


def gui_cloud_smoke():
    """Two app windows (= two computers) with encrypted stores sync through an in-memory cloud."""
    import shutil
    import tempfile

    try:
        import tkinter as tk
        root = tk.Tk()
    except Exception as exc:
        print(f"SKIP  gui cloud ({exc})")
        return 0
    from tkinter import messagebox

    from nmt_tutor import storage
    from nmt_tutor.cloud import sync
    from nmt_tutor.cloud.fake import FakeCloud
    from nmt_tutor.profiles import new_profile
    from nmt_tutor.storage.keystore import MemoryKeyStore
    from nmt_tutor.ui_tk.app import NmtTutorApp

    for name in ("showinfo", "showwarning", "showerror"):
        setattr(messagebox, name, lambda *a, **k: None)
    setattr(messagebox, "askyesno", lambda *a, **k: True)
    errors = []
    root.report_callback_exception = lambda *exc: errors.append(exc)
    cloud = FakeCloud()
    ks = MemoryKeyStore()
    tmp_a, tmp_b = tempfile.mkdtemp(prefix="nmt_gui_a_"), tempfile.mkdtemp(prefix="nmt_gui_b_")

    def make_app(folder, window):
        store = storage.open_repository(folder, keystore=ks, import_legacy=False)
        app = NmtTutorApp(window, store)
        app._cloud_client_obj = cloud
        return store, app

    try:
        # Computer A: a profile with one finished session, then «Зберігати в хмарі».
        store_a, app_a = make_app(tmp_a, root)
        prof = new_profile("Хмара", subjects=["math"], targets={"math": 180})
        store_a.save_profile(prof)
        pid = prof["id"]
        app_a.enter_profile(prof)
        root.update()
        app_a._apply_preset(["math"])
        app_a._start_session()
        root.update()
        answer_all(app_a, root)
        app_a.show_cabinet()
        root.update()
        if "підключити" not in app_a.cloud_status()[0]:
            errors.append(("cabinet does not offer the cloud", app_a.cloud_status()))
        app_a.cloud_connect()
        fill_cloud_dialog(app_a, root, "gui@example.com", cloud.codes.get("gui@example.com") or "123456")
        if not pump(root, lambda: sync.get_link(store_a, pid) and sync.get_link(store_a, pid).get("last_sync")):
            errors.append(("first sync did not finish", sync.get_link(store_a, pid)))
        if len(cloud.tables["sessions"]) != 1 or not cloud.tables["session_answers"]:
            errors.append(("cloud should hold 1 session with answers", {t: len(v) for t, v in cloud.tables.items()}))
        if "збережено в хмарі" not in app_a._cloud_status_label.cget("text"):
            errors.append(("status line not updated", app_a._cloud_status_label.cget("text")))
        app_a._setup_menus()

        # Offline: a linked profile cannot start a training.
        app_a.show_setup()
        root.update()
        app_a._apply_preset(["math"])
        cloud.offline = True
        old_plan = app_a.plan
        app_a._start_session()
        pump(root, lambda: not getattr(app_a, "_training_starting", False))
        if app_a.plan is not old_plan:
            errors.append(("training started without the internet",))
        cloud.offline = False

        # Online: the server registers the start, the result with answers and hints is uploaded automatically.
        app_a._start_session()
        if not pump(root, lambda: app_a.plan is not old_plan):
            errors.append(("training did not start online",))
        sid = sync.cloud_id(app_a.session_uid)
        if cloud.tables["sessions"].get(sid, {}).get("status") != "active":
            errors.append(("begin_session was not called", cloud.tables["sessions"].get(sid)))
        app_a._step_next_hint()
        root.update()
        answer_all(app_a, root)
        if not pump(root, lambda: cloud.tables["sessions"].get(sid, {}).get("status") == "finished", seconds=8):
            errors.append(("auto sync after a session did not upload",))
        if not any(h["session_id"] == sid for h in cloud.tables["hint_events"].values()):
            errors.append(("opened hint was not uploaded",))
        pump(root, lambda: not getattr(app_a, "_cloud_busy", False) and getattr(app_a, "_cloud_sync_job", None) is None)
        if "🔥" not in app_a.cloud_status()[0]:
            errors.append(("streak not shown", app_a.cloud_status()[0]))

        # Computer B: no profiles yet -> «Вже маєш профіль у хмарі?» -> e-mail code -> profile with history.
        win_b = tk.Toplevel(root)
        store_b, app_b = make_app(tmp_b, win_b)
        root.update()
        app_b.cloud_sign_in_from_picker()
        fill_cloud_dialog(app_b, root, "gui@example.com", "123456")
        if not pump(root, lambda: app_b.profile is not None and len(store_b.for_profile(pid).list_results()) == 2):
            errors.append(("profile not restored on computer B",
                           app_b.profile and len(store_b.for_profile(pid).list_results())))
        app_b.show_cabinet()
        root.update()

        # Sign out on B keeps the local copy.
        app_b.cloud_disconnect()
        root.update()
        if sync.is_linked(store_b, pid) or len(store_b.for_profile(pid).list_results()) != 2:
            errors.append(("sign-out lost data or kept the link",))
        for _ in range(100):
            root.update()
        store_a.close()
        store_b.close()
    finally:
        cancel_pending(root)
        root.destroy()
        shutil.rmtree(tmp_a, ignore_errors=True)
        shutil.rmtree(tmp_b, ignore_errors=True)
    print(f"{'OK  ' if not errors else 'FAIL'}  gui cloud ({len(errors)} errors)")
    for exc in errors:
        print(exc)
    return len(errors)


if __name__ == "__main__":
    code = selftest_main(sys.argv)
    if "--no-gui" not in sys.argv:
        code = code or (1 if gui_smoke() else 0)
        code = code or (1 if gui_cloud_smoke() else 0)
    sys.exit(code)
