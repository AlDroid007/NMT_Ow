"""Main Tkinter window: shared state, menus and helpers; screens come from the mixins."""

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from .. import APP_TITLE, APP_VERSION
from ..config import CUSTOM_BANKS_UI
from ..data import bank_size
from ..generators import generator_count
from ..resources import app_file, launcher_path, is_frozen
from .screens.cabinet import CabinetScreenMixin
from .screens.cloud import CloudMixin
from .screens.drill import DrillMixin
from .screens.profiles import ProfilesScreenMixin
from .screens.results import ResultsScreenMixin
from .screens.session import SessionScreenMixin
from .screens.setup import SetupScreenMixin
from .scroll import SmoothScrollView
from .theme import IS_MAC, IS_WIN, PALETTE, os_label, pick_fonts


class NmtTutorApp(ProfilesScreenMixin, CabinetScreenMixin, CloudMixin, SetupScreenMixin, SessionScreenMixin, DrillMixin,
                  ResultsScreenMixin):
    def __init__(self, root, store):
        self.root = root
        # Whole user data store; `self.repo` is the active profile's view of it (None on the picker).
        self.store = store
        self.repo = None
        self.profile = None
        self.root.title(APP_TITLE)

        try:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
        except Exception:
            sw, sh = 1440, 900
        win_w = min(1280, max(940, sw - 48))
        win_h = min(820, max(640, sh - 80))
        pos_x = max(0, (sw - win_w) // 2)
        pos_y = max(20, (sh - win_h) // 2)
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.minsize(880, 600)
        self.root.configure(bg=PALETTE["bg"])

        self.fonts = pick_fonts(self.root)
        self._configure_ttk_styles()
        self._set_app_icon()
        self._setup_menus()
        SmoothScrollView.install_global_wheel(self.root)

        self.custom_bank = {}
        self.focus_section = None
        self.plan = []
        self.current_block_idx = 0
        self.current_q_idx = 0
        self.tutor_mode = True
        self.length_mode = "quick"
        self.is_mistake_drill = False
        self.timer_seconds = 0
        self.timer_running = False
        self._timer_job = None
        self.active_drill = None
        self.drill_used_prompts = []
        self.q_hint_level = 0
        self.q_hints_10 = []
        self.drill_hint_level = 0
        self.drill_hints_10 = []
        self._chat_labels = []
        self._pane = None
        self._pane_orient = "horizontal"
        self._drill_modal = None

        self.main_container = tk.Frame(self.root, bg=PALETTE["bg"])
        self.main_container.pack(fill="both", expand=True)

        self.start_profiles()
        for notice in getattr(self.store, "startup_notices", ()) or ():
            self.root.after(300, lambda n=notice: messagebox.showwarning("Дані користувача", n))

    # --- storage helpers ---------------------------------------------------
    def _load_custom_banks(self):
        if self.repo is None:
            return {}
        try:
            return self.repo.load_custom_banks()
        except Exception as exc:
            print(f"Could not load custom banks: {exc}", file=sys.stderr)
            return {}

    # --- window setup ---------------------------------------------------------
    def _set_app_icon(self):
        if IS_WIN:
            ico_path = app_file("owl_icon.ico")
            if os.path.exists(ico_path):
                try:
                    self.root.iconbitmap(default=ico_path)
                except Exception:
                    pass
        png_path = app_file("owl_icon.png")
        if os.path.exists(png_path):
            try:
                self._icon_img = tk.PhotoImage(file=png_path)
                self.root.iconphoto(True, self._icon_img)
            except Exception:
                pass

    def _setup_menus(self):
        """Builds the menu bar for the current state: training menus only while a profile is active."""
        try:
            accel_o = "⌘O" if IS_MAC else "Ctrl+O"
            accel_q = "⌘Q" if IS_MAC else "Ctrl+Q"
            active = self.profile is not None

            menubar = tk.Menu(self.root)
            file_menu = tk.Menu(menubar, tearoff=0)
            banks = active and CUSTOM_BANKS_UI
            if banks:
                file_menu.add_command(label="Додати свій банк (.json)…", accelerator=accel_o, command=self._on_load_json)
                file_menu.add_command(label="Зберегти шаблон (.json)…", command=self._on_export_template)
            if IS_WIN:
                file_menu.add_command(label="Створити ярлик на Робочому столі", command=self._create_windows_shortcut)
            if banks or IS_WIN:
                file_menu.add_separator()
            file_menu.add_command(label="Вийти з програми", accelerator=accel_q, command=self._quit_app)
            menubar.add_cascade(label="Файл", menu=file_menu)

            if active:
                profile_menu = tk.Menu(menubar, tearoff=0)
                profile_menu.add_command(label="Особистий кабінет", command=self.show_cabinet)
                profile_menu.add_command(label="Редагувати профіль…", command=lambda: self.show_profile_form(self.profile))
                if self.cloud_enabled():
                    profile_menu.add_separator()
                    if self.cloud_linked():
                        profile_menu.add_command(label="☁️ Синхронізувати зараз", command=lambda: self.cloud_sync(manual=True))
                        profile_menu.add_command(label="☁️ Вийти з хмари на цьому комп’ютері", command=self.cloud_disconnect)
                        profile_menu.add_command(label="☁️ Видалити дані з хмари…", command=self.cloud_delete_account)
                    else:
                        profile_menu.add_command(label="☁️ Зберігати в хмарі…", command=self.cloud_connect)
                profile_menu.add_separator()
                profile_menu.add_command(label="Змінити профіль", command=self.switch_profile)
                menubar.add_cascade(label="Профіль", menu=profile_menu)

                nav_menu = tk.Menu(menubar, tearoff=0)
                nav_menu.add_command(label="Вибір предметів", command=self.show_setup)
                nav_menu.add_command(label="Програми НМТ та шкала 100–200", command=self._show_reference_dialog)
                menubar.add_cascade(label="Навігація", menu=nav_menu)

            help_menu = tk.Menu(menubar, tearoff=0)
            help_menu.add_command(label="Про програму «НМТ Сова-Репетитор»", command=self._show_about_dialog)
            menubar.add_cascade(label="Довідка", menu=help_menu)

            old = getattr(self, "_menubar", None)
            self.root.config(menu=menubar)
            self._menubar = menubar
            if old is not None:
                try:
                    old.destroy()
                except Exception:
                    pass
            if not getattr(self, "_menu_keys_bound", False):
                self._menu_keys_bound = True
                if IS_MAC:
                    self.root.bind_all("<Command-q>", lambda _e: self._quit_app())
                    self.root.bind_all("<Command-o>", lambda _e: self._load_json_if_active())
                    self.root.createcommand("tk::mac::Quit", self._quit_app)
                    self.root.createcommand("tk::mac::ShowHelp", self._show_about_dialog)
                else:
                    self.root.bind_all("<Control-q>", lambda _e: self._quit_app())
                    self.root.bind_all("<Control-o>", lambda _e: self._load_json_if_active())
        except Exception:
            pass

    def _load_json_if_active(self):
        """⌘O / Ctrl+O: only with an active profile (banks belong to a profile) and the bank UI shown."""
        if self.profile is not None and CUSTOM_BANKS_UI:
            self._on_load_json()

    def _create_windows_shortcut(self):
        if not IS_WIN:
            return
        try:
            import subprocess
            if is_frozen():
                # Packaged build: the exe itself is the target and carries the icon.
                pyw_exe = sys.executable
                target_args = ""
                app_dir = os.path.dirname(sys.executable)
                ico_path = sys.executable
            else:
                target_py = launcher_path()
                target_args = f'"{target_py}"'
                app_dir = os.path.dirname(target_py)
                ico_path = app_file("owl_icon.ico")
                pyw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
                if not os.path.exists(pyw_exe):
                    pyw_exe = sys.executable
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            lnk_path = os.path.join(desktop, "НМТ Сова-Репетитор.lnk")
            ps = (
                "$ws = New-Object -ComObject WScript.Shell; "
                f"$s = $ws.CreateShortcut('{lnk_path}'); "
                f"$s.TargetPath = '{pyw_exe}'; "
                f"$s.Arguments = '{target_args}'; "
                f"$s.WorkingDirectory = '{app_dir}'; "
                + (f"$s.IconLocation = '{ico_path}'; " if os.path.exists(ico_path) else "")
                + "$s.Save()"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
            messagebox.showinfo("Ярлик створено", f"Ярлик «НМТ Сова-Репетитор» успішно додано на Робочий стіл!\n\n{lnk_path}")
        except Exception as exc:
            messagebox.showerror("Не вдалося створити ярлик", f"Виникла помилка:\n{exc}")

    def _quit_app(self):
        self._stop_timer()
        try:
            self.store.close()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def _show_about_dialog(self):
        messagebox.showinfo(
            "Про програму",
            f"{APP_TITLE}\nВерсія {APP_VERSION} ({os_label()})\n\n"
            "• Усі 12 предметів НМТ (програми 2022–2026 рр.)\n"
            f"• Вбудовано {bank_size()} завдань та {generator_count()} генераторів\n"
            "• Багаторівневі підказки Сови-Лізи (рівні 1–10)\n"
            "• Плавна анімована прокрутка та адаптація під екран\n"
            "• Профілі учнів з цілями, особистий кабінет і PIN-код\n"
            "• Хмарне збереження профілю (вхід кодом із пошти)\n"
            "• Результати, звіти та власні банки зберігаються зашифровано в Документи/NMT_Tutor"
        )

    def _configure_ttk_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background=PALETTE["bg"])
        style.configure("TLabel", background=PALETTE["card"], foreground=PALETTE["text"], font=self.fonts["body"])
        style.configure("TCheckbutton", background=PALETTE["card"], foreground=PALETTE["text"], font=self.fonts["body"])
        style.configure("TRadiobutton", background=PALETTE["card"], foreground=PALETTE["text"], font=self.fonts["body"])
        style.configure("Soft.TRadiobutton", background=PALETTE["card_soft"], foreground=PALETTE["text"], font=self.fonts["body_sm"])
        style.configure(
            "TCombobox",
            font=self.fonts["bold"],
            padding=4,
            fieldbackground="#FFFFFF",
            background="#EEF2FF",
            foreground=PALETTE["text"],
        )
        style.map("TCombobox", fieldbackground=[("readonly", "#FFFFFF")], foreground=[("readonly", PALETTE["text"])])
        style.configure("TEntry", padding=6, fieldbackground="#FFFFFF", foreground=PALETTE["text"])

    def _clear_main(self):
        self._stop_timer()
        self._screen = None
        self._chat_labels = []
        for w in self.main_container.winfo_children():
            w.destroy()

    # --- session timer --------------------------------------------------------
    def _stop_timer(self):
        self.timer_running = False
        if self._timer_job is not None:
            try:
                self.root.after_cancel(self._timer_job)
            except Exception:
                pass
            self._timer_job = None

    def _tick_timer(self):
        self._timer_job = None
        if not self.timer_running:
            return
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            mins, secs = divmod(self.timer_seconds, 60)
            hrs, mins = divmod(mins, 60)
            if hrs:
                self.lbl_timer.config(text=f"⏱ {hrs}:{mins:02d}:{secs:02d}")
            else:
                self.lbl_timer.config(text=f"⏱ {mins:02d}:{secs:02d}")
            self._timer_job = self.root.after(1000, self._tick_timer)
        else:
            self.lbl_timer.config(text="⏱ Час вийшов!")
