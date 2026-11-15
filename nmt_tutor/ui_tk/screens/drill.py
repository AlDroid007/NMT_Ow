"""Identical-example drill shown after a mistake (inline card and full-screen window)."""

import tkinter as tk
from tkinter import messagebox

from ...engine import evaluate_answer, generate_identical_drill, is_empty_answer
from ...hints import build_10_hints
from ..scroll import SmoothScrollView
from ..theme import PALETTE
from ..widgets import RoundedButton, RoundedCard


class DrillMixin:
    def _show_new_drill(self, source_q):
        drill = generate_identical_drill(source_q, used_prompts=self.drill_used_prompts)
        self.drill_used_prompts.append(drill["prompt"])
        self.active_drill = (source_q, drill)
        self.drill_hints_10 = build_10_hints(drill)
        self.drill_hint_level = 0

        for w in self.drill_frame.winfo_children():
            w.destroy()
        self.drill_card.pack(fill="x", padx=2, pady=(8, 18))

        hdr = tk.Frame(self.drill_frame, bg=PALETTE["soft_mint"])
        hdr.pack(fill="x", pady=(0, 6))
        lbl_hdr = tk.Label(
            hdr,
            text="🔁 Опрацювання на ідентичному прикладі (закріплюємо правило!):",
            font=self.fonts["h3"],
            bg=PALETTE["soft_mint"],
            fg="#0F766E",
            wraplength=240,
            justify="left",
        )
        lbl_hdr.pack(side="left", fill="x", expand=True)
        RoundedButton(
            hdr,
            text="⤢ На весь екран",
            command=self._open_drill_fullscreen,
            bg="#FFFFFF",
            hover_bg="#D1FAE5",
            fg="#0F766E",
            border_color=PALETTE["soft_mint_bd"],
            font=self.fonts["small"],
            radius=11,
            height=26,
            min_width=112,
            pad_x=8,
            parent_bg=PALETTE["soft_mint"],
        ).pack(side="right", padx=(6, 0))
        hdr.bind("<Configure>", lambda e, l=lbl_hdr: l.config(wraplength=max(130, e.width - 130)))

        inner = tk.Frame(self.drill_frame, bg=PALETTE["soft_mint"])
        inner.pack(fill="x", pady=2)
        self.drill_answer_getter = self._build_answer_widgets(inner, drill, PALETTE["soft_mint"], is_drill=True)

        self.lbl_drill_fb = tk.Label(
            self.drill_frame,
            text="",
            font=self.fonts["body_sm"],
            bg=PALETTE["soft_mint"],
            fg=PALETTE["text"],
            wraplength=260,
            justify="left",
        )
        self.drill_frame.bind("<Configure>", lambda e, l=self.lbl_drill_fb: l.config(wraplength=max(160, e.width - 16)))

        # Адаптивна 2-рядна .grid() панель кнопок (ніколи не обрізається й не перекривається)
        d_btns = tk.Frame(self.drill_frame, bg=PALETTE["soft_mint"])
        d_btns.pack(fill="x", pady=(10, 2))
        btn_chk = RoundedButton(
            d_btns,
            text="✓ Перевірити",
            command=self._submit_drill,
            bg=PALETTE["accent"],
            hover_bg=PALETTE["accent_hover"],
            fg="#FFFFFF",
            font=self.fonts["bold_sm"],
            radius=14,
            height=34,
            min_width=120,
            pad_x=12,
            parent_bg=PALETTE["soft_mint"],
        )
        self.btn_drill_hint = RoundedButton(
            d_btns,
            text="💡 Підказка (1/10)",
            command=self._step_drill_hint,
            bg=PALETTE["soft_amber"],
            hover_bg="#FEF08A",
            fg="#92400E",
            border_color=PALETTE["soft_amber_bd"],
            font=self.fonts["small"],
            radius=14,
            height=34,
            min_width=128,
            pad_x=10,
            parent_bg=PALETTE["soft_mint"],
        )
        btn_other = RoundedButton(
            d_btns,
            text="Інший ↻",
            command=lambda: self._show_new_drill(source_q),
            bg="#FFFFFF",
            hover_bg="#D1FAE5",
            fg="#0F766E",
            border_color=PALETTE["soft_mint_bd"],
            font=self.fonts["small"],
            radius=14,
            height=34,
            min_width=88,
            pad_x=10,
            parent_bg=PALETTE["soft_mint"],
        )

        d_btns._mode = None

        def _layout_drill_btns(w=None):
            cur_w = w or d_btns.winfo_width() or 380
            mode = "wide" if cur_w >= 362 else "compact"
            if mode == d_btns._mode:
                return
            d_btns._mode = mode
            btn_chk.grid_forget()
            self.btn_drill_hint.grid_forget()
            btn_other.grid_forget()
            if mode == "wide":
                btn_chk.grid(row=0, column=0, padx=(0, 6), pady=(0, 2), sticky="w")
                self.btn_drill_hint.grid(row=0, column=1, padx=(0, 6), pady=(0, 2), sticky="w")
                btn_other.grid(row=0, column=2, pady=(0, 2), sticky="w")
            else:
                btn_chk.grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky="w")
                self.btn_drill_hint.grid(row=0, column=1, pady=(0, 6), sticky="w")
                btn_other.grid(row=1, column=0, columnspan=2, sticky="w")
            self.drill_card._schedule_auto_height()

        d_btns.bind("<Configure>", lambda e: _layout_drill_btns(e.width))
        _layout_drill_btns(380)

        self.drill_card.sync_height(notify=True)
        self.tutor_scroll.sync_scrollregion()
        self.tutor_scroll.scroll_to_bottom(delay_ms=70)
        self.root.after(240, self._realign_drill_scroll)

    def _realign_drill_scroll(self):
        try:
            if self.drill_card.winfo_exists() and self.drill_card.winfo_ismapped():
                self.drill_card.sync_height(notify=True)
                self.tutor_scroll.scroll_to_bottom(delay_ms=20)
        except Exception:
            pass

    def _open_drill_fullscreen(self):
        if not self.active_drill:
            return
        source_q, drill = self.active_drill
        if self._drill_modal is not None:
            try:
                self._drill_modal.destroy()
            except Exception:
                pass

        win = tk.Toplevel(self.root)
        win.title("🔁 Опрацювання ідентичного прикладу • Сова-Ліза")
        try:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
        except Exception:
            sw, sh = 1280, 800
        mw = min(820, max(520, sw - 100))
        mh = min(680, max(440, sh - 120))
        win.geometry(f"{mw}x{mh}+{(sw - mw)//2}+{(sh - mh)//2}")
        win.configure(bg=PALETTE["bg"])
        self._drill_modal = win

        card = RoundedCard(win, bg=PALETTE["soft_mint"], border=PALETTE["soft_mint_bd"], parent_bg=PALETTE["bg"], radius=20, pad=16)
        card.pack(fill="both", expand=True, padx=16, pady=16)

        top_m = tk.Frame(card.inner, bg=PALETTE["soft_mint"])
        top_m.pack(side="top", fill="x", pady=(0, 8))
        tk.Label(top_m, text="🔁 Ідентичний приклад (повний екран)", font=self.fonts["h2"], bg=PALETTE["soft_mint"], fg="#0F766E").pack(side="left")
        RoundedButton(
            top_m,
            text="✕ Згорнути",
            command=win.destroy,
            bg="#FFFFFF",
            hover_bg="#FEE2E2",
            fg=PALETTE["text"],
            border_color=PALETTE["border"],
            font=self.fonts["small"],
            radius=12,
            height=28,
            min_width=95,
            parent_bg=PALETTE["soft_mint"],
        ).pack(side="right")

        btns_m = tk.Frame(card.inner, bg=PALETTE["soft_mint"])
        btns_m.pack(side="bottom", fill="x", pady=(10, 0))

        m_scroll = SmoothScrollView(card.inner, bg=PALETTE["soft_mint"], bottom_pad=24)
        m_scroll.pack(side="top", fill="both", expand=True)

        getter = self._build_answer_widgets(m_scroll.inner, drill, PALETTE["soft_mint"], is_drill=True)
        lbl_fb = tk.Label(m_scroll.inner, text="", font=self.fonts["body_sm"], bg=PALETTE["soft_mint"], fg=PALETTE["text"], wraplength=mw - 100, justify="left")
        lbl_fb.pack(anchor="w", pady=(10, 4))
        m_scroll.sync_scrollregion()

        def _submit_modal():
            d_ans = getter()
            if is_empty_answer(d_ans):
                messagebox.showinfo("Немає відповіді", "Обери або введи відповідь.", parent=win)
                return
            ok, _, u_repr, c_repr = evaluate_answer(drill, d_ans)
            self.plan[self.current_block_idx]["drills_done"] += 1
            self._append_chat("student_lbl", "🎓 Учень (ідентичний приклад):", f"Моя відповідь: {u_repr}")
            if ok:
                self.owl_tutor.set_mood("happy")
                self.lbl_owl_status.config(text="Ура! Тепер ти точно знаєш це правило! Можеш тиснути «Далі →».")
                lbl_fb.config(text=f"✅ Супер! «{u_repr}» — правильно!\n{drill['solution']}", fg=PALETTE["ok_fg"])
                self._append_chat("tutor_lbl", "🦉 Сова-Ліза:", f"✅ Супер! «{u_repr}» — правильно!\n{drill['solution']}", body_tag="ok")
            else:
                self.owl_tutor.set_mood("explain")
                lbl_fb.config(text=f"❌ Неточність ({u_repr}). Правильна відповідь: {c_repr}.\n🔍 Розбір: {drill['solution']}", fg=PALETTE["err_fg"])
                self._append_chat("err", "🦉 Сова-Ліза (перевірка прикладу):", f"Неточність ({u_repr}). Правильна відповідь: {c_repr}.\n{drill['solution']}")
            m_scroll.scroll_to_bottom(delay_ms=40)

        def _hint_modal():
            if self.drill_hint_level >= 10:
                return
            self.drill_hint_level += 1
            lvl = self.drill_hint_level
            lbl_fb.config(text=f"💡 Підказка {lvl}/10:\n{self.drill_hints_10[lvl - 1]}", fg="#78350F")
            self._step_drill_hint_update_ui(lvl)
            m_scroll.scroll_to_bottom(delay_ms=40)

        RoundedButton(btns_m, text="✓ Перевірити", command=_submit_modal, bg=PALETTE["accent"], hover_bg=PALETTE["accent_hover"], fg="#FFFFFF", font=self.fonts["bold_sm"], radius=14, height=36, min_width=130, parent_bg=PALETTE["soft_mint"]).pack(side="left", padx=(0, 8))
        RoundedButton(btns_m, text="💡 Підказка (1..10)", command=_hint_modal, bg=PALETTE["soft_amber"], hover_bg="#FEF08A", fg="#92400E", border_color=PALETTE["soft_amber_bd"], font=self.fonts["small"], radius=14, height=36, min_width=145, parent_bg=PALETTE["soft_mint"]).pack(side="left", padx=(0, 8))
        RoundedButton(btns_m, text="Інший приклад ↻", command=lambda: (win.destroy(), self._show_new_drill(source_q), self._open_drill_fullscreen()), bg="#FFFFFF", hover_bg="#D1FAE5", fg="#0F766E", border_color=PALETTE["soft_mint_bd"], font=self.fonts["small"], radius=14, height=36, min_width=130, parent_bg=PALETTE["soft_mint"]).pack(side="right")

    def _step_drill_hint_update_ui(self, lvl):
        if hasattr(self, "btn_drill_hint") and self.btn_drill_hint.winfo_exists():
            if lvl < 10:
                self.btn_drill_hint.set_text(f"💡 Підказка ({lvl + 1}/10)")
            else:
                self.btn_drill_hint.set_text("💡 10/10")
                self.btn_drill_hint.set_state("disabled")

    def _step_drill_hint(self):
        if not self.active_drill or self.drill_hint_level >= 10:
            return
        self.drill_hint_level += 1
        lvl = self.drill_hint_level
        self.owl_tutor.set_mood("thinking")
        self._append_chat(
            "tutor_lbl",
            f"🦉 Сова-Ліза (до прикладу • {lvl}/10):",
            self.drill_hints_10[lvl - 1],
            body_tag=("ok" if lvl == 10 else "hint"),
        )
        if hasattr(self, "lbl_drill_fb") and self.lbl_drill_fb.winfo_exists():
            self.lbl_drill_fb.config(text=f"💡 Підказка {lvl}/10:\n{self.drill_hints_10[lvl - 1]}", fg="#78350F")
            self.lbl_drill_fb.pack(anchor="w", pady=(6, 2))
            self.drill_card.sync_height(notify=True)
        self._step_drill_hint_update_ui(lvl)
        self.tutor_scroll.scroll_to_bottom(delay_ms=60)

    def _submit_drill(self):
        if not self.active_drill:
            return
        source_q, drill = self.active_drill
        d_ans = self.drill_answer_getter()
        if is_empty_answer(d_ans):
            messagebox.showinfo("Немає відповіді", "Розв’яжи схожий приклад та обери/введи відповідь.")
            return

        ok, _, u_repr, c_repr = evaluate_answer(drill, d_ans)
        self.plan[self.current_block_idx]["drills_done"] += 1

        self._append_chat("student_lbl", "🎓 Учень (ідентичний приклад):", f"Моя відповідь: {u_repr}")
        if ok:
            self.owl_tutor.set_mood("happy")
            self.lbl_owl_status.config(text="Ура! Тепер ти точно знаєш це правило! Можеш тиснути «Далі →».")
            if hasattr(self, "lbl_drill_fb") and self.lbl_drill_fb.winfo_exists():
                self.lbl_drill_fb.config(text=f"✅ Правильно («{u_repr}»)! {drill['solution']}", fg=PALETTE["ok_fg"])
                self.lbl_drill_fb.pack(anchor="w", pady=(6, 2))
                self.drill_card.sync_height(notify=True)
            self._append_chat(
                "tutor_lbl",
                "🦉 Сова-Ліза:",
                f"✅ Супер! «{u_repr}» — правильно!\n{drill['solution']}\nТепер ти впевнено впораєшся з таким типом завдань на НМТ. Можемо рухатися далі (або натисни «Інший ↻» для ще одного тренування).",
                body_tag="ok"
            )
        else:
            self.owl_tutor.set_mood("explain")
            self.lbl_owl_status.config(text="Майже вийшло! Перевір розбір і спробуй ще один ідентичний приклад нижче.")
            self._append_chat(
                "err",
                "🦉 Сова-Ліза (перевірка схожого прикладу):",
                f"Знову є неточність ({u_repr}). Правильна відповідь: {c_repr}.\n🔍 Поглянь крок за кроком: {drill['solution']}\nСпробуймо ще один ідентичний приклад!"
            )
            self._show_new_drill(source_q)
