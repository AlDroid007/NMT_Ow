"""Rounded canvas widgets: buttons, cards, hint stepper, subject tiles and answer rows.

Canvas items are created once; hover and selection changes only recolour them,
and a full re-layout happens only when the widget size actually changes.
"""

import tkinter as tk

from .scroll import SmoothScrollView
from .theme import PALETTE, draw_round_rect, hand_cursor, move_round_rect, style_round_rect, text_width


class RoundedButton(tk.Canvas):
    """Кнопка-пігулка із закругленими кутами, hover-ефектом та м’якою рамкою."""

    def __init__(
        self,
        parent,
        text,
        command=None,
        bg=PALETTE["primary"],
        hover_bg=PALETTE["primary_hover"],
        fg="#FFFFFF",
        border_color="",
        font=None,
        radius=16,
        height=38,
        min_width=110,
        pad_x=18,
        parent_bg=PALETTE["card"],
        state="normal",
    ):
        self._text = text
        self._command = command
        self._bg = bg
        self._hover_bg = hover_bg
        self._fg = fg
        self._border = border_color
        self._font = font or ("Helvetica", 11, "bold")
        self._radius = radius
        self._height = height
        self._pad_x = pad_x
        self._state = state
        self._hover = False
        self._parent_bg = parent_bg
        self._min_w = max(min_width, text_width(self._font, self._text) + 2 * pad_x)
        self._shape = None
        self._label = None

        super().__init__(
            parent,
            width=self._min_w,
            height=height + 2,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            cursor=hand_cursor() if state == "normal" else "arrow",
        )
        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_click)
        self._redraw()

    def set_state(self, state):
        if state == self._state:
            return
        self._state = state
        self.configure(cursor=hand_cursor() if state == "normal" else "arrow")
        self._restyle()

    def set_text(self, text):
        self._text = text
        new_w = max(self._min_w, text_width(self._font, text) + 2 * self._pad_x)
        if new_w != self._min_w:
            self._min_w = new_w
            self.configure(width=new_w)
            self._redraw()
        else:
            self._restyle()

    def set_colors(self, bg=None, hover_bg=None, fg=None, border_color=None):
        if bg is not None:
            self._bg = bg
        if hover_bg is not None:
            self._hover_bg = hover_bg
        if fg is not None:
            self._fg = fg
        if border_color is not None:
            self._border = border_color
        self._restyle()

    def _on_enter(self, _e):
        if self._state == "normal" and not self._hover:
            self._hover = True
            self._restyle()

    def _on_leave(self, _e):
        if self._hover:
            self._hover = False
            self._restyle()

    def _on_click(self, e):
        if self._state != "normal" or not self._command:
            return
        if 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height():
            self._command()

    def _redraw(self):
        w = max(self._min_w, self.winfo_width())
        h = max(self._height, self.winfo_height() - 2)
        if self._shape is None:
            self._shape = draw_round_rect(self, 2, 1, w - 2, h, r=self._radius)
            self._label = self.create_text(0, 0, font=self._font)
        move_round_rect(self, self._shape, 2, 1, w - 2, h, r=self._radius)
        self.coords(self._label, w / 2.0, (h + 1) / 2.0)
        self._restyle()

    def _restyle(self):
        if self._shape is None:
            return
        if self._state == "disabled":
            fill, fg, bd = "#CBD5E1", "#64748B", ""
        else:
            fill = self._hover_bg if self._hover else self._bg
            fg, bd = self._fg, self._border
        style_round_rect(self, self._shape, fill, bd, 1 if bd else 0)
        self.itemconfigure(self._label, text=self._text, fill=fg)


class RoundedCard(tk.Canvas):
    """Контейнер із плавно закругленими кутами; авто-висота завжди синхронізує SmoothScrollView."""

    def __init__(self, parent, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=12, shadow=True, auto_height=False, **kwargs):
        if auto_height and "height" not in kwargs:
            kwargs["height"] = 60
        super().__init__(parent, bg=parent_bg, highlightthickness=0, bd=0, **kwargs)
        self._card_bg = bg
        self._border = border
        self._radius = radius
        self._pad = pad
        self._shadow = shadow
        self._auto_height = auto_height
        self._sync_job = None
        self._bg_size = None

        self.inner = tk.Frame(self, bg=bg)
        self._win_id = self.create_window(pad, pad, window=self.inner, anchor="nw")
        self.bind("<Configure>", self._on_resize)
        if auto_height:
            self.inner.bind("<Configure>", self._schedule_auto_height)

    def _notify_scroll_ancestors(self):
        w = self.master
        while w is not None:
            if isinstance(w, SmoothScrollView):
                w._schedule_sync(delay=16)
                break
            w = getattr(w, "master", None)

    def _schedule_auto_height(self, _e=None):
        if not self._auto_height or self._sync_job is not None:
            return
        try:
            self._sync_job = self.after(16, self._run_auto_height)
        except Exception:
            self._sync_job = None

    def _run_auto_height(self):
        self._sync_job = None
        self.sync_height(notify=True)

    def sync_height(self, notify=True):
        if not self._auto_height:
            return
        try:
            if not self.winfo_exists():
                return
            self.inner.update_idletasks()
            req_h = self.inner.winfo_reqheight() + 2 * self._pad + 8
            cur_h = int(float(self.cget("height") or 0))
            if req_h != cur_h and req_h > 24:
                self.configure(height=req_h)
                self._redraw_bg(max(40, self.winfo_width()), req_h)
            if notify:
                self._notify_scroll_ancestors()
        except Exception:
            pass

    def _redraw_bg(self, w, h):
        if self._bg_size == (w, h):
            return
        self._bg_size = (w, h)
        self.delete("bg_shape")
        if self._shadow and w > 12 and h > 12:
            draw_round_rect(self, 3, 4, w - 2, h - 1, r=self._radius, fill=PALETTE["shadow"], outline="", width=0, tags="bg_shape")
        draw_round_rect(self, 2, 1, w - 3, h - 3, r=self._radius, fill=self._card_bg, outline=self._border, width=1, tags="bg_shape")
        self.tag_lower("bg_shape")

    def _on_resize(self, e):
        w = max(40, e.width)
        h = max(40, e.height)
        self._redraw_bg(w, h)
        inner_w = max(20, w - 2 * self._pad)
        self.itemconfig(self._win_id, width=inner_w)
        if not self._auto_height:
            inner_h = max(20, h - 2 * self._pad)
            self.itemconfig(self._win_id, height=inner_h)
        else:
            self._schedule_auto_height()
        self.coords(self._win_id, self._pad, self._pad)


class HintStepperBar(tk.Frame):
    """Інтерактивна шкала підказок 1 → 10 із круглими точками та кроковим перемикачем."""

    def __init__(self, parent, fonts, on_step, on_select_level=None, bg=PALETTE["card_soft"]):
        super().__init__(parent, bg=bg)
        self.fonts = fonts
        self.on_step = on_step
        self.on_select_level = on_select_level
        self._bg = bg
        self._current = 0  # 0..10

        top = tk.Frame(self, bg=bg)
        top.pack(fill="x", padx=10, pady=(6, 4))
        self.lbl_title = tk.Label(top, text="💡 Підказки Сови: 0 / 10", font=fonts["bold_sm"], bg=bg, fg="#92400E")
        self.lbl_title.pack(side="left")

        self.btn_next_hint = RoundedButton(
            top,
            text="Підказка 1/10 →",
            command=self.on_step,
            bg=PALETTE["soft_amber"],
            hover_bg="#FEF08A",
            fg="#92400E",
            border_color=PALETTE["soft_amber_bd"],
            font=fonts["small"],
            radius=12,
            height=26,
            min_width=130,
            pad_x=10,
            parent_bg=bg,
        )
        self.btn_next_hint.pack(side="right")

        self.dots_canvas = tk.Canvas(self, height=28, bg=bg, highlightthickness=0, bd=0, cursor=hand_cursor())
        self.dots_canvas.pack(fill="x", padx=10, pady=(0, 6))
        self.dots_canvas.bind("<Configure>", lambda _e: self._redraw_dots())
        self.dots_canvas.bind("<ButtonRelease-1>", self._on_dot_click)
        self._dot_boxes = []

    def set_level(self, level):
        self._current = max(0, min(10, int(level)))
        if self._current == 0:
            self.lbl_title.config(text="💡 Підказки Сови: 0 / 10 (від легкого натяку до розповіді)")
            self.btn_next_hint.set_text("Підказка 1/10 →")
            self.btn_next_hint.set_state("normal")
        elif self._current < 10:
            self.lbl_title.config(text=f"💡 Відкрито підказок: {self._current} / 10")
            self.btn_next_hint.set_text(f"Ще підказка ({self._current + 1}/10) →")
            self.btn_next_hint.set_state("normal")
        else:
            self.lbl_title.config(text="💡 Відкрито всі 10 / 10 (повна відповідь і розповідь!)")
            self.btn_next_hint.set_text("Усі 10/10 відкрито ✓")
            self.btn_next_hint.set_state("disabled")
        self._redraw_dots()

    def _redraw_dots(self):
        c = self.dots_canvas
        c.delete("all")
        self._dot_boxes = []
        w = max(240, c.winfo_width())
        step = w / 10.0
        for i in range(1, 11):
            cx = (i - 0.5) * step
            cy = 14
            r_w = min(13, max(9, step * 0.38))
            if i <= self._current:
                fill = "#D97706" if i == 10 else "#F59E0B"
                fg = "#FFFFFF"
                bd = ""
            elif i == self._current + 1:
                fill = "#FEF3C7"
                fg = "#92400E"
                bd = "#F59E0B"
            else:
                fill = "#FFFFFF"
                fg = "#94A3B8"
                bd = PALETTE["border"]
            draw_round_rect(c, cx - r_w, cy - 11, cx + r_w, cy + 11, r=9, fill=fill, outline=bd, width=1 if bd else 0)
            c.create_text(cx, cy, text=str(i), fill=fg, font=(self.fonts["family"], 8, "bold"))
            self._dot_boxes.append((i, cx - r_w, cy - 12, cx + r_w, cy + 12))

    def _on_dot_click(self, e):
        if not self.on_select_level:
            return
        for lvl, x1, y1, x2, y2 in self._dot_boxes:
            if x1 - 4 <= e.x <= x2 + 4 and y1 <= e.y <= y2:
                self.on_select_level(lvl)
                return


class SubjectTile(tk.Canvas):
    """Закруглена інтерактивна плитка для вибору предмета НМТ."""

    def __init__(self, parent, sid, cfg, var, fonts, on_change=None):
        super().__init__(parent, height=64, bg=PALETTE["card"], highlightthickness=0, bd=0, cursor=hand_cursor())
        self.sid = sid
        self.cfg = cfg
        self.var = var
        self.fonts = fonts
        self.on_change = on_change
        self._hover = False
        self._bg_item = None

        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._toggle)
        self.var.trace_add("write", lambda *_: self._redraw())
        self._redraw()

    def _on_enter(self, _e):
        self._hover = True
        self._restyle_bg()

    def _on_leave(self, _e):
        self._hover = False
        self._restyle_bg()

    def _toggle(self, _e):
        self.var.set(not self.var.get())
        if self.on_change:
            self.on_change()

    def _bg_style(self):
        if bool(self.var.get()):
            return PALETTE["soft_indigo"], PALETTE["primary"], 2
        if self._hover:
            return "#F3F6FD", "#BAC5E6", 1
        return PALETTE["card_soft"], PALETTE["border"], 1

    def _restyle_bg(self):
        if self._bg_item is not None:
            style_round_rect(self, self._bg_item, *self._bg_style())

    def _redraw(self):
        self.delete("all")
        w = max(210, self.winfo_width())
        h = max(62, self.winfo_height())
        selected = bool(self.var.get())

        fill, border, bw = self._bg_style()
        self._bg_item = draw_round_rect(self, 2, 2, w - 2, h - 2, r=15, fill=fill, outline=border, width=bw)

        cx, cy = 22, h / 2.0
        if selected:
            draw_round_rect(self, cx - 10, cy - 10, cx + 10, cy + 10, r=7, fill=PALETTE["primary"], outline="")
            self.create_text(cx, cy, text="✓", fill="#FFFFFF", font=self.fonts["bold_sm"])
        else:
            draw_round_rect(self, cx - 10, cy - 10, cx + 10, cy + 10, r=7, fill="#FFFFFF", outline="#94A3B8", width=1.5)

        self.create_text(42, 21, text=self.cfg["name"], anchor="w", fill=PALETTE["text"], font=self.fonts["h3"])
        meta = f"{self.cfg['total_tasks']} завдань • макс. {self.cfg['max_score']} б. • поріг {self.cfg['threshold']}"
        self.create_text(42, 43, text=meta, anchor="w", fill=PALETTE["muted"], font=self.fonts["small"])

        if self.cfg["mandatory"]:
            badge_txt = "Обов’язковий"
            b_bg, b_fg = PALETTE["chip_req_bg"], PALETTE["chip_req_fg"]
        else:
            badge_txt = "За вибором"
            b_bg, b_fg = PALETTE["chip_opt_bg"], PALETTE["chip_opt_fg"]
        bw_px = 88 if self.cfg["mandatory"] else 78
        draw_round_rect(self, w - bw_px - 12, 11, w - 12, 30, r=10, fill=b_bg, outline="")
        self.create_text(w - bw_px / 2.0 - 12, 20.5, text=badge_txt, fill=b_fg, font=(self.fonts["family"], 8, "bold"))


class _ChoiceRow(tk.Frame):
    """Shared rounded answer row: badge on the left, wrapped text, hover and selection states."""

    MIN_H = 44
    V_PAD = 20
    RADIUS = 14
    BADGE_HALF = 13
    BADGE_R = 10
    TEXT_X = 50

    def __init__(self, parent, key_txt, item_txt, var, fonts, base_bg, active_bg, active_bd, text_font, badge_font):
        super().__init__(parent, bg=base_bg)
        self.key_txt = key_txt
        self.item_txt = item_txt
        self.var = var
        self.fonts = fonts
        self.base_bg = base_bg
        self.active_bg = active_bg
        self.active_bd = active_bd
        self._text_font = text_font
        self._badge_font = badge_font
        self._hover = False
        self._items = None
        self._layout_w = None

        self.canvas = tk.Canvas(self, bg=base_bg, highlightthickness=0, bd=0, height=self.MIN_H, cursor=hand_cursor())
        self.canvas.pack(fill="x", expand=True)

        self.canvas.bind("<Configure>", lambda _e: self._layout())
        self.canvas.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Leave>", self._on_leave)
        self.canvas.bind("<ButtonRelease-1>", self._activate)
        self.var.trace_add("write", lambda *_: self._restyle())

    def _is_selected(self):
        raise NotImplementedError

    def _activate(self, _e):
        raise NotImplementedError

    def _badge_text(self, selected):
        return self.key_txt

    def _on_enter(self, _e):
        self._hover = True
        self._restyle()

    def _on_leave(self, _e):
        self._hover = False
        self._restyle()

    def _layout(self):
        c = self.canvas
        w = max(220, c.winfo_width())
        if self._items is not None and w == self._layout_w:
            return
        self._layout_w = w
        avail_w = max(130, w - self.TEXT_X - 16)
        if self._items is None:
            bg = draw_round_rect(c, 0, 0, 10, 10, r=self.RADIUS)
            badge = draw_round_rect(c, 0, 0, 10, 10, r=self.BADGE_R)
            badge_txt = c.create_text(0, 0, font=self._badge_font)
            txt = c.create_text(0, 0, text=self.item_txt, anchor="w", font=self._text_font, fill=PALETTE["text"])
            self._items = (bg, badge, badge_txt, txt)
        bg, badge, badge_txt, txt = self._items
        c.itemconfigure(txt, width=avail_w)
        bbox = c.bbox(txt)
        th = (bbox[3] - bbox[1]) if bbox else self.MIN_H - self.V_PAD
        h = max(self.MIN_H, th + self.V_PAD)
        if int(c.cget("height")) != h:
            c.configure(height=h)
        cy = h / 2.0
        move_round_rect(c, bg, 2, 2, w - 2, h - 2, r=self.RADIUS)
        move_round_rect(c, badge, 12, cy - self.BADGE_HALF, 38, cy + self.BADGE_HALF, r=self.BADGE_R)
        c.coords(badge_txt, 25, cy)
        c.coords(txt, self.TEXT_X, cy)
        self._restyle()

    def _restyle(self):
        if self._items is None:
            return
        bg, badge, badge_txt, _txt = self._items
        selected = self._is_selected()
        if selected:
            fill, bd, bw = self.active_bg, self.active_bd, 2
            badge_bg, badge_fg = self.active_bd, "#FFFFFF"
        else:
            fill = "#F3F6FD" if self._hover else "#FAFBFD"
            bd = "#BDC8E6" if self._hover else PALETTE["border"]
            bw = 1
            badge_bg, badge_fg = "#E8ECF8", PALETTE["text"]
        style_round_rect(self.canvas, bg, fill, bd, bw)
        style_round_rect(self.canvas, badge, badge_bg)
        self.canvas.itemconfigure(badge_txt, text=self._badge_text(selected), fill=badge_fg)


class RoundedOptionRow(_ChoiceRow):
    """Закруглена інтерактивна кнопка-варіант відповіді (А/Б/В/Г/Д)."""

    def __init__(self, parent, label_txt, option_txt, var, fonts, base_bg=PALETTE["card"], active_bg=PALETTE["soft_indigo"], active_bd=PALETTE["primary"]):
        super().__init__(parent, label_txt, option_txt, var, fonts, base_bg, active_bg, active_bd,
                         text_font=fonts["body"], badge_font=fonts["bold_sm"])

    @property
    def label_txt(self):
        return self.key_txt

    def _is_selected(self):
        return self.var.get() == self.key_txt

    def _activate(self, _e):
        self.var.set(self.key_txt)


class RoundedCheckRow(_ChoiceRow):
    """Закруглена інтерактивна кнопка-прапорець (для завдань «обери 3 із 7») із перенесенням тексту."""

    MIN_H = 40
    V_PAD = 18
    RADIUS = 13
    BADGE_HALF = 12
    BADGE_R = 8

    def __init__(self, parent, key_txt, item_txt, var, fonts, base_bg=PALETTE["card"], active_bg="#D1FAE5", active_bd=PALETTE["accent"]):
        super().__init__(parent, key_txt, item_txt, var, fonts, base_bg, active_bg, active_bd,
                         text_font=fonts["body_sm"], badge_font=(fonts["family"], 9, "bold"))

    def _is_selected(self):
        return bool(self.var.get())

    def _badge_text(self, selected):
        return f"✓ {self.key_txt}" if selected else self.key_txt

    def _activate(self, _e):
        self.var.set(not self.var.get())
