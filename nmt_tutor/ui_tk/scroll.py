"""Smooth animated scroll area with a rounded pill scrollbar."""

import time
import tkinter as tk
from tkinter import ttk

from .theme import IS_MAC, PALETTE, draw_round_rect, hand_cursor, move_round_rect, style_round_rect


def _cancel(widget, job):
    if job is not None:
        try:
            widget.after_cancel(job)
        except Exception:
            pass


class SmoothScrollView(tk.Frame):
    """
    Плавна молодіжна область прокрутки для macOS:
    - 60fps cubic ease-out анімація без затримок на трекпаді;
    - додатковий нижній запас (bottom_pad), щоб завжди докручувалося до самого низу;
    - видимий закруглений скролбар-пігулка + підтримка PageUp/PageDown/Home/End.
    """

    _REGISTRY = []

    def __init__(self, parent, bg=PALETTE["card"], pad_right=6, bottom_pad=32):
        super().__init__(parent, bg=bg)
        self._bg = bg
        self._bottom_pad = bottom_pad
        self._start_frac = 0.0
        self._target_frac = 0.0
        self._current_frac = 0.0
        self._anim_start_t = 0.0
        self._anim_duration = 0.22
        self._anim_job = None
        self._sync_job = None
        self._bottom_job = None
        self._hover_sb = False
        self._dragging = False
        self._scrolling_active = False
        self._drag_offset = 0.0
        self._thumb_coords = (0.0, 1.0)
        self._resize_listeners = []
        # Scrollbar canvas items are created once and then only moved/recoloured.
        self._sb_track = None
        self._sb_thumb = None
        self._sb_state = None

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.sb_canvas = tk.Canvas(self, width=12, bg=bg, highlightthickness=0, bd=0, cursor=hand_cursor())
        self.sb_canvas.pack(side="right", fill="y", padx=(pad_right, 0))

        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._schedule_sync)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self._on_yscroll)
        self.bind("<Map>", lambda _e: self._schedule_sync(delay=30))

        self.sb_canvas.bind("<Configure>", lambda _e: self._draw_scrollbar())
        self.sb_canvas.bind("<Enter>", lambda _e: self._set_sb_hover(True))
        self.sb_canvas.bind("<Leave>", lambda _e: self._set_sb_hover(False))
        self.sb_canvas.bind("<ButtonPress-1>", self._on_sb_press)
        self.sb_canvas.bind("<B1-Motion>", self._on_sb_drag)
        self.sb_canvas.bind("<ButtonRelease-1>", lambda _e: self._on_sb_release())

        SmoothScrollView._REGISTRY.append(self)
        self.bind("<Destroy>", self._on_destroy)

    def _on_destroy(self, e):
        if e.widget is self:
            for name in ("_anim_job", "_sync_job", "_bottom_job"):
                _cancel(self, getattr(self, name))
                setattr(self, name, None)
            if self in SmoothScrollView._REGISTRY:
                SmoothScrollView._REGISTRY.remove(self)

    def register_width_listener(self, callback):
        self._resize_listeners.append(callback)

    def _schedule_sync(self, _e=None, delay=20):
        if self._sync_job is not None:
            return
        try:
            self._sync_job = self.after(delay, self._run_scheduled_sync)
        except Exception:
            self._sync_job = None

    def _run_scheduled_sync(self):
        self._sync_job = None
        self.sync_scrollregion()

    def _content_and_view_heights(self):
        try:
            cw = max(120, self.canvas.winfo_width())
            ch = max(1, self.canvas.winfo_height())
            if ch <= 2:
                ch = max(1, self.canvas.winfo_reqheight())
            bbox = self.canvas.bbox("all")
            bbox_h = (bbox[3] - bbox[1]) if bbox else 0
            req_h = max(self.inner.winfo_reqheight(), bbox_h) + self._bottom_pad
            return cw, ch, max(ch, req_h)
        except Exception:
            return 300, 300, 300

    def sync_scrollregion(self):
        try:
            if not self.winfo_exists():
                return
            self.inner.update_idletasks()
            cw, ch, total_h = self._content_and_view_heights()
            self.canvas.configure(scrollregion=(0, 0, cw, total_h))
            self._clamp_and_sync()
        except Exception:
            pass

    def _on_canvas_configure(self, e):
        try:
            w = max(120, e.width)
            self.canvas.itemconfig(self._win_id, width=w)
            for cb in list(self._resize_listeners):
                try:
                    cb(w)
                except Exception:
                    pass
            self._schedule_sync(delay=14)
        except Exception:
            pass

    def _max_top_frac(self):
        try:
            _, ch, total_h = self._content_and_view_heights()
            if total_h <= ch + 2:
                return 0.0
            return max(0.0, min(1.0, (total_h - ch) / float(total_h)))
        except Exception:
            return 0.0

    def _clamp_and_sync(self):
        max_top = self._max_top_frac()
        if self._target_frac > max_top:
            self._target_frac = max_top
        if self._current_frac > max_top:
            self._current_frac = max_top
            try:
                self.canvas.yview_moveto(self._current_frac)
            except Exception:
                pass
        try:
            f0, f1 = self.canvas.yview()
            self._thumb_coords = (float(f0), float(f1))
        except Exception:
            pass
        self._draw_scrollbar()

    def _on_yscroll(self, first, last):
        try:
            self._thumb_coords = (float(first), float(last))
            if self._anim_job is None and not self._dragging:
                self._current_frac = float(first)
            self._draw_scrollbar()
        except Exception:
            pass

    def _set_sb_hover(self, state):
        self._hover_sb = state
        self._draw_scrollbar()

    def _on_sb_release(self):
        self._dragging = False
        self._draw_scrollbar()

    def _draw_scrollbar(self):
        c = self.sb_canvas
        try:
            if not c.winfo_exists():
                return
            w = max(10, c.winfo_width())
            h = max(30, c.winfo_height())
            f0, f1 = self._thumb_coords
            visible = f1 - f0 < 0.992
            active = self._hover_sb or self._dragging or self._scrolling_active
            state = (w, h, round(f0, 5), round(f1, 5), visible, active)
            if state == self._sb_state:
                return  # nothing changed since the last frame
            self._sb_state = state
            if self._sb_track is None:
                self._sb_track = draw_round_rect(c, 2, 4, w - 2, h - 4, r=4, fill=PALETTE["scroll_track"], outline="")
                self._sb_thumb = draw_round_rect(c, 2, 4, w - 2, 34, r=4.5, fill=PALETTE["scroll_thumb"], outline="")
            if not visible:
                c.itemconfigure(self._sb_track, state="hidden")
                c.itemconfigure(self._sb_thumb, state="hidden")
                return
            track_h = max(1, h - 8)
            y1 = 4 + f0 * track_h
            y2 = 4 + f1 * track_h
            if y2 - y1 < 30:
                mid = (y1 + y2) / 2.0
                y1 = max(4, mid - 15)
                y2 = min(h - 4, y1 + 30)
                if y2 - y1 < 30:
                    y1 = max(4, h - 4 - 30)
            thumb_col = PALETTE["scroll_thumb_hover"] if active else PALETTE["scroll_thumb"]
            pad_x = 1.5 if active else 2.2
            move_round_rect(c, self._sb_track, 2, 4, w - 2, h - 4, r=4)
            move_round_rect(c, self._sb_thumb, pad_x, y1, w - pad_x, y2, r=4.5)
            style_round_rect(c, self._sb_thumb, thumb_col)
            c.itemconfigure(self._sb_track, state="normal")
            c.itemconfigure(self._sb_thumb, state="normal")
        except Exception:
            pass

    def _on_sb_press(self, e):
        self.sync_scrollregion()
        h = max(30, self.sb_canvas.winfo_height())
        track_h = max(1, h - 8)
        f0, f1 = self._thumb_coords
        y1 = 4 + f0 * track_h
        y2 = 4 + f1 * track_h
        self._dragging = True
        if y1 <= e.y <= y2:
            self._drag_offset = e.y - y1
        else:
            self._drag_offset = (y2 - y1) / 2.0
            self._move_thumb_to(e.y - self._drag_offset, smooth=True)

    def _on_sb_drag(self, e):
        if self._dragging:
            self._move_thumb_to(e.y - self._drag_offset, smooth=False)

    def _stop_animation(self):
        _cancel(self, self._anim_job)
        self._anim_job = None
        self._scrolling_active = False

    def _jump_to(self, frac):
        self._stop_animation()
        self._start_frac = self._target_frac = self._current_frac = frac
        try:
            self.canvas.yview_moveto(frac)
        except Exception:
            pass
        self._draw_scrollbar()

    def _move_thumb_to(self, top_px, smooth=False):
        h = max(30, self.sb_canvas.winfo_height())
        track_h = max(1, h - 8)
        frac = max(0.0, min(self._max_top_frac(), (top_px - 4) / track_h))
        if smooth:
            self.smooth_scroll_to(frac)
        else:
            self._jump_to(frac)

    def scroll_by_pixels(self, delta_px):
        """Плавна анімована прокрутка (cubic ease-out) на задану кількість пікселів."""
        try:
            _, ch, total_h = self._content_and_view_heights()
            if total_h <= ch + 2:
                return
            max_top = max(0.0, (total_h - ch) / float(total_h))
            delta_frac = float(delta_px) / float(total_h)
            new_target = max(0.0, min(max_top, self._target_frac + delta_frac))
            self.smooth_scroll_to(new_target, duration=0.18)
        except Exception:
            pass

    def scroll_by_pixels_now(self, delta_px):
        """Immediate scroll (trackpad deltas already carry the OS momentum)."""
        try:
            _, ch, total_h = self._content_and_view_heights()
            if total_h <= ch + 2:
                return
            max_top = max(0.0, (total_h - ch) / float(total_h))
            base = self._target_frac if self._anim_job is not None else self._current_frac
            self._jump_to(max(0.0, min(max_top, base + float(delta_px) / float(total_h))))
        except Exception:
            pass

    def smooth_scroll_to(self, target_frac, duration=0.26):
        max_top = self._max_top_frac()
        self._start_frac = self._current_frac
        self._target_frac = max(0.0, min(max_top, float(target_frac)))
        self._anim_start_t = time.monotonic()
        self._anim_duration = max(0.10, float(duration))
        self._scrolling_active = True
        if self._anim_job is None:
            self._animate_step()

    def scroll_to_top(self, immediate=False):
        if immediate:
            _cancel(self, self._bottom_job)
            self._bottom_job = None
            self._jump_to(0.0)
        else:
            self.smooth_scroll_to(0.0)

    def scroll_to_bottom(self, delay_ms=60):
        """Scrolls to the end once pending content is laid out.

        Calls in quick succession are merged (the last one wins), so adding many
        chat bubbles at once triggers one layout pass and one animation.
        """
        _cancel(self, self._bottom_job)
        self._bottom_job = None

        def _go():
            self._bottom_job = None
            try:
                if not self.winfo_exists():
                    return
                self.sync_scrollregion()
                self.smooth_scroll_to(self._max_top_frac(), duration=0.32)
            except Exception:
                pass

        self._bottom_job = self.after(delay_ms, _go)

    def _animate_step(self):
        self._anim_job = None
        try:
            if not self.winfo_exists():
                return
            elapsed = time.monotonic() - self._anim_start_t
            t = min(1.0, elapsed / self._anim_duration)
            eased = 1.0 - ((1.0 - t) ** 3)
            self._current_frac = self._start_frac + (self._target_frac - self._start_frac) * eased
            if t >= 1.0 or abs(self._target_frac - self._current_frac) < 0.0005:
                self._current_frac = self._target_frac
                self.canvas.yview_moveto(self._current_frac)
                self._scrolling_active = False
                self._draw_scrollbar()
                return
            self.canvas.yview_moveto(self._current_frac)
            self._draw_scrollbar()
            self._anim_job = self.after(16, self._animate_step)
        except Exception:
            self._scrolling_active = False
            self._anim_job = None

    @classmethod
    def install_global_wheel(cls, root):
        """Прив’язує колесо миші, трекпад macOS і клавіші прокрутки до активного SmoothScrollView."""
        def _find_scroll_view(widget):
            w = widget
            while w is not None:
                if isinstance(w, SmoothScrollView):
                    return w
                try:
                    pname = w.winfo_parent()
                    w = w.nametowidget(pname) if pname else None
                except Exception:
                    break
            return None

        try:
            tk_major = int(str(root.tk.call("info", "patchlevel")).split(".")[0])
        except Exception:
            tk_major = 8

        def _view_under_pointer(event):
            try:
                target_w = root.winfo_containing(event.x_root, event.y_root) or event.widget
            except Exception:
                target_w = getattr(event, "widget", None)
            return _find_scroll_view(target_w)

        def _handle_wheel(event, fixed_dir=0):
            sv = _view_under_pointer(event)
            if sv is None:
                return
            if fixed_dir != 0:
                sv.scroll_by_pixels(fixed_dir * 76)
                return
            delta = getattr(event, "delta", 0)
            if delta == 0:
                return
            if IS_MAC and tk_major < 9:
                # Tk 8.6 on macOS reports small line deltas (trackpad included).
                px = max(-160, min(160, -delta * 18))
            else:
                # Tk 9 (all platforms) and Windows: 120 units per wheel notch.
                px = max(-240, min(240, -(delta / 120.0) * 84))
            sv.scroll_by_pixels(px)

        def _handle_touchpad(event):
            # Tk 9: two-finger trackpad scrolling arrives as <TouchpadScroll> with packed pixel deltas.
            sv = _view_under_pointer(event)
            if sv is None:
                return
            try:
                _dx, dy = root.tk.splitlist(root.tk.call("tk::PreciseScrollDeltas", event.delta))
                dy = float(dy)
            except Exception:
                return
            if dy:
                sv.scroll_by_pixels_now(-dy)

        def _handle_key(direction):
            try:
                fw = root.focus_get()
                if isinstance(fw, (tk.Entry, tk.Text, ttk.Entry, ttk.Combobox)):
                    return
                x, y = root.winfo_pointerxy()
                target_w = root.winfo_containing(x, y) or fw
            except Exception:
                target_w = None
            sv = _find_scroll_view(target_w)
            if sv is None and cls._REGISTRY:
                sv = cls._REGISTRY[-1]
            if sv is None:
                return
            if direction == "end":
                sv.scroll_to_bottom(delay_ms=10)
            elif direction == "home":
                sv.scroll_to_top()
            else:
                sv.scroll_by_pixels(direction)

        root.bind_all("<MouseWheel>", lambda e: _handle_wheel(e, 0))
        if tk_major >= 9:
            try:
                root.bind_all("<TouchpadScroll>", _handle_touchpad)
            except tk.TclError:
                pass
        root.bind_all("<Button-4>", lambda e: _handle_wheel(e, -1))
        root.bind_all("<Button-5>", lambda e: _handle_wheel(e, 1))
        root.bind_all("<Prior>", lambda _e: _handle_key(-240))
        root.bind_all("<Next>", lambda _e: _handle_key(240))
        root.bind_all("<End>", lambda _e: _handle_key("end"))
        root.bind_all("<Home>", lambda _e: _handle_key("home"))
