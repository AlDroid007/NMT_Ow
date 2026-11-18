"""Cloud backup and sync of a profile through Supabase (no GUI imports, stdlib only).

The encrypted local database stays the main copy: the app works offline, and a
profile linked to a cloud account is synced in the background (cloud/sync.py).

* settings.py  — project URL and public key (cloud_config.json or environment);
* http.py      — small JSON-over-HTTPS client with a working certificate store;
* supabase.py  — Supabase Auth (e-mail one-time code) and the REST API (PostgREST);
* sync.py      — what is uploaded and downloaded, and the per-profile link state.

The database schema lives in supabase/migrations/ at the repository root.
"""

from .http import CloudError, NetworkError  # noqa: F401
from .settings import CloudSettings, load_settings  # noqa: F401


def is_configured():
    """True when a Supabase project is set up for this build (cloud features are shown)."""
    return load_settings() is not None
