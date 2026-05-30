"""
Persistent user settings, stored at %APPDATA%/Scores/settings.json.
"""

import json
import os
from pathlib import Path

_SETTINGS_DIR = Path(os.environ.get('APPDATA', Path.home())) / 'Scores'
_SETTINGS_FILE = _SETTINGS_DIR / 'settings.json'

_DEFAULTS = {
    'default_view_mode': 0,          # 0=Table, 1=Quick List, 2=Full List
    'auto_refresh_interval': '1 minute',
    'sport_order': [],               # [] = use API default order
    'sport_visibility': {},          # {} = all visible
}

_cache: dict | None = None


def _load() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    try:
        if _SETTINGS_FILE.exists():
            with open(_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                _cache = json.load(f)
        else:
            _cache = {}
    except Exception:
        _cache = {}
    return _cache


def get(key: str, default=None):
    if default is None:
        default = _DEFAULTS.get(key)
    return _load().get(key, default)


def set(key: str, value) -> None:
    data = _load()
    data[key] = value
    try:
        _SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f'[WARNING] Failed to save settings: {e}')
