"""Local SQLite implementation of the repository with encrypted record payloads.

Only ids, creation timestamps, the owning profile id (a random UUID), the
schema version and settings keys are stored in clear; every payload (profiles,
results, report text and title, bank contents and name, setting values) is
AES-GCM encrypted with the key from the OS key store. Sign-in identities are
looked up by a keyed hash, never stored in clear.
"""

import sqlite3
from datetime import datetime

from .base import KeyMismatchError, Repository
from .crypto import DecryptionError

_KEY_CHECK = b"nmt-tutor-key-check-v1"


def _migrate_to_v1(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value BLOB NOT NULL
        );
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            payload BLOB NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            payload BLOB NOT NULL
        );
        CREATE TABLE IF NOT EXISTS custom_banks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            payload BLOB NOT NULL
        );
        """
    )


def _migrate_to_v2(conn):
    """Profiles: every data row gets an owner (NULL = data from before profiles)."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            payload BLOB NOT NULL
        );
        CREATE TABLE IF NOT EXISTS identities (
            provider TEXT NOT NULL,
            subject_hash TEXT NOT NULL,
            profile_id TEXT NOT NULL,
            PRIMARY KEY (provider, subject_hash)
        );
        """
    )
    # executescript commits on its own, so the column step must be safe to repeat.
    for table in ("results", "reports", "custom_banks"):
        cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        if "profile_id" not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN profile_id TEXT")
    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS results_profile ON results (profile_id);
        CREATE INDEX IF NOT EXISTS reports_profile ON reports (profile_id);
        CREATE INDEX IF NOT EXISTS custom_banks_profile ON custom_banks (profile_id);
        CREATE INDEX IF NOT EXISTS identities_profile ON identities (profile_id);
        """
    )


# Index i migrates the schema from version i to i + 1 (PRAGMA user_version).
MIGRATIONS = [_migrate_to_v1, _migrate_to_v2]
_DATA_TABLES = ("results", "reports", "custom_banks")
SCHEMA_VERSION = len(MIGRATIONS)


def _now():
    return datetime.now().isoformat(timespec="seconds")


class SQLiteRepository(Repository):
    def __init__(self, path, cipher):
        self.path = path
        self._cipher = cipher
        self.startup_notices = []
        self._conn = sqlite3.connect(path)
        try:
            self._migrate()
            self._check_key()
        except Exception:
            self._conn.close()
            raise

    # --- internals -----------------------------------------------------------
    def _migrate(self):
        version = self._conn.execute("PRAGMA user_version").fetchone()[0]
        if version > SCHEMA_VERSION:
            raise RuntimeError(f"Database schema v{version} is newer than this app (v{SCHEMA_VERSION}).")
        with self._conn:
            for step in range(version, SCHEMA_VERSION):
                MIGRATIONS[step](self._conn)
                self._conn.execute(f"PRAGMA user_version = {step + 1}")

    def _check_key(self):
        row = self._conn.execute("SELECT value FROM meta WHERE key = '_key_check'").fetchone()
        aad = b"meta:_key_check"
        if row is None:
            with self._conn:
                self._conn.execute(
                    "INSERT INTO meta (key, value) VALUES ('_key_check', ?)",
                    (self._cipher.encrypt(_KEY_CHECK, aad),),
                )
            return
        try:
            ok = self._cipher.decrypt(row[0], aad) == _KEY_CHECK
        except DecryptionError:
            ok = False
        if not ok:
            raise KeyMismatchError("The database was encrypted with a different key.")

    def _insert(self, table, obj, created_at=None, profile_id=None):
        created = created_at or _now()
        blob = self._cipher.encrypt_json(obj, table.encode("ascii"))
        with self._conn:
            cur = self._conn.execute(
                f"INSERT INTO {table} (created_at, payload, profile_id) VALUES (?, ?, ?)", (created, blob, profile_id)
            )
        return cur.lastrowid

    def _rows(self, table, profile_id, order="ASC"):
        rows = self._conn.execute(
            f"SELECT id, created_at, payload FROM {table} WHERE profile_id IS ? ORDER BY id {order}", (profile_id,)
        ).fetchall()
        aad = table.encode("ascii")
        return [(rid, created, self._cipher.decrypt_json(blob, aad)) for rid, created, blob in rows]

    def _row(self, table, rid, profile_id):
        row = self._conn.execute(
            f"SELECT id, created_at, payload FROM {table} WHERE id = ? AND profile_id IS ?", (rid, profile_id)
        ).fetchone()
        if row is None:
            return None
        return row[0], row[1], self._cipher.decrypt_json(row[2], table.encode("ascii"))

    # --- results -------------------------------------------------------------
    def save_result(self, result, profile_id=None):
        return self._insert("results", result, result.get("finished_at"), profile_id)

    def list_results(self, subject=None, profile_id=None):
        out = []
        for rid, created, payload in self._rows("results", profile_id):
            if subject is None or any(s.get("subject") == subject for s in payload.get("subjects", [])):
                rec = dict(payload)
                rec.update(id=rid, created_at=created)
                out.append(rec)
        return out

    # --- reports -------------------------------------------------------------
    def save_report(self, text, title=None, created_at=None, profile_id=None):
        return self._insert("reports", {"title": title or "", "text": text}, created_at, profile_id)

    def list_reports(self, profile_id=None):
        return [
            {"id": rid, "created_at": created, "title": p.get("title", "")}
            for rid, created, p in self._rows("reports", profile_id, "DESC")
        ]

    def get_report(self, report_id, profile_id=None):
        row = self._row("reports", report_id, profile_id)
        if row is None:
            return None
        rid, created, p = row
        return {"id": rid, "created_at": created, "title": p.get("title", ""), "text": p.get("text", "")}

    # --- custom banks --------------------------------------------------------
    def save_custom_bank(self, name, bank, created_at=None, profile_id=None):
        return self._insert("custom_banks", {"name": name, "bank": bank}, created_at, profile_id)

    def list_custom_banks(self, profile_id=None):
        return [
            {
                "id": rid,
                "created_at": created,
                "name": p.get("name", ""),
                "tasks": sum(len(v) for v in p.get("bank", {}).values()),
            }
            for rid, created, p in self._rows("custom_banks", profile_id)
        ]

    def get_custom_bank(self, bank_id, profile_id=None):
        row = self._row("custom_banks", bank_id, profile_id)
        return row[2].get("bank", {}) if row else None

    def load_custom_banks(self, profile_id=None):
        merged = {}
        for _rid, _created, p in self._rows("custom_banks", profile_id):
            for k, v in p.get("bank", {}).items():
                merged.setdefault(k, []).extend(v)
        return merged

    def delete_custom_bank(self, bank_id, profile_id=None):
        with self._conn:
            self._conn.execute("DELETE FROM custom_banks WHERE id = ? AND profile_id IS ?", (bank_id, profile_id))

    # --- profiles ------------------------------------------------------------
    def list_profiles(self):
        rows = self._conn.execute("SELECT payload FROM profiles ORDER BY created_at, id").fetchall()
        return [self._cipher.decrypt_json(r[0], b"profiles") for r in rows]

    def get_profile(self, profile_id):
        row = self._conn.execute("SELECT payload FROM profiles WHERE id = ?", (profile_id,)).fetchone()
        return self._cipher.decrypt_json(row[0], b"profiles") if row else None

    def save_profile(self, profile):
        pid = profile["id"]
        blob = self._cipher.encrypt_json(profile, b"profiles")
        created = profile.get("created_at") or _now()
        updated = profile.get("updated_at") or created
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO profiles (id, created_at, updated_at, payload) VALUES (?, ?, ?, ?)",
                (pid, created, updated, blob),
            )
            self._conn.execute("DELETE FROM identities WHERE profile_id = ?", (pid,))
            for ident in profile.get("identities", []):
                self._conn.execute(
                    "INSERT OR REPLACE INTO identities (provider, subject_hash, profile_id) VALUES (?, ?, ?)",
                    (ident["provider"], self._cipher.lookup_hash(f"{ident['provider']}:{ident['subject']}"), pid),
                )
        return pid

    def delete_profile(self, profile_id):
        with self._conn:
            for table in _DATA_TABLES:
                self._conn.execute(f"DELETE FROM {table} WHERE profile_id = ?", (profile_id,))
            self._conn.execute("DELETE FROM identities WHERE profile_id = ?", (profile_id,))
            self._conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            self._conn.execute("DELETE FROM meta WHERE key LIKE ?", (f"profile:{profile_id}:%",))

    def find_profile_by_identity(self, provider, subject):
        row = self._conn.execute(
            "SELECT profile_id FROM identities WHERE provider = ? AND subject_hash = ?",
            (provider, self._cipher.lookup_hash(f"{provider}:{subject}")),
        ).fetchone()
        return self.get_profile(row[0]) if row else None

    def count_unassigned(self):
        return sum(
            self._conn.execute(f"SELECT COUNT(*) FROM {table} WHERE profile_id IS NULL").fetchone()[0]
            for table in _DATA_TABLES
        )

    def assign_unassigned(self, profile_id):
        moved = 0
        with self._conn:
            for table in _DATA_TABLES:
                moved += self._conn.execute(
                    f"UPDATE {table} SET profile_id = ? WHERE profile_id IS NULL", (profile_id,)
                ).rowcount
        return moved

    # --- settings ------------------------------------------------------------
    def get_meta(self, key, default=None):
        row = self._conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        if row is None:
            return default
        return self._cipher.decrypt_json(row[0], b"meta:" + key.encode("utf-8"))

    def set_meta(self, key, value):
        blob = self._cipher.encrypt_json(value, b"meta:" + key.encode("utf-8"))
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                (key, blob),
            )

    def close(self):
        try:
            self._conn.close()
        except sqlite3.Error:
            pass
