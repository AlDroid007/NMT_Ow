"""Canvas widgets of the profile screens: profile tiles, avatar choices, subject stat cards, progress chart."""

import tkinter as tk

from ..cabinet import format_when
from ..profiles import avatar_text, days_until_exam, days_word, has_pin, short_name
from .theme import PALETTE, draw_round_rect, hand_cursor, style_round_rect, text_width


def emoji_font(fonts, size):
    return (fonts["family"], size)


class ProfileTile(tk.Canvas):
    """Clickable card of one profile on the «Хто займається?» screen (or the «new profile» tile)."""

    W, H = 196, 176

    def __init__(self, parent, fonts, on_click, profile=None, bg=PALETTE["card"], highlight=False):
        super().__init__(parent, width=self.W, height=self.H, bg=bg, highlightthickness=0, bd=0, cursor=hand_cursor())
        self.fonts = fonts
        self.profile = profile
        self._on_click = on_click
        self._hover = False
        self._highlight = highlight
        self._bg_item = None
        self._draw()
        self.bind("<Enter>", lambda _e: self._set_hover(True))
        self.bind("<Leave>", lambda _e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", self._click)

    def _style(self):
        if self._hover:
            return PALETTE["soft_indigo"], PALETTE["primary"], 2
        if self._highlight:
            return PALETTE["card_soft"], PALETTE["soft_indigo_bd"], 2
        return PALETTE["card_soft"], PALETTE["border"], 1

    def _set_hover(self, value):
        self._hover = value
        if self._bg_item is not None:
            style_round_rect(self, self._bg_item, *self._style())

    def _click(self, e):
        if 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height():
            self._on_click(self.profile)

    def _draw(self):
        w, h = self.W, self.H
        self._bg_item = draw_round_rect(self, 3, 3, w - 3, h - 3, r=20, fill="", outline="", width=0)
        style_round_rect(self, self._bg_item, *self._style())
        cx = w / 2.0
        if self.profile is None:
            self.create_oval(cx - 34, 22, cx + 34, 90, fill="#FFFFFF", outline=PALETTE["soft_indigo_bd"], width=2, dash=(4, 3))
            self.create_text(cx, 56, text="+", fill=PALETTE["primary"], font=(self.fonts["family"], 30, "bold"))
            self.create_text(cx, 114, text="Новий профіль", fill=PALETTE["text"], font=self.fonts["h3"])
            self.create_text(cx, 138, text="для ще одного учня", fill=PALETTE["muted"], font=self.fonts["small"])
            return
        p = self.profile
        self.create_oval(cx - 34, 22, cx + 34, 90, fill="#FFFFFF", outline=PALETTE["soft_indigo_bd"], width=2)
        self.create_text(cx, 57, text=avatar_text(p), font=emoji_font(self.fonts, 30), fill=PALETTE["text"])
        name = short_name(p["name"], 18)
        self.create_text(cx, 114, text=name, fill=PALETTE["text"], font=self.fonts["h3"])
        days = days_until_exam(p)
        if days is not None and days >= 0:
            sub = f"до НМТ {days} {days_word(days)}"
        else:
            sub = f"предметів: {len(p.get('subjects') or [])}"
        self.create_text(cx, 138, text=sub, fill=PALETTE["muted"], font=self.fonts["small"])
        if has_pin(p):
            self.create_text(w - 22, 22, text="🔒", font=emoji_font(self.fonts, 12))


class AvatarChoice(tk.Canvas):
    """One emoji in the avatar picker; `var` holds the chosen emoji."""

    S = 46

    def __init__(self, parent, emoji, var, fonts, bg=PALETTE["card"]):
        super().__init__(parent, width=self.S, height=self.S, bg=bg, highlightthickness=0, bd=0, cursor=hand_cursor())
        self.emoji = emoji
        self.var = var
        self._hover = False
        self._ring = self.create_oval(3, 3, self.S - 3, self.S - 3, width=2)
        self.create_text(self.S / 2, self.S / 2 + 1, text=emoji, font=emoji_font(fonts, 20))
        self.bind("<Enter>", lambda _e: self._set_hover(True))
        self.bind("<Leave>", lambda _e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", lambda _e: self.var.set(self.emoji))
        self.var.trace_add("write", lambda *_: self._restyle())
        self._restyle()

    def _set_hover(self, value):
        self._hover = value
        self._restyle()

    def _restyle(self):
        try:
            selected = self.var.get() == self.emoji
        except tk.TclError:
            return
        if selected:
            self.itemconfigure(self._ring, fill=PALETTE["soft_indigo"], outline=PALETTE["primary"])
        elif self._hover:
            self.itemconfigure(self._ring, fill="#F3F6FD", outline="#BAC5E6")
        else:
            self.itemconfigure(self._ring, fill=PALETTE["card_soft"], outline=PALETTE["border"])


class SubjectStatCard(tk.Canvas):
    """Cabinet card with one subject's level, goal and accuracy."""

    H = 128

    def __init__(self, parent, stats, fonts, bg=PALETTE["card"], on_click=None, selected=False):
        super().__init__(parent, height=self.H, bg=bg, highlightthickness=0, bd=0,
                         cursor=hand_cursor() if on_click else "arrow")
        self.stats = stats
        self.fonts = fonts
        self._on_click = on_click
        self._selected = selected
        self.bind("<Configure>", lambda _e: self._draw())
        if on_click:
            self.bind("<ButtonRelease-1>", lambda _e: on_click(stats["subject"]))

    def set_selected(self, value):
        if value != self._selected:
            self._selected = value
            self._draw()

    def _draw(self):
        self.delete("all")
        s = self.stats
        w = max(200, self.winfo_width())
        h = self.H
        border = PALETTE["primary"] if self._selected else PALETTE["border"]
        draw_round_rect(self, 2, 2, w - 2, h - 2, r=16, fill=PALETTE["card_soft"], outline=border, width=2 if self._selected else 1)
        self.create_text(16, 20, text=s["name"], anchor="w", fill=PALETTE["text"], font=self.fonts["h3"])
        if not s["sessions"]:
            self.create_text(16, 58, text="Ще не тренувався(лась)", anchor="w", fill=PALETTE["muted"], font=self.fonts["body_sm"])
            if s["target"]:
                self.create_text(16, 84, text=f"Ціль: {s['target']}", anchor="w", fill=PALETTE["muted"], font=self.fonts["small"])
            return
        level = s["recent"]
        big = str(level) if level is not None else "< поріг"
        color = PALETTE["text"] if level is not None else PALETTE["err_fg"]
        self.create_text(16, 54, text=big, anchor="w", fill=color, font=(self.fonts["family"], 22, "bold"))
        self.create_text(16, 84, text=f"рівень • тренувань: {s['sessions']}", anchor="w", fill=PALETTE["muted"], font=self.fonts["small"])
        chip_font = (self.fonts["family"], 9, "bold")
        if s["target"]:
            if s["gap"] is not None and s["gap"] <= 0:
                chip, bg, fg = f"🎯 ціль {s['target']} досягнута", PALETTE["ok_bg"], PALETTE["ok_fg"]
            elif s["gap"] is not None:
                chip, bg, fg = f"до цілі {s['target']}: ще {s['gap']}", PALETTE["soft_amber"], "#92400E"
            else:
                chip, bg, fg = f"ціль {s['target']}", PALETTE["soft_amber"], "#92400E"
            tw = text_width(chip_font, chip) + 20
            draw_round_rect(self, w - tw - 12, 45, w - 12, 67, r=11, fill=bg, outline="")
            self.create_text(w - tw / 2 - 12, 56, text=chip, fill=fg, font=chip_font)
        if s["trend"]:
            arrow = "▲" if s["trend"] > 0 else "▼"
            tcol = PALETTE["ok_fg"] if s["trend"] > 0 else PALETTE["err_fg"]
            self.create_text(w - 16, 84, text=f"{arrow} {abs(s['trend'])} за останні", anchor="e", fill=tcol, font=self.fonts["small"])
        parts = []
        if s["best"] is not None:
            parts.append(f"найкращий {s['best']}")
        if s["accuracy"] is not None:
            parts.append(f"правильних {s['accuracy']}%")
        self.create_text(16, 106, text=" • ".join(parts), anchor="w", fill=PALETTE["muted"], font=self.fonts["small"])


class ProgressChart(tk.Canvas):
    """Line chart of NMT scores (100–200) over sessions, with the goal as a dashed line."""

    H = 250
    PAD_L, PAD_R, PAD_T, PAD_B = 44, 24, 18, 34

    def __init__(self, parent, fonts, bg=PALETTE["card"]):
        super().__init__(parent, height=self.H, bg=bg, highlightthickness=0, bd=0)
        self.fonts = fonts
        self._points = []
        self._target = None
        self.bind("<Configure>", lambda _e: self._draw())

    def set_data(self, points, target=None):
        self._points = list(points)
        self._target = target
        self._draw()

    def _y(self, score, top, bottom):
        return bottom - (score - 100) / 100.0 * (bottom - top)

    def _draw(self):
        self.delete("all")
        w = max(300, self.winfo_width())
        h = self.H
        left, right, top, bottom = self.PAD_L, w - self.PAD_R, self.PAD_T, h - self.PAD_B
        for score in (100, 125, 150, 175, 200):
            y = self._y(score, top, bottom)
            self.create_line(left, y, right, y, fill="#E8ECF7")
            self.create_text(left - 8, y, text=str(score), anchor="e", fill=PALETTE["muted"], font=self.fonts["small"])
        pts = self._points
        if not pts:
            self.create_text((left + right) / 2, (top + bottom) / 2, text="Ще немає тренувань із цього предмета",
                             fill=PALETTE["muted"], font=self.fonts["body"])
            return
        if self._target:
            ty = self._y(self._target, top, bottom)
            self.create_line(left, ty, right, ty, fill=PALETTE["accent"], dash=(6, 4), width=2)
            self.create_text(right, ty - 9, text=f"ціль {self._target}", anchor="e", fill=PALETTE["accent"], font=self.fonts["bold_sm"])
        n = len(pts)
        span = right - left - 20
        xs = [left + 10 + (span * i / (n - 1) if n > 1 else span / 2) for i in range(n)]
        line = []
        for x, p in zip(xs, pts):
            if p["nmt_200"] is not None:
                line.extend((x, self._y(p["nmt_200"], top, bottom)))
        if len(line) >= 4:
            self.create_line(*line, fill=PALETTE["primary"], width=3, smooth=False, capstyle="round", joinstyle="round")
        r = 5 if n <= 30 else 3
        for x, p in zip(xs, pts):
            if p["nmt_200"] is None:
                y = self._y(100, top, bottom)
                self.create_oval(x - r, y - r, x + r, y + r, outline=PALETTE["err_fg"], width=2, fill="#FFFFFF")
            else:
                y = self._y(p["nmt_200"], top, bottom)
                self.create_oval(x - r, y - r, x + r, y + r, outline="#FFFFFF", width=2, fill=PALETTE["primary"])
        last = pts[-1]
        lx = xs[-1]
        if last["nmt_200"] is not None:
            ly = self._y(last["nmt_200"], top, bottom)
            self.create_text(lx, ly - 14, text=str(last["nmt_200"]), fill=PALETTE["primary"], font=self.fonts["bold_sm"])
        step = max(1, int(n / max(1, (right - left) / 70)) + (1 if n > 1 else 0))
        for i in range(0, n, step):
            self.create_text(xs[i], bottom + 16, text=format_when(pts[i]["at"])[:5], fill=PALETTE["muted"], font=self.fonts["small"])
        if any(p["nmt_200"] is None for p in pts):
            self.create_text(left + 6, top + 2, text="○ — нижче порогу «склав»", anchor="nw", fill=PALETTE["err_fg"], font=self.fonts["small"])
