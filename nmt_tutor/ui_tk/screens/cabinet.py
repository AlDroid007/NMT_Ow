"""Personal cabinet: subject levels and goals, progress chart, weak topics and training history."""

import tkinter as tk
from tkinter import filedialog, messagebox

from ...cabinet import cabinet_subjects, format_when, history, progress_series, subject_stats, weak_topics
from ...config import SUBJECTS_CONFIG
from ...engine import build_section_plan
from ...profiles import avatar_text, days_until_exam, days_word, short_name, target_for
from ...storage import files, paths
from ..owl import OwlMascot
from ..profile_widgets import ProgressChart, SubjectStatCard, emoji_font
from ..scroll import SmoothScrollView
from ..theme import PALETTE
from ..widgets import RoundedButton, RoundedCard

HISTORY_LIMIT = 30


class CabinetScreenMixin:
    def show_cabinet(self):
        if self.profile is None:
            self.start_profiles()
            return
        self._clear_main()
        profile = self.profile
        try:
            results = self.repo.list_results()
        except Exception as exc:
            messagebox.showerror("Кабінет", f"Не вдалося прочитати результати:\n{exc}")
            results = []

        # --- header -------------------------------------------------------------
        header = tk.Frame(self.main_container, bg=PALETTE["nav"], height=78)
        header.pack(fill="x")
        header.pack_propagate(False)
        av = tk.Canvas(header, width=54, height=54, bg=PALETTE["nav"], highlightthickness=0, bd=0)
        av.pack(side="left", padx=(22, 10), pady=12)
        av.create_oval(2, 2, 52, 52, fill="#FFFFFF", outline=PALETTE["soft_indigo_bd"], width=2)
        av.create_text(27, 28, text=avatar_text(profile), font=emoji_font(self.fonts, 22))
        title_wrap = tk.Frame(header, bg=PALETTE["nav"])
        title_wrap.pack(side="left", pady=10)
        tk.Label(title_wrap, text=short_name(profile["name"], 24), font=self.fonts["h1"], bg=PALETTE["nav"],
                 fg=PALETTE["nav_fg"]).pack(anchor="w")
        days = days_until_exam(profile)
        if days is None:
            sub = "Дату НМТ не вказано"
        elif days > 0:
            sub = f"До НМТ {days} {days_word(days)}"
        elif days == 0:
            sub = "НМТ сьогодні — успіху! 🍀"
        else:
            sub = "Дата НМТ минула — онови її в профілі"
        scored = sum(1 for r in results if not r.get("mistake_drill"))
        sub = f"Особистий кабінет • {sub} • тренувань: {scored}"
        tk.Label(title_wrap, text=sub, font=self.fonts["small"], bg=PALETTE["nav"], fg="#CBD5E1").pack(anchor="w")
        self._nav_button(header, "⇄ Змінити профіль", self.switch_profile, min_width=150).pack_configure(padx=(0, 22))
        self._nav_button(header, "✎ Профіль", lambda: self.show_profile_form(self.profile), min_width=110)
        self._nav_button(header, "🚀 До тренування", self.show_setup, min_width=160)

        scroll = SmoothScrollView(self.main_container, bg=PALETTE["bg"])
        scroll.pack(fill="both", expand=True, padx=14, pady=(10, 0))
        page = scroll.inner

        subjects = cabinet_subjects(results, profile)
        if not results:
            self._cabinet_empty(page, subjects)
        stats = [subject_stats(results, sid, profile) for sid in subjects]

        # --- subject cards -------------------------------------------------------
        if stats:
            card = self._cabinet_card(page, "📚 Мої предмети", "Рівень — середній бал НМТ за останні 3 тренування")
            grid = tk.Frame(card.inner, bg=PALETTE["card"])
            grid.pack(fill="x")
            for c in range(3):
                grid.columnconfigure(c, weight=1, uniform="subj")
            self._stat_cards = {}
            for i, st in enumerate(stats):
                w = SubjectStatCard(grid, st, self.fonts, on_click=self._cabinet_select_subject)
                w.grid(row=i // 3, column=i % 3, sticky="ew", padx=4, pady=4)
                self._stat_cards[st["subject"]] = w

        # --- chart -----------------------------------------------------------------
        if subjects:
            card = self._cabinet_card(page, "📈 Прогрес", "Бал НМТ (100–200) у кожному тренуванні; пунктир — твоя ціль")
            self._chart_tabs = tk.Frame(card.inner, bg=PALETTE["card"])
            self._chart_tabs.pack(fill="x", pady=(0, 6))
            self._chart = ProgressChart(card.inner, self.fonts)
            self._chart.pack(fill="x")
            self._cabinet_results = results
            with_data = [st["subject"] for st in stats if st["sessions"]]
            self._cabinet_select_subject((with_data or subjects)[0])

        # --- weak topics -------------------------------------------------------------
        topics = weak_topics(results, subjects)
        card = self._cabinet_card(page, "🎯 Слабкі теми", "Розділи з найбільшою кількістю помилок (свіжі тренування важать більше)")
        if not topics:
            tk.Label(card.inner, text="Поки що слабких тем немає. Пройди тренування — і Сова-Ліза підкаже, що повторити.",
                     font=self.fonts["body_sm"], bg=PALETTE["card"], fg=PALETTE["muted"]).pack(anchor="w")
        worst = max((t["mistakes"] for t in topics), default=1)
        for t in topics:
            row = tk.Frame(card.inner, bg=PALETTE["card"])
            row.pack(fill="x", pady=3)
            RoundedButton(row, text="Потренувати", command=lambda s=t["subject"], sec=t["section"]: self.start_focus_session(s, sec),
                          bg=PALETTE["soft_indigo"], hover_bg="#DCE2FF", fg=PALETTE["primary"], border_color=PALETTE["soft_indigo_bd"],
                          font=self.fonts["bold_sm"], radius=12, height=30, min_width=120, parent_bg=PALETTE["card"]).pack(side="right")
            bar = tk.Canvas(row, width=120, height=12, bg=PALETTE["card"], highlightthickness=0, bd=0)
            bar.pack(side="right", padx=12)
            bar.create_rectangle(0, 2, 120, 10, fill=PALETTE["soft_rose"], outline="")
            bar.create_rectangle(0, 2, max(6, 120 * t["mistakes"] / worst), 10, fill="#F87171", outline="")
            txt = tk.Frame(row, bg=PALETTE["card"])
            txt.pack(side="left", fill="x", expand=True)
            tk.Label(txt, text=t["section"], font=self.fonts["bold"], bg=PALETTE["card"], fg=PALETTE["text"], anchor="w",
                     justify="left").pack(anchor="w")
            tk.Label(txt, text=f"{t['subject_name']} • помилок: {t['mistakes']}", font=self.fonts["small"], bg=PALETTE["card"],
                     fg=PALETTE["muted"]).pack(anchor="w")

        # --- history -------------------------------------------------------------------
        rows = history(results, limit=HISTORY_LIMIT)
        card = self._cabinet_card(page, "🗓 Історія тренувань",
                                  f"Останні {HISTORY_LIMIT}" if len(results) > HISTORY_LIMIT else None)
        if not rows:
            tk.Label(card.inner, text="Тут з’являться твої тренування.", font=self.fonts["body_sm"], bg=PALETTE["card"],
                     fg=PALETTE["muted"]).pack(anchor="w")
        for i, h in enumerate(rows):
            row = tk.Frame(card.inner, bg=PALETTE["card_soft"] if i % 2 == 0 else PALETTE["card"])
            row.pack(fill="x")
            if h["report_id"] is not None:
                RoundedButton(row, text="📄 Звіт", command=lambda rid=h["report_id"]: self._show_report(rid), bg=PALETTE["card"],
                              hover_bg=PALETTE["soft_indigo"], fg=PALETTE["text"], border_color=PALETTE["border"],
                              font=self.fonts["small"], radius=11, height=26, min_width=80, parent_bg=row.cget("bg")).pack(side="right", padx=8, pady=4)
            tk.Label(row, text=format_when(h["at"]), font=self.fonts["bold_sm"], bg=row.cget("bg"), fg=PALETTE["text"],
                     width=16, anchor="w").pack(side="left", padx=(8, 4), pady=6)
            tk.Label(row, text=h["title"], font=self.fonts["small"], bg=row.cget("bg"), fg=PALETTE["muted"], width=22,
                     anchor="w").pack(side="left")
            parts = []
            for s in h["subjects"]:
                score = s["nmt_200"] if s["nmt_200"] is not None else "<поріг"
                parts.append(f"{s['name']}: {score}")
            tk.Label(row, text="   ".join(parts), font=self.fonts["body_sm"], bg=row.cget("bg"), fg=PALETTE["text"],
                     anchor="w", justify="left", wraplength=560).pack(side="left", fill="x", expand=True)

    def _cabinet_card(self, page, title, hint=None):
        card = RoundedCard(page, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=18, pad=14,
                           auto_height=True)
        card.pack(fill="x", pady=(0, 12))
        head = tk.Frame(card.inner, bg=PALETTE["card"])
        head.pack(fill="x", pady=(0, 6))
        tk.Label(head, text=title, font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(side="left")
        if hint:
            tk.Label(head, text=hint, font=self.fonts["small"], bg=PALETTE["card"], fg=PALETTE["muted"]).pack(side="left", padx=12)
        return card

    def _cabinet_empty(self, page, subjects):
        card = RoundedCard(page, bg=PALETTE["soft_indigo"], border=PALETTE["soft_indigo_bd"], parent_bg=PALETTE["bg"], radius=18,
                           pad=12, shadow=False, auto_height=True)
        card.pack(fill="x", pady=(0, 12))
        owl = OwlMascot(card.inner, size=80, bg=PALETTE["soft_indigo"])
        owl.pack(side="left", padx=(4, 14))
        txt = tk.Frame(card.inner, bg=PALETTE["soft_indigo"])
        txt.pack(side="left", fill="x", expand=True, pady=6)
        tk.Label(txt, text="Тут буде твій прогрес 🦉", font=self.fonts["h3"], bg=PALETTE["soft_indigo"], fg="#1E2B58").pack(anchor="w")
        tk.Label(txt, text="Пройди перше тренування — і Сова-Ліза покаже рівень з кожного предмета, графік, слабкі теми та історію.",
                 font=self.fonts["body_sm"], bg=PALETTE["soft_indigo"], fg="#334155", wraplength=640, justify="left").pack(anchor="w", pady=(2, 6))
        RoundedButton(txt, text="🚀 Почати тренування", command=self.show_setup, font=self.fonts["bold"], radius=14, height=36,
                      min_width=200, parent_bg=PALETTE["soft_indigo"]).pack(anchor="w")

    def _cabinet_select_subject(self, subject_id):
        chart = getattr(self, "_chart", None)
        if chart is None or not chart.winfo_exists():
            return
        self._chart_subject = subject_id
        chart.set_data(progress_series(self._cabinet_results, subject_id), target_for(self.profile, subject_id))
        for sid, card in getattr(self, "_stat_cards", {}).items():
            card.set_selected(sid == subject_id)
        for w in self._chart_tabs.winfo_children():
            w.destroy()
        for sid in cabinet_subjects(self._cabinet_results, self.profile):
            active = sid == subject_id
            RoundedButton(self._chart_tabs, text=SUBJECTS_CONFIG[sid]["name"], command=lambda s=sid: self._cabinet_select_subject(s),
                          bg=PALETTE["primary"] if active else PALETTE["card_soft"],
                          hover_bg=PALETTE["primary_hover"] if active else PALETTE["soft_indigo"],
                          fg="#FFFFFF" if active else PALETTE["text"], border_color="" if active else PALETTE["border"],
                          font=self.fonts["small"], radius=12, height=28, min_width=60, pad_x=10,
                          parent_bg=PALETTE["card"]).pack(side="left", padx=(0, 6), pady=2)

    def _show_report(self, report_id):
        try:
            rep = self.repo.get_report(report_id)
        except Exception as exc:
            messagebox.showerror("Звіт", f"Не вдалося відкрити звіт:\n{exc}")
            return
        if not rep:
            messagebox.showwarning("Звіт", "Звіт не знайдено.")
            return
        win = tk.Toplevel(self.root)
        win.title(f"Звіт від {format_when(rep['created_at'])}")
        win.geometry("760x560")
        win.configure(bg=PALETTE["bg"])
        card = RoundedCard(win, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=18, pad=14)
        card.pack(fill="both", expand=True, padx=14, pady=(14, 6))
        txt = tk.Text(card.inner, wrap="word", font=self.fonts["body"], bg=PALETTE["card"], fg=PALETTE["text"], padx=10, pady=8, relief="flat")
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", rep["text"])
        txt.config(state="disabled")

        def save():
            path = filedialog.asksaveasfilename(parent=win, title="Зберегти звіт", initialdir=paths.data_dir(), defaultextension=".txt",
                                                initialfile=(rep["title"] or "nmt_report") + ".txt", filetypes=[("Text files", "*.txt")])
            if path:
                files.write_text(path, rep["text"])

        RoundedButton(win, text="💾 Зберегти (.txt)", command=save, bg=PALETTE["accent"], hover_bg=PALETTE["accent_hover"],
                      font=self.fonts["bold_sm"], radius=14, height=36, min_width=170, parent_bg=PALETTE["bg"]).pack(side="right", padx=14, pady=(0, 12))

    def start_focus_session(self, subject_id, section):
        """Short tutor-mode session on one weak topic."""
        plan = build_section_plan(subject_id, section, n=8, custom_bank=self.custom_bank)
        if not plan:
            messagebox.showinfo("Тема", "Для цієї теми поки немає завдань.")
            return
        self.tutor_mode = True
        self.length_mode = "focus"
        self.is_mistake_drill = False
        self.focus_section = section
        self.plan = plan
        self.current_block_idx = 0
        self.current_q_idx = 0
        self.timer_seconds = 30 * 60
        self._build_test_view()
        self._load_current_question()
        self._tick_timer()
