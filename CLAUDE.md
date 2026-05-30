# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Scores** is a PyQt6 desktop application for Windows that displays live sports scores, standings, play-by-play, stats, and news. It is built with an accessibility-first philosophy — screen reader support, keyboard-only navigation, and multiple view modes are core features, not afterthoughts.

Current version: see `VERSION` file. Distributed as a standalone `Scores.exe` (~40MB) via GitHub releases.

## Commands

**Run from source:**
```powershell
.venv\Scripts\activate
python scores.py
# Or with a sport pre-selected:
python main.py --sport mlb
```

**Build executable:**
```powershell
pyinstaller Scores.spec
# Output: dist\Scores.exe
```

**Setup dev environment:**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Run tests:**
```powershell
pytest tests/
```

## Architecture

### Entry Points

- `main.py` — CLI argument parser; passes sport selection into the main window
- `scores.py` — The entire UI (9,700+ lines): `QApplication`, main window, all dialogs, all views, refresh logic, keyboard handling

### Data Layer

- `espn_api.py` (4,100+ lines) — All network calls. Fetches from ESPN's undocumented API (`site.api.espn.com/apis/site/v2/sports`) and the official MLB Stats API (`statsapi.mlb.com`). Contains per-sport logic for scores, standings, play-by-play, box scores, injuries, news, and advanced stats.
- `services/api_service.py` — Thin wrapper around `espn_api.py` with unified error handling
- `services/venue_service.py` — Stadium/venue info
- `services/football_calendar.py` — NFL week/season calendar utilities
- `models/` — `GameData`, `NewsData`, `StandingsData` dataclasses

### UI Components

- `accessible_table.py` (1,000+ lines) — Custom `QTableWidget` subclass powering every data table. Implements three view modes: **Table** (grid), **Quick List** (comma-separated), **Full List** (key: value pairs). Concrete subclasses: `StandingsTable`, `BoxscoreTable`, `InjuryTable`, `LeadersTable`.
- `pitch_exploration_dialog.py` — Interactive dialog for exploring MLB pitch coordinates with audio feedback
- `windows_notifications.py` — Windows UIA screen reader notifications

### Audio System (MLB only)

- `simple_audio_mapper.py` — Maps pitch (x, y) coordinates to audio frequencies via `winsound`
- `stereo_audio_mapper.py` — Stereo variant with left/right channel positioning for pitch location

### Utilities

- `text_utils.py` — ESPN text cleaning (strips HTML/placeholders from news content)
- `timezone_utils.py` — Converts ESPN UTC times to local timezone
- `exceptions.py` — `ApiError`, `DataModelError`

## Key Patterns

**Sports supported:** MLB, NFL, NBA, NHL, WNBA, NCAAF, NCAAM, NCAAWB, NCAAH, NCAAWH, Soccer. ESPN sport/league slugs are used as identifiers throughout (e.g., `"baseball/mlb"`, `"football/nfl"`).

**Accessibility view modes:** `accessible_table.py` controls three view modes toggled via Alt+V / Alt+T / Alt+Q / Alt+F. When modifying any table/standings/stats display, verify all three modes render correctly.

**Window titles** are set dynamically throughout `scores.py` to give screen readers hierarchical context (e.g., `"Yankees vs Red Sox - MLB - Sports Scores"`). Maintain this pattern when adding new views or dialogs.

**Play-by-play parsing** is sport-specific and lives entirely in `espn_api.py`. MLB play-by-play uses ESPN's `summaryType` field (`S`=scoring, `I`=inning marker, `N`=substitution) and has several workarounds for ESPN data quirks documented in recent commits.

**No test framework for UI** — UI correctness is verified manually. `tests/` covers data parsing and utility functions.

## Reference

- `TheBench/ESPN_API_GUIDE.md` — Comprehensive documentation of the ESPN API endpoints used
- `TheBench/TECHNICAL_GUIDE.md` — Architecture reference with more detail
- `CHANGELOG.md` — Version history
