"""Non-persistent repository kept in memory (tests, or a session without the encrypted store)."""

import copy
from datetime import datetime

from .base import Repository

_DATA_TABLES = ("results", "reports", "custom_banks")


def _now():
    return datetime.now().isoformat(timespec="seconds")


class MemoryRepository(Repository):
    def __init__(self):
        self.startup_notices = []
        # rows: [rid, created_at, profile_id, payload]
        self._tables = {t: [] for t in _DATA_TABLES}
        self._meta = {}
        self._profiles = {}
        self._next_id = 1

    def _insert(self, table, obj, created_at=None, profile_id=None):
        rid = self._next_id
        self._next_id += 1
        self._tables[table].append([rid, created_at or _now(), profile_id, copy.deepcopy(obj)])
        return rid

    def _rows(self, table, profile_id):
        return [(rid, c, copy.deepcopy(p)) for rid, c, owner, p in self._tables[table] if owner == profile_id]

    def _row(self, table, rid, profile_id):
        for row_id, c, p in self._rows(table, profile_id):
            if row_id == rid:
                return row_id, c, p
        return None

    def save_result(self, result, profile_id=None):
        return self._insert("results", result, result.get("finished_at"), profile_id)

    def list_results(self, subject=None, profile_id=None):
        out = []
        for rid, created, p in self._rows("results", profile_id):
            if subject is None or any(s.get("subject") == subject for s in p.get("subjects", [])):
                p.update(id=rid, created_at=created)
                out.append(p)
        return out

    def save_report(self, text, title=None, created_at=None, profile_id=None):
        return self._insert("reports", {"title": title or "", "text": text}, created_at, profile_id)

    def list_reports(self, profile_id=None):
        return [{"id": rid, "created_at": c, "title": p["title"]} for rid, c, p in reversed(self._rows("reports", profile_id))]

    def get_report(self, report_id, profile_id=None):
        row = self._row("reports", report_id, profile_id)
        if row is None:
            return None
        rid, c, p = row
        return {"id": rid, "created_at": c, "title": p["title"], "text": p["text"]}

    def save_custom_bank(self, name, bank, created_at=None, profile_id=None):
        return self._insert("custom_banks", {"name": name, "bank": bank}, created_at, profile_id)

    def list_custom_banks(self, profile_id=None):
        return [
            {"id": rid, "created_at": c, "name": p["name"], "tasks": sum(len(v) for v in p["bank"].values())}
            for rid, c, p in self._rows("custom_banks", profile_id)
        ]

    def get_custom_bank(self, bank_id, profile_id=None):
        row = self._row("custom_banks", bank_id, profile_id)
        return row[2]["bank"] if row else None

    def delete_custom_bank(self, bank_id, profile_id=None):
        self._tables["custom_banks"] = [r for r in self._tables["custom_banks"] if not (r[0] == bank_id and r[2] == profile_id)]

    def get_meta(self, key, default=None):
        return copy.deepcopy(self._meta.get(key, default))

    def set_meta(self, key, value):
        self._meta[key] = copy.deepcopy(value)

    # --- profiles ------------------------------------------------------------
    def list_profiles(self):
        return sorted((copy.deepcopy(p) for p in self._profiles.values()), key=lambda p: (p.get("created_at", ""), p["id"]))

    def get_profile(self, profile_id):
        p = self._profiles.get(profile_id)
        return copy.deepcopy(p) if p else None

    def save_profile(self, profile):
        self._profiles[profile["id"]] = copy.deepcopy(profile)
        return profile["id"]

    def delete_profile(self, profile_id):
        self._profiles.pop(profile_id, None)
        for t in _DATA_TABLES:
            self._tables[t] = [r for r in self._tables[t] if r[2] != profile_id]
        prefix = f"profile:{profile_id}:"
        self._meta = {k: v for k, v in self._meta.items() if not k.startswith(prefix)}

    def find_profile_by_identity(self, provider, subject):
        for p in self._profiles.values():
            if any(i["provider"] == provider and i["subject"] == subject for i in p.get("identities", [])):
                return copy.deepcopy(p)
        return None

    def count_unassigned(self):
        return sum(1 for t in _DATA_TABLES for r in self._tables[t] if r[2] is None)

    def assign_unassigned(self, profile_id):
        moved = 0
        for t in _DATA_TABLES:
            for r in self._tables[t]:
                if r[2] is None:
                    r[2] = profile_id
                    moved += 1
        return moved
