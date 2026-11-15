#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
НМТ Тренажер із Репетитором (2022–2026) — запускач.
Відкривається подвійним кліком через Python Launcher (macOS) або python.exe (Windows).
Увесь код програми лежить у папці «nmt_tutor» поруч із цим файлом.
Консольний режим: python3 nmt_tutor_mac.py --cli
"""

import os
import sys

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

if sys.version_info < (3, 8):
    sys.exit("Потрібен Python 3.8 або новіший: https://www.python.org/downloads/")

try:
    from nmt_tutor.app import main
except ImportError as exc:
    sys.exit(
        "Не знайдено папку «nmt_tutor» поруч із nmt_tutor_mac.py.\n"
        f"Розпакуйте архів повністю й запустіть знову. ({exc})"
    )

if __name__ == "__main__":
    main()
