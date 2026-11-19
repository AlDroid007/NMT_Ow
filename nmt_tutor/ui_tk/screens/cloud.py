"""Cloud account in the Tk UI: sign in with an e-mail code, link a profile, background sync.

The network runs on a worker thread; everything that touches the database or widgets
runs on the Tk thread (see cloud/sync.py: prepare -> exchange -> commit).
Hidden entirely when the build has no cloud project configured.
"""

import queue
import sys
import threading
import tkinter as tk
import uuid
from datetime import datetime
from tkinter import messagebox

from ...cloud import load_settings, sync
from ...cloud.http import CloudError, NetworkError
from ...cloud.supabase import AuthExpiredError, SupabaseClient, normalize_email
from ...profiles import PROVIDER_CLOUD
from ..owl import OwlMascot
from ..theme import PALETTE
from ..widgets import RoundedButton, RoundedCard

AUTO_SYNC_DELAY_MS = 1500


class CloudMixin:
    # --- plumbing -----------------------------------------------------------------
    def _cloud_client(self):
        if not hasattr(self, "_cloud_client_obj"):
            settings = load_settings()
            self._cloud_client_obj = SupabaseClient(settings) if settings else None
        return self._cloud_client_obj

    def cloud_enabled(self):
        return self._cloud_client() is not None and getattr(self.store, "supports_sync", False)

    def _run_in_background(self, work, on_done, on_error):
        """Runs `work()` on a worker thread and calls on_done(result) / on_error(exc) on the Tk thread."""
        box = queue.Queue()

        def runner():
            try:
                box.put((True, work()))
            except Exception as exc:  # noqa: BLE001 - reported to the UI
                box.put((False, exc))

        def poll():
            try:
                ok, value = box.get_nowait()
            except queue.Empty:
                try:
                    self.root.after(100, poll)
                except tk.TclError:
                    pass  # window closed
                return
            (on_done if ok else on_error)(value)

        threading.Thread(target=runner, daemon=True).start()
        self.root.after(100, poll)

    def cloud_linked(self, profile_id=None):
        pid = profile_id or (self.profile or {}).get("id")
        return bool(pid) and self.cloud_enabled() and sync.is_linked(self.store, pid)

    # --- sign-in dialog -----------------------------------------------------------------
    def _cloud_sign_in_dialog(self, title, intro, on_session):
        """Two steps: e-mail -> code from the letter. Calls on_session(CloudSession) on success."""
        client = self._cloud_client()
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=PALETTE["bg"])
        win.resizable(False, False)
        win.transient(self.root)
        card = RoundedCard(win, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=18, pad=18,
                           width=440, height=360)
        card.pack(padx=14, pady=14)
        inner = card.inner
        OwlMascot(inner, size=56, bg=PALETTE["card"]).pack()
        tk.Label(inner, text=title, font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(pady=(2, 0))
        hint = tk.Label(inner, text=intro, font=self.fonts["body_sm"], bg=PALETTE["card"], fg=PALETTE["muted"],
                        justify="center", wraplength=380)
        hint.pack(pady=(2, 8))

        state = {"step": "email", "email": "", "busy": False}
        var = tk.StringVar()
        entry = tk.Entry(inner, textvariable=var, font=self.fonts["h3"], justify="center", relief="flat",
                         bg=PALETTE["card_soft"], highlightthickness=2, highlightbackground=PALETTE["border"],
                         highlightcolor=PALETTE["primary"], width=28)
        entry.pack(ipady=5)
        status = tk.Label(inner, text="", font=self.fonts["small"], bg=PALETTE["card"], fg=PALETTE["err_fg"],
                          wraplength=380, justify="center")
        status.pack(pady=(6, 2))

        row = tk.Frame(inner, bg=PALETTE["card"])
        row.pack(fill="x", side="bottom")
        main_btn = RoundedButton(row, text="Надіслати код", command=lambda: submit(), font=self.fonts["bold"], radius=14,
                                 height=36, min_width=150, parent_bg=PALETTE["card"])
        main_btn.pack(side="right")
        RoundedButton(row, text="Скасувати", command=win.destroy, bg=PALETTE["card_soft"], hover_bg=PALETTE["soft_indigo"],
                      fg=PALETTE["text"], border_color=PALETTE["border"], font=self.fonts["bold_sm"], radius=14, height=36,
                      min_width=100, parent_bg=PALETTE["card"]).pack(side="right", padx=8)
        back = tk.Label(row, text="", font=self.fonts["small"], bg=PALETTE["card"], fg=PALETTE["primary"], cursor="hand2")
        back.pack(side="left")

        def alive():
            try:
                return bool(win.winfo_exists())
            except tk.TclError:
                return False

        def set_busy(busy, text=""):
            state["busy"] = busy
            main_btn.set_state("disabled" if busy else "normal")
            status.config(text=text, fg=PALETTE["muted"] if busy else PALETTE["err_fg"])

        def show_code_step():
            state["step"] = "code"
            var.set("")
            hint.config(text=f"Ми надіслали код на {state['email']}.\nВведи цифри з листа (перевір і «Спам»).")
            main_btn.set_text("Підтвердити")
            back.config(text="← Інша пошта")
            set_busy(False)
            entry.focus_set()

        def show_email_step(_e=None):
            if state["busy"]:
                return
            state["step"] = "email"
            var.set(state["email"])
            hint.config(text=intro)
            main_btn.set_text("Надіслати код")
            back.config(text="")
            set_busy(False)
            entry.focus_set()

        def failed(exc):
            if alive():
                set_busy(False, str(exc) if isinstance(exc, CloudError) else f"Помилка: {exc}")

        def submit(_e=None):
            if state["busy"] or not alive():
                return
            if state["step"] == "email":
                try:
                    email = normalize_email(var.get())
                except CloudError as exc:
                    status.config(text=str(exc), fg=PALETTE["err_fg"])
                    return
                state["email"] = email
                set_busy(True, "Надсилаємо код…")
                self._run_in_background(lambda: client.send_code(email),
                                        lambda _r: alive() and show_code_step(), failed)
            else:
                code = var.get()
                set_busy(True, "Перевіряємо код…")

                def verified(session):
                    if alive():
                        win.destroy()
                        on_session(session)

                self._run_in_background(lambda: client.verify_code(state["email"], code), verified, failed)

        back.bind("<Button-1>", show_email_step)
        entry.bind("<Return>", submit)
        win.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - win.winfo_reqwidth()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - win.winfo_reqheight()) // 3
        win.geometry(f"+{max(0, x)}+{max(0, y)}")
        try:
            win.grab_set()
        except tk.TclError:
            pass
        entry.focus_set()
        self._cloud_dialog = win
        return win

    # --- link the active profile ----------------------------------------------------------
    def cloud_connect(self):
        """Profile menu / cabinet: sign in and link the active profile to that cloud account."""
        if self.profile is None or not self.cloud_enabled():
            return
        pid = self.profile["id"]
        self._cloud_sign_in_dialog(
            "Хмарне збереження",
            "Твої тренування та прогрес збережуться в хмарі — їх можна буде відкрити на іншому комп’ютері.\n"
            "Введи свою пошту, ми надішлемо код для входу.",
            lambda session: self._cloud_link_profile(pid, session),
        )

    def _cloud_link_profile(self, pid, session, then=None):
        """Links profile `pid` to the account unless the account already has another profile."""
        def checked(row):
            if row is not None and sync.local_id(row["id"]) != pid:
                messagebox.showwarning(
                    "Пошта вже використовується",
                    f"До пошти {session.email} уже прив’язано інший профіль — «{row.get('name')}».\n\n"
                    "Одна пошта = один профіль. Щоб відкрити той профіль на цьому комп’ютері, обери "
                    "«☁️ Увійти через пошту» на екрані «Хто займається?». Для цього профілю використай іншу пошту.",
                )
                return
            try:
                profile = sync.attach(self.store, pid, session)
            except Exception as exc:
                messagebox.showerror("Хмара", f"Не вдалося підключити хмару:\n{exc}")
                return
            if self.profile is not None and self.profile["id"] == pid:
                self.profile = profile
                self._setup_menus()
            if then:
                then()
            self.cloud_sync(manual=True)

        self._run_in_background(lambda: sync.fetch_account_profile(self._cloud_client(), session), checked,
                                lambda exc: messagebox.showerror("Хмара", str(exc)))

    def cloud_disconnect(self):
        if self.profile is None:
            return
        email = sync.linked_email(self.store, self.profile["id"]) or ""
        if not messagebox.askyesno(
            "Вийти з хмари",
            f"Відключити хмару ({email}) на цьому комп’ютері?\n\nУсе залишиться і тут, і в хмарі. "
            "Нові тренування перестануть зберігатися в хмарі, доки не підключиш її знову.",
        ):
            return
        sync.detach(self.store, self.profile["id"])
        self.profile = self.store.get_profile(self.profile["id"])
        self._setup_menus()
        self._cloud_refresh_view(changed=False)

    def cloud_delete_account(self):
        if self.profile is None:
            return
        pid = self.profile["id"]
        job = sync.prepare(self.store, pid)
        if job is None:
            return
        if not messagebox.askyesno(
            "Видалити дані з хмари",
            f"Видалити хмарний акаунт {job.session.email} і ВСІ збережені в хмарі тренування та прогрес?\n\n"
            "На цьому комп’ютері все залишиться. Скасувати видалення з хмари неможливо.",
            icon="warning",
        ):
            return
        client = self._cloud_client()

        def work():
            client.rpc(job.session, "delete_my_account")

        def done(_r):
            sync.detach(self.store, pid)
            if self.profile is not None and self.profile["id"] == pid:
                self.profile = self.store.get_profile(pid)
                self._setup_menus()
            self._cloud_refresh_view(changed=False)
            messagebox.showinfo("Хмара", "Хмарний акаунт і всі дані в хмарі видалено. На цьому комп’ютері все залишилось.")

        self._run_in_background(work, done, lambda exc: messagebox.showerror("Хмара", f"Не вдалося видалити:\n{exc}"))

    # --- restore / sign in from the profile picker ------------------------------------------------
    def cloud_sign_in_from_picker(self):
        """«Хто займається?»: open (or download) the profile that belongs to an e-mail."""
        if not self.cloud_enabled():
            return
        self._cloud_sign_in_dialog(
            "Увійти через пошту",
            "Відкрий свій профіль із хмари — з усіма тренуваннями та прогресом.\nВведи пошту, ми надішлемо код.",
            self._cloud_open_account,
        )

    def _cloud_open_account(self, session):
        local = self.store.find_profile_by_identity(PROVIDER_CLOUD, session.user_id)
        if local is not None:
            # The e-mail code proves the owner, so the local PIN is not asked again.
            profile = sync.attach(self.store, local["id"], session, from_cloud=True)
            self.enter_profile(profile)
            return

        def fetched(row):
            if row is None:
                if messagebox.askyesno(
                    "Профілю ще немає",
                    f"У хмарі ще немає профілю для {session.email}.\n\nСтворити новий профіль і зберігати його в хмарі "
                    "з цією поштою?",
                ):
                    self._pending_cloud_session = session
                    self.show_new_profile_form()
                return
            pid = sync.local_id(row["id"])
            if self.store.get_profile(pid) is None:
                self.store.save_profile(sync.profile_from_cloud(row, session), _dirty=False)
            profile = sync.attach(self.store, pid, session, from_cloud=True)
            self.enter_profile(profile)
            self.cloud_sync(manual=True)

        self._run_in_background(lambda: sync.fetch_account_profile(self._cloud_client(), session), fetched,
                                lambda exc: messagebox.showerror("Хмара", str(exc)))

    def _cloud_after_profile_created(self, profile):
        """Links a just-created profile to the e-mail the user signed in with on the picker."""
        session = getattr(self, "_pending_cloud_session", None)
        self._pending_cloud_session = None
        if session is not None and self.cloud_enabled():
            self._cloud_link_profile(profile["id"], session)

    # --- sync ------------------------------------------------------------------------------------
    def cloud_sync_soon(self):
        """Debounced background sync of the active profile after a change."""
        if self.profile is None or not self.cloud_linked():
            return
        job = getattr(self, "_cloud_sync_job", None)
        if job is not None:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass
        self._cloud_sync_job = self.root.after(AUTO_SYNC_DELAY_MS, self._cloud_auto_sync)

    def _cloud_auto_sync(self):
        self._cloud_sync_job = None
        self.cloud_sync(manual=False)

    def cloud_sync(self, manual=False):
        if self.profile is None or not self.cloud_enabled():
            return
        if getattr(self, "_cloud_busy", False):
            self._cloud_again = True
            return
        pid = self.profile["id"]
        job = sync.prepare(self.store, pid)
        if job is None:
            return
        self._cloud_busy = True
        self._cloud_again = False
        self._cloud_refresh_view(changed=False)

        def done(outcome):
            self._cloud_busy = False
            try:
                changed = sync.commit(self.store, job, outcome)
            except Exception as exc:
                print(f"Cloud sync: could not store downloaded data: {exc}", file=sys.stderr)
                changed = 0
            if self.profile is not None and self.profile["id"] == pid:
                self.profile = self.store.get_profile(pid) or self.profile
                self.custom_bank = self._load_custom_banks()
                self._update_window_title()
            self._cloud_refresh_view(changed=changed > 0)
            if self._cloud_again:
                self.cloud_sync_soon()

        def failed(exc):
            self._cloud_busy = False
            try:
                sync.fail(self.store, job, exc)
            except Exception as err:
                print(f"Cloud sync: could not save the failure state: {err}", file=sys.stderr)
            print(f"Cloud sync failed: {exc}", file=sys.stderr)
            self._cloud_refresh_view(changed=False)
            if isinstance(exc, AuthExpiredError):
                if manual or messagebox.askyesno("Хмара", f"{exc}\n\nУвійти зараз?"):
                    self._cloud_relogin(pid)
            elif manual:
                messagebox.showwarning("Хмара", f"Не вдалося синхронізувати:\n{exc}\n\nДані збережено на комп’ютері, "
                                       "синхронізація повториться пізніше.")

        self._run_in_background(lambda: sync.exchange(self._cloud_client(), job), done, failed)

    def _cloud_relogin(self, pid):
        email = sync.linked_email(self.store, pid) or ""
        self._cloud_sign_in_dialog("Увійти в хмару знову", f"Вхід застарів. Підтвердь пошту {email} кодом із листа.",
                                   lambda session: self._cloud_link_profile(pid, session))

    # --- start of a training ----------------------------------------------------------------------
    def begin_training(self, subjects, length_mode, tutor_mode, start, mistake_drill=False, focus_section=None):
        """Registers a new training and then calls start().

        A profile linked to the cloud needs the internet here: the server records the
        start (and, with purchases, will check limits). Other profiles start at once.
        """
        if getattr(self, "_training_starting", False):
            return
        session_uid = uuid.uuid4().hex
        started_at = datetime.now().isoformat(timespec="seconds")

        def go(_result=None):
            self._training_starting = False
            self._set_waiting(False)
            self.session_uid = session_uid
            self.session_started_at = started_at
            start()

        if self.profile is None or not self.cloud_linked():
            go()
            return
        job = sync.prepare(self.store, self.profile["id"])
        if job is None:
            go()
            return
        pid = self.profile["id"]
        self._training_starting = True
        self._set_waiting(True)
        client = self._cloud_client()

        def work():
            try:
                return sync.begin_session(client, job, session_uid, subjects, length_mode, tutor_mode,
                                          mistake_drill, focus_section)
            except Exception as exc:
                exc.cloud_session = job.session
                raise

        def done(outcome):
            sync.remember_session(self.store, pid, job.session)
            if not outcome.get("allowed", True):
                self._training_starting = False
                self._set_waiting(False)
                messagebox.showinfo("Тренування", outcome.get("message") or "Зараз розпочати тренування не можна.")
                return
            go()

        def failed(exc):
            self._training_starting = False
            self._set_waiting(False)
            session = getattr(exc, "cloud_session", None)
            if session is not None:
                sync.remember_session(self.store, pid, session)
            if isinstance(exc, AuthExpiredError):
                if messagebox.askyesno("Хмара", f"{exc}\n\nУвійти зараз?"):
                    self._cloud_relogin(pid)
            elif isinstance(exc, NetworkError):
                messagebox.showwarning("Потрібен інтернет",
                                       "Щоб почати тренування, потрібне підключення до інтернету.\n\n"
                                       "Перевір з’єднання і спробуй ще раз.")
            else:
                messagebox.showerror("Тренування", f"Не вдалося почати тренування:\n{exc}")

        self._run_in_background(work, done, failed)

    def _set_waiting(self, waiting):
        try:
            self.root.configure(cursor="watch" if waiting else "")
        except tk.TclError:
            pass

    # --- status ------------------------------------------------------------------------------------
    def cloud_status(self):
        """(text, clickable action or None) for the cabinet header; ("", None) when the cloud is off."""
        if self.profile is None or not self.cloud_enabled():
            return "", None
        link = sync.get_link(self.store, self.profile["id"])
        if not link or not link.get("session"):
            return "☁️ Зберігати в хмарі — підключити", self.cloud_connect
        email = link["session"].get("email", "")
        if getattr(self, "_cloud_busy", False):
            return f"☁️ {email} • синхронізація…", None
        if link.get("last_error"):
            return f"☁️ {email} • не вдалося синхронізувати — повторити", lambda: self.cloud_sync(manual=True)
        when = (link.get("last_sync") or "")[11:16]
        text = f"☁️ {email} • збережено в хмарі {when}" if when else f"☁️ {email}"
        streak = sync.current_streak(link)
        if streak:
            text = f"🔥 {streak} {self._days_in_row(streak)} поспіль • " + text
        return text, lambda: self.cloud_sync(manual=True)

    @staticmethod
    def _days_in_row(n):
        from ...profiles import days_word

        return days_word(n)

    def _cloud_refresh_view(self, changed):
        """Updates the cabinet after a sync: full redraw when data changed, otherwise only the status line."""
        if getattr(self, "_screen", None) != "cabinet":
            return
        if changed:
            self.show_cabinet()
            return
        label = getattr(self, "_cloud_status_label", None)
        try:
            if label is not None and label.winfo_exists():
                text, _action = self.cloud_status()
                label.config(text=text)
        except tk.TclError:
            pass
