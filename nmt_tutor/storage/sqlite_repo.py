"""Local SQLite implementation of the repository with encrypted record payloads.

Only ids, creation timestamps, the schema version and settings keys are stored
in clear; every payload (results, report text and title, bank contents and
name, setting values) is AES-GCM encrypted with the key from the OS key store.
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


# Index i migrates the schema from version i to i + 1 (PRAGMA user_version).
MIGRATIONS = [_migrate_to_v1]
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

    def _insert(self, table, obj, created_at=None):
        created = created_at or _now()
        blob = self._cipher.encrypt_json(obj, table.encode("ascii"))
        with self._conn:
            cur = self._conn.execute(f"INSERT INTO {table} (created_at, payload) VALUES (?, ?)", (created, blob))
        return cur.lastrowid

    def _rows(self, table, order="ASC"):
        rows = self._conn.execute(f"SELECT id, created_at, payload FROM {table} ORDER BY id {order}").fetchall()
        aad = table.encode("ascii")
        return [(rid, created, self._cipher.decrypt_json(blob, aad)) for rid, created, blob in rows]

    def _row(self, table, rid):
        row = self._conn.execute(f"SELECT id, created_at, payload FROM {table} WHERE id = ?", (rid,)).fetchone()
        if row is None:
            return None
        return row[0], row[1], self._cipher.decrypt_json(row[2], table.encode("ascii"))

    # --- results -------------------------------------------------------------
    def save_result(self, result):
        return self._insert("results", result, result.get("finished_at"))

    def list_results(self, subject=None):
        out = []
        for rid, created, payload in self._rows("results"):
            if subject is None or any(s.get("subject") == subject for s in payload.get("subjects", [])):
                rec = dict(payload)
                rec.update(id=rid, created_at=created)
                out.append(rec)
        return out

    # --- reports -------------------------------------------------------------
    def save_report(self, text, title=None, created_at=None):
        return self._insert("reports", {"title": title or "", "text": text}, created_at)

    def list_reports(self):
        return [
            {"id": rid, "created_at": created, "title": p.get("title", "")}
            for rid, created, p in self._rows("reports", "DESC")
        ]

    def get_report(self, report_id):
        row = self._row("reports", report_id)
        if row is None:
            return None
        rid, created, p = row
        return {"id": rid, "created_at": created, "title": p.get("title", ""), "text": p.get("text", "")}

    # --- custom banks --------------------------------------------------------
    def save_custom_bank(self, name, bank, created_at=None):
        return self._insert("custom_banks", {"name": name, "bank": bank}, created_at)

    def list_custom_banks(self):
        return [
            {
                "id": rid,
                "created_at": created,
                "name": p.get("name", ""),
                "tasks": sum(len(v) for v in p.get("bank", {}).values()),
            }
            for rid, created, p in self._rows("custom_banks")
        ]

    def get_custom_bank(self, bank_id):
        row = self._row("custom_banks", bank_id)
        return row[2].get("bank", {}) if row else None

    def load_custom_banks(self):
        merged = {}
        for _rid, _created, p in self._rows("custom_banks"):
            for k, v in p.get("bank", {}).items():
                merged.setdefault(k, []).extend(v)
        return merged

    def delete_custom_bank(self, bank_id):
        with self._conn:
            self._conn.execute("DELETE FROM custom_banks WHERE id = ?", (bank_id,))

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
