"""Custom task banks: validation rules and the example template (pure data, no file access)."""

from .config import SUBJECTS_CONFIG


class InvalidBankError(ValueError):
    pass


def validate_custom_bank(data):
    """Keeps only well-formed tasks of known subjects and fills the optional fields.

    Returns {subject_id: [task, ...]} (possibly empty). Raises InvalidBankError if
    the top level is not an object.
    """
    if not isinstance(data, dict):
        raise InvalidBankError("JSON має бути об’єктом вигляду {'english': [...], 'math': [...]}.")
    validated = {}
    for subj_id, items in data.items():
        if subj_id not in SUBJECTS_CONFIG or not isinstance(items, list):
            continue
        clean_list = []
        for idx, q in enumerate(items):
            if isinstance(q, dict) and "prompt" in q and "answer" in q and "qtype" in q:
                item = dict(q)
                item.setdefault("id", f"custom_{subj_id}_{idx+1}")
                item["subject"] = subj_id
                item.setdefault("section", "Користувацький банк")
                item.setdefault("source", "Завантажений файл користувача")
                item.setdefault("max_points", 1)
                item.setdefault("hint", "Уважно перечитай умову завдання.")
                item.setdefault("rule", "Пояснення не вказано у файлі користувача.")
                item.setdefault("solution", f"Правильна відповідь: {item['answer']}")
                clean_list.append(item)
        if clean_list:
            validated[subj_id] = clean_list
    return validated


def merge_banks(target, extra):
    """Appends the tasks of `extra` to `target` in place and returns `target`."""
    for k, v in extra.items():
        target.setdefault(k, []).extend(v)
    return target


def bank_task_count(bank):
    return sum(len(v) for v in bank.values())


# Приклад відкритого JSON-банку, щоб користувач міг додавати тести 2022–2025 рр.
CUSTOM_BANK_TEMPLATE = {
    "english": [
        {
            "id": "my_eng_2025_1",
            "section": "Use of English: Граматика",
            "source": "Архів НМТ-2025",
            "qtype": "single",
            "max_points": 1,
            "prompt": "She _______ in Kyiv since 2022.",
            "options": ["lives", "lived", "has lived", "is living"],
            "labels": ["A", "B", "C", "D"],
            "answer": "C",
            "hint": "Зверни увагу на маркер 'since 2022' (дія почалася в минулому й триває дотепер).",
            "rule": "Із прийменниками 'since' (з якогось моменту) та 'for' (протягом) для дії, що досі триває, вживається Present Perfect.",
            "solution": "Дія почалася у 2022 році й триває зараз → has lived (C).",
            "drill_key": "eng_passive_past",
        }
    ],
    "math": [
        {
            "id": "my_math_2025_1",
            "section": "Числа і вирази",
            "source": "Архів НМТ-2025",
            "qtype": "short",
            "max_points": 2,
            "prompt": "Товар коштував 500 грн. Після знижки 10 % його ціна стала дорівнювати (грн):",
            "answer": "450",
            "hint": "Знайди 90 % від 500.",
            "rule": "Ціна зі знижкою 10 % становить 0,9 від початкової ціни.",
            "solution": "500 · 0,9 = 450 грн.",
            "drill_key": "math_percent_trip",
        }
    ],
}
