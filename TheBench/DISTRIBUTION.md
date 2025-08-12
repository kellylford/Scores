# Sports Scores Application - Distribution Guide

This document lists the minimal set of files required to distribute and run the desktop application, along with a dependency graph for maintainers and packagers.

## Essential Files for Distribution

### Top-Level Files
- `scores.py`                # Main application logic and entry point
- `espn_api.py`              # ESPN API integration
- `exceptions.py`            # Error handling
- `accessible_table.py`      # Table widgets for accessible UI
- `requirements.txt`         # Python dependencies

### Submodules
- `services/api_service.py`  # API service abstraction
- `models/game.py`           # Game data model
- `models/news.py`           # News data model
- `models/standings.py`      # Standings data model

### Third-Party Dependencies
- PyQt6
- Standard Python libraries (sys, os, datetime, typing, webbrowser)

### Optional (only if referenced in code)
- `native_accessible_table.py` (for advanced accessibility)

### Not Required
- All test files (`test_*.py`)
- All documentation (`*.md` except this one)
- All sample data (`*.json`)
- All web files (`web_app/`)
- All `.spec` files (PyInstaller configs)
- All demo/example files

## Directory Structure for Distribution

```
Scores/
├── scores.py
├── espn_api.py
├── exceptions.py
├── accessible_table.py
├── requirements.txt
├── services/
│   └── api_service.py
├── models/
│   ├── game.py
│   ├── news.py
│   └── standings.py
└── LICENSE
```

## Dependency Graph

```
scores.py
├── espn_api.py
├── exceptions.py
├── accessible_table.py
├── services/api_service.py
│   └── espn_api.py
├── models/game.py
├── models/news.py
├── models/standings.py
└── requirements.txt
```

- `scores.py` is the main entry point and imports all other modules.
- `espn_api.py` is used for all ESPN API calls and may be used by `api_service.py`.
- `exceptions.py` provides custom error classes used throughout the app.
- `accessible_table.py` provides table widgets for UI.
- `services/api_service.py` abstracts API calls and may import `espn_api.py`.
- `models/game.py`, `models/news.py`, `models/standings.py` define data structures for each type of data.
- `requirements.txt` lists all Python dependencies (PyQt6, etc.).

## Notes
- If you add new sports, create new modules in `models/` and update imports accordingly.
- For packaging, use PyInstaller or similar tools with this minimal set.
- For distribution, include the LICENSE file.

---
This guide ensures maintainers and packagers know exactly which files are required for a clean, working distribution of the desktop application.
