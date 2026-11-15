"""Screen 3: results on the 100–200 scale, report export and mistake practice."""

import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

from ...engine import build_mistake_drill_plan, build_session_result, format_results_report
from ...storage import files, paths
from ..owl import OwlMascot
from ..theme import PALETTE
from ..widgets import RoundedButton, RoundedCard


class ResultsScreenMixin:
    # -------------------------------------------------------------------
    # 3. ЕКРАН РЕЗУЛЬТАТІВ ТА ОЦІНКИ 100–200
    # -------------------------------------------------------------------
    def _finish_session(self):
        self._clear_main()
        self._last_report_text = format_results_report(self.plan)
        self._record_session()

        header = tk.Frame(self.main_container, bg=PALETTE["nav"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📊 Результати тренування НМТ (шкала 100–200)", font=self.fonts["h1"], bg=PALETTE["nav"], fg="#FFFFFF").pack(side="left", padx=24, pady=18)

        wrap = tk.Frame(self.main_container, bg=PALETTE["bg"])
        wrap.pack(fill="both", expand=True, padx=24, pady=14)

        has_mistakes = any(b["mistakes"] for b in self.plan)
        top_owl_card = RoundedCard(wrap, bg=PALETTE["soft_indigo"], border=PALETTE["soft_indigo_bd"], parent_bg=PALETTE["bg"], radius=18, pad=12, shadow=False, height=112)
        top_owl_card.pack(fill="x", pady=(0, 12))
        top_owl_card.pack_propagate(False)
        owl_res = OwlMascot(top_owl_card.inner, size=88, bg=PALETTE["soft_indigo"])
        owl_res.set_mood("explain" if has_mistakes else "happy")
        owl_res.pack(side="left", padx=(4, 14))
        res_msg = (
            "Чудова робота! У тебе є кілька помилок, і ми можемо прямо зараз відпрацювати їх на ідентичних прикладах!"
            if has_mistakes
            else "Фантастично! Жодної помилки — ти повністю готовий(а) до такого варіанта НМТ!"
        )
        tk.Label(top_owl_card.inner, text="Підсумок від Сови-Лізи 🦉", font=self.fonts["h3"], bg=PALETTE["soft_indigo"], fg="#1E2B58").pack(anchor="w", pady=(8, 2))
        tk.Label(top_owl_card.inner, text=res_msg, font=self.fonts["body"], bg=PALETTE["soft_indigo"], fg="#334155", wraplength=780, justify="left").pack(anchor="w")

        rep_card = RoundedCard(wrap, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=16)
        rep_card.pack(fill="both", expand=True)
        txt = tk.Text(rep_card.inner, wrap="word", font=self.fonts["body"], bg=PALETTE["card"], fg=PALETTE["text"], padx=10, pady=8, relief="flat")
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", self._last_report_text)
        txt.config(state="disabled")

        actions = tk.Frame(self.main_container, bg=PALETTE["bg"])
        actions.pack(fill="x", padx=24, pady=(0, 16))

        if has_mistakes:
            RoundedButton(
                actions,
                text="🔁 Відпрацювати помилки з Совою",
                command=self._start_mistake_drill_session,
                bg=PALETTE["primary"],
                hover_bg=PALETTE["primary_hover"],
                fg="#FFFFFF",
                font=self.fonts["bold"],
                radius=16,
                height=40,
                min_width=270,
                parent_bg=PALETTE["bg"],
            ).pack(side="left", padx=(0, 10))
        RoundedButton(
            actions,
            text="💾 Зберегти звіт (.txt)",
            command=self._save_report,
            bg=PALETTE["accent"],
            hover_bg=PALETTE["accent_hover"],
            fg="#FFFFFF",
            font=self.fonts["bold"],
            radius=16,
            height=40,
            min_width=195,
            parent_bg=PALETTE["bg"],
        ).pack(side="left", padx=(0, 10))
        RoundedButton(
            actions,
            text="🏠 Обрати інші предмети",
            command=self.show_setup,
            bg=PALETTE["card"],
            hover_bg=PALETTE["soft_indigo"],
            fg=PALETTE["text"],
            border_color=PALETTE["border"],
            font=self.fonts["bold_sm"],
            radius=16,
            height=40,
            min_width=210,
            parent_bg=PALETTE["bg"],
        ).pack(side="right")

    def _record_session(self):
        """Stores the finished session and its report in the encrypted user data store (once per plan)."""
        if getattr(self, "_recorded_plan", None) is self.plan:
            return
        if not any(block["answers"] for block in self.plan):
            return  # finished without answering anything: nothing to remember
        self._recorded_plan = self.plan
        try:
            result = build_session_result(self.plan, self.length_mode, self.tutor_mode, self.is_mistake_drill)
            self.repo.save_result(result)
            self.repo.save_report(self._last_report_text, title=f"nmt_report_{datetime.now().strftime('%Y%m%d_%H%M')}")
        except Exception as exc:
            print(f"Could not save the session result: {exc}", file=sys.stderr)

    def _start_mistake_drill_session(self):
        drill_plan = build_mistake_drill_plan(self.plan)
        if drill_plan:
            self.tutor_mode = True
            self.is_mistake_drill = True
            self.plan = drill_plan
            self.current_block_idx = 0
            self.current_q_idx = 0
            self.timer_seconds = 30 * 60
            self._build_test_view()
            self._load_current_question()
            self._tick_timer()

    def _save_report(self):
        path = filedialog.asksaveasfilename(
            title="Зберегти звіт",
            initialdir=paths.data_dir(),
            defaultextension=".txt",
            initialfile=f"nmt_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            filetypes=[("Text files", "*.txt")],
        )
        if not path:
            return
        files.write_text(path, getattr(self, "_last_report_text", None) or format_results_report(self.plan))
        messagebox.showinfo("Збережено", f"Звіт збережено:\n{path}")
