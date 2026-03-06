# Scores Repository — Copilot Instructions

This repository contains two apps:
- **Python app** (`scores.py`, `espn_api.py`, etc.) — mature Windows desktop app using PyQt6 and the ESPN API. Treat this as the source of truth for data and behavior.
- **iOS app** (`iOS/SportsScoresApp/`) — SwiftUI app being built to parity with the Python app. Uses the same ESPN API endpoints.

## Key facts
- All sports data comes from `site.api.espn.com/apis/site/v2/sports/{sport}/{league}/...`
- Standings use a different base: `site.api.espn.com/apis/v2/sports/...`
- ESPN date strings come back **without seconds** (`"2025-03-27T19:00Z"`). Always use a multi-format date parser, never a single-format ISO8601 parser.
- MLB spring training = seasontype 1, regular = 2, postseason = 3. In February/March, default to spring training (type 1 with current year).
- NBA/WNBA use year+1 season format (2025-26 season → `season=2026`).
- Team IDs from the scoreboard endpoint are the canonical IDs to use for schedule/detail lookups.

## Before claiming something works
Run `curl` against the real ESPN API and inspect the response. Don't assume the data shape or that a feature works without seeing actual API output.
