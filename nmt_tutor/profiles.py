"""User profile model (no UI, no storage): who is studying, their goals and how they sign in.

A profile is a plain JSON-friendly dict so every backend (local SQLite now, a cloud
database later) stores it the same way:

    {
      "id": "3f2c…",                       # UUID hex, stable across devices and backends
      "name": "Ліза",
      "avatar": {"kind": "emoji", "value": "🦉"},   # or {"kind": "url", "value": "https://…"}
      "subjects": ["ukrmova", "math", …],   # what the student takes
      "targets": {"math": 180, …},          # wanted NMT score 100–200 per subject
      "exam_date": "2027-05-20" | None,
      "identities": [{"provider": "local", "subject": "<id>", "email": None}, …],
      "pin": None | {PIN hash record, see auth.local},
      "created_at": "…", "updated_at": "…",
    }

`identities` holds every way to sign in to this profile. Now it is only "local";
Google and Apple sign-in will add {"provider": "google"|"apple", "subject": <the
provider's user id>, "email": …} to the same list, so an existing local profile can be
linked to an account without losing its results.
"""

import uuid
from datetime import date, datetime

from .config import SUBJECTS_CONFIG, SUBJECTS_ORDER

AVATARS = ["🦉", "🦊", "🐼", "🐱", "🐶", "🐯", "🦁", "🐸", "🐨", "🐰", "🦄", "🐙", "🐝", "🚀", "⭐", "🎧", "📚", "⚽"]
DEFAULT_AVATAR = AVATARS[0]
DEFAULT_SUBJECTS = ["ukrmova", "math", "history", "english"]
NAME_MAX = 40
SCORE_MIN, SCORE_MAX = 100, 200
DEFAULT_TARGET = 170

PROVIDER_LOCAL = "local"
PROVIDER_GOOGLE = "google"
PROVIDER_APPLE = "apple"
#: Cloud account (Supabase Auth user id); signed in with an e-mail code now, Google / Apple later.
PROVIDER_CLOUD = "cloud"


class ProfileError(ValueError):
    """Invalid profile data; the message is shown to the user (Ukrainian)."""


def _now():
    return datetime.now().isoformat(timespec="seconds")


def new_profile_id():
    return uuid.uuid4().hex


def new_profile(name, avatar=DEFAULT_AVATAR, subjects=None, targets=None, exam_date=None,
                provider=PROVIDER_LOCAL, provider_subject=None, email=None):
    """Creates a validated profile. For a local profile the identity subject is the profile id."""
    pid = new_profile_id()
    now = _now()
    profile = {
        "id": pid,
        "name": name,
        "avatar": avatar if isinstance(avatar, dict) else {"kind": "emoji", "value": avatar or DEFAULT_AVATAR},
        "subjects": list(subjects if subjects is not None else DEFAULT_SUBJECTS),
        "targets": dict(targets or {}),
        "exam_date": exam_date,
        "identities": [],
        "pin": None,
        "created_at": now,
        "updated_at": now,
    }
    link_identity(profile, provider, provider_subject or pid, email=email)
    return normalize_profile(profile)


def parse_exam_date(text):
    """Accepts 'ДД.ММ.РРРР' or 'РРРР-ММ-ДД' (or empty); returns ISO 'YYYY-MM-DD' or None."""
    text = (text or "").strip()
    if not text:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    raise ProfileError("Дату НМТ введіть у форматі ДД.ММ.РРРР, наприклад 20.05.2027.")


def format_exam_date(iso):
    if not iso:
        return ""
    try:
        return date.fromisoformat(iso).strftime("%d.%m.%Y")
    except ValueError:
        return ""


def normalize_profile(profile):
    """Validates and cleans a profile in place (raises ProfileError); returns it."""
    name = " ".join(str(profile.get("name") or "").split())
    if not name:
        raise ProfileError("Введіть ім’я.")
    if len(name) > NAME_MAX:
        raise ProfileError(f"Ім’я задовге (до {NAME_MAX} символів).")
    profile["name"] = name

    avatar = profile.get("avatar") or {}
    if avatar.get("kind") not in ("emoji", "url") or not avatar.get("value"):
        avatar = {"kind": "emoji", "value": DEFAULT_AVATAR}
    profile["avatar"] = {"kind": avatar["kind"], "value": str(avatar["value"])}

    subjects = [s for s in SUBJECTS_ORDER if s in set(profile.get("subjects") or [])]
    profile["subjects"] = subjects

    targets = {}
    for sid, score in (profile.get("targets") or {}).items():
        if sid not in SUBJECTS_CONFIG:
            continue
        try:
            score = int(score)
        except (TypeError, ValueError):
            raise ProfileError(f"Ціль для «{SUBJECTS_CONFIG[sid]['name']}» має бути числом від 100 до 200.")
        if not SCORE_MIN <= score <= SCORE_MAX:
            raise ProfileError(f"Ціль для «{SUBJECTS_CONFIG[sid]['name']}» має бути від 100 до 200.")
        targets[sid] = score
    profile["targets"] = targets

    exam = profile.get("exam_date")
    profile["exam_date"] = parse_exam_date(exam) if exam else None

    if not profile.get("identities"):
        raise ProfileError("Профіль без способу входу.")
    profile.setdefault("pin", None)
    profile.setdefault("created_at", _now())
    profile.setdefault("updated_at", profile["created_at"])
    return profile


def touch(profile):
    profile["updated_at"] = _now()
    return profile


def link_identity(profile, provider, subject, email=None):
    """Adds (or refreshes) a way to sign in to the profile."""
    ids = profile.setdefault("identities", [])
    for ident in ids:
        if ident["provider"] == provider and ident["subject"] == subject:
            if email:
                ident["email"] = email
            return ident
    ident = {"provider": provider, "subject": str(subject), "email": email}
    ids.append(ident)
    return ident


def identity(profile, provider):
    for ident in profile.get("identities", []):
        if ident["provider"] == provider:
            return ident
    return None


def avatar_text(profile):
    """Emoji to draw for the profile (image avatars fall back to the first letter)."""
    av = profile.get("avatar") or {}
    if av.get("kind") == "emoji":
        return av.get("value") or DEFAULT_AVATAR
    return (profile.get("name") or "?")[:1].upper()


def short_name(name, limit):
    """Name cut to `limit` characters with an ellipsis (for narrow buttons and tiles)."""
    return name if len(name) <= limit else name[: limit - 1].rstrip() + "…"


def has_pin(profile):
    return bool(profile.get("pin"))


def days_until_exam(profile, today=None):
    """Days left until the exam date (0 on the day, negative after it) or None."""
    iso = profile.get("exam_date")
    if not iso:
        return None
    try:
        exam = date.fromisoformat(iso)
    except ValueError:
        return None
    return (exam - (today or date.today())).days


def days_word(n):
    """Ukrainian plural of «день»."""
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        return "день"
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return "дні"
    return "днів"


def target_for(profile, subject_id):
    return (profile.get("targets") or {}).get(subject_id)
