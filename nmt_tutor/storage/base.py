"""Repository interface for user data (results, progress, reports, custom banks).

UI and core code talk only to this interface. The first implementation is the
encrypted local SQLite database (sqlite_repo.py); a cloud backend (Supabase,
Firebase, CloudKit, ...) can be added as another subclass without touching them.
"""

import abc


class StorageError(RuntimeError):
    pass


class KeyMismatchError(StorageError):
    """The database was encrypted with a different key."""


class Repository(abc.ABC):
    #: User-facing messages collected while opening the store (shown once by the UI).
    startup_notices = ()

    # --- session results -------------------------------------------------
    @abc.abstractmethod
    def save_result(self, result):
        """Stores a finished session (see engine.build_session_result); returns its id."""

    @abc.abstractmethod
    def list_results(self, subject=None):
        """Results oldest first: [{"id", "created_at", **result}]; optionally only those with `subject`."""

    def get_progress(self):
        """Per-subject aggregate over all stored results."""
        progress = {}
        for res in self.list_results():
            for s in res.get("subjects", []):
                p = progress.setdefault(s["subject"], {
                    "sessions": 0,
                    "best_nmt_200": None,
                    "last_nmt_200": None,
                    "last_at": None,
                    "drills_done": 0,
                    "weak_sections": {},
                })
                p["sessions"] += 1
                nmt = s.get("nmt_200")
                if nmt is not None and (p["best_nmt_200"] is None or nmt > p["best_nmt_200"]):
                    p["best_nmt_200"] = nmt
                p["last_nmt_200"] = nmt
                p["last_at"] = res["created_at"]
                p["drills_done"] += s.get("drills_done", 0)
                for sec, cnt in s.get("weak_sections", {}).items():
                    p["weak_sections"][sec] = p["weak_sections"].get(sec, 0) + cnt
        return progress

    # --- text reports ------------------------------------------------------
    @abc.abstractmethod
    def save_report(self, text, title=None, created_at=None):
        """Stores a report; returns its id."""

    @abc.abstractmethod
    def list_reports(self):
        """[{"id", "created_at", "title"}], newest first."""

    @abc.abstractmethod
    def get_report(self, report_id):
        """{"id", "created_at", "title", "text"} or None."""

    # --- custom task banks -------------------------------------------------
    @abc.abstractmethod
    def save_custom_bank(self, name, bank, created_at=None):
        """Stores a validated bank {subject_id: [task, ...]}; returns its id."""

    @abc.abstractmethod
    def list_custom_banks(self):
        """[{"id", "created_at", "name", "tasks"}], oldest first."""

    @abc.abstractmethod
    def get_custom_bank(self, bank_id):
        """The stored bank dict or None."""

    @abc.abstractmethod
    def delete_custom_bank(self, bank_id):
        pass

    def load_custom_banks(self):
        """All stored banks merged into one {subject_id: [task, ...]}."""
        merged = {}
        for info in self.list_custom_banks():
            bank = self.get_custom_bank(info["id"]) or {}
            for k, v in bank.items():
                merged.setdefault(k, []).extend(v)
        return merged

    # --- small key/value settings -------------------------------------------
    @abc.abstractmethod
    def get_meta(self, key, default=None):
        pass

    @abc.abstractmethod
    def set_meta(self, key, value):
        pass

    def close(self):
        pass
