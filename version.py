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
"""

__version__ = "0.9.8"
