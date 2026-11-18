"""Which Supabase project the app talks to.

Resolution order:
1. environment variables NMT_SUPABASE_URL and NMT_SUPABASE_KEY (tests, developers);
2. nmt_tutor/cloud_config.json shipped with the app:
       {"supabase_url": "https://xxxx.supabase.co", "supabase_key": "<publishable / anon key>"}

The key is the project's public (publishable / anon) key. It is meant to be shipped
inside apps: what a signed-in user may read or change is enforced by Row Level
Security in the database. Never put the secret (service_role) key here.
"""

import json
import os
from dataclasses import dataclass

from ..resources import PACKAGE_DIR

ENV_URL = "NMT_SUPABASE_URL"
ENV_KEY = "NMT_SUPABASE_KEY"
CONFIG_FILENAME = "cloud_config.json"


@dataclass(frozen=True)
class CloudSettings:
    url: str
    key: str


def config_path():
    return os.path.join(PACKAGE_DIR, CONFIG_FILENAME)


def _clean(url, key):
    url = (url or "").strip().rstrip("/")
    key = (key or "").strip()
    if not url.startswith(("https://", "http://")) or not key:
        return None
    return CloudSettings(url, key)


def load_settings():
    """CloudSettings, or None when the cloud is not set up for this build."""
    env = _clean(os.environ.get(ENV_URL), os.environ.get(ENV_KEY))
    if env:
        return env
    try:
        with open(config_path(), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return _clean(data.get("supabase_url"), data.get("supabase_key"))
