"""Minimal JSON-over-HTTPS client on urllib (no third-party HTTP library needed).

Certificates: python.org builds on macOS ship without a CA store until
"Install Certificates.command" is run, so the context falls back to `certifi`
when installed and then to the macOS system root certificates.
"""

import json
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT = 20

_ssl_context = None


class CloudError(RuntimeError):
    """A cloud request failed. `message` is safe to show the user (Ukrainian)."""

    def __init__(self, message, status=None, code=None, detail=None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.detail = detail


class NetworkError(CloudError):
    """No connection to the server (offline, DNS, TLS, timeout)."""


def _macos_system_roots():
    try:
        pem = subprocess.run(
            ["/usr/bin/security", "find-certificate", "-a", "-p",
             "/System/Library/Keychains/SystemRootCertificates.keychain"],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return pem if "BEGIN CERTIFICATE" in pem else None


def ssl_context():
    global _ssl_context
    if _ssl_context is not None:
        return _ssl_context
    ctx = ssl.create_default_context()
    try:
        import certifi

        ctx.load_verify_locations(certifi.where())
    except Exception:
        if sys.platform == "darwin" and not ctx.cert_store_stats().get("x509_ca"):
            pem = _macos_system_roots()
            if pem:
                ctx.load_verify_locations(cadata=pem)
    _ssl_context = ctx
    return ctx


def _error_message(status, body):
    """(code, readable detail) from a Supabase / PostgREST error body."""
    if isinstance(body, dict):
        code = body.get("error_code") or body.get("code") or body.get("error")
        detail = body.get("msg") or body.get("message") or body.get("error_description") or body.get("error")
        return (str(code) if code is not None else None), (str(detail) if detail else None)
    return None, (body[:300] if isinstance(body, str) and body else None)


def request(method, url, headers=None, params=None, body=None, timeout=TIMEOUT):
    """Sends a request; returns the decoded JSON body (None when empty). Raises CloudError."""
    if params:
        url = f"{url}?{urllib.parse.urlencode(params, safe=',.:()*')}"
    data = None
    hdrs = {"Accept": "application/json"}
    hdrs.update(headers or {})
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    context = ssl_context() if url.startswith("https://") else None
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            parsed = json.loads(raw.decode("utf-8")) if raw else None
        except ValueError:
            parsed = raw.decode("utf-8", "replace")
        code, detail = _error_message(exc.code, parsed)
        raise CloudError(f"Сервер відповів помилкою {exc.code}" + (f": {detail}" if detail else ""),
                         status=exc.code, code=code, detail=detail) from None
    except (urllib.error.URLError, OSError, ssl.SSLError) as exc:
        reason = getattr(exc, "reason", exc)
        raise NetworkError(f"Немає з’єднання з хмарою ({reason}). Перевір інтернет і спробуй ще раз.") from None
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except ValueError:
        raise CloudError("Сервер повернув незрозумілу відповідь.") from None
