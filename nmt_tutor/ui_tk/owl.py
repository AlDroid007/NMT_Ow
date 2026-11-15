"""Owl helper mascot drawn on a canvas, with moods and blinking."""

import tkinter as tk

from .theme import IS_MAC, PALETTE


class OwlMascot(tk.Canvas):
    """Розумна, мила та виразна Сова-Ліза з живими реакціями."""

    def __init__(self, parent, size=104, bg=PALETTE["soft_indigo"]):
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0, bd=0)
        self._size = size
        self._bg = bg
        self._mood = "idle"
        self._blink = False
        self._blink_job = None
        self._draw()
        self._schedule_blink()
        self.bind("<Destroy>", self._on_destroy)

    def _on_destroy(self, e):
        if e.widget is self and self._blink_job is not None:
            try:
                self.after_cancel(self._blink_job)
            except Exception:
                pass
            self._blink_job = None

    def set_mood(self, mood):
        if mood == self._mood and not self._blink:
            return  # already showing this mood
        self._mood = mood
        self._blink = False
        self._draw()

    def _schedule_blink(self):
        self._blink_job = None
        try:
            if not self.winfo_exists():
                return
            if self._mood in ("idle", "explain") and not self._blink:
                self._blink = True
                self._draw()
                self.after(160, self._unblink)
            self._blink_job = self.after(3600, self._schedule_blink)
        except Exception:
            pass

    def _unblink(self):
        try:
            if self.winfo_exists():
                self._blink = False
                self._draw()
        except Exception:
            pass

    def _draw(self):
        self.delete("all")
        s = self._size / 120.0
        med_bg = {
            "idle": "#E0E7FF",
            "thinking": "#FEF3C7",
            "happy": "#DCFCE7",
            "explain": "#E0F2FE",
        }.get(self._mood, "#E0E7FF")
        self.create_oval(6 * s, 6 * s, 114 * s, 114 * s, fill=med_bg, outline="#C7D2FE", width=max(1, int(1.5 * s)))
        self.create_line(18 * s, 102 * s, 102 * s, 102 * s, fill="#94A3B8", width=max(2, int(2.5 * s)), capstyle="round")
        for fx in (47, 73):
            self.create_oval((fx - 6) * s, 96 * s, (fx + 6) * s, 104 * s, fill="#F59E0B", outline="#D97706", width=1)
        self.create_oval(27 * s, 44 * s, 93 * s, 101 * s, fill="#5B619D", outline="#43487D", width=max(1, int(1.5 * s)))
        self.create_oval(39 * s, 58 * s, 81 * s, 97 * s, fill="#FEF7EC", outline="")
        for row_y, xs in [(72, [50, 60, 70]), (81, [54, 66])]:
            for px in xs:
                self.create_arc((px - 4) * s, (row_y - 3) * s, (px + 4) * s, (row_y + 4) * s, start=200, extent=140, style="arc", outline="#D9C5A8", width=max(1, int(1.3 * s)))

        self.create_oval(20 * s, 56 * s, 38 * s, 88 * s, fill="#4B518B", outline="#3C4174", width=1)
        if self._mood == "explain":
            self.create_polygon(84 * s, 66 * s, 106 * s, 48 * s, 109 * s, 58 * s, 90 * s, 79 * s, fill="#4B518B", outline="#3C4174", width=1, smooth=True)
        elif self._mood == "happy":
            self.create_polygon(28 * s, 64 * s, 12 * s, 46 * s, 16 * s, 39 * s, 34 * s, 58 * s, fill="#4B518B", outline="#3C4174", width=1, smooth=True)
            self.create_polygon(92 * s, 64 * s, 108 * s, 46 * s, 104 * s, 39 * s, 86 * s, 58 * s, fill="#4B518B", outline="#3C4174", width=1, smooth=True)
        else:
            self.create_oval(82 * s, 56 * s, 100 * s, 88 * s, fill="#4B518B", outline="#3C4174", width=1)

        self.create_polygon(28 * s, 36 * s, 21 * s, 16 * s, 42 * s, 27 * s, fill="#4B518B", outline="#3C4174", width=1, smooth=True)
        self.create_polygon(92 * s, 36 * s, 99 * s, 16 * s, 78 * s, 27 * s, fill="#4B518B", outline="#3C4174", width=1, smooth=True)
        self.create_oval(25 * s, 22 * s, 95 * s, 70 * s, fill="#646AB0", outline="#43487D", width=max(1, int(1.5 * s)))
        self.create_oval(30 * s, 32 * s, 63 * s, 63 * s, fill="#FFF9F0", outline="")
        self.create_oval(57 * s, 32 * s, 90 * s, 63 * s, fill="#FFF9F0", outline="")

        cheek_col = "#FDA4AF" if self._mood == "happy" else "#FECDD3"
        self.create_oval(31 * s, 51 * s, 40 * s, 57 * s, fill=cheek_col, outline="")
        self.create_oval(80 * s, 51 * s, 89 * s, 57 * s, fill=cheek_col, outline="")

        if self._mood == "happy":
            self.create_arc(37 * s, 40 * s, 55 * s, 55 * s, start=15, extent=150, style="arc", outline="#1E293B", width=max(2, int(2.6 * s)))
            self.create_arc(65 * s, 40 * s, 83 * s, 55 * s, start=15, extent=150, style="arc", outline="#1E293B", width=max(2, int(2.6 * s)))
        elif self._blink:
            self.create_arc(37 * s, 44 * s, 55 * s, 53 * s, start=190, extent=160, style="arc", outline="#1E293B", width=max(2, int(2.2 * s)))
            self.create_arc(65 * s, 44 * s, 83 * s, 53 * s, start=190, extent=160, style="arc", outline="#1E293B", width=max(2, int(2.2 * s)))
        else:
            dx, dy = (1.5, -2.0) if self._mood == "thinking" else (0.0, 0.0)
            for ex in (46, 74):
                self.create_oval((ex - 9.5) * s, 36.5 * s, (ex + 9.5) * s, 55.5 * s, fill="#FFFFFF", outline="#CBD5E1", width=1)
                self.create_oval((ex - 7.5 + dx) * s, (38.5 + dy) * s, (ex + 7.5 + dx) * s, (53.5 + dy) * s, fill="#F59E0B", outline="")
                self.create_oval((ex - 4.8 + dx) * s, (41.2 + dy) * s, (ex + 4.8 + dx) * s, (50.8 + dy) * s, fill="#1E293B", outline="")
                self.create_oval((ex - 3.0 + dx) * s, (41.5 + dy) * s, (ex + 0.2 + dx) * s, (44.7 + dy) * s, fill="#FFFFFF", outline="")
                self.create_oval((ex + 1.5 + dx) * s, (46.5 + dy) * s, (ex + 3.2 + dx) * s, (48.2 + dy) * s, fill="#FFFFFF", outline="")

        gl_col = "#B45309"
        gw = max(1, int(2.0 * s))
        self.create_oval(34.5 * s, 34.5 * s, 57.5 * s, 57.5 * s, outline=gl_col, width=gw)
        self.create_oval(62.5 * s, 34.5 * s, 85.5 * s, 57.5 * s, outline=gl_col, width=gw)
        self.create_arc(56.5 * s, 42 * s, 63.5 * s, 48 * s, start=0, extent=180, style="arc", outline=gl_col, width=gw)
        self.create_polygon(56 * s, 50 * s, 64 * s, 50 * s, 60 * s, 58 * s, fill="#F97316", outline="#EA580C", width=1, smooth=True)
        self.create_polygon(36 * s, 21 * s, 60 * s, 12 * s, 84 * s, 21 * s, 60 * s, 29 * s, fill="#262F4D", outline="#1E253D", width=1)
        self.create_rectangle(46 * s, 23 * s, 74 * s, 28 * s, fill="#334155", outline="")
        self.create_line(60 * s, 21 * s, 82 * s, 24 * s, 84 * s, 34 * s, fill="#FBBF24", width=max(1, int(2.0 * s)))
        self.create_oval(81 * s, 32 * s, 87 * s, 38 * s, fill="#F59E0B", outline="")

        star_f = "Avenir Next" if IS_MAC else "Segoe UI"
        if self._mood == "happy":
            for sx, sy in [(18, 22), (101, 24), (96, 86)]:
                self.create_text(sx * s, sy * s, text="✦", fill="#F59E0B", font=(star_f, max(8, int(11 * s)), "bold"))
        elif self._mood == "thinking":
            self.create_oval(92 * s, 10 * s, 112 * s, 29 * s, fill="#FFFFFF", outline="#F59E0B", width=1)
            self.create_text(102 * s, 19.5 * s, text="?", fill="#D97706", font=(star_f, max(9, int(12 * s)), "bold"))
