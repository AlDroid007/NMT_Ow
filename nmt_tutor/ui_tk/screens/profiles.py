"""Profile screens: «Хто займається?» picker, PIN check and the create/edit profile form."""

import tkinter as tk
from tkinter import messagebox

from ...auth import available_providers
from ...auth.local import PIN_LENGTH, PinGuard, hash_pin, is_valid_pin
from ...config import SUBJECTS_CONFIG, SUBJECTS_ORDER
from ...profiles import (AVATARS, DEFAULT_AVATAR, DEFAULT_TARGET, PROVIDER_CLOUD, PROVIDER_LOCAL, SCORE_MAX,
                         SCORE_MIN, ProfileError, avatar_text, format_exam_date, has_pin, new_profile,
                         normalize_profile, parse_exam_date, touch)
from ..owl import OwlMascot
from ..scroll import SmoothScrollView
from ..theme import PALETTE
from ..profile_widgets import AvatarChoice, ProfileTile, emoji_font
from ..widgets import RoundedButton, RoundedCard, SubjectTile

LAST_PROFILE_KEY = "last_profile_id"


class ProfilesScreenMixin:
    # -------------------------------------------------------------------
    # ВИБІР ПРОФІЛЮ
    # -------------------------------------------------------------------
    def start_profiles(self):
        """First screen: the picker, or the form when there are no profiles yet."""
        try:
            profiles = self.store.list_profiles()
        except Exception as exc:
            messagebox.showerror("Профілі", f"Не вдалося прочитати профілі:\n{exc}")
            profiles = []
        if profiles:
            self.show_profiles()
        else:
            self.show_profile_form(None)

    def _nav_header(self, title, subtitle):
        header = tk.Frame(self.main_container, bg=PALETTE["nav"], height=74)
        header.pack(fill="x")
        header.pack_propagate(False)
        title_wrap = tk.Frame(header, bg=PALETTE["nav"])
        title_wrap.pack(side="left", padx=24, pady=10)
        tk.Label(title_wrap, text=title, font=self.fonts["h1"], bg=PALETTE["nav"], fg=PALETTE["nav_fg"]).pack(anchor="w")
        tk.Label(title_wrap, text=subtitle, font=self.fonts["small"], bg=PALETTE["nav"], fg="#CBD5E1").pack(anchor="w")
        return header

    def _nav_button(self, parent, text, command, min_width=150):
        btn = RoundedButton(
            parent,
            text=text,
            command=command,
            bg=PALETTE["nav_accent"],
            hover_bg="#425182",
            fg="#FFFFFF",
            border_color="#526296",
            font=self.fonts["bold_sm"],
            radius=14,
            height=36,
            min_width=min_width,
            parent_bg=PALETTE["nav"],
        )
        btn.pack(side="right", padx=(0, 12), pady=18)
        return btn

    def show_profiles(self):
        self._clear_main()
        self._leave_profile()
        self._pending_cloud_session = None
        profiles = self.store.list_profiles()
        last_id = self.store.get_meta(LAST_PROFILE_KEY)
        profiles.sort(key=lambda p: p["id"] != last_id)  # last used first, otherwise creation order

        header = self._nav_header("Хто займається?", "Оберіть свій профіль — у кожного учня свої результати, цілі та банки завдань")
        if self.cloud_enabled():
            self._nav_button(header, "☁️ Увійти через пошту", self.cloud_sign_in_from_picker, min_width=190).pack_configure(padx=(0, 22))

        body = tk.Frame(self.main_container, bg=PALETTE["bg"])
        body.pack(fill="both", expand=True, padx=20, pady=14)
        card = RoundedCard(body, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=16)
        card.pack(fill="both", expand=True)

        hello = tk.Frame(card.inner, bg=PALETTE["card"])
        hello.pack(fill="x", pady=(0, 10))
        owl = OwlMascot(hello, size=72, bg=PALETTE["card"])
        owl.pack(side="left", padx=(4, 12))
        tk.Label(hello, text="Привіт! Хто сьогодні тренується? 🦉", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", pady=(14, 2))
        tk.Label(hello, text="Натисни на свою картку. Якщо профіль захищено 🔒, Сова-Ліза попросить PIN-код.",
                 font=self.fonts["body_sm"], bg=PALETTE["card"], fg=PALETTE["muted"]).pack(anchor="w")

        scroll = SmoothScrollView(card.inner, bg=PALETTE["card"])
        scroll.pack(fill="both", expand=True)
        grid = scroll.inner
        tiles = [ProfileTile(grid, self.fonts, self._on_profile_tile, p, highlight=(p["id"] == last_id)) for p in profiles]
        tiles.append(ProfileTile(grid, self.fonts, lambda _p: self.show_profile_form(None)))
        self._profile_tiles = tiles

        def relayout(event=None):
            width = event.width if event is not None else grid.winfo_width()
            cols = max(1, int(width // (ProfileTile.W + 16)))
            if getattr(grid, "_cols", None) == cols:
                return
            grid._cols = cols
            for i, tile in enumerate(tiles):
                tile.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="nw")

        grid.bind("<Configure>", relayout, add="+")
        relayout()

    def _on_profile_tile(self, profile):
        if has_pin(profile):
            self._ask_pin(profile, lambda: self.enter_profile(profile))
        else:
            self.enter_profile(profile)

    def enter_profile(self, profile):
        """Makes `profile` the active one and opens subject selection."""
        self.profile = profile
        self.repo = self.store.for_profile(profile["id"])
        try:
            self.store.set_meta(LAST_PROFILE_KEY, profile["id"])
        except Exception:
            pass
        self.custom_bank = self._load_custom_banks()
        self._update_window_title()
        self._setup_menus()
        self.show_setup()
        self.cloud_sync_soon()

    def _leave_profile(self):
        self.profile = None
        self.repo = None
        self.custom_bank = {}
        self._update_window_title()
        self._setup_menus()

    def switch_profile(self):
        if getattr(self, "timer_running", False) and not messagebox.askyesno(
            "Змінити профіль", "Поточне тренування буде перервано без збереження. Змінити профіль?"
        ):
            return
        self.show_profiles()

    # -------------------------------------------------------------------
    # PIN
    # -------------------------------------------------------------------
    def _pin_guard(self):
        guard = getattr(self, "_pin_guard_obj", None)
        if guard is None:
            guard = self._pin_guard_obj = PinGuard()
        return guard

    def _digits_only(self, proposed):
        return proposed == "" or (proposed.isdigit() and len(proposed) <= PIN_LENGTH)

    def _ask_pin(self, profile, on_success):
        win = tk.Toplevel(self.root)
        win.title("PIN-код")
        win.configure(bg=PALETTE["bg"])
        win.resizable(False, False)
        win.transient(self.root)
        card = RoundedCard(win, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=18, pad=18, width=360, height=290)
        card.pack(padx=14, pady=14)
        inner = card.inner
        tk.Label(inner, text=avatar_text(profile), font=emoji_font(self.fonts, 30), bg=PALETTE["card"]).pack(pady=(4, 0))
        tk.Label(inner, text=profile["name"], font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack()
        tk.Label(inner, text="Введіть PIN-код (4 цифри)", font=self.fonts["body_sm"], bg=PALETTE["card"], fg=PALETTE["muted"]).pack(pady=(2, 8))
        vcmd = (win.register(self._digits_only), "%P")
        var = tk.StringVar()
        entry = tk.Entry(inner, textvariable=var, show="●", width=6, justify="center", font=(self.fonts["family"], 20, "bold"),
                         validate="key", validatecommand=vcmd, relief="flat", bg=PALETTE["card_soft"],
                         highlightthickness=2, highlightbackground=PALETTE["border"], highlightcolor=PALETTE["primary"])
        entry.pack(ipady=4)
        status = tk.Label(inner, text="", font=self.fonts["small"], bg=PALETTE["card"], fg=PALETTE["err_fg"])
        status.pack(pady=(6, 4))

        def submit(_e=None):
            if not win.winfo_exists() or not var.get():
                return
            ok, msg = self._pin_guard().check(profile, var.get())
            if ok:
                win.destroy()
                on_success()
            else:
                status.config(text=msg)
                var.set("")

        def forgot():
            win.destroy()
            self._forgot_pin(profile)

        row = tk.Frame(inner, bg=PALETTE["card"])
        row.pack(fill="x", pady=(4, 0))
        RoundedButton(row, text="Увійти", command=submit, font=self.fonts["bold"], radius=14, height=36, min_width=120,
                      parent_bg=PALETTE["card"]).pack(side="right")
        RoundedButton(row, text="Скасувати", command=win.destroy, bg=PALETTE["card_soft"], hover_bg=PALETTE["soft_indigo"],
                      fg=PALETTE["text"], border_color=PALETTE["border"], font=self.fonts["bold_sm"], radius=14, height=36,
                      min_width=100, parent_bg=PALETTE["card"]).pack(side="right", padx=8)
        link = tk.Label(row, text="Забули PIN?", font=self.fonts["small"], bg=PALETTE["card"], fg=PALETTE["primary"], cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda _e: forgot())
        entry.bind("<Return>", submit)
        var.trace_add("write", lambda *_: len(var.get()) == PIN_LENGTH and win.after(60, submit))
        win.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - win.winfo_reqwidth()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - win.winfo_reqheight()) // 3
        win.geometry(f"+{max(0, x)}+{max(0, y)}")
        try:
            win.grab_set()
        except tk.TclError:
            pass
        entry.focus_set()
        self._pin_dialog = win
        return win

    def _forgot_pin(self, profile):
        if not messagebox.askyesno(
            "Забули PIN?",
            "PIN-код зберігається лише в зашифрованому вигляді, тому відновити його неможливо.\n\n"
            f"Можна видалити профіль «{profile['name']}» разом з усіма його результатами, звітами й банками "
            "та створити новий.\n\nВидалити профіль?",
            icon="warning",
        ):
            return
        self._delete_profile(profile, confirm=True)

    def _delete_profile(self, profile, confirm=True):
        if confirm and not messagebox.askyesno(
            "Видалити профіль",
            f"Точно видалити профіль «{profile['name']}»?\n\nУсі його результати, звіти й власні банки буде видалено "
            "назавжди. Скасувати це неможливо.",
            icon="warning",
        ):
            return
        try:
            self.store.delete_profile(profile["id"])
        except Exception as exc:
            messagebox.showerror("Помилка", f"Не вдалося видалити профіль:\n{exc}")
            return
        self.start_profiles()

    # -------------------------------------------------------------------
    # СТВОРЕННЯ / РЕДАГУВАННЯ ПРОФІЛЮ
    # -------------------------------------------------------------------
    def show_new_profile_form(self):
        """Short form for a new profile: only the name and an optional PIN (the rest is set later in «Мій профіль»)."""
        self._clear_main()
        self._leave_profile()
        first_run = not self.store.list_profiles()
        if first_run:
            self._nav_header("Створимо твій профіль", "Потрібні лише ім’я та, за бажанням, PIN-код")
        else:
            self._nav_header("Новий профіль", "Окремі результати та налаштування для ще одного учня")

        body = tk.Frame(self.main_container, bg=PALETTE["bg"])
        body.pack(fill="both", expand=True)
        card = RoundedCard(body, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=22,
                           width=470, height=470 if self.cloud_enabled() else 430)
        card.place(relx=0.5, rely=0.45, anchor="center")
        form = card.inner

        owl = OwlMascot(form, size=72, bg=PALETTE["card"])
        owl.pack(pady=(0, 6))
        tk.Label(form, text="Як тебе звати?", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w")
        self.var_pname = tk.StringVar()
        name_entry = tk.Entry(form, textvariable=self.var_pname, font=self.fonts["h3"], relief="flat", bg=PALETTE["card_soft"],
                              highlightthickness=2, highlightbackground=PALETTE["border"], highlightcolor=PALETTE["primary"])
        name_entry.pack(fill="x", ipady=6, pady=(4, 14))

        tk.Label(form, text="PIN-код (4 цифри)", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w")
        tk.Label(form, text="Необов’язково: щоб ніхто інший не зайшов у твій профіль.\nЗабутий PIN відновити не можна.",
                 font=self.fonts["small"], bg=PALETTE["card"], fg=PALETTE["muted"], justify="left").pack(anchor="w", pady=(0, 6))
        pin_row = tk.Frame(form, bg=PALETTE["card"])
        pin_row.pack(anchor="w")
        vcmd = (self.root.register(self._digits_only), "%P")
        self.var_pin1 = tk.StringVar()
        self.var_pin2 = tk.StringVar()
        for label, var in (("PIN:", self.var_pin1), ("Ще раз:", self.var_pin2)):
            tk.Label(pin_row, text=label, font=self.fonts["body_sm"], bg=PALETTE["card"], fg=PALETTE["muted"]).pack(side="left", padx=(0, 6))
            ent = tk.Entry(pin_row, textvariable=var, show="●", width=6, justify="center", font=self.fonts["h3"], validate="key",
                           validatecommand=vcmd, relief="flat", bg=PALETTE["card_soft"], highlightthickness=2,
                           highlightbackground=PALETTE["border"], highlightcolor=PALETTE["primary"])
            ent.pack(side="left", padx=(0, 16), ipady=3)
            ent.bind("<Return>", lambda _e: self._save_new_profile())
        name_entry.bind("<Return>", lambda _e: self._save_new_profile())

        actions = tk.Frame(form, bg=PALETTE["card"])
        actions.pack(fill="x", side="bottom")
        RoundedButton(actions, text="✨ Створити профіль", command=self._save_new_profile, font=self.fonts["h3"], radius=16,
                      height=42, min_width=210, parent_bg=PALETTE["card"]).pack(side="right")
        if self.cloud_enabled() and getattr(self, "_pending_cloud_session", None) is None:
            link = tk.Label(form, text="Вже маєш профіль у хмарі? ☁️ Увійти через пошту", font=self.fonts["small"],
                            bg=PALETTE["card"], fg=PALETTE["primary"], cursor="hand2")
            link.pack(side="bottom", anchor="w", pady=(0, 10))
            link.bind("<Button-1>", lambda _e: self.cloud_sign_in_from_picker())
        elif getattr(self, "_pending_cloud_session", None) is not None:
            tk.Label(form, text=f"☁️ Профіль зберігатиметься в хмарі: {self._pending_cloud_session.email}",
                     font=self.fonts["small"], bg=PALETTE["card"], fg=PALETTE["ok_fg"]).pack(side="bottom", anchor="w", pady=(0, 10))
        if not first_run:
            RoundedButton(actions, text="Скасувати", command=self.show_profiles, bg=PALETTE["card_soft"], hover_bg=PALETTE["soft_indigo"],
                          fg=PALETTE["text"], border_color=PALETTE["border"], font=self.fonts["bold_sm"], radius=16, height=42,
                          min_width=120, parent_bg=PALETTE["card"]).pack(side="right", padx=10)
        name_entry.focus_set()

    def _save_new_profile(self):
        pin1, pin2 = self.var_pin1.get(), self.var_pin2.get()
        try:
            profile = new_profile(self.var_pname.get(), provider=PROVIDER_LOCAL)
            if pin1 or pin2:
                if not is_valid_pin(pin1):
                    raise ProfileError("PIN-код має складатися рівно з 4 цифр (або залиште обидва поля порожніми).")
                if pin1 != pin2:
                    raise ProfileError("PIN-коди не збігаються. Введіть однаковий PIN двічі.")
                profile["pin"] = hash_pin(pin1)
        except ProfileError as exc:
            messagebox.showwarning("Перевірте профіль", str(exc))
            return
        self._store_profile(profile, creating=True)

    def show_profile_form(self, profile=None):
        """Full form to edit `profile`; profile=None opens the short «new profile» form instead."""
        if profile is None:
            self.show_new_profile_form()
            return
        self._clear_main()
        self._form_profile = dict(profile)
        self._nav_header("Мій профіль", "Ім’я, аватар, предмети, цілі та захист PIN-кодом")

        body = tk.Frame(self.main_container, bg=PALETTE["bg"])
        body.pack(fill="both", expand=True, padx=20, pady=(14, 0))
        card = RoundedCard(body, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=16)
        card.pack(fill="both", expand=True)
        scroll = SmoothScrollView(card.inner, bg=PALETTE["card"])
        scroll.pack(fill="both", expand=True)
        form = scroll.inner

        def section(text, hint=None):
            tk.Label(form, text=text, font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", pady=(12, 2))
            if hint:
                tk.Label(form, text=hint, font=self.fonts["small"], bg=PALETTE["card"], fg=PALETTE["muted"], justify="left").pack(anchor="w", pady=(0, 4))

        # --- how to sign in -----------------------------------------------------
        ways = ", ".join(self._provider_title(i["provider"]) + (f" ({i['email']})" if i.get("email") else "")
                         for i in profile.get("identities", []))
        section("Спосіб входу", ways)

        # --- name ------------------------------------------------------------------
        section("Як тебе звати?")
        self.var_pname = tk.StringVar(value=profile["name"])
        name_entry = tk.Entry(form, textvariable=self.var_pname, font=self.fonts["h3"], width=30, relief="flat",
                              bg=PALETTE["card_soft"], highlightthickness=2, highlightbackground=PALETTE["border"],
                              highlightcolor=PALETTE["primary"])
        name_entry.pack(anchor="w", ipady=5)

        # --- avatar ----------------------------------------------------------------
        section("Аватар")
        current_av = (profile.get("avatar") or {}).get("value")
        self.var_avatar = tk.StringVar(value=current_av if current_av in AVATARS else DEFAULT_AVATAR)
        av_row = tk.Frame(form, bg=PALETTE["card"])
        av_row.pack(anchor="w")
        for i, emo in enumerate(AVATARS):
            AvatarChoice(av_row, emo, self.var_avatar, self.fonts).grid(row=i // 9, column=i % 9, padx=3, pady=3)

        # --- subjects ----------------------------------------------------------------
        section("Мої предмети НМТ", "Їх буде позначено одразу на екрані вибору, а в кабінеті — показано прогрес")
        chosen = set(profile.get("subjects") or [])
        self.prof_subj_vars = {}
        grid = tk.Frame(form, bg=PALETTE["card"])
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        for idx, sid in enumerate(SUBJECTS_ORDER):
            var = tk.BooleanVar(value=sid in chosen)
            self.prof_subj_vars[sid] = var
            r, c = divmod(idx, 2)
            SubjectTile(grid, sid, SUBJECTS_CONFIG[sid], var, self.fonts, on_change=self._refresh_target_rows).grid(
                row=r, column=c, sticky="nsew", padx=4, pady=3)

        # --- goals ---------------------------------------------------------------------
        section("Мої цілі", "Бажаний бал НМТ за шкалою 100–200 для кожного предмета")
        old_targets = dict(profile.get("targets") or {})
        self.prof_target_vars = {sid: tk.StringVar(value=str(old_targets.get(sid, DEFAULT_TARGET))) for sid in SUBJECTS_ORDER}
        self.prof_targets_box = tk.Frame(form, bg=PALETTE["card"])
        self.prof_targets_box.pack(fill="x")
        self._refresh_target_rows()

        # --- exam date ------------------------------------------------------------------
        section("Дата НМТ", "Наприклад 20.05.2027 — у кабінеті з’явиться відлік днів. Можна залишити порожнім.")
        self.var_exam = tk.StringVar(value=format_exam_date(profile.get("exam_date")))
        tk.Entry(form, textvariable=self.var_exam, font=self.fonts["body"], width=14, relief="flat", bg=PALETTE["card_soft"],
                 highlightthickness=2, highlightbackground=PALETTE["border"], highlightcolor=PALETTE["primary"]).pack(anchor="w", ipady=4)

        # --- PIN ------------------------------------------------------------------------
        section("PIN-код", "Щоб брат чи сестра не заходили у твій профіль. Забутий PIN відновити не можна.")
        had_pin = has_pin(profile)
        self.var_use_pin = tk.BooleanVar(value=had_pin)
        tk.Checkbutton(form, text="Захистити профіль PIN-кодом (4 цифри)", variable=self.var_use_pin, command=self._toggle_pin_rows,
                       font=self.fonts["body"], bg=PALETTE["card"], fg=PALETTE["text"], activebackground=PALETTE["card"],
                       selectcolor=PALETTE["card"]).pack(anchor="w")
        self.prof_pin_box = tk.Frame(form, bg=PALETTE["card"])
        vcmd = (self.root.register(self._digits_only), "%P")
        self.var_pin1 = tk.StringVar()
        self.var_pin2 = tk.StringVar()
        for label, var in (("PIN:", self.var_pin1), ("Ще раз:", self.var_pin2)):
            tk.Label(self.prof_pin_box, text=label, font=self.fonts["body_sm"], bg=PALETTE["card"], fg=PALETTE["muted"]).pack(side="left", padx=(0, 6))
            tk.Entry(self.prof_pin_box, textvariable=var, show="●", width=6, justify="center", font=self.fonts["h3"],
                     validate="key", validatecommand=vcmd, relief="flat", bg=PALETTE["card_soft"], highlightthickness=2,
                     highlightbackground=PALETTE["border"], highlightcolor=PALETTE["primary"]).pack(side="left", padx=(0, 16), ipady=3)
        if had_pin:
            tk.Label(self.prof_pin_box, text="порожньо — залишити поточний", font=self.fonts["small"], bg=PALETTE["card"],
                     fg=PALETTE["muted"]).pack(side="left")
        self._toggle_pin_rows()

        # --- actions --------------------------------------------------------------------
        actions = tk.Frame(self.main_container, bg=PALETTE["bg"])
        actions.pack(fill="x", padx=20, pady=12)
        RoundedButton(actions, text="💾 Зберегти", command=self._save_profile_form,
                      font=self.fonts["h3"], radius=16, height=42, min_width=220, parent_bg=PALETTE["bg"]).pack(side="right")
        RoundedButton(actions, text="Скасувати", command=self.show_cabinet, bg=PALETTE["card"], hover_bg=PALETTE["soft_indigo"],
                      fg=PALETTE["text"], border_color=PALETTE["border"], font=self.fonts["bold_sm"], radius=16, height=42,
                      min_width=130, parent_bg=PALETTE["bg"]).pack(side="right", padx=10)
        RoundedButton(actions, text="🗑 Видалити профіль", command=lambda: self._delete_profile(self.profile),
                      bg=PALETTE["soft_rose"], hover_bg=PALETTE["err_bg"], fg=PALETTE["err_fg"], border_color=PALETTE["soft_rose_bd"],
                      font=self.fonts["bold_sm"], radius=16, height=42, min_width=180, parent_bg=PALETTE["bg"]).pack(side="left")
        name_entry.focus_set()

    def _provider_title(self, provider_id):
        for prov in available_providers():
            if prov.id == provider_id:
                return f"{prov.icon} {prov.title}"
        return {"google": "Google", "apple": "Apple", PROVIDER_CLOUD: "☁️ Хмарний акаунт"}.get(provider_id, provider_id)

    def _refresh_target_rows(self):
        box = getattr(self, "prof_targets_box", None)
        if box is None or not box.winfo_exists():
            return
        for w in box.winfo_children():
            w.destroy()
        chosen = [sid for sid in SUBJECTS_ORDER if self.prof_subj_vars[sid].get()]
        if not chosen:
            tk.Label(box, text="Спершу оберіть предмети вище.", font=self.fonts["body_sm"], bg=PALETTE["card"], fg=PALETTE["muted"]).pack(anchor="w")
            return
        for i, sid in enumerate(chosen):
            r, c = divmod(i, 2)
            cell = tk.Frame(box, bg=PALETTE["card"])
            cell.grid(row=r, column=c, sticky="w", padx=(0, 28), pady=2)
            tk.Label(cell, text=SUBJECTS_CONFIG[sid]["name"], font=self.fonts["body_sm"], bg=PALETTE["card"], fg=PALETTE["text"],
                     width=26, anchor="w").pack(side="left")
            tk.Spinbox(cell, from_=SCORE_MIN, to=SCORE_MAX, increment=5, textvariable=self.prof_target_vars[sid], width=5,
                       font=self.fonts["bold"], justify="center", relief="flat", bg=PALETTE["card_soft"],
                       highlightthickness=1, highlightbackground=PALETTE["border"]).pack(side="left")

    def _toggle_pin_rows(self):
        if self.var_use_pin.get():
            self.prof_pin_box.pack(anchor="w", pady=(6, 0))
        else:
            self.prof_pin_box.pack_forget()

    def _collect_profile_form(self):
        """Profile dict from the form (raises ProfileError with a message for the user)."""
        subjects = [sid for sid in SUBJECTS_ORDER if self.prof_subj_vars[sid].get()]
        targets = {sid: self.prof_target_vars[sid].get().strip() for sid in subjects}
        exam = parse_exam_date(self.var_exam.get())
        base = self._form_profile
        profile = dict(base)
        profile.update(name=self.var_pname.get(), avatar={"kind": "emoji", "value": self.var_avatar.get()},
                       subjects=subjects, targets=targets, exam_date=exam)
        normalize_profile(profile)
        touch(profile)
        pin1, pin2 = self.var_pin1.get(), self.var_pin2.get()
        if not self.var_use_pin.get():
            profile["pin"] = None
        elif pin1 or pin2 or not has_pin(base):
            if not is_valid_pin(pin1):
                raise ProfileError("PIN-код має складатися рівно з 4 цифр.")
            if pin1 != pin2:
                raise ProfileError("PIN-коди не збігаються. Введіть однаковий PIN двічі.")
            profile["pin"] = hash_pin(pin1)
        return profile

    def _save_profile_form(self):
        try:
            profile = self._collect_profile_form()
        except ProfileError as exc:
            messagebox.showwarning("Перевірте профіль", str(exc))
            return
        self._store_profile(profile, creating=False)

    def _store_profile(self, profile, creating):
        try:
            first = creating and not self.store.list_profiles()
            self.store.save_profile(profile)
            moved = self.store.assign_unassigned(profile["id"]) if first and self.store.count_unassigned() else 0
        except Exception as exc:
            messagebox.showerror("Помилка", f"Не вдалося зберегти профіль:\n{exc}")
            return
        if moved:
            messagebox.showinfo("Твої попередні результати",
                                f"Результати, звіти й банки з попередніх тренувань (записів: {moved}) додано до профілю «{profile['name']}».")
        if creating:
            self.enter_profile(profile)
            self._cloud_after_profile_created(profile)
        else:
            self.profile = profile
            self._update_window_title()
            self._setup_menus()
            self.show_cabinet()
            self.cloud_sync_soon()

    def _update_window_title(self):
        from ... import APP_TITLE

        name = self.profile["name"] if getattr(self, "profile", None) else None
        self.root.title(f"{APP_TITLE} — {name}" if name else APP_TITLE)
