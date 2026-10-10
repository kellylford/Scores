"""Single source of truth for the application version.

`scores.py` re-exports this as its `__version__`, the in-app updater compares it
against the newest GitHub release, and the release workflow refuses to build a
`v*` tag whose version does not match this string and the VERSION file. Keeping
it in its own module means the updater can read the version without importing
the whole PyQt6 UI.

One version covers both apps: a v<x.y.z> tag releases Windows and uploads the
iOS app to TestFlight at the same version. When releasing: bump here, in the
VERSION file and in the iOS project's MARKETING_VERSION, and add
docs/release-notes-v<x.y.z>.md. tests/unit/test_version_sync.py checks they agree.

A fourth part (0.9.9.1) marks a Windows-only patch release: the iOS project
keeps the three-part version it shipped at (App Store marketing versions allow
only three parts) and ios-release.yml skips the build for that tag. The next
release of both apps goes to the next three-part version.
"""

__version__ = "0.9.9.1"
