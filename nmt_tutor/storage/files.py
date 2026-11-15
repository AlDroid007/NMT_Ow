"""Files the user picks explicitly (import/export). The only place doing user file I/O."""

import json

from ..banks import validate_custom_bank


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def import_custom_bank_file(path):
    """Reads and validates a custom bank .json; returns {subject_id: [task, ...]}."""
    return validate_custom_bank(read_json(path))
