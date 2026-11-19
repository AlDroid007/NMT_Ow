"""Sync of one profile with the cloud, and the profile <-> cloud account link.

What travels:
* the profile (name, avatar, subjects, goals, exam date) — both ways;
* finished trainings — up through the server function submit_session (session, result
  per subject, every answer, every hint; the server updates statistics and the streak),
  down as finished sessions from other devices (rebuilt into local results for the cabinet);
* profile metadata written by the server (streak, later medals) — down only.
Reports and custom banks stay on the device. The PIN never leaves the device.

A sync round has three phases, so a GUI can keep the database on its own thread and
run only the network part in the background:

    job = prepare(store, profile_id)          # local: what to upload (no network)
    outcome = exchange(client, job)           # network: upload, then download changes
    commit(store, job, outcome)               # local: mark uploads done, store downloads

On an error call fail(store, job, exc): it keeps the renewed session (refresh tokens
rotate) and marks the trainings uploaded before the error. sync_profile() runs it all.
"""

import copy
import re
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from ..config import SUBJECTS_CONFIG
from ..profiles import PROVIDER_CLOUD, link_identity, normalize_profile, touch
from .http import CloudError
from .supabase import CloudSession

LINK_KEY = "cloud"
CURSOR_OVERLAP = timedelta(seconds=60)
LENGTH_MODES = ("quick", "medium", "full", "focus")
ID_CHUNK = 100

# --- ids and times -----------------------------------------------------------------


def cloud_id(hex_id):
    return str(uuid.UUID(hex_id))


def local_id(cloud_uuid):
    return uuid.UUID(cloud_uuid).hex


_FRACTION = re.compile(r"\.(\d+)")


def _parse_time(text):
    text = text.strip().replace("Z", "+00:00").replace(" ", "T", 1)
    text = _FRACTION.sub(lambda m: "." + (m.group(1) + "000000")[:6], text, count=1)
    return datetime.fromisoformat(text)


def to_cloud_time(local_iso):
    """Local naive ISO time from the app -> ISO time with the computer's UTC offset."""
    dt = _parse_time(local_iso)
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt.isoformat()


def to_local_time(cloud_iso):
    """Server time with offset -> local naive ISO time (how the app stores times)."""
    dt = _parse_time(cloud_iso)
    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)
    return dt.isoformat(timespec="seconds")


# --- link between a profile and a cloud account ------------------------------------------


def get_link(store, profile_id):
    """{"session", "cursor", "last_sync", "last_error", "meta"} or None."""
    if not getattr(store, "supports_sync", False):
        return None
    return store.get_meta(f"profile:{profile_id}:{LINK_KEY}")


def _save_link(store, profile_id, link):
    store.set_meta(f"profile:{profile_id}:{LINK_KEY}", link)


def is_linked(store, profile_id):
    link = get_link(store, profile_id)
    return bool(link and link.get("session"))


def linked_email(store, profile_id):
    link = get_link(store, profile_id) or {}
    return (link.get("session") or {}).get("email")


def current_streak(link, today=None):
    """Days in a row from the server's streak, 0 when it is broken (no training yesterday or today)."""
    streak = ((link or {}).get("meta") or {}).get("streak") or {}
    try:
        last = date.fromisoformat(streak.get("last_day") or "")
    except ValueError:
        return 0
    today = today or date.today()
    return int(streak.get("current") or 0) if last >= today - timedelta(days=1) else 0


def attach(store, profile_id, session, from_cloud=False):
    """Links the profile to the cloud account of `session` (main thread).

    A new link uploads everything the profile has, unless the profile itself was just
    downloaded from that account.
    """
    profile = store.get_profile(profile_id)
    if profile is None:
        raise CloudError("Профіль не знайдено.")
    old = get_link(store, profile_id) or {}
    same_account = (old.get("session") or {}).get("user_id") == session.user_id
    profile["identities"] = [i for i in profile.get("identities", []) if i["provider"] != PROVIDER_CLOUD]
    link_identity(profile, PROVIDER_CLOUD, session.user_id, email=session.email)
    touch(profile)
    store.save_profile(profile, _dirty=not from_cloud)
    if not from_cloud and not same_account:
        store.sync_mark_all_dirty(profile_id)
    keep = same_account
    _save_link(store, profile_id, {
        "session": session.to_dict(),
        "cursor": old.get("cursor") if keep else None,
        "last_sync": old.get("last_sync") if keep else None,
        "last_error": None,
        "meta": old.get("meta") if keep else None,
    })
    return profile


def detach(store, profile_id):
    """Forgets the cloud account on this device; local data and cloud data stay."""
    profile = store.get_profile(profile_id)
    if profile is not None:
        profile["identities"] = [i for i in profile.get("identities", []) if i["provider"] != PROVIDER_CLOUD]
        touch(profile)
        store.save_profile(profile, _dirty=False)
    store.set_meta(f"profile:{profile_id}:{LINK_KEY}", None)


def remember_session(store, profile_id, session, error=None):
    """Keeps a (possibly renewed) session, e.g. after a failed round (main thread)."""
    link = get_link(store, profile_id)
    if not link or (link.get("session") or {}).get("user_id") != session.user_id:
        return
    link["session"] = session.to_dict()
    if error is not None:
        link["last_error"] = error
    _save_link(store, profile_id, link)


# --- cloud profile of an account -------------------------------------------------------


def fetch_account_profile(client, session):
    """The account's profile row in the cloud, or None (network)."""
    rows = client.select_all(session, "profiles", {"owner": f"eq.{session.user_id}"}, order="created_at.asc")
    return rows[0] if rows else None


def profile_from_cloud(row, session):
    """A new local profile built from the account's cloud profile (no PIN)."""
    pid = local_id(row["id"])
    profile = {
        "id": pid,
        "name": row.get("name") or "Учень",
        "avatar": row.get("avatar") or {},
        "subjects": row.get("subjects") or [],
        "targets": row.get("targets") or {},
        "exam_date": row.get("exam_date"),
        "identities": [],
        "pin": None,
        "created_at": to_local_time(row["created_at"]),
        "updated_at": to_local_time(row.get("updated_at") or row["created_at"]),
    }
    link_identity(profile, "local", pid)
    link_identity(profile, PROVIDER_CLOUD, session.user_id, email=session.email)
    return normalize_profile(profile)


# --- conversion ----------------------------------------------------------------------------


def _profile_row(p):
    return {
        "id": cloud_id(p["id"]),
        "name": p["name"],
        "avatar": p.get("avatar") or {},
        "subjects": p.get("subjects") or [],
        "targets": p.get("targets") or {},
        "exam_date": p.get("exam_date"),
        "created_at": to_cloud_time(p.get("created_at") or datetime.now().isoformat()),
    }


def _time_or(value, fallback):
    try:
        return to_cloud_time(value) if value else fallback
    except ValueError:
        return fallback


def session_payload(rec, profile_id):
    """Argument of submit_session() for a local result (see the SQL migration)."""
    p = rec["payload"]
    finished = _time_or(p.get("finished_at"), to_cloud_time(rec["created_at"]))
    started = _time_or(p.get("started_at"), finished)
    mode = p.get("length_mode")
    return {
        "id": cloud_id(rec["uid"]),
        "profile_id": cloud_id(profile_id),
        "started_at": started,
        "finished_at": finished,
        "length_mode": mode if mode in LENGTH_MODES else "quick",
        "tutor_mode": bool(p.get("tutor_mode", True)),
        "mistake_drill": bool(p.get("mistake_drill")),
        "focus_section": p.get("focus_section"),
        "subjects": [
            {"subject": s["subject"], "earned": s.get("earned", 0), "max_points": s.get("actual_max", 0),
             "projected_raw": s.get("projected_raw"), "nmt_200": s.get("nmt_200"), "is_full": bool(s.get("is_full")),
             "drills_done": s.get("drills_done", 0)}
            for s in p.get("subjects", [])
        ],
        "answers": [dict(a, answered_at=_time_or(a.get("answered_at"), finished)) for a in p.get("answers", [])],
        "hints": [dict(h, opened_at=_time_or(h.get("opened_at"), finished)) for h in p.get("hints", [])],
    }


def result_from_cloud(session_row, subject_rows, answer_rows):
    """A local result record (what the cabinet reads) rebuilt from cloud rows."""
    weak = {}
    for a in answer_rows:
        if not a.get("is_correct"):
            per = weak.setdefault(a["subject"], {})
            sec = a.get("section") or "Загальне"
            per[sec] = per.get(sec, 0) + 1
    subjects = []
    for s in subject_rows:
        cfg = SUBJECTS_CONFIG.get(s["subject"], {})
        subjects.append({
            "subject": s["subject"], "name": cfg.get("name", s["subject"]), "earned": s.get("earned", 0),
            "actual_max": s.get("max_points", 0), "projected_raw": s.get("projected_raw"),
            "official_max": cfg.get("max_score"), "threshold": cfg.get("threshold"), "nmt_200": s.get("nmt_200"),
            "is_full": bool(s.get("is_full")), "drills_done": s.get("drills_done", 0),
            "weak_sections": weak.get(s["subject"], {}),
        })
    order = {sid: i for i, sid in enumerate(session_row.get("subjects") or [])}
    subjects.sort(key=lambda s: order.get(s["subject"], 99))
    finished = to_local_time(session_row.get("finished_at") or session_row["started_at"])
    payload = {
        "finished_at": finished,
        "started_at": to_local_time(session_row["started_at"]),
        "session_uid": local_id(session_row["id"]),
        "length_mode": session_row.get("length_mode"),
        "tutor_mode": bool(session_row.get("tutor_mode")),
        "mistake_drill": bool(session_row.get("mistake_drill")),
        "subjects": subjects,
        "from_cloud": True,
    }
    if session_row.get("focus_section"):
        payload["focus_section"] = session_row["focus_section"]
    return {"uid": local_id(session_row["id"]), "created_at": finished, "payload": payload}


# --- start of a training ------------------------------------------------------------------


def begin_session(client, job, session_uid, subjects, length_mode, tutor_mode, mistake_drill=False, focus_section=None):
    """Registers the start of a training on the server (network). Returns its answer dict."""
    session = job.session
    return client.rpc(session, "begin_session", {
        "p_session_id": cloud_id(session_uid),
        "p_profile_id": cloud_id(job.profile_id),
        "p_subjects": list(subjects),
        "p_length_mode": length_mode if length_mode in LENGTH_MODES else "quick",
        "p_tutor_mode": bool(tutor_mode),
        "p_mistake_drill": bool(mistake_drill),
        "p_focus_section": focus_section,
    }) or {}


# --- the three phases ---------------------------------------------------------------------


@dataclass
class SyncJob:
    profile_id: str
    session: CloudSession
    cursor: str = None
    outbox: dict = field(default_factory=dict)
    known: set = field(default_factory=set)
    uploaded: list = field(default_factory=list)  # filled by exchange(), also when it fails midway


@dataclass
class SyncOutcome:
    session: CloudSession
    pulled: dict
    cursor: str = None
    meta: dict = None


def prepare(store, profile_id):
    """What to upload for a linked profile, or None when it is not linked (main thread)."""
    link = get_link(store, profile_id)
    if not link or not link.get("session"):
        return None
    return SyncJob(profile_id, CloudSession.from_dict(link["session"]), link.get("cursor"),
                   store.sync_outbox(profile_id), store.sync_known_results(profile_id))


def exchange(client, job):
    """Uploads the outbox, then downloads what changed in the cloud (network only, any thread).

    On failure the raised error carries `cloud_session`; pass the job to fail().
    """
    job.session = copy.copy(job.session)
    try:
        return _exchange(client, job)
    except Exception as exc:
        exc.cloud_session = job.session
        raise


def _exchange(client, job):
    session = job.session
    pid = job.profile_id
    client.ensure_fresh(session)
    if job.outbox.get("profile"):
        client.upsert(session, "profiles", [_profile_row(job.outbox["profile"])])
    for rec in job.outbox.get("results", ()):
        client.rpc(session, "submit_session", {"p_session": session_payload(rec, pid)})
        job.uploaded.append(rec["uid"])

    since = (_parse_time(job.cursor) - CURSOR_OVERLAP).isoformat() if job.cursor else None
    newest = [job.cursor] if job.cursor else []
    pulled = {"profile": None, "results": []}

    flt = {"id": f"eq.{cloud_id(pid)}"}
    if since:
        flt["updated_at"] = f"gte.{since}"
    rows = client.select_all(session, "profiles", flt)
    if rows:
        row = rows[0]
        pulled["profile"] = {
            "name": row.get("name"), "avatar": row.get("avatar") or {}, "subjects": row.get("subjects") or [],
            "targets": row.get("targets") or {}, "exam_date": row.get("exam_date"),
            "updated_at": to_local_time(row["updated_at"]),
        }
        newest.append(row["updated_at"])

    meta_rows = client.select_all(session, "profile_meta", {"profile_id": f"eq.{cloud_id(pid)}"}, order="profile_id.asc")
    meta = meta_rows[0].get("data") if meta_rows else None

    flt = {"profile_id": f"eq.{cloud_id(pid)}", "status": "eq.finished"}
    if since:
        flt["updated_at"] = f"gte.{since}"
    sessions = client.select_all(session, "sessions", flt)
    newest.extend(r["updated_at"] for r in sessions)
    fresh = [r for r in sessions if local_id(r["id"]) not in job.known and local_id(r["id"]) not in job.uploaded]
    for i in range(0, len(fresh), ID_CHUNK):
        chunk = fresh[i:i + ID_CHUNK]
        ids = f"in.({','.join(r['id'] for r in chunk)})"
        subj = client.select_all(session, "session_subjects", {"session_id": ids}, order="session_id.asc,subject.asc")
        answers = client.select_all(session, "session_answers", {"session_id": ids, "is_correct": "is.false"},
                                    order="session_id.asc,subject.asc,question_no.asc")
        for row in chunk:
            pulled["results"].append(result_from_cloud(
                row, [s for s in subj if s["session_id"] == row["id"]], [a for a in answers if a["session_id"] == row["id"]]))
    cursor = max(newest, key=_parse_time) if newest else None
    return SyncOutcome(session, pulled, cursor, meta)


def commit(store, job, outcome):
    """Marks uploads as done, stores downloads, the cursor and server metadata (main thread).

    Returns how many local rows changed.
    """
    pid = job.profile_id
    link = get_link(store, pid)
    if not link or (link.get("session") or {}).get("user_id") != job.session.user_id:
        return 0  # signed out or switched account while the round was running
    store.sync_ack(pid, job.outbox)
    changed = store.sync_apply(pid, outcome.pulled)
    link.update(session=outcome.session.to_dict(), cursor=outcome.cursor,
                last_sync=datetime.now().isoformat(timespec="seconds"), last_error=None)
    if outcome.meta is not None:
        link["meta"] = outcome.meta
    _save_link(store, pid, link)
    return changed


def fail(store, job, exc):
    """After a failed exchange: keep the renewed session, mark trainings uploaded before the error."""
    if job.uploaded:
        store.sync_ack(job.profile_id, {"results": job.outbox.get("results", [])}, uploaded_results=job.uploaded)
    remember_session(store, job.profile_id, getattr(exc, "cloud_session", None) or job.session, error=str(exc))


def sync_profile(store, client, profile_id):
    """One full sync round on the calling thread; returns (uploaded trainings, changed locally) or None."""
    job = prepare(store, profile_id)
    if job is None:
        return None
    try:
        outcome = exchange(client, job)
    except Exception as exc:
        fail(store, job, exc)
        raise
    return len(job.uploaded), commit(store, job, outcome)
