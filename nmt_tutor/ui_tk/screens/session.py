"""Screen 2: the test view (task card, owl chat with 10-level hints, answer widgets)."""

import tkinter as tk
from tkinter import messagebox, ttk

from ...config import SUBJECTS_CONFIG, SUBJECTS_ORDER
from ...engine import block_score, build_session_plan, evaluate_answer, is_empty_answer
from ...hints import build_10_hints
from ..owl import OwlMascot
from ..scroll import SmoothScrollView
from ..theme import PALETTE
from ..widgets import HintStepperBar, RoundedButton, RoundedCard, RoundedCheckRow, RoundedOptionRow


class SessionScreenMixin:
    # -------------------------------------------------------------------
    # 2. ЕКРАН ТЕСТУВАННЯ + ЄДИНА ПЛАВНО ПРОКРУЧУВАНА ПРАВА ПАНЕЛЬ
    # -------------------------------------------------------------------
    def _start_session(self):
        selected = [sid for sid in SUBJECTS_ORDER if self.subj_vars[sid].get()]
        if not selected:
            messagebox.showwarning("Оберіть предмети", "Позначте бодай один предмет НМТ для початку тренування.")
            return
        self.tutor_mode = (self.var_mode.get() == "tutor")
        self.length_mode = self.var_length.get()
        self.plan = build_session_plan(selected, length_mode=self.length_mode, custom_bank=self.custom_bank)
        self.current_block_idx = 0
        self.current_q_idx = 0
        self.is_mistake_drill = False
        self.focus_section = None
        self.timer_seconds = len(selected) * 60 * 60
        self._build_test_view()
        self._load_current_question()
        self._tick_timer()

    def _on_pane_configure(self, e):
        if self._pane is None:
            return
        want_orient = "vertical" if e.width < 820 else "horizontal"
        if want_orient != self._pane_orient:
            self._pane_orient = want_orient
            try:
                self._pane.configure(orient=want_orient)
            except Exception:
                pass

    def _build_test_view(self):
        self._clear_main()

        top = tk.Frame(self.main_container, bg=PALETTE["nav"], height=64)
        top.pack(fill="x")
        top.pack_propagate(False)

        self.lbl_subj_title = tk.Label(top, text="", font=self.fonts["h2"], bg=PALETTE["nav"], fg="#FFFFFF")
        self.lbl_subj_title.pack(side="left", padx=20)

        RoundedButton(
            top,
            text="Завершити тест",
            command=self._finish_session,
            bg="#EF4444",
            hover_bg="#DC2626",
            fg="#FFFFFF",
            font=self.fonts["bold_sm"],
            radius=14,
            height=34,
            min_width=136,
            parent_bg=PALETTE["nav"],
        ).pack(side="right", padx=16, pady=14)

        self.lbl_timer = tk.Label(top, text="⏱ 60:00", font=self.fonts["h3"], bg=PALETTE["nav_accent"], fg="#BFDBFE", padx=12, pady=5)
        self.lbl_timer.pack(side="right", padx=8)
        self.lbl_score_live = tk.Label(top, text="Бал: 0", font=self.fonts["h3"], bg=PALETTE["nav_accent"], fg="#A7F3D0", padx=12, pady=5)
        self.lbl_score_live.pack(side="right", padx=8)

        subj_bar = tk.Frame(self.main_container, bg=PALETTE["bg"])
        subj_bar.pack(fill="x", padx=18, pady=(8, 2))
        self.subj_tab_btns = []
        for idx, b in enumerate(self.plan):
            cname = SUBJECTS_CONFIG[b["subject"]]["name"]
            btn = RoundedButton(
                subj_bar,
                text=cname,
                command=lambda i=idx: self._switch_block(i),
                bg=PALETTE["card"],
                hover_bg=PALETTE["soft_indigo"],
                fg=PALETTE["text"],
                border_color=PALETTE["border"],
                font=self.fonts["bold_sm"],
                radius=14,
                height=30,
                min_width=100,
                pad_x=12,
                parent_bg=PALETTE["bg"],
            )
            btn.pack(side="left", padx=(0, 8), pady=2)
            self.subj_tab_btns.append(btn)

        self._pane_orient = "horizontal"
        pane = tk.PanedWindow(self.main_container, orient="horizontal", bg=PALETTE["bg"], sashwidth=10, sashrelief="flat", bd=0)
        pane.pack(fill="both", expand=True, padx=18, pady=(6, 14))
        pane.bind("<Configure>", self._on_pane_configure)
        self._pane = pane

        # ЛІВА КОЛОНКА: Завдання (нижні кнопки закріплені ПЕРШИМИ з side="bottom", тому ніколи не зникають!)
        q_card = RoundedCard(pane, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=16)
        pane.add(q_card, minsize=380, stretch="always")
        q_wrap = q_card.inner

        meta_row = tk.Frame(q_wrap, bg=PALETTE["card"])
        meta_row.pack(fill="x", pady=(0, 4))
        self.lbl_q_num = tk.Label(meta_row, text="", font=self.fonts["h3"], bg=PALETTE["card"], fg=PALETTE["primary"])
        self.lbl_q_num.pack(side="left")
        self.lbl_q_source = tk.Label(meta_row, text="", font=self.fonts["small"], bg=PALETTE["soft_indigo"], fg="#3730A3", padx=10, pady=3)
        self.lbl_q_source.pack(side="right")

        self.lbl_q_section = tk.Label(q_wrap, text="", font=self.fonts["small"], bg=PALETTE["card"], fg=PALETTE["muted"])
        self.lbl_q_section.pack(anchor="w", pady=(0, 6))

        # Закріплені нижні кнопки завдання (звичайний tk.Frame + .grid(), ніколи не зникають і не обрізаються)
        q_actions = tk.Frame(q_wrap, bg=PALETTE["card"])
        q_actions.pack(side="bottom", fill="x", pady=(10, 2))
        q_actions.columnconfigure(2, weight=1)
        self.btn_submit = RoundedButton(
            q_actions,
            text="✓ Перевірити відповідь",
            command=self._submit_question,
            bg=PALETTE["primary"],
            hover_bg=PALETTE["primary_hover"],
            fg="#FFFFFF",
            font=self.fonts["bold_sm"],
            radius=16,
            height=38,
            min_width=164,
            pad_x=12,
            parent_bg=PALETTE["card"],
        )
        self.btn_hint = RoundedButton(
            q_actions,
            text="💡 Підказка (1/10)",
            command=self._step_next_hint,
            bg=PALETTE["soft_amber"],
            hover_bg="#FEF08A",
            fg="#92400E",
            border_color=PALETTE["soft_amber_bd"],
            font=self.fonts["bold_sm"],
            radius=16,
            height=38,
            min_width=144,
            pad_x=10,
            parent_bg=PALETTE["card"],
        )
        self.btn_next = RoundedButton(
            q_actions,
            text="Далі →",
            command=self._next_question,
            bg=PALETTE["accent"],
            hover_bg=PALETTE["accent_hover"],
            fg="#FFFFFF",
            font=self.fonts["bold_sm"],
            radius=16,
            height=38,
            min_width=94,
            pad_x=12,
            parent_bg=PALETTE["card"],
        )
        q_actions._mode = None

        def _layout_q_actions(w=None):
            cur_w = w or q_actions.winfo_width() or 520
            mode = "wide" if cur_w >= 430 else "compact"
            if mode == q_actions._mode:
                return
            q_actions._mode = mode
            self.btn_submit.grid_forget()
            self.btn_hint.grid_forget()
            self.btn_next.grid_forget()
            if mode == "wide":
                self.btn_submit.grid(row=0, column=0, padx=(0, 6), sticky="w")
                self.btn_hint.grid(row=0, column=1, padx=(0, 6), sticky="w")
                self.btn_next.grid(row=0, column=2, sticky="e")
            else:
                self.btn_submit.grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky="w")
                self.btn_hint.grid(row=0, column=1, pady=(0, 6), sticky="w")
                self.btn_next.grid(row=1, column=0, columnspan=3, sticky="e")

        q_actions.bind("<Configure>", lambda e: _layout_q_actions(e.width))
        _layout_q_actions(520)

        self.q_scroll = SmoothScrollView(q_wrap, bg=PALETTE["card"], bottom_pad=24)
        self.q_scroll.pack(side="top", fill="both", expand=True, pady=4)
        self.q_inner = self.q_scroll.inner

        # ПРАВА КОЛОНКА: Закріплена Сова-Ліза + 10-рівневий степпер + ЄДИНА плавна область прокрутки
        t_card = RoundedCard(pane, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=14)
        pane.add(t_card, minsize=360, stretch="always")
        t_wrap = t_card.inner

        owl_banner = RoundedCard(t_wrap, bg=PALETTE["soft_indigo"], border=PALETTE["soft_indigo_bd"], parent_bg=PALETTE["card"], radius=18, pad=10, shadow=False, height=106)
        owl_banner.pack(fill="x", pady=(0, 8))
        owl_banner.pack_propagate(False)
        ob_in = owl_banner.inner

        self.owl_tutor = OwlMascot(ob_in, size=86, bg=PALETTE["soft_indigo"])
        self.owl_tutor.pack(side="left", padx=(2, 10))

        owl_info = tk.Frame(ob_in, bg=PALETTE["soft_indigo"])
        owl_info.pack(side="left", fill="both", expand=True, pady=2)
        tk.Label(
            owl_info,
            text="Сова-Ліза • Мудрий Репетитор",
            font=self.fonts["h3"],
            bg=PALETTE["soft_indigo"],
            fg="#1E2B58",
        ).pack(anchor="w")
        self.lbl_owl_status = tk.Label(
            owl_info,
            text="Читаю умову разом із тобою. Тисни підказку (1–10) або обирай відповідь!",
            font=self.fonts["body_sm"],
            bg=PALETTE["soft_indigo"],
            fg="#334155",
            wraplength=280,
            justify="left",
        )
        self.lbl_owl_status.pack(anchor="w", pady=(3, 0))
        owl_info.bind("<Configure>", lambda e: self.lbl_owl_status.config(wraplength=max(160, e.width - 12)))

        # Шкала 10 рівнів підказок під Совою-Лізою
        self.hint_stepper = HintStepperBar(
            t_wrap,
            self.fonts,
            on_step=self._step_next_hint,
            on_select_level=self._show_hint_level,
            bg=PALETTE["card_soft"],
        )
        self.hint_stepper.pack(fill="x", pady=(0, 6))

        # ЄДИНА ПЛАВНА ОБЛАСТЬ ПРОКРУТКИ: Чат-бульбашки + Блок ідентичного прикладу!
        self.tutor_scroll = SmoothScrollView(t_wrap, bg=PALETTE["card"], bottom_pad=32)
        self.tutor_scroll.pack(fill="both", expand=True, pady=(2, 0))
        self.tutor_scroll.register_width_listener(self._on_tutor_width_change)

        self.chat_stack = tk.Frame(self.tutor_scroll.inner, bg=PALETTE["card"])
        self.chat_stack.pack(fill="x", padx=2, pady=(2, 4))

        # Блок ідентичних прикладів усередині тієї ж прокрутки — прокручується до самого низу!
        self.drill_card = RoundedCard(
            self.tutor_scroll.inner,
            bg=PALETTE["soft_mint"],
            border=PALETTE["soft_mint_bd"],
            parent_bg=PALETTE["card"],
            radius=18,
            pad=12,
            shadow=False,
            auto_height=True,
        )
        self.drill_frame = self.drill_card.inner

        self.timer_running = True

    def _on_tutor_width_change(self, new_w):
        wrap = max(160, new_w - 58)
        for lbl in list(self._chat_labels):
            try:
                if lbl.winfo_exists():
                    lbl.config(wraplength=wrap)
            except Exception:
                pass
        try:
            if self.drill_card.winfo_ismapped():
                self.drill_card.sync_height(notify=False)
            self.tutor_scroll._schedule_sync(delay=20)
        except Exception:
            pass

    def _update_tab_styles(self):
        for idx, btn in enumerate(self.subj_tab_btns):
            if idx == self.current_block_idx:
                btn.set_colors(bg=PALETTE["primary"], hover_bg=PALETTE["primary_hover"], fg="#FFFFFF", border_color=PALETTE["primary"])
            else:
                btn.set_colors(bg=PALETTE["card"], hover_bg=PALETTE["soft_indigo"], fg=PALETTE["text"], border_color=PALETTE["border"])

    def _append_chat(self, speaker_tag, speaker_title, message, body_tag=None):
        bg_map = {
            "student_lbl": PALETTE["card_soft"],
            "tutor_lbl": PALETTE["soft_indigo"],
            "err": PALETTE["soft_rose"],
        }
        bd_map = {
            "student_lbl": PALETTE["border"],
            "tutor_lbl": PALETTE["soft_indigo_bd"],
            "err": PALETTE["soft_rose_bd"],
        }
        title_col = {
            "student_lbl": "#475569",
            "tutor_lbl": PALETTE["primary"],
            "err": PALETTE["err_fg"],
        }
        if body_tag == "ok":
            b_bg, b_bd, b_fg = PALETTE["ok_bg"], "#86EFAC", PALETTE["ok_fg"]
        elif body_tag == "hint":
            b_bg, b_bd, b_fg = PALETTE["soft_amber"], PALETTE["soft_amber_bd"], "#78350F"
        elif body_tag == "rule":
            b_bg, b_bd, b_fg = "#EEF2FF", "#A5B4FC", PALETTE["text"]
        else:
            b_bg = bg_map.get(speaker_tag, PALETTE["card_soft"])
            b_bd = bd_map.get(speaker_tag, PALETTE["border"])
            b_fg = PALETTE["text"]

        bubble = RoundedCard(
            self.chat_stack,
            bg=b_bg,
            border=b_bd,
            parent_bg=PALETTE["card"],
            radius=15,
            pad=10,
            shadow=False,
            auto_height=True,
        )
        bubble.pack(fill="x", pady=(0, 6))

        try:
            cur_w = max(220, self.tutor_scroll.canvas.winfo_width() - 58)
        except Exception:
            cur_w = 340

        tk.Label(
            bubble.inner,
            text=speaker_title,
            font=self.fonts["bold_sm"],
            bg=b_bg,
            fg=title_col.get(speaker_tag, PALETTE["primary"]),
            anchor="w",
        ).pack(anchor="w")
        lbl_msg = tk.Label(
            bubble.inner,
            text=message,
            font=self.fonts["body_sm"],
            bg=b_bg,
            fg=b_fg,
            wraplength=cur_w,
            justify="left",
        )
        lbl_msg.pack(anchor="w", pady=(2, 0))
        self._chat_labels.append(lbl_msg)
        self.tutor_scroll.scroll_to_bottom(delay_ms=50)

    def _update_live_score(self, block):
        earned_total, max_so_far = block_score(block)
        self.lbl_score_live.config(text=f"Бал: {earned_total} / {max_so_far}")

    def _clear_chat(self):
        self._chat_labels = []
        for w in self.chat_stack.winfo_children():
            w.destroy()

    def _capture_pending_answer(self):
        """Counts an answer that was chosen but not checked with «Перевірити».

        The student can leave a task with «Далі →», a subject tab or «Завершити тест»;
        the chosen answer is then scored quietly (no tutor explanation) instead of being lost.
        """
        if not self.plan:
            return
        block = self.plan[self.current_block_idx]
        idx = self.current_q_idx
        getter = getattr(self, "active_answer_getter", None)
        if idx in block["answers"] or getter is None:
            return
        try:
            u_ans = getter()
        except Exception:  # widgets already destroyed
            return
        if is_empty_answer(u_ans):
            return
        ok, pts, _, _ = evaluate_answer(block["questions"][idx], u_ans)
        block["answers"][idx] = u_ans
        block["points"][idx] = pts
        if not ok and idx not in block["mistakes"]:
            block["mistakes"].append(idx)

    def _switch_block(self, b_idx):
        self._capture_pending_answer()
        self.current_block_idx = b_idx
        self.current_q_idx = 0
        self._load_current_question()

    def _build_answer_widgets(self, parent, q, bg_color, is_drill=False):
        qt = q["qtype"]
        try:
            base_wrap = max(220, parent.winfo_width() - 28) if parent.winfo_width() > 80 else 440
        except Exception:
            base_wrap = 440

        lbl_prompt = tk.Label(parent, text=q["prompt"], font=self.fonts["body"], bg=bg_color, fg=PALETTE["text"], justify="left", wraplength=base_wrap)
        lbl_prompt.pack(anchor="w", pady=(2, 10))
        parent.bind("<Configure>", lambda e, lbl=lbl_prompt: lbl.config(wraplength=max(200, e.width - 24)))

        if qt == "single":
            var = tk.StringVar(value="")
            active_bg = "#D1FAE5" if is_drill else PALETTE["soft_indigo"]
            active_bd = PALETTE["accent"] if is_drill else PALETTE["primary"]
            for lbl, opt in zip(q["labels"], q["options"]):
                row = RoundedOptionRow(parent, lbl, opt, var, self.fonts, base_bg=bg_color, active_bg=active_bg, active_bd=active_bd)
                row.pack(fill="x", pady=3)
            return lambda: var.get()

        elif qt == "short":
            tk.Label(parent, text="Відповідь (число або десятковий дріб):", font=self.fonts["small"], bg=bg_color, fg=PALETTE["muted"]).pack(anchor="w")
            ent_wrap = tk.Frame(parent, bg=PALETTE["border"], padx=1, pady=1)
            ent_wrap.pack(anchor="w", pady=6)
            ent = tk.Entry(ent_wrap, font=self.fonts["h3"], width=20, bg="#FFFFFF", fg=PALETTE["text"], insertbackground=PALETTE["text"], relief="flat", bd=6)
            ent.pack()
            return lambda: ent.get().strip()

        elif qt == "matching":
            right_box = tk.Frame(parent, bg=PALETTE["card_soft"], highlightbackground=PALETTE["border"], highlightthickness=1)
            right_box.pack(fill="x", pady=(2, 8))
            r_lbls = []
            for rk, rv in q["right"].items():
                rl = tk.Label(right_box, text=f"{rk}) {rv}", font=self.fonts["small"], bg=PALETTE["card_soft"], fg=PALETTE["text"], wraplength=max(200, base_wrap - 20), justify="left")
                rl.pack(anchor="w", padx=10, pady=2)
                r_lbls.append(rl)
            right_box.bind("<Configure>", lambda e, lst=r_lbls: [x.config(wraplength=max(180, e.width - 24)) for x in lst])

            choices = list(q["right"].keys())
            combos = {}
            for idx, row_text in enumerate(q["left"], 1):
                row_f = tk.Frame(parent, bg=bg_color)
                row_f.pack(fill="x", pady=4)
                l_lbl = tk.Label(row_f, text=row_text, font=self.fonts["body_sm"], bg=bg_color, fg=PALETTE["text"], wraplength=max(160, base_wrap - 90), justify="left")
                l_lbl.pack(side="left", anchor="w", fill="x", expand=True)
                cb = ttk.Combobox(row_f, values=choices, state="readonly", width=5, font=self.fonts["bold"])
                cb.pack(side="right", padx=(8, 4))
                row_f.bind("<Configure>", lambda e, ll=l_lbl: ll.config(wraplength=max(140, e.width - 86)))
                combos[str(idx)] = cb
            return lambda: {k: c.get() for k, c in combos.items()}

        elif qt == "sequence":
            s_lbls = []
            for k, v in q["items"].items():
                sl = tk.Label(parent, text=f"{k}) {v}", font=self.fonts["body_sm"], bg=bg_color, fg=PALETTE["text"], wraplength=base_wrap, justify="left")
                sl.pack(anchor="w", pady=2)
                s_lbls.append(sl)
            parent.bind("<Configure>", lambda e, lbl=lbl_prompt, lst=s_lbls: [lbl.config(wraplength=max(160, e.width - 24))] + [x.config(wraplength=max(160, e.width - 24)) for x in lst])

            grid_f = tk.Frame(parent, bg=bg_color)
            grid_f.pack(fill="x", pady=8)
            letters = list(q["items"].keys())
            cbs = []
            for pos in range(1, 5):
                r_i, c_i = divmod(pos - 1, 2)
                cell = tk.Frame(grid_f, bg=bg_color)
                cell.grid(row=r_i, column=c_i, sticky="w", padx=(0, 14), pady=3)
                tk.Label(cell, text=f"{pos}-е:", font=self.fonts["bold_sm"], bg=bg_color, fg=PALETTE["text"]).pack(side="left", padx=(0, 4))
                cb = ttk.Combobox(cell, values=letters, state="readonly", width=4, font=self.fonts["bold"])
                cb.pack(side="left")
                cbs.append(cb)
            return lambda: "".join(c.get() for c in cbs)

        elif qt == "multi3":
            vars_map = {}
            active_bg = "#D1FAE5" if is_drill else PALETTE["soft_indigo"]
            active_bd = PALETTE["accent"] if is_drill else PALETTE["primary"]
            for k, v in q["items"].items():
                bv = tk.BooleanVar(value=False)
                vars_map[k] = bv
                row = RoundedCheckRow(parent, k, v, bv, self.fonts, base_bg=bg_color, active_bg=active_bg, active_bd=active_bd)
                row.pack(fill="x", pady=2)
            return lambda: [k for k, bv in vars_map.items() if bv.get()]

        return lambda: ""

    def _load_current_question(self):
        block = self.plan[self.current_block_idx]
        cfg = SUBJECTS_CONFIG[block["subject"]]
        qs = block["questions"]
        q = qs[self.current_q_idx]

        self._update_tab_styles()
        self.lbl_subj_title.config(text=f"{cfg['name']} ({self.current_block_idx + 1}/{len(self.plan)})")
        self.lbl_q_num.config(text=f"Завдання {self.current_q_idx + 1} із {len(qs)}  •  макс. {q.get('max_points', 1)} б.")
        self.lbl_q_source.config(text=q.get("source", ""))
        self.lbl_q_section.config(text=f"Тема: {q.get('section', '')}")

        self._update_live_score(block)

        for w in self.q_inner.winfo_children():
            w.destroy()
        self.q_scroll.scroll_to_top(immediate=True)

        self.active_answer_getter = self._build_answer_widgets(self.q_inner, q, PALETTE["card"], is_drill=False)
        self.drill_card.pack_forget()
        self.active_drill = None

        self.q_hints_10 = build_10_hints(q)
        self.q_hint_level = 0
        self.hint_stepper.set_level(0)
        self.btn_hint.set_text("💡 Підказка (1/10)")
        self.btn_hint.set_state("normal" if self.tutor_mode else "disabled")

        self._clear_chat()
        self.tutor_scroll.scroll_to_top(immediate=True)
        self.owl_tutor.set_mood("idle")
        if self.tutor_mode:
            self.lbl_owl_status.config(text="Уважно прочитай умову. Якщо застрягнеш — відкривай підказки по кроках (1 → 10)!")
            self._append_chat(
                "tutor_lbl",
                "🦉 Сова-Ліза:",
                f"Ми на завданні №{self.current_q_idx + 1} ({q['section']}). "
                "Спробуй розв’язати самостійно або натисни «Підказка (1/10)» — я проведу тебе крок за кроком від легкого натяку до повної розповіді!"
            )
        else:
            self.lbl_owl_status.config(text="Режим іспиту: фіксую твої відповіді. Після фінішу розберемо кожну помилку!")
            self._append_chat(
                "tutor_lbl",
                "⏱ Режим іспиту:",
                "Відповідай на завдання блоку. Детальний розбір помилок та опрацювання ідентичних прикладів будуть доступні після завершення."
            )

        already = self.current_q_idx in block["answers"]
        self.btn_submit.set_state("disabled" if already else "normal")

    def _step_next_hint(self):
        if self.q_hint_level >= 10:
            return
        self._show_hint_level(self.q_hint_level + 1)

    def _show_hint_level(self, level):
        if not self.tutor_mode:
            messagebox.showinfo("Режим іспиту", "У режимі іспиту підказки вимкнені — перевірка буде наприкінці.")
            return
        lvl = max(1, min(10, int(level)))
        if not self.q_hints_10:
            block = self.plan[self.current_block_idx]
            self.q_hints_10 = build_10_hints(block["questions"][self.current_q_idx])

        if lvl > self.q_hint_level:
            # Відкриваємо проміжні рівні послідовно або прямо до обраного рівня
            start_lvl = self.q_hint_level + 1
            self._append_chat("student_lbl", "🎓 Учень:", f"Сова-Ліза, дай підказку рівня {lvl}/10!")
            for cur in range(start_lvl, lvl + 1):
                self._append_chat(
                    "tutor_lbl",
                    f"🦉 Сова-Ліза • Підказка {cur}/10:",
                    self.q_hints_10[cur - 1],
                    body_tag=("ok" if cur == 10 else "hint"),
                )
            self.q_hint_level = lvl
        else:
            # Повторно показуємо обраний рівень із лінійки 1..10
            self._append_chat(
                "tutor_lbl",
                f"🦉 Сова-Ліза • Повтор підказки {lvl}/10:",
                self.q_hints_10[lvl - 1],
                body_tag=("ok" if lvl == 10 else "hint"),
            )

        self.hint_stepper.set_level(self.q_hint_level)
        if self.q_hint_level < 10:
            self.btn_hint.set_text(f"💡 Підказка ({self.q_hint_level + 1}/10)")
            self.btn_hint.set_state("normal")
            self.owl_tutor.set_mood("thinking")
            self.lbl_owl_status.config(text=f"Підказка {self.q_hint_level}/10 відкрита! Якщо треба глибше — натисни наступний рівень.")
        else:
            self.btn_hint.set_text("💡 Усі 10/10 відкрито")
            self.btn_hint.set_state("disabled")
            self.owl_tutor.set_mood("explain")
            self.lbl_owl_status.config(text="Ось повна розповідь і правило (10/10)! Тепер сміливо закріпимо на прикладі.")
        self.tutor_scroll.scroll_to_bottom(delay_ms=60)

    def _submit_question(self):
        block = self.plan[self.current_block_idx]
        q = block["questions"][self.current_q_idx]
        u_ans = self.active_answer_getter()

        if is_empty_answer(u_ans):
            messagebox.showinfo("Немає відповіді", "Спочатку оберіть або введіть варіант відповіді.")
            return

        ok, pts, u_repr, c_repr = evaluate_answer(q, u_ans)
        block["answers"][self.current_q_idx] = u_ans
        block["points"][self.current_q_idx] = pts
        self.btn_submit.set_state("disabled")

        self._update_live_score(block)

        if not ok and self.current_q_idx not in block["mistakes"]:
            block["mistakes"].append(self.current_q_idx)

        if not self.tutor_mode:
            self._append_chat("student_lbl", "🎓 Учень:", f"Відповідь збережено: {u_repr}")
            self._next_question()
            return

        self._append_chat("student_lbl", "🎓 Учень:", f"Моя відповідь: {u_repr}")
        if ok:
            self.owl_tutor.set_mood("happy")
            self.lbl_owl_status.config(text="Браво! Абсолютно точно! Рухаймося далі з таким же темпом!")
            self._append_chat(
                "tutor_lbl",
                "🦉 Сова-Ліза:",
                f"✅ Чудово! Абсолютно правильно (+{pts} б.).\n{q['solution']}",
                body_tag="ok"
            )
        else:
            self.owl_tutor.set_mood("explain")
            self.lbl_owl_status.config(text="Нічого страшного! Зараз усе просто поясню й попрактикуємося на ідентичному прикладі нижче.")
            self._append_chat(
                "err",
                "🦉 Сова-Ліза — є помилка! Нумо розберемо зрозуміло:",
                f"Ти відповів(ла): {u_repr}, а правильна відповідь: {c_repr} (набрано {pts} із {q.get('max_points', 1)} б.)."
            )
            self._append_chat("tutor_lbl", "📘 Правило простими словами:", q["rule"], body_tag="rule")
            self._append_chat("tutor_lbl", "🔍 Покроковий розбір саме цього завдання:", q["solution"])
            self._launch_identical_drill(q)

    def _launch_identical_drill(self, source_q):
        self.drill_used_prompts = [source_q["prompt"]]
        self._show_new_drill(source_q)

    def _next_question(self):
        self._capture_pending_answer()
        block = self.plan[self.current_block_idx]
        if self.current_q_idx + 1 < len(block["questions"]):
            self.current_q_idx += 1
            self._load_current_question()
        elif self.current_block_idx + 1 < len(self.plan):
            self.current_block_idx += 1
            self.current_q_idx = 0
            self._load_current_question()
        else:
            self._finish_session()
