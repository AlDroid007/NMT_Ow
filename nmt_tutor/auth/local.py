"""Local profiles on this computer and their optional PIN lock.

The PIN only keeps other people at the same computer out of a profile; it is not
an encryption secret (all profiles share the database key from the OS key store).
It is stored as a salted PBKDF2 hash, never in clear.
"""

import hashlib
import hmac
import os
import time

from ..profiles import PROVIDER_LOCAL
from . import AuthIdentity, AuthProvider

PIN_LENGTH = 4
PIN_ITERATIONS = 120_000
MAX_ATTEMPTS = 5
LOCK_SECONDS = 30


class LocalAuth(AuthProvider):
    id = PROVIDER_LOCAL
    title = "Локальний профіль на цьому комп’ютері"
    icon = "💻"

    def sign_in(self, profile_id=None, **_kwargs):
        return AuthIdentity(provider=self.id, subject=profile_id)


def is_valid_pin(pin):
    return isinstance(pin, str) and len(pin) == PIN_LENGTH and pin.isdigit()


def hash_pin(pin):
    """PIN hash record to keep in profile["pin"]."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, PIN_ITERATIONS)
    return {"algo": "pbkdf2_sha256", "iterations": PIN_ITERATIONS, "salt": salt.hex(), "hash": digest.hex()}


def verify_pin(record, pin):
    if not record or not isinstance(pin, str):
        return False
    try:
        salt = bytes.fromhex(record["salt"])
        digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, int(record["iterations"]))
        return hmac.compare_digest(digest.hex(), record["hash"])
    except (KeyError, ValueError, TypeError):
        return False


class PinGuard:
    """Counts wrong PINs per profile; after MAX_ATTEMPTS the profile is locked for LOCK_SECONDS."""

    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self._fails = {}
        self._locked_until = {}

    def seconds_locked(self, profile_id):
        left = self._locked_until.get(profile_id, 0) - self._clock()
        return max(0, int(left + 0.999))

    def check(self, profile, pin):
        """Returns (ok, message). The message explains a wrong PIN or the lock (Ukrainian)."""
        pid = profile["id"]
        wait = self.seconds_locked(pid)
        if wait:
            return False, f"Забагато спроб. Спробуйте через {wait} с."
        if verify_pin(profile.get("pin"), pin):
            self._fails.pop(pid, None)
            return True, ""
        fails = self._fails.get(pid, 0) + 1
        if fails >= MAX_ATTEMPTS:
            self._fails.pop(pid, None)
            self._locked_until[pid] = self._clock() + LOCK_SECONDS
            return False, f"Забагато спроб. Спробуйте через {LOCK_SECONDS} с."
        self._fails[pid] = fails
        return False, f"Неправильний PIN. Залишилось спроб: {MAX_ATTEMPTS - fails}."
