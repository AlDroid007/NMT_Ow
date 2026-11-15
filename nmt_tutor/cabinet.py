"""Personal cabinet numbers computed from stored session results (no UI, no storage).

Input is the list from Repository.list_results() (oldest first); each result has
"subjects": [compute_subject_summary(...)] — see engine.build_session_result.
Mistake-practice sessions only repeat wrong answers, so they are left out of the
score statistics and the chart but still count for weak topics.
"""

from datetime import datetime

from .config import SUBJECTS_CONFIG, SUBJECTS_ORDER
from .profiles import target_for

RECENT_WINDOW = 3          # sessions in the "recent level" average
WEAK_DECAY = 0.85          # weight of a mistake per session it is older
WEAK_HISTORY = 12          # sessions per subject looked at for weak topics

MODE_TITLES = {
    "tutor": "Із Совою",
    "exam": "Режим іспиту",
    "drill": "Робота над помилками",
    "focus": "Тема",
}


def _scored(results):
    return [r for r in results if not r.get("mistake_drill")]


def _entries(results, subject_id):
    """(result, subject summary) pairs of one subject, oldest first."""
    out = []
    for res in results:
        for s in res.get("subjects", []):
            if s.get("subject") == subject_id:
                out.append((res, s))
    return out


def _mean(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values)) if values else None


def subject_stats(results, subject_id, profile=None):
    """Numbers for one subject card."""
    entries = _entries(_scored(results), subject_id)
    scores = [s.get("nmt_200") for _r, s in entries]
    earned = sum(s.get("earned", 0) for _r, s in entries)
    total = sum(s.get("actual_max", 0) for _r, s in entries)
    passed = [v for v in scores if v is not None]
    recent = _mean(scores[-RECENT_WINDOW:]) if passed else None
    before = _mean(scores[-2 * RECENT_WINDOW:-RECENT_WINDOW]) if len(scores) > RECENT_WINDOW else None
    target = target_for(profile, subject_id) if profile else None
    return {
        "subject": subject_id,
        "name": SUBJECTS_CONFIG[subject_id]["name"],
        "sessions": len(entries),
        "failed": len(scores) - len(passed),
        "avg": _mean(passed),
        "best": max(passed) if passed else None,
        "last": scores[-1] if scores else None,
        "recent": recent,
        "trend": (recent - before) if recent is not None and before is not None else None,
        "accuracy": round(100 * earned / total) if total else None,
        "drills_done": sum(s.get("drills_done", 0) for _r, s in _entries(results, subject_id)),
        "target": target,
        "gap": (target - recent) if target is not None and recent is not None else None,
        "last_at": entries[-1][0].get("created_at") if entries else None,
    }


def cabinet_subjects(results, profile=None):
    """Subjects shown in the cabinet: the profile's own plus any with results, in NMT order."""
    wanted = set((profile or {}).get("subjects") or [])
    for res in results:
        for s in res.get("subjects", []):
            wanted.add(s.get("subject"))
    return [sid for sid in SUBJECTS_ORDER if sid in wanted]


def progress_series(results, subject_id):
    """Chart points, oldest first: {"at", "nmt_200" (None = below threshold), "accuracy"}."""
    points = []
    for res, s in _entries(_scored(results), subject_id):
        mx = s.get("actual_max") or 0
        points.append({
            "at": res.get("created_at"),
            "nmt_200": s.get("nmt_200"),
            "accuracy": round(100 * s.get("earned", 0) / mx) if mx else None,
        })
    return points


def weak_topics(results, subjects=None, limit=8):
    """Sections with the most mistakes; recent sessions weigh more.

    Returns [{"subject", "subject_name", "section", "mistakes", "score"}], worst first.
    """
    subjects = subjects or SUBJECTS_ORDER
    scores = {}
    for sid in subjects:
        entries = _entries(results, sid)[-WEAK_HISTORY:]
        for age, (_res, s) in enumerate(reversed(entries)):
            weight = WEAK_DECAY ** age
            for section, cnt in (s.get("weak_sections") or {}).items():
                item = scores.setdefault((sid, section), {"subject": sid, "subject_name": SUBJECTS_CONFIG[sid]["name"],
                                                          "section": section, "mistakes": 0, "score": 0.0})
                item["mistakes"] += cnt
                item["score"] += cnt * weight
    ranked = sorted(scores.values(), key=lambda x: (-x["score"], -x["mistakes"], x["subject_name"], x["section"]))
    for item in ranked:
        item["score"] = round(item["score"], 2)
    return ranked[:limit]


def session_mode(result):
    if result.get("mistake_drill"):
        return "drill"
    if result.get("focus_section"):
        return "focus"
    return "tutor" if result.get("tutor_mode") else "exam"


def history(results, limit=None):
    """Rows for the history list, newest first."""
    rows = []
    for res in reversed(results):
        mode = session_mode(res)
        title = MODE_TITLES[mode]
        if mode == "focus":
            title = f"Тема: {res['focus_section']}"
        rows.append({
            "id": res.get("id"),
            "at": res.get("created_at"),
            "mode": mode,
            "title": title,
            "report_id": res.get("report_id"),
            "subjects": [
                {"subject": s.get("subject"), "name": SUBJECTS_CONFIG.get(s.get("subject"), {}).get("name", s.get("subject")),
                 "nmt_200": s.get("nmt_200"), "earned": s.get("earned"), "actual_max": s.get("actual_max")}
                for s in res.get("subjects", [])
            ],
        })
        if limit and len(rows) >= limit:
            break
    return rows


def format_when(iso):
    """'15.11.2026 21:40' from an ISO timestamp."""
    try:
        return datetime.fromisoformat(iso).strftime("%d.%m.%Y %H:%M")
    except (TypeError, ValueError):
        return iso or ""
