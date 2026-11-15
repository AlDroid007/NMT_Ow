"""Built-in task bank (189 tasks, 2022–2026), read from bundled JSON on first use."""

import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
_BANK = None


def _read(name):
    with open(os.path.join(_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


def get_bank():
    """Returns {subject_id: [task, ...]}: official 2026 samples first, then the 2022–2025 archive."""
    global _BANK
    if _BANK is None:
        bank = {sid: list(items) for sid, items in _read("bank_static.json").items()}
        for sid, items in _read("archive_2022_2025.json").items():
            for item in items:
                item_copy = dict(item)
                item_copy["subject"] = sid
                bank.setdefault(sid, []).append(item_copy)
        _BANK = bank
    return _BANK


def bank_size():
    return sum(len(v) for v in get_bank().values())
