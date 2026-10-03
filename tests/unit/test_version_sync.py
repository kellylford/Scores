"""One version for both apps.

A v* tag releases Windows (scores.yml) and uploads iOS to TestFlight
(ios-release.yml). The iOS workflow sets the marketing version from VERSION at
build time, but the iOS project files carry it too, for local Xcode builds.
This fails as soon as any of them drift, rather than when a release does.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from version import __version__  # noqa: E402


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


VERSION = read("VERSION").strip()


def test_version_file_matches_version_py():
    assert VERSION == __version__


def test_ios_project_yml_matches():
    found = re.findall(r"MARKETING_VERSION:\s*([0-9.]+)", read("iOS", "SportsScoresApp", "project.yml"))
    assert found and set(found) == {VERSION}


def test_ios_xcode_project_matches():
    pbx = read("iOS", "SportsScoresApp", "SportsScores.xcodeproj", "project.pbxproj")
    found = re.findall(r"MARKETING_VERSION = ([0-9.]+);", pbx)
    assert found and set(found) == {VERSION}
