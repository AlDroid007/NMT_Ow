"""Non-persistent repository kept in memory (tests, or a session without the encrypted store)."""

import copy
from datetime import datetime

from .base import Repository


def _now():
    return datetime.now().isoformat(timespec="seconds")


class MemoryRepository(Repository):
    def __init__(self):
        self.startup_notices = []
        self._tables = {"results": [], "reports": [], "custom_banks": []}
        self._meta = {}
        self._next_id = 1

    def _insert(self, table, obj, created_at=None):
        rid = self._next_id
        self._next_id += 1
        self._tables[table].append((rid, created_at or _now(), copy.deepcopy(obj)))
        return rid

    def save_result(self, result):
        return self._insert("results", result, result.get("finished_at"))

    def list_results(self, subject=None):
        out = []
        for rid, created, p in self._tables["results"]:
            if subject is None or any(s.get("subject") == subject for s in p.get("subjects", [])):
                rec = copy.deepcopy(p)
                rec.update(id=rid, created_at=created)
                out.append(rec)
        return out

    def save_report(self, text, title=None, created_at=None):
        return self._insert("reports", {"title": title or "", "text": text}, created_at)

    def list_reports(self):
        return [{"id": rid, "created_at": c, "title": p["title"]} for rid, c, p in reversed(self._tables["reports"])]

    def get_report(self, report_id):
        for rid, c, p in self._tables["reports"]:
            if rid == report_id:
                return {"id": rid, "created_at": c, "title": p["title"], "text": p["text"]}
        return None

    def save_custom_bank(self, name, bank, created_at=None):
        return self._insert("custom_banks", {"name": name, "bank": bank}, created_at)

    def list_custom_banks(self):
        return [
            {"id": rid, "created_at": c, "name": p["name"], "tasks": sum(len(v) for v in p["bank"].values())}
            for rid, c, p in self._tables["custom_banks"]
        ]

    def get_custom_bank(self, bank_id):
        for rid, _c, p in self._tables["custom_banks"]:
            if rid == bank_id:
                return copy.deepcopy(p["bank"])
        return None

    def delete_custom_bank(self, bank_id):
        self._tables["custom_banks"] = [row for row in self._tables["custom_banks"] if row[0] != bank_id]

    def get_meta(self, key, default=None):
        return copy.deepcopy(self._meta.get(key, default))

    def set_meta(self, key, value):
        self._meta[key] = copy.deepcopy(value)
