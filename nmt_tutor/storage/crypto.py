"""AES-256-GCM encryption of stored records (package `cryptography`).

Blob layout: 1 byte format version | 12 byte random nonce | ciphertext + 16 byte tag.
The associated data (AAD) binds a blob to its table, so blobs cannot be swapped
between tables without failing authentication.
"""

import json
import os

FORMAT_VERSION = 1
NONCE_SIZE = 12
KEY_SIZE = 32

INSTALL_HINT = "python3 -m pip install cryptography"


class CryptoUnavailableError(RuntimeError):
    """The `cryptography` package is not installed."""


class DecryptionError(RuntimeError):
    """Wrong key or tampered data."""


def _aesgcm():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise CryptoUnavailableError(
            "Для шифрування даних потрібен пакет «cryptography».\n"
            f"Встановіть його один раз командою в Терміналі:\n\n{INSTALL_HINT}"
        ) from exc
    return AESGCM


def require_cryptography():
    _aesgcm()


def generate_key():
    return os.urandom(KEY_SIZE)


class Cipher:
    def __init__(self, key):
        if not isinstance(key, (bytes, bytearray)) or len(key) != KEY_SIZE:
            raise ValueError("Encryption key must be 32 bytes.")
        self._aes = _aesgcm()(bytes(key))

    def encrypt(self, plaintext, aad):
        nonce = os.urandom(NONCE_SIZE)
        return bytes([FORMAT_VERSION]) + nonce + self._aes.encrypt(nonce, plaintext, aad)

    def decrypt(self, blob, aad):
        blob = bytes(blob)
        if len(blob) < 1 + NONCE_SIZE + 16 or blob[0] != FORMAT_VERSION:
            raise DecryptionError("Unknown encrypted record format.")
        nonce = blob[1:1 + NONCE_SIZE]
        try:
            return self._aes.decrypt(nonce, blob[1 + NONCE_SIZE:], aad)
        except Exception as exc:  # cryptography raises InvalidTag
            raise DecryptionError("Record cannot be decrypted with this key.") from exc

    def encrypt_json(self, obj, aad):
        return self.encrypt(json.dumps(obj, ensure_ascii=False).encode("utf-8"), aad)

    def decrypt_json(self, blob, aad):
        return json.loads(self.decrypt(blob, aad).decode("utf-8"))
