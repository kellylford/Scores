"""
Version information for the Scores application.
Single source of truth for version management.
"""

__version__ = "0.55.0"
__version_info__ = (0, 55, 0)

def get_version() -> str:
    """Get the current version string."""
    return __version__

def get_version_info() -> tuple:
    """Get the current version as a tuple."""
    return __version_info__