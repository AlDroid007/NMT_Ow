"""Shared helpers and the registry used by every generator module."""

import random

GEN_SOURCE = "Генератор за програмою НМТ (2022–2026)"

# drill_key -> generator function; filled as subject modules get imported.
REGISTRY = {}


def register_drill(key):
    def deco(fn):
        REGISTRY[key] = fn
        return fn
    return deco


def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def fmt_num(val):
    if abs(val - round(val)) < 1e-9:
        return str(int(round(val)))
    s = f"{val:.4f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


def case_table_generator(key, subject, section, prompt_head, cases):
    """Builds and registers a generator that picks one prepared A–D case.

    Each case is a tuple (sentence, options, answer, hint, rule, solution).
    """

    def generate():
        c = random.choice(cases)
        return {
            "subject": subject,
            "section": section,
            "source": GEN_SOURCE,
            "qtype": "single",
            "max_points": 1,
            "prompt": prompt_head + c[0],
            "options": c[1],
            "labels": ["A", "B", "C", "D"],
            "answer": c[2],
            "hint": c[3],
            "rule": c[4],
            "solution": c[5],
            "drill_key": key,
        }

    generate.__name__ = "gen_" + key
    return register_drill(key)(generate)
