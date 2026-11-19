"""Local SQLite implementation of the repository with encrypted record payloads.

Only ids, sync ids (random UUIDs), timestamps, the owning profile id (a random
UUID), sync flags, the schema version and settings keys are stored in clear; every payload (profiles,
results, report text and title, bank contents and name, setting values) is
AES-GCM encrypted with the key from the OS key store. Sign-in identities are
looked up by a keyed hash, never stored in clear.
"""

import sqlite3
import time
import uuid
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


def _migrate_to_v3(conn):
    """Cloud sync of sessions: every result gets a UUID (`uid` = session id in the cloud)
    and a `dirty` mark (0 = the cloud has it, otherwise a change number, so a row changed
    while an upload was in flight stays dirty). Profiles get the same `dirty` mark.
    """
    cols = {row[1] for row in conn.execute("PRAGMA table_info(results)")}
    if "uid" not in cols:
        conn.execute("ALTER TABLE results ADD COLUMN uid TEXT")
    if "dirty" not in cols:
        conn.execute("ALTER TABLE results ADD COLUMN dirty INTEGER NOT NULL DEFAULT 0")
    for (rid,) in conn.execute("SELECT id FROM results WHERE uid IS NULL").fetchall():
        conn.execute("UPDATE results SET uid = ?, dirty = 1 WHERE id = ?", (uuid.uuid4().hex, rid))
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS results_uid ON results (uid)")
    cols = {row[1] for row in conn.execute("PRAGMA table_info(profiles)")}
    if "dirty" not in cols:
        conn.execute("ALTER TABLE profiles ADD COLUMN dirty INTEGER NOT NULL DEFAULT 1")


# Index i migrates the schema from version i to i + 1 (PRAGMA user_version).
MIGRATIONS = [_migrate_to_v1, _migrate_to_v2, _migrate_to_v3]
_DATA_TABLES = ("results", "reports", "custom_banks")
SCHEMA_VERSION = len(MIGRATIONS)


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _change_no():
    """Non-zero, increasing change number for the `dirty` column."""
    return time.time_ns()


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
            if table == "results":
                # The session id from the app becomes the cloud id; old results get a fresh one.
                uid = obj.get("session_uid") or uuid.uuid4().hex
                cur = self._conn.execute(
                    "INSERT INTO results (created_at, payload, profile_id, uid, dirty) VALUES (?, ?, ?, ?, ?)",
                    (created, blob, profile_id, uid, _change_no()),
                )
            else:
                cur = self._conn.execute(
                    f"INSERT INTO {table} (created_at, payload, profile_id) VALUES (?, ?, ?)", (created, blob, profile_id)
                )
        return cur.lastrowid

    def _rows(self, table, profile_id, order="ASC"):
        # Rows pulled from the cloud arrive later than newer local ones, so order by time, not id.
        rows = self._conn.execute(
            f"SELECT id, created_at, payload FROM {table} WHERE profile_id IS ? ORDER BY created_at {order}, id {order}",
            (profile_id,),
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

    def save_profile(self, profile, _dirty=True):
        pid = profile["id"]
        blob = self._cipher.encrypt_json(profile, b"profiles")
        created = profile.get("created_at") or _now()
        updated = profile.get("updated_at") or created
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO profiles (id, created_at, updated_at, payload, dirty) VALUES (?, ?, ?, ?, ?)",
                (pid, created, updated, blob, _change_no() if _dirty else 0),
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

    # --- cloud sync (see cloud/sync.py) --------------------------------------
    supports_sync = True

    def sync_outbox(self, profile_id):
        """What the cloud does not have yet: the profile (if changed) and finished sessions."""
        out = {"profile": None, "results": []}
        row = self._conn.execute("SELECT payload, dirty FROM profiles WHERE id = ?", (profile_id,)).fetchone()
        if row is None:
            return out
        if row[1]:
            out["profile"] = dict(self._cipher.decrypt_json(row[0], b"profiles"), _dirty=row[1])
        rows = self._conn.execute(
            "SELECT uid, created_at, payload, dirty FROM results WHERE profile_id = ? AND dirty != 0 ORDER BY created_at, id",
            (profile_id,),
        ).fetchall()
        for uid, created, blob, dirty in rows:
            out["results"].append({"uid": uid, "created_at": created, "payload": self._cipher.decrypt_json(blob, b"results"),
                                   "_dirty": dirty})
        return out

    def sync_known_results(self, profile_id):
        """UUIDs of the profile's results already on this device."""
        return {r[0] for r in self._conn.execute("SELECT uid FROM results WHERE profile_id = ?", (profile_id,))}

    def sync_mark_all_dirty(self, profile_id):
        """Queues the whole profile for upload (after linking it to another cloud account)."""
        with self._conn:
            self._conn.execute("UPDATE profiles SET dirty = ? WHERE id = ?", (_change_no(), profile_id))
            self._conn.execute("UPDATE results SET dirty = ? WHERE profile_id = ?", (_change_no(), profile_id))

    def sync_ack(self, profile_id, outbox, uploaded_results=None):
        """Marks uploads as done, unless the rows changed again since sync_outbox()."""
        with self._conn:
            prof = outbox.get("profile")
            if prof:
                self._conn.execute("UPDATE profiles SET dirty = 0 WHERE id = ? AND dirty = ?", (profile_id, prof["_dirty"]))
            done = set(uploaded_results) if uploaded_results is not None else None
            for rec in outbox.get("results", ()):
                if done is None or rec["uid"] in done:
                    self._conn.execute("UPDATE results SET dirty = 0 WHERE uid = ? AND dirty = ?", (rec["uid"], rec["_dirty"]))

    def sync_apply(self, profile_id, pulled):
        """Stores what came from the cloud (profile fields, sessions from other devices). Returns rows changed."""
        changed = 0
        cloud_prof = pulled.get("profile")
        if cloud_prof:
            row = self._conn.execute("SELECT payload, dirty FROM profiles WHERE id = ?", (profile_id,)).fetchone()
            if row is not None and not row[1]:
                local = self._cipher.decrypt_json(row[0], b"profiles")
                fields = ("name", "avatar", "subjects", "targets", "exam_date")
                if any(local.get(f) != cloud_prof.get(f) for f in fields):
                    local.update({f: cloud_prof.get(f) for f in fields})
                    local["updated_at"] = cloud_prof.get("updated_at") or local.get("updated_at")
                    self.save_profile(local, _dirty=False)
                    changed += 1
        with self._conn:
            for rec in pulled.get("results", ()):
                exists = self._conn.execute("SELECT 1 FROM results WHERE uid = ?", (rec["uid"],)).fetchone()
                if exists:
                    continue  # sessions never change after they are finished
                blob = self._cipher.encrypt_json(rec["payload"], b"results")
                self._conn.execute(
                    "INSERT INTO results (created_at, payload, profile_id, uid, dirty) VALUES (?, ?, ?, ?, 0)",
                    (rec["created_at"], blob, profile_id, rec["uid"]),
                )
                changed += 1
        return changed

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
