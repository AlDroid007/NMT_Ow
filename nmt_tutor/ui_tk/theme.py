"""Colours, fonts and canvas drawing helpers shared by the Tkinter widgets."""

import sys
from tkinter import font as tkfont

PALETTE = {
    "bg": "#F3F5FC",
    "card": "#FFFFFF",
    "card_soft": "#F8FAFF",
    "shadow": "#E4E8F5",
    "nav": "#262F4D",
    "nav_accent": "#344068",
    "nav_fg": "#FFFFFF",
    "primary": "#5B6EF5",
    "primary_hover": "#485BE2",
    "accent": "#22A094",
    "accent_hover": "#19877C",
    "soft_indigo": "#EEF1FF",
    "soft_indigo_bd": "#C7D2FE",
    "soft_mint": "#ECFCF6",
    "soft_mint_bd": "#6EE7B7",
    "soft_amber": "#FFF9E6",
    "soft_amber_bd": "#FCD34D",
    "soft_rose": "#FFF1F2",
    "soft_rose_bd": "#FECDD3",
    "text": "#1E293B",
    "muted": "#64748B",
    "border": "#DCE2F2",
    "ok_bg": "#DCFCE7",
    "ok_fg": "#15803D",
    "err_bg": "#FEE2E2",
    "err_fg": "#B91C1C",
    "chip_req_bg": "#EDE9FE",
    "chip_req_fg": "#5B21B6",
    "chip_opt_bg": "#E0F2FE",
    "chip_opt_fg": "#0369A1",
    "scroll_track": "#EBF0FA",
    "scroll_thumb": "#B4C0E4",
    "scroll_thumb_hover": "#5B6EF5",
}

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform.startswith("win")


def os_label():
    return "macOS" if IS_MAC else "Windows" if IS_WIN else "Desktop"


def hand_cursor():
    return "pointinghand" if IS_MAC else "hand2"


def pick_fonts(root):
    try:
        avail = set(tkfont.families(root))
    except Exception:
        avail = set()

    if IS_MAC:
        candidates = ["Avenir Next", "SF Pro Text", "Nunito", "Helvetica Neue", "Helvetica"]
    elif IS_WIN:
        candidates = ["Segoe UI Variable Text", "Segoe UI", "Trebuchet MS", "Calibri", "Arial"]
    else:
        candidates = ["DejaVu Sans", "Liberation Sans", "Ubuntu"]

    base = candidates[-1]
    for c in candidates:
        if c in avail:
            base = c
            break

    return {
        "family": base,
        "h1": (base, 17, "bold"),
        "h2": (base, 13, "bold"),
        "h3": (base, 11, "bold"),
        "body": (base, 11),
        "body_sm": (base, 10),
        "small": (base, 9),
        "bold": (base, 11, "bold"),
        "bold_sm": (base, 10, "bold"),
        "mono": ("Menlo" if IS_MAC else "Consolas" if IS_WIN else "DejaVu Sans Mono", 10),
    }


_FONTS = {}
_WIDTHS = {}


def text_width(font, text):
    """Pixel width of `text` in `font`; Font objects and results are cached."""
    key = (font, text)
    width = _WIDTHS.get(key)
    if width is None:
        try:
            f_obj = _FONTS.get(font)
            if f_obj is None:
                f_obj = _FONTS[font] = tkfont.Font(font=font)
            width = f_obj.measure(text)
        except Exception:
            width = len(text) * 8
        _WIDTHS[key] = width
    return width


def round_rect_points(x1, y1, x2, y2, r=16):
    w = max(0, x2 - x1)
    h = max(0, y2 - y1)
    r = max(0, min(r, w / 2.0, h / 2.0))
    return [
        x1 + r, y1, x1 + r, y1,
        x2 - r, y1, x2 - r, y1,
        x2, y1, x2, y1 + r, x2, y1 + r,
        x2, y2 - r, x2, y2 - r, x2, y2,
        x2 - r, y2, x2 - r, y2,
        x1 + r, y2, x1 + r, y2, x1, y2,
        x1, y2 - r, x1, y2 - r,
        x1, y1 + r, x1, y1 + r, x1, y1,
    ]


def draw_round_rect(canvas, x1, y1, x2, y2, r=16, fill="", outline="", width=1, tags=None):
    """Малює плавний прямокутник із закругленими кутами на tk.Canvas."""
    kw = {"smooth": True, "splinesteps": 24, "fill": fill if fill else ""}
    if outline and width > 0:
        kw["outline"] = outline
        kw["width"] = width
    else:
        kw["outline"] = ""
        kw["width"] = 0
    if tags:
        kw["tags"] = tags
    return canvas.create_polygon(round_rect_points(x1, y1, x2, y2, r), **kw)


def style_round_rect(canvas, item, fill, outline="", width=1):
    """Recolours an existing rounded rectangle (same rules as draw_round_rect)."""
    if outline and width > 0:
        canvas.itemconfigure(item, fill=fill or "", outline=outline, width=width)
    else:
        canvas.itemconfigure(item, fill=fill or "", outline="", width=0)


def move_round_rect(canvas, item, x1, y1, x2, y2, r=16):
    """Reshapes an existing rounded rectangle instead of recreating it."""
    canvas.coords(item, *round_rect_points(x1, y1, x2, y2, r))
