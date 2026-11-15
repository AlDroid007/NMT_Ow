"""Repository interface for user data (profiles, results, progress, reports, custom banks).

UI and core code talk only to this interface. The first implementation is the
encrypted local SQLite database (sqlite_repo.py); a cloud backend (Supabase,
Firebase, CloudKit, ...) can be added as another subclass without touching them.

Every result, report and custom bank belongs to a profile (`profile_id`). The data
methods take `profile_id=None`, which means rows not owned by any profile yet
(data from before profiles existed). The UI works with `repo.for_profile(id)`,
a view in which the same methods see only that profile's data.
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
    def save_result(self, result, profile_id=None):
        """Stores a finished session (see engine.build_session_result); returns its id."""

    @abc.abstractmethod
    def list_results(self, subject=None, profile_id=None):
        """Results oldest first: [{"id", "created_at", **result}]; optionally only those with `subject`."""

    def get_progress(self, profile_id=None):
        """Per-subject aggregate over the stored results."""
        progress = {}
        for res in self.list_results(profile_id=profile_id):
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
    def save_report(self, text, title=None, created_at=None, profile_id=None):
        """Stores a report; returns its id."""

    @abc.abstractmethod
    def list_reports(self, profile_id=None):
        """[{"id", "created_at", "title"}], newest first."""

    @abc.abstractmethod
    def get_report(self, report_id, profile_id=None):
        """{"id", "created_at", "title", "text"} or None."""

    # --- custom task banks -------------------------------------------------
    @abc.abstractmethod
    def save_custom_bank(self, name, bank, created_at=None, profile_id=None):
        """Stores a validated bank {subject_id: [task, ...]}; returns its id."""

    @abc.abstractmethod
    def list_custom_banks(self, profile_id=None):
        """[{"id", "created_at", "name", "tasks"}], oldest first."""

    @abc.abstractmethod
    def get_custom_bank(self, bank_id, profile_id=None):
        """The stored bank dict or None."""

    @abc.abstractmethod
    def delete_custom_bank(self, bank_id, profile_id=None):
        pass

    def load_custom_banks(self, profile_id=None):
        """All stored banks merged into one {subject_id: [task, ...]}."""
        merged = {}
        for info in self.list_custom_banks(profile_id=profile_id):
            bank = self.get_custom_bank(info["id"], profile_id=profile_id) or {}
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

    # --- profiles ---------------------------------------------------------------
    @abc.abstractmethod
    def list_profiles(self):
        """All profiles (see profiles.py), oldest first."""

    @abc.abstractmethod
    def get_profile(self, profile_id):
        """The profile dict or None."""

    @abc.abstractmethod
    def save_profile(self, profile):
        """Inserts or replaces a profile (keyed by profile["id"]) and its sign-in identities."""

    @abc.abstractmethod
    def delete_profile(self, profile_id):
        """Deletes the profile with all its results, reports and custom banks."""

    @abc.abstractmethod
    def find_profile_by_identity(self, provider, subject):
        """Profile that signs in with (provider, subject), or None."""

    @abc.abstractmethod
    def count_unassigned(self):
        """Number of results, reports and banks not owned by any profile."""

    @abc.abstractmethod
    def assign_unassigned(self, profile_id):
        """Gives every unowned result, report and bank to the profile; returns how many."""

    def for_profile(self, profile_id):
        """View of this repository limited to one profile's data."""
        return ProfileScope(self, profile_id)

    def close(self):
        pass


class ProfileScope(Repository):
    """The Repository API bound to one profile; profile management goes to the full store."""

    def __init__(self, repo, profile_id):
        self.store = repo
        self.profile_id = profile_id
        self.startup_notices = ()

    def save_result(self, result, profile_id=None):
        return self.store.save_result(result, profile_id=self.profile_id)

    def list_results(self, subject=None, profile_id=None):
        return self.store.list_results(subject, profile_id=self.profile_id)

    def save_report(self, text, title=None, created_at=None, profile_id=None):
        return self.store.save_report(text, title, created_at, profile_id=self.profile_id)

    def list_reports(self, profile_id=None):
        return self.store.list_reports(profile_id=self.profile_id)

    def get_report(self, report_id, profile_id=None):
        return self.store.get_report(report_id, profile_id=self.profile_id)

    def save_custom_bank(self, name, bank, created_at=None, profile_id=None):
        return self.store.save_custom_bank(name, bank, created_at, profile_id=self.profile_id)

    def list_custom_banks(self, profile_id=None):
        return self.store.list_custom_banks(profile_id=self.profile_id)

    def get_custom_bank(self, bank_id, profile_id=None):
        return self.store.get_custom_bank(bank_id, profile_id=self.profile_id)

    def delete_custom_bank(self, bank_id, profile_id=None):
        return self.store.delete_custom_bank(bank_id, profile_id=self.profile_id)

    def load_custom_banks(self, profile_id=None):
        return self.store.load_custom_banks(profile_id=self.profile_id)

    def get_meta(self, key, default=None):
        return self.store.get_meta(f"profile:{self.profile_id}:{key}", default)

    def set_meta(self, key, value):
        self.store.set_meta(f"profile:{self.profile_id}:{key}", value)

    @property
    def profile(self):
        return self.store.get_profile(self.profile_id)

    def list_profiles(self):
        return self.store.list_profiles()

    def get_profile(self, profile_id):
        return self.store.get_profile(profile_id)

    def save_profile(self, profile):
        return self.store.save_profile(profile)

    def delete_profile(self, profile_id):
        return self.store.delete_profile(profile_id)

    def find_profile_by_identity(self, provider, subject):
        return self.store.find_profile_by_identity(provider, subject)

    def count_unassigned(self):
        return self.store.count_unassigned()

    def assign_unassigned(self, profile_id):
        return self.store.assign_unassigned(profile_id)

    def for_profile(self, profile_id):
        return self.store.for_profile(profile_id)

    def close(self):
        """The store is shared by every profile view; it is closed by its owner."""
