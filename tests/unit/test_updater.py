"""Tests for the in-app update check (services/updater.py).

The release feed is faked rather than fetched: these cover the version
comparison, tag filtering and asset selection, which is where a wrong answer
means either nagging users about an update they already have or never telling
them about one at all.
"""

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services import updater  # noqa: E402


class TestIsNewer:
    def test_higher_patch_is_newer(self):
        assert updater.is_newer("0.8.1", "0.8.0")

    def test_higher_minor_is_newer(self):
        assert updater.is_newer("0.9.0", "0.8.9")

    def test_same_version_is_not_newer(self):
        assert not updater.is_newer("0.8.0", "0.8.0")

    def test_older_is_not_newer(self):
        assert not updater.is_newer("0.7.9", "0.8.0")

    def test_short_and_long_forms_compare_equal(self):
        # 0.8 and 0.8.0 are the same release written two ways.
        assert not updater.is_newer("0.8", "0.8.0")
        assert not updater.is_newer("0.8.0", "0.8")

    def test_double_digit_segments_compare_numerically(self):
        # The failure a string comparison would make: "0.10.0" < "0.9.0".
        assert updater.is_newer("0.10.0", "0.9.0")
        assert not updater.is_newer("0.9.0", "0.10.0")


class TestReleaseVersion:
    def test_v_prefixed_tag(self):
        assert updater._release_version("v0.8.0") == "0.8.0"

    def test_tag_without_prefix_is_ignored(self):
        assert updater._release_version("0.8.0") is None

    def test_non_version_v_tag_is_ignored(self):
        # A tag that merely starts with a v must not be read as a release.
        assert updater._release_version("venue-fix") is None

    def test_empty_tag(self):
        assert updater._release_version("") is None


def _release(tag, assets=(), draft=False, prerelease=False, body=""):
    return {
        "tag_name": tag,
        "draft": draft,
        "prerelease": prerelease,
        "body": body,
        "assets": [{"name": n, "browser_download_url": f"https://example.test/{n}"}
                   for n in assets],
    }


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def _check(releases, current="0.8.0"):
    with patch.object(updater.requests, "get", return_value=_FakeResponse(releases)):
        return updater.check_for_update(current_version=current)


class TestCheckForUpdate:
    def test_newer_release_returns_setup_asset(self):
        info = _check([_release("v0.9.0", ["Scores-0.9.0-Setup.exe", "Scores.exe"],
                                body="Notes here")])
        assert info["version"] == "0.9.0"
        assert info["url"].endswith("Scores-0.9.0-Setup.exe")
        assert info["notes"] == "Notes here"

    def test_same_version_returns_none(self):
        assert _check([_release("v0.8.0", ["Scores-0.8.0-Setup.exe"])]) is None

    def test_older_release_returns_none(self):
        assert _check([_release("v0.7.0", ["Scores-0.7.0-Setup.exe"])]) is None

    def test_drafts_and_prereleases_are_ignored(self):
        releases = [
            _release("v1.0.0", ["Scores-1.0.0-Setup.exe"], draft=True),
            _release("v0.9.9", ["Scores-0.9.9-Setup.exe"], prerelease=True),
        ]
        assert _check(releases) is None

    def test_highest_version_wins_regardless_of_feed_order(self):
        releases = [
            _release("v0.8.5", ["Scores-0.8.5-Setup.exe"]),
            _release("v0.10.0", ["Scores-0.10.0-Setup.exe"]),
            _release("v0.9.0", ["Scores-0.9.0-Setup.exe"]),
        ]
        assert _check(releases)["version"] == "0.10.0"

    def test_release_without_installer_asset_has_no_url(self):
        # The caller falls back to opening the downloads page.
        info = _check([_release("v0.9.0", ["Scores.exe"])])
        assert info["version"] == "0.9.0"
        assert info["url"] is None

    def test_empty_feed_returns_none(self):
        assert _check([]) is None

    def test_api_failure_propagates(self):
        # A failed check must not read as "up to date".
        with patch.object(updater.requests, "get", side_effect=RuntimeError("offline")):
            with pytest.raises(RuntimeError):
                updater.check_for_update(current_version="0.8.0")
