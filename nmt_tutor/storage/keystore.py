"""Storage of the data encryption key in the operating system's secret store.

- macOS: login Keychain, through the system `security` tool (no extra packages).
  The key is passed to `security` on stdin, never on the command line.
- Windows: DPAPI (CryptProtectData) via ctypes; the protected blob is kept in
  the data folder and can only be opened by the same Windows user.
- Other systems: a file readable only by the owner (weaker; no OS secret store).
- iOS (future, BeeWare): add a KeyStore subclass backed by the iOS Keychain.
"""

import os
import subprocess
import sys

from .crypto import KEY_SIZE, generate_key

SERVICE = "NMT_Tutor"
ACCOUNT = "data-encryption-key-v1"


class KeyStoreError(RuntimeError):
    pass


class KeyStore:
    def get_key(self):
        """Returns the stored key (bytes) or None if there is none yet."""
        raise NotImplementedError

    def set_key(self, key):
        raise NotImplementedError


class MemoryKeyStore(KeyStore):
    """Keeps the key in memory only (tests, fallback sessions)."""

    def __init__(self, key=None):
        self._key = key

    def get_key(self):
        return self._key

    def set_key(self, key):
        self._key = key


class MacKeychainKeyStore(KeyStore):
    SECURITY = "/usr/bin/security"
    _NOT_FOUND = 44  # errSecItemNotFound exit code of `security`

    def __init__(self, service=SERVICE, account=ACCOUNT):
        self.service = service
        self.account = account

    def get_key(self):
        proc = subprocess.run(
            [self.SECURITY, "find-generic-password", "-s", self.service, "-a", self.account, "-w"],
            capture_output=True, text=True,
        )
        if proc.returncode == self._NOT_FOUND:
            return None
        if proc.returncode != 0:
            raise KeyStoreError(f"Keychain read failed: {proc.stderr.strip()}")
        try:
            return bytes.fromhex(proc.stdout.strip())
        except ValueError as exc:
            raise KeyStoreError("Keychain item is not a valid key.") from exc

    def set_key(self, key):
        # Interactive mode reads the command from stdin, keeping the key out of `ps`.
        cmd = (
            f'add-generic-password -U -s "{self.service}" -a "{self.account}" '
            f'-l "NMT Tutor data key" -w {bytes(key).hex()}\n'
        )
        proc = subprocess.run([self.SECURITY, "-i"], input=cmd, capture_output=True, text=True)
        if proc.returncode != 0 or "error" in (proc.stderr or "").lower():
            raise KeyStoreError(f"Keychain write failed: {(proc.stderr or proc.stdout).strip()}")

    def delete_key(self):
        subprocess.run(
            [self.SECURITY, "delete-generic-password", "-s", self.service, "-a", self.account],
            capture_output=True, text=True,
        )


class WindowsDpapiKeyStore(KeyStore):
    def __init__(self, path):
        self.path = path

    @staticmethod
    def _crypt(data, protect):
        import ctypes
        from ctypes import wintypes

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

        buf = ctypes.create_string_buffer(bytes(data), len(data))
        blob_in = DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
        blob_out = DATA_BLOB()
        crypt32 = ctypes.windll.crypt32
        fn = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
        CRYPTPROTECT_UI_FORBIDDEN = 0x01
        if not fn(ctypes.byref(blob_in), None, None, None, None, CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(blob_out)):
            raise KeyStoreError("DPAPI call failed.")
        try:
            return ctypes.string_at(blob_out.pbData, blob_out.cbData)
        finally:
            ctypes.windll.kernel32.LocalFree(blob_out.pbData)

    def get_key(self):
        if not os.path.exists(self.path):
            return None
        with open(self.path, "rb") as f:
            return self._crypt(f.read(), protect=False)

    def set_key(self, key):
        protected = self._crypt(key, protect=True)
        with open(self.path, "wb") as f:
            f.write(protected)


class FileKeyStore(KeyStore):
    def __init__(self, path):
        self.path = path

    def get_key(self):
        if not os.path.exists(self.path):
            return None
        with open(self.path, "rb") as f:
            return f.read()

    def set_key(self, key):
        fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(bytes(key))


def default_keystore(key_file_path):
    if sys.platform == "darwin" and os.path.exists(MacKeychainKeyStore.SECURITY):
        return MacKeychainKeyStore()
    if sys.platform.startswith("win"):
        return WindowsDpapiKeyStore(key_file_path)
    return FileKeyStore(key_file_path)


def get_or_create_key(store):
    """Returns the existing key or creates, saves and re-reads a new one."""
    key = store.get_key()
    if key is not None:
        if len(key) != KEY_SIZE:
            raise KeyStoreError("Stored key has a wrong length.")
        return key
    key = generate_key()
    store.set_key(key)
    if store.get_key() != key:
        raise KeyStoreError("The new key could not be read back from the key store.")
    return key
