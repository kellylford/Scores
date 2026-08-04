"""In-app update check via GitHub Releases (mirrors WeatherFast's update feed).

Reads the repository's releases, compares the newest `v<semver>` tag to the
running version and — when newer — downloads the installer asset and launches
it. The app then exits so the per-user installer can replace files without
elevation.

Only meaningful for a frozen (PyInstaller) build; running from source there is
nothing for an installer to replace, so the caller gates the automatic check on
``is_frozen()``. A manual check still works from source and reports honestly.
"""

import os
import re
import sys
import tempfile

import requests

from version import __version__

GITHUB_REPO = "kellylford/Scores"
RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases?per_page=30"
RELEASES_PAGE = f"https://github.com/{GITHUB_REPO}/releases/latest"
# Windows releases are tagged `v<semver>` (e.g. v0.8.0).
TAG_PREFIX = "v"

_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": f"Scores/{__version__}",
}


def hold_app_mutex():
    """Create and hold the named mutex the installer looks for.

    installer/scores.iss declares AppMutex=ScoresRunning, which lets Setup detect
    a running copy and wait for it to close instead of failing to overwrite a
    locked Scores.exe. The handle must stay alive for the life of the process, so
    callers keep the return value.
    """
    try:
        import ctypes
        return ctypes.windll.kernel32.CreateMutexW(None, False, "ScoresRunning")
    except Exception:
        return None


def _version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "")) or (0,)


def is_newer(latest, current):
    """True if `latest` is a higher version than `current`."""
    a, b = _version_tuple(latest), _version_tuple(current)
    n = max(len(a), len(b))
    a += (0,) * (n - len(a))  # zero-pad so 0.8 and 0.8.0 compare equal
    b += (0,) * (n - len(b))
    return a > b


def _release_version(tag):
    """Return the semver from a `v<semver>` tag, else None.

    Guards against tags that merely start with a letter v (e.g. `venue-fix`) by
    requiring the remainder to start with a digit.
    """
    if tag and tag.startswith(TAG_PREFIX):
        rest = tag[len(TAG_PREFIX):]
        if rest[:1].isdigit():
            return rest
    return None


def is_frozen():
    """True when running from the PyInstaller build rather than from source."""
    return getattr(sys, "frozen", False)


def is_installed():
    """True when running from the per-user install location the installer writes.

    A portable copy can still update — the installer just relocates it to
    %LocalAppData%\\Programs\\Scores — so this only exists to word the prompt
    accurately.
    """
    if not is_frozen():
        return False
    local = os.environ.get("LOCALAPPDATA") or ""
    if not local:
        return False
    target = os.path.join(local, "Programs", "Scores").lower()
    return os.path.dirname(os.path.abspath(sys.executable)).lower() == target


def check_for_update(current_version=None):
    """Return {'version', 'url', 'notes'} for the newest release if it is newer
    than the running version, else None.

    Raises on network/API failure so a manual check can report "couldn't check"
    rather than silently claiming the app is up to date.
    """
    current = current_version or __version__
    resp = requests.get(RELEASES_URL, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    releases = resp.json() or []

    best, best_ver = None, None
    for r in releases:
        if r.get("draft") or r.get("prerelease"):
            continue
        ver = _release_version(r.get("tag_name") or "")
        if not ver:
            continue
        if best is None or _version_tuple(ver) > _version_tuple(best_ver):
            best, best_ver = r, ver

    if best is None or not is_newer(best_ver, current):
        return None

    url = None
    for asset in best.get("assets", []):
        if (asset.get("name") or "").lower().endswith("setup.exe"):
            url = asset.get("browser_download_url")
            break
    return {"version": best_ver, "url": url, "notes": best.get("body") or ""}


def download_installer(url, progress=None, should_cancel=None):
    """Download the installer to a temp file and return its path.

    ``progress`` (optional) is called with (downloaded_bytes, total_bytes).
    ``should_cancel`` (optional) is polled between chunks; when it returns True
    the partial file is deleted and None is returned.
    """
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    total = int(resp.headers.get("Content-Length") or 0)
    name = os.path.basename(url) or "Scores-Setup.exe"
    path = os.path.join(tempfile.gettempdir(), name)
    done = 0
    with open(path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            if should_cancel and should_cancel():
                f.close()
                try:
                    os.remove(path)
                except OSError:
                    pass
                return None
            if chunk:
                f.write(chunk)
                done += len(chunk)
                if progress:
                    progress(done, total)
    return path


def launch_installer(path):
    """Launch the downloaded installer.

    The caller must close the app immediately afterwards: the installer waits on
    the ScoresRunning mutex (see main.py) before replacing the executable.
    """
    os.startfile(path)  # noqa: S606
