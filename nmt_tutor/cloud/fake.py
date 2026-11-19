"""In-memory stand-in for SupabaseClient (self-test and tests; no network).

It mimics what the app relies on: rows owned by the signed-in user, profile upsert,
a server-side `updated_at`, eq./gte./is./in. filters, one profile per account and the
server functions begin_session / submit_session (with stats rows and the streak) /
delete_my_account. The real behaviour is checked by tests/cloud_integration_test.py.
"""

import itertools
import time
import uuid
from datetime import date, datetime, timedelta, timezone

from .http import CloudError
from .supabase import CloudSession

_TABLES = ("profiles", "profile_meta", "sessions", "session_subjects", "session_answers", "hint_events")


class FakeCloud:
    def __init__(self):
        self.tables = {t: {} for t in _TABLES}
        self.users = {}  # email -> user id
        self.codes = {}  # email -> code
        self._tick = itertools.count(1)
        self._base = datetime.now(timezone.utc)
        self.requests = 0
        self.offline = False

    def _now(self):
        return (self._base + timedelta(milliseconds=next(self._tick))).isoformat()

    def _check_online(self):
        if self.offline:
            from .http import NetworkError

            raise NetworkError("Немає з’єднання з хмарою (fake offline).")

    # --- auth ------------------------------------------------------------------
    def send_code(self, email):
        self._check_online()
        self.codes[email] = "123456"

    def verify_code(self, email, code):
        self._check_online()
        if self.codes.get(email) != code:
            raise CloudError("Код неправильний або застарів.", status=403)
        uid = self.users.setdefault(email, str(uuid.uuid4()))
        return CloudSession(uid, email, f"access-{uid}", f"refresh-{uuid.uuid4()}", time.time() + 3600)

    def refresh(self, session):
        session.refresh_token = f"refresh-{uuid.uuid4()}"
        session.expires_at = time.time() + 3600
        return session

    def ensure_fresh(self, session):
        if session.expires_at - time.time() < 120:
            self.refresh(session)
        return session

    # --- REST ------------------------------------------------------------------
    def _uid(self, session):
        self._check_online()
        self.requests += 1
        if session.user_id not in self.users.values():
            raise CloudError("JWT invalid", status=401)
        return session.user_id

    def upsert(self, session, table, rows):
        owner = self._uid(session)
        if table != "profiles":
            raise CloudError("permission denied", status=403)
        tbl = self.tables[table]
        for row in rows:
            cur = tbl.get(row["id"])
            if cur is not None and cur["owner"] != owner:
                raise CloudError("row-level security", status=403)
            if cur is None and any(r["owner"] == owner for r in tbl.values()):
                raise CloudError("duplicate key value violates unique constraint", status=409, code="23505")
            merged = dict(cur or {}, **row)
            merged["owner"] = owner
            merged["updated_at"] = self._now()
            tbl[row["id"]] = merged
            if cur is None:
                self.tables["profile_meta"][row["id"]] = {"profile_id": row["id"], "owner": owner, "data": {},
                                                          "client_data": {}, "updated_at": self._now()}

    @staticmethod
    def _match(row, filters):
        for col, cond in (filters or {}).items():
            op, _, val = cond.partition(".")
            cur = row.get(col)
            if op == "eq" and str(cur) != val:
                return False
            if op == "gte" and not (cur or "") >= val:
                return False
            if op == "is" and cur is not {"true": True, "false": False, "null": None}[val]:
                return False
            if op == "in" and str(cur) not in val.strip("()").split(","):
                return False
        return True

    def select_all(self, session, table, filters=None, order="updated_at.asc,id.asc"):
        owner = self._uid(session)
        rows = self.tables[table].values() if isinstance(self.tables[table], dict) else self.tables[table]
        out = [dict(r) for r in rows if r["owner"] == owner and self._match(r, filters)]
        keys = [part.split(".")[0] for part in order.split(",")]
        return sorted(out, key=lambda r: tuple(str(r.get(k) or "") for k in keys))

    # --- server functions --------------------------------------------------------
    def rpc(self, session, function, args=None):
        owner = self._uid(session)
        args = args or {}
        if function == "begin_session":
            return self._begin(owner, args)
        if function == "submit_session":
            return self._submit(owner, args["p_session"])
        if function == "delete_my_account":
            for name, tbl in self.tables.items():
                for key in [k for k, r in tbl.items() if r["owner"] == owner]:
                    del tbl[key]
            self.users = {e: u for e, u in self.users.items() if u != owner}
            return None
        raise CloudError(f"unknown function {function}", status=404)

    def _own_profile(self, owner, pid):
        prof = self.tables["profiles"].get(pid)
        if prof is None or prof["owner"] != owner:
            raise CloudError("profile not found", status=400)

    def _begin(self, owner, a):
        self._own_profile(owner, a["p_profile_id"])
        sid = a["p_session_id"]
        cur = self.tables["sessions"].get(sid)
        if cur is None:
            cur = {"id": sid, "owner": owner, "profile_id": a["p_profile_id"], "status": "active",
                   "started_at": self._now(), "finished_at": None, "length_mode": a["p_length_mode"],
                   "tutor_mode": a["p_tutor_mode"], "mistake_drill": a["p_mistake_drill"],
                   "focus_section": a["p_focus_section"], "subjects": a["p_subjects"], "imported": False,
                   "updated_at": self._now()}
            self.tables["sessions"][sid] = cur
        elif cur["owner"] != owner:
            raise CloudError("not allowed", status=400)
        return {"allowed": True, "session_id": sid, "started_at": cur["started_at"]}

    def _submit(self, owner, p):
        self._own_profile(owner, p["profile_id"])
        sid = p["id"]
        cur = self.tables["sessions"].get(sid)
        if cur is not None and cur["owner"] != owner:
            raise CloudError("not allowed", status=400)
        if cur is not None and cur["status"] == "finished":
            return {"ok": True, "already": True}
        if cur is None:
            cur = {"id": sid, "owner": owner, "profile_id": p["profile_id"], "started_at": p["started_at"],
                   "length_mode": p["length_mode"], "tutor_mode": p["tutor_mode"], "mistake_drill": p["mistake_drill"],
                   "focus_section": p.get("focus_section"), "subjects": [s["subject"] for s in p["subjects"]],
                   "imported": True}
            self.tables["sessions"][sid] = cur
        cur.update(status="finished", finished_at=p["finished_at"], updated_at=self._now())
        for s in p["subjects"]:
            self.tables["session_subjects"][(sid, s["subject"])] = dict(s, session_id=sid, owner=owner)
        for a in p["answers"]:
            self.tables["session_answers"][(sid, a["subject"], a["question_no"])] = dict(a, session_id=sid, owner=owner)
        for h in p["hints"]:
            key = (sid, h["subject"], h["question_no"], h["level"], next(self._tick))
            self.tables["hint_events"][key] = dict(h, session_id=sid, owner=owner)
        return {"ok": True, "streak": self._streak(p["profile_id"], p["finished_at"])}

    def _streak(self, pid, finished_at):
        meta = self.tables["profile_meta"][pid]
        st = meta["data"].get("streak") or {}
        today = datetime.fromisoformat(finished_at).astimezone().date()
        last = date.fromisoformat(st["last_day"]) if st.get("last_day") else None
        cur_n, best = st.get("current", 0), st.get("best", 0)
        if last is None or today > last + timedelta(days=1):
            cur_n = 1
        elif today == last + timedelta(days=1):
            cur_n += 1
        elif today < last:
            return st
        st = {"current": cur_n, "best": max(best, cur_n), "last_day": max(today, last or today).isoformat()}
        meta["data"] = dict(meta["data"], streak=st)
        meta["updated_at"] = self._now()
        return st
