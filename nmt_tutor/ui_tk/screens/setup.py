"""Screen 1: subject selection and session settings."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ...banks import CUSTOM_BANK_TEMPLATE, bank_task_count, merge_banks
from ...config import SUBJECTS_CONFIG, SUBJECTS_ORDER
from ...data import bank_size
from ...generators import generator_count
from ...storage import files, paths
from ..owl import OwlMascot
from ..scroll import SmoothScrollView
from ..theme import IS_WIN, PALETTE, os_label
from ..widgets import RoundedButton, RoundedCard, SubjectTile


class SetupScreenMixin:
    # -------------------------------------------------------------------
    # 1. ЕКРАН ВИБОРУ ПРЕДМЕТІВ І НАЛАШТУВАНЬ
    # -------------------------------------------------------------------
    def show_setup(self):
        self._clear_main()

        header = tk.Frame(self.main_container, bg=PALETTE["nav"], height=74)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_wrap = tk.Frame(header, bg=PALETTE["nav"])
        title_wrap.pack(side="left", padx=24, pady=10)
        tk.Label(
            title_wrap,
            text="НМТ Тренажер • Репетитор Сова-Ліза (2022–2026)",
            font=self.fonts["h1"],
            bg=PALETTE["nav"],
            fg=PALETTE["nav_fg"],
        ).pack(anchor="w")
        tk.Label(
            title_wrap,
            text=f"Версія для {os_label()} • Усі 12 предметів, 10 рівнів підказок та шкала 100–200",
            font=self.fonts["small"],
            bg=PALETTE["nav"],
            fg="#CBD5E1",
        ).pack(anchor="w")

        RoundedButton(
            header,
            text="📘 Програми та шкала 100–200",
            command=self._show_reference_dialog,
            bg=PALETTE["nav_accent"],
            hover_bg="#425182",
            fg="#FFFFFF",
            border_color="#526296",
            font=self.fonts["bold_sm"],
            radius=14,
            height=36,
            min_width=230,
            parent_bg=PALETTE["nav"],
        ).pack(side="right", padx=22, pady=18)

        body = tk.Frame(self.main_container, bg=PALETTE["bg"])
        body.pack(fill="both", expand=True, padx=20, pady=14)

        left_card = RoundedCard(body, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=14)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 12))
        left = left_card.inner

        welcome_box = RoundedCard(left, bg=PALETTE["soft_indigo"], border=PALETTE["soft_indigo_bd"], parent_bg=PALETTE["card"], radius=18, pad=8, shadow=False, height=110)
        welcome_box.pack(fill="x", pady=(0, 10))
        welcome_box.pack_propagate(False)
        w_in = welcome_box.inner

        owl_welcome = OwlMascot(w_in, size=88, bg=PALETTE["soft_indigo"])
        owl_welcome.pack(side="left", padx=(4, 10))

        w_txt = tk.Frame(w_in, bg=PALETTE["soft_indigo"])
        w_txt.pack(side="left", fill="both", expand=True, pady=4)
        tk.Label(
            w_txt,
            text="Привіт! Я Сова-Ліза — твій персональний репетитор НМТ 🦉",
            font=self.fonts["h3"],
            bg=PALETTE["soft_indigo"],
            fg="#1E2B58",
        ).pack(anchor="w")
        lbl_wdesc = tk.Label(
            w_txt,
            text=(
                "Обирай предмети нижче (усе вже вбудовано всередину!). "
                "У кожному завданні є 10 рівнів підказок (від легкого натяку до повної розповіді) та схожі приклади після помилки."
            ),
            font=self.fonts["body_sm"],
            bg=PALETTE["soft_indigo"],
            fg="#334155",
            wraplength=520,
            justify="left",
        )
        lbl_wdesc.pack(anchor="w", pady=(3, 0))
        w_txt.bind("<Configure>", lambda e, l=lbl_wdesc: l.config(wraplength=max(220, e.width - 12)))

        tk.Label(left, text="1. Оберіть предмети самостійно (клікай на картки):", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", pady=(0, 6))

        preset_bar = tk.Frame(left, bg=PALETTE["card"])
        preset_bar.pack(fill="x", pady=(0, 6))
        presets = [
            ("Стандарт НМТ (3 + Англ.)", ["ukrmova", "math", "history", "english"]),
            ("Лише обов’язкові (3)", ["ukrmova", "math", "history"]),
            ("Усі 12 предметів", SUBJECTS_ORDER),
            ("Скинути", []),
        ]
        for p_title, p_list in presets:
            RoundedButton(
                preset_bar,
                text=p_title,
                command=lambda lst=p_list: self._apply_preset(lst),
                bg=PALETTE["card_soft"],
                hover_bg=PALETTE["soft_indigo"],
                fg=PALETTE["text"],
                border_color=PALETTE["border"],
                font=self.fonts["small"],
                radius=12,
                height=28,
                min_width=85,
                pad_x=11,
                parent_bg=PALETTE["card"],
            ).pack(side="left", padx=(0, 6))

        grid_scroll = SmoothScrollView(left, bg=PALETTE["card"])
        grid_scroll.pack(fill="both", expand=True, pady=2)
        grid_wrap = grid_scroll.inner
        grid_wrap.columnconfigure(0, weight=1)
        grid_wrap.columnconfigure(1, weight=1)

        self.subj_vars = {}
        default_sel = {"ukrmova", "math", "history", "english"}
        for idx, sid in enumerate(SUBJECTS_ORDER):
            cfg = SUBJECTS_CONFIG[sid]
            var = tk.BooleanVar(value=(sid in default_sel))
            self.subj_vars[sid] = var
            r, c = divmod(idx, 2)
            tile = SubjectTile(grid_wrap, sid, cfg, var, self.fonts)
            tile.grid(row=r, column=c, sticky="nsew", padx=4, pady=3)

        right_card = RoundedCard(body, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=16, width=376)
        right_card.pack(side="right", fill="y")
        right_card.pack_propagate(False)
        right = right_card.inner

        tk.Label(right, text="2. Режим підготовки:", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", pady=(0, 6))
        self.var_mode = tk.StringVar(value="tutor")
        mode_box = tk.Frame(right, bg=PALETTE["card_soft"], highlightbackground=PALETTE["border"], highlightthickness=1)
        mode_box.pack(fill="x", pady=(0, 10))
        ttk.Radiobutton(
            mode_box,
            text="🦉 Із Совою-Репетитором (рекомендовано)\n10 рівнів підказок + схожий приклад при помилці",
            variable=self.var_mode,
            value="tutor",
            style="Soft.TRadiobutton",
        ).pack(anchor="w", padx=10, pady=(8, 4))
        ttk.Radiobutton(
            mode_box,
            text="⏱ Режим іспиту НМТ\nТаймер без підказок, підсумок наприкінці",
            variable=self.var_mode,
            value="exam",
            style="Soft.TRadiobutton",
        ).pack(anchor="w", padx=10, pady=(0, 8))

        tk.Label(right, text="3. Обсяг тесту:", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", pady=(0, 6))
        self.var_length = tk.StringVar(value="quick")
        len_box = tk.Frame(right, bg=PALETTE["card_soft"], highlightbackground=PALETTE["border"], highlightthickness=1)
        len_box.pack(fill="x", pady=(0, 10))
        ttk.Radiobutton(len_box, text="Швидке тренування (8 завд. / предмет)", variable=self.var_length, value="quick", style="Soft.TRadiobutton").pack(anchor="w", padx=10, pady=(7, 3))
        ttk.Radiobutton(len_box, text="Середній блок (15 завд. / предмет)", variable=self.var_length, value="medium", style="Soft.TRadiobutton").pack(anchor="w", padx=10, pady=3)
        ttk.Radiobutton(len_box, text="Повний формат НМТ (22 / 24 / 30 / 32)", variable=self.var_length, value="full", style="Soft.TRadiobutton").pack(anchor="w", padx=10, pady=(3, 7))

        total_static = bank_size()
        extra_cnt = bank_task_count(self.custom_bank)
        tk.Label(right, text="4. База завдань (2022–2026):", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", pady=(0, 4))
        base_msg = f"Вбудовано {total_static} завдань НМТ 2022–2026 рр. + {generator_count()} генераторів."
        if extra_cnt:
            base_msg += f" Додатково: {extra_cnt}."
        self.lbl_custom = tk.Label(
            right,
            text=base_msg,
            font=self.fonts["small"],
            bg=PALETTE["card"],
            fg=PALETTE["ok_fg"],
            wraplength=330,
            justify="left",
        )
        self.lbl_custom.pack(anchor="w", pady=(0, 6))

        json_row = tk.Frame(right, bg=PALETTE["card"])
        json_row.pack(fill="x", pady=(0, 6))
        RoundedButton(
            json_row,
            text="📂 Додати .json",
            command=self._on_load_json,
            bg=PALETTE["card_soft"],
            hover_bg=PALETTE["soft_indigo"],
            fg=PALETTE["text"],
            border_color=PALETTE["border"],
            font=self.fonts["small"],
            radius=12,
            height=30,
            min_width=140,
            pad_x=8,
            parent_bg=PALETTE["card"],
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        RoundedButton(
            json_row,
            text="💾 Шаблон .json",
            command=self._on_export_template,
            bg=PALETTE["card_soft"],
            hover_bg=PALETTE["soft_indigo"],
            fg=PALETTE["text"],
            border_color=PALETTE["border"],
            font=self.fonts["small"],
            radius=12,
            height=30,
            min_width=140,
            pad_x=8,
            parent_bg=PALETTE["card"],
        ).pack(side="right", fill="x", expand=True)

        if IS_WIN:
            RoundedButton(
                right,
                text="📌 Ярлик на Робочий стіл",
                command=self._create_windows_shortcut,
                bg=PALETTE["soft_indigo"],
                hover_bg="#DCE2FF",
                fg=PALETTE["primary"],
                border_color=PALETTE["soft_indigo_bd"],
                font=self.fonts["small"],
                radius=12,
                height=30,
                min_width=290,
                parent_bg=PALETTE["card"],
            ).pack(fill="x", pady=(0, 6))

        RoundedButton(
            right,
            text="🚀 Розпочати тренування",
            command=self._start_session,
            bg=PALETTE["primary"],
            hover_bg=PALETTE["primary_hover"],
            fg="#FFFFFF",
            font=self.fonts["h3"],
            radius=18,
            height=44,
            min_width=310,
            parent_bg=PALETTE["card"],
        ).pack(side="bottom", fill="x", pady=(6, 0))

    def _apply_preset(self, sids):
        s_set = set(sids)
        for sid, var in self.subj_vars.items():
            var.set(sid in s_set)

    def _on_load_json(self):
        path = filedialog.askopenfilename(
            title="Оберіть JSON-файл із завданнями НМТ",
            initialdir=paths.data_dir(),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            loaded = files.import_custom_bank_file(path)
            if not loaded:
                messagebox.showwarning("Порожній файл", "У вибраному файлі не знайдено коректних завдань для предметів НМТ.")
                return
            self.repo.save_custom_bank(os.path.basename(path), loaded)
            merge_banks(self.custom_bank, loaded)
            total = bank_task_count(self.custom_bank)
            self.lbl_custom.config(text=f"Додано з вашого файлу: {total} завдань (активні разом із вбудованою базою!).", fg=PALETTE["ok_fg"])
        except Exception as exc:
            messagebox.showerror("Помилка завантаження", f"Не вдалося прочитати файл:\n{exc}")

    def _on_export_template(self):
        path = filedialog.asksaveasfilename(
            title="Зберегти шаблон бази завдань",
            initialdir=paths.data_dir(),
            defaultextension=".json",
            initialfile="nmt_custom_bank_template.json",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return
        try:
            files.write_json(path, CUSTOM_BANK_TEMPLATE)
            messagebox.showinfo("Готово", f"Шаблон збережено:\n{path}\n\nВи можете додавати туди власні тести й підвантажувати їх у програму.")
        except Exception as exc:
            messagebox.showerror("Помилка", str(exc))

    def _show_reference_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Офіційна структура НМТ та шкали 100–200")
        win.geometry("780x560")
        win.configure(bg=PALETTE["bg"])
        card = RoundedCard(win, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=18, pad=16)
        card.pack(fill="both", expand=True, padx=16, pady=16)
        txt = tk.Text(card.inner, wrap="word", font=self.fonts["body"], bg=PALETTE["card"], fg=PALETTE["text"], padx=10, pady=8, relief="flat")
        txt.pack(fill="both", expand=True)
        lines = ["СТРУКТУРА НМТ І ЧИННІ ПРОГРАМИ (2022–2026)\n" + "=" * 58 + "\n"]
        for sid in SUBJECTS_ORDER:
            c = SUBJECTS_CONFIG[sid]
            lines.append(f"• {c['name']} ({'Обов’язковий' if c['mandatory'] else 'За вибором'})")
            lines.append(f"  Завдань: {c['total_tasks']} | Макс. бал: {c['max_score']} | Поріг «склав»: {c['threshold']} (100 б.)")
            lines.append(f"  Програма: {c['program_order']}")
            lines.append(f"  Форми: {c['structure']}\n")
        txt.insert("1.0", "\n".join(lines))
        txt.config(state="disabled")
