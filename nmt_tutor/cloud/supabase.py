"""Supabase over plain HTTPS: Auth (e-mail one-time code, token refresh) and the REST API.

Only the endpoints the app needs:
  POST /auth/v1/otp                                send a sign-in code to an e-mail
  POST /auth/v1/verify                             exchange e-mail + code for a session
  POST /auth/v1/token?grant_type=refresh_token     renew the session
  GET/POST /rest/v1/<table>                        PostgREST select / upsert
  POST /rest/v1/rpc/<function>                     call a database function

Google / Apple sign-in will add an `id_token` grant here and give the same CloudSession.
"""

import re
import time
from dataclasses import asdict, dataclass

from . import http
from .http import CloudError

#: Renew the access token when it has less than this many seconds left.
REFRESH_MARGIN = 120
PAGE_SIZE = 500

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AuthExpiredError(CloudError):
    """The saved session can no longer be renewed: the user has to sign in again."""


@dataclass
class CloudSession:
    user_id: str
    email: str
    access_token: str
    refresh_token: str
    expires_at: float

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: data[k] for k in ("user_id", "email", "access_token", "refresh_token", "expires_at")})

    @classmethod
    def from_auth_response(cls, body):
        user = body.get("user") or {}
        expires_at = body.get("expires_at") or (time.time() + float(body.get("expires_in") or 3600))
        return cls(
            user_id=user.get("id") or "",
            email=user.get("email") or "",
            access_token=body["access_token"],
            refresh_token=body["refresh_token"],
            expires_at=float(expires_at),
        )


def normalize_email(email):
    email = (email or "").strip().lower()
    if not _EMAIL_RE.match(email):
        raise CloudError("Введи правильну адресу пошти, наприклад liza@gmail.com.")
    return email


def _auth_message(exc, action):
    code = (exc.code or "").lower()
    if isinstance(exc, http.NetworkError):
        return str(exc)
    if exc.status == 429 or "rate_limit" in code:
        return "Забагато запитів. Зачекай хвилину й спробуй ще раз."
    if action == "verify" and (exc.status in (400, 401, 403) or "otp" in code):
        return "Код неправильний або застарів. Перевір пошту чи надішли новий код."
    if action == "otp" and "signup_disabled" in code:
        return "Реєстрацію нових акаунтів у хмарі вимкнено. Звернись до адміністратора."
    return str(exc)


class SupabaseClient:
    def __init__(self, settings):
        self.url = settings.url
        self.key = settings.key

    # --- auth ------------------------------------------------------------------
    def _auth(self, path, body, params=None, action=""):
        try:
            return http.request("POST", f"{self.url}/auth/v1/{path}", headers={"apikey": self.key},
                                params=params, body=body)
        except CloudError as exc:
            raise CloudError(_auth_message(exc, action), exc.status, exc.code, exc.detail) from None

    def send_code(self, email):
        """E-mails a one-time sign-in code (the account is created on first use)."""
        self._auth("otp", {"email": normalize_email(email), "create_user": True}, action="otp")

    def verify_code(self, email, code):
        code = "".join((code or "").split())
        if not code.isdigit() or not 6 <= len(code) <= 10:
            raise CloudError("Код складається з цифр із листа (зазвичай 6).")
        body = self._auth("verify", {"type": "email", "email": normalize_email(email), "token": code}, action="verify")
        session = CloudSession.from_auth_response(body or {})
        if not session.user_id:
            raise CloudError("Сервер не повернув акаунт користувача.")
        return session

    def refresh(self, session):
        """Renews the session in place (the refresh token rotates)."""
        try:
            body = http.request("POST", f"{self.url}/auth/v1/token", headers={"apikey": self.key},
                                params={"grant_type": "refresh_token"}, body={"refresh_token": session.refresh_token})
        except http.NetworkError:
            raise
        except CloudError as exc:
            if exc.status in (400, 401, 403):
                raise AuthExpiredError("Вхід у хмару застарів. Увійди ще раз через пошту.",
                                       exc.status, exc.code, exc.detail) from None
            raise
        fresh = CloudSession.from_auth_response(body or {})
        session.access_token = fresh.access_token
        session.refresh_token = fresh.refresh_token
        session.expires_at = fresh.expires_at
        if fresh.email:
            session.email = fresh.email
        return session

    def ensure_fresh(self, session):
        if session.expires_at - time.time() < REFRESH_MARGIN:
            self.refresh(session)
        return session

    # --- REST ------------------------------------------------------------------
    def _rest(self, session, method, path, params=None, body=None, prefer=None):
        self.ensure_fresh(session)
        for attempt in (0, 1):
            headers = {"apikey": self.key, "Authorization": f"Bearer {session.access_token}"}
            if prefer:
                headers["Prefer"] = prefer
            try:
                return http.request(method, f"{self.url}/rest/v1/{path}", headers=headers, params=params, body=body)
            except CloudError as exc:
                if exc.status == 401 and attempt == 0 and not isinstance(exc, http.NetworkError):
                    self.refresh(session)
                    continue
                raise

    def select_all(self, session, table, filters=None, order="updated_at.asc,id.asc"):
        """Every row matching `filters` ({column: "op.value"}), fetched page by page."""
        rows = []
        offset = 0
        while True:
            params = {"select": "*", "order": order, "limit": PAGE_SIZE, "offset": offset}
            params.update(filters or {})
            page = self._rest(session, "GET", table, params=params) or []
            rows.extend(page)
            if len(page) < PAGE_SIZE:
                return rows
            offset += PAGE_SIZE

    def upsert(self, session, table, rows):
        """Inserts or updates rows by primary key `id`."""
        for i in range(0, len(rows), PAGE_SIZE):
            self._rest(session, "POST", table, params={"on_conflict": "id"}, body=rows[i:i + PAGE_SIZE],
                       prefer="resolution=merge-duplicates,return=minimal")

    def rpc(self, session, function, args=None):
        return self._rest(session, "POST", f"rpc/{function}", body=args or {})
