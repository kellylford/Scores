# Windows Feature Parity Plan

This document maps features present in the iOS app (as of May 2026) that are missing or incomplete in the Windows PyQt6 app, and proposes a phased implementation roadmap.

**Explicitly out of scope:** Touch-explore features (stadium terrain audio tours, interactive drag-on-canvas pitch zone). The Windows audio pitch mapper that already exists is not affected.

---

## Feature Gap Summary

| Feature | iOS | Windows | Gap |
|---|---|---|---|
| Team Favorites | Full (live situation, news, drag-reorder, persistent) | None | Missing |
| NFL Draft viewer | Full (years, rounds, live) | None | Missing |
| Transactions hub | Full (by sport + team, paginated) | None | Missing |
| Team Hub — Roster tab | Full | None | Missing |
| Team Hub — Info tab | Full (coach, venue, next game) | Partial (schedule only) | Needs expansion |
| Team Hub — Transactions tab | Full | None | Missing |
| Soccer leagues | 11 leagues | 1 (EPL only) | 10 leagues missing |
| Golf (PGA + LPGA) | Full (leaderboard, schedule, results) | None | Missing |
| Settings persistence | Full (all prefs saved) | None | Missing |
| Home sport ordering | Full (reorder + hide) | None | Missing |
| Screen reader name format | 4 options (abbrev/city/nickname/full) | None | Missing |
| Auto-refresh | Persistent, all views | Live Scores only, not saved | Partial |
| Weather in game info | Shown when available | Commented out | Easy fix |
| Polls — NCAAM/NCAAWB | Yes | Yes | Done |
| Win probability / season series | Yes | Yes | Done |
| Unified live scores | Yes | Yes | Done |
| Broadcast network display | Yes | Yes | Done |
| Odds / officials | Yes | Yes | Done |

---

## Phase 1 — Settings Persistence (Foundation)

**Why first:** Several later features (favorites, auto-refresh, name format) require a working persistence layer. Build this once so everything else can use it.

### What to implement
- Introduce a `settings.py` module wrapping Python's `json` (or `QSettings`) to load/save a settings file on disk (e.g., `%APPDATA%\Scores\settings.json`).
- Settings to expose immediately:
  - **Default table view mode** (Table / Quick List / Full List) — currently lost each session
  - **Auto-refresh interval** — currently only in Live Scores and not saved
  - **Screen reader team name format** — new (see Phase 3)
  - **Home sport order + visibility** — new (see Phase 2)
- Apply the saved default table view mode at startup so the user's preferred mode is active from the first open.

### Key files to touch
- New: `settings.py`
- `scores.py` — read settings at startup, write on change
- `accessible_table.py` — respect default view mode from settings

---

## Phase 2 — Home Page Customization & Soccer Expansion

### 2a — Home Sport Ordering and Visibility

**What to implement:**
- A Settings dialog (accessible from the main window) with a list of sports the user can reorder (drag or Up/Down buttons) and toggle visibility.
- Order and visibility stored via Phase 1 settings.
- Home screen sport list rebuilt from saved order/visibility on launch.

### 2b — Soccer Expansion (10 additional leagues)

**Current state:** Only `soccer/eng.1` (English Premier League) is defined.

**Leagues to add** (using ESPN slugs):
| League | ESPN slug |
|---|---|
| MLS | `soccer/usa.1` |
| NWSL | `soccer/usa.nwsl` |
| La Liga | `soccer/esp.1` |
| Bundesliga | `soccer/ger.1` |
| Serie A | `soccer/ita.1` |
| Ligue 1 | `soccer/fra.1` |
| UEFA Champions League | `soccer/uefa.champions` |
| UEFA Europa League | `soccer/uefa.europa` |
| Liga MX | `soccer/mex.1` |
| CONCACAF Champions Cup | `soccer/concacaf.champions` |

**What to implement:**
- Add a "Soccer" hub entry on the home screen that expands to show all soccer leagues (similar to how NCAA sports are grouped).
- Or: add them as individual entries in the sport list, optionally grouped.
- Each league already works through the existing `get_scores` / `get_standings` / `get_news` paths — this is largely a constants + UI change.

---

## Phase 3 — Team Hub Expansion

**Current state:** `TeamScheduleDialog` exists and shows a team's schedule. A `SimpleTeamsDialog` exists for browsing teams. These are entry points to expand.

### What to implement

Expand `TeamScheduleDialog` (or create a new `TeamHubDialog`) into a tabbed view with:

**Tab 1 — Info**
- Team record (overall, home, away)
- Standing position and division
- Head coach name
- Venue name and location
- Next scheduled game (opponent, date, home/away)
- ESPN endpoint: `site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams/{id}`

**Tab 2 — Roster**
- Full roster: player number, name, position, age, height/weight where available
- Accessible table with Table/Quick List/Full List modes
- ESPN endpoint: `site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams/{id}/roster`

**Tab 3 — Schedule** *(already partially exists)*
- Full season schedule: date, opponent, home/away, result/score for completed games, time for upcoming
- Existing `TeamScheduleDialog` content moves here

**Tab 4 — News**
- Team-specific headlines
- ESPN endpoint: `site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams/{id}/news`

**Tab 5 — Transactions**
- Recent player moves for this team (signings, releases, trades, injuries)
- Paginated list
- ESPN endpoint: `site.api.espn.com/apis/site/v2/sports/{sport}/{league}/transactions?team={id}`
- Note: not all sports/leagues have transaction data — handle gracefully

### Screen reader name format preference (Phase 3 addition)
Add a setting (persisted via Phase 1) for how team names are read:
- **Abbreviation** — "BOS"
- **City** — "Boston"
- **Nickname** — "Red Sox"
- **Full Name** — "Boston Red Sox"

Apply this preference wherever team names appear in accessible labels throughout the app.

---

## Phase 4 — Transactions Hub

A league-level transactions browser, separate from the per-team view in Phase 3.

### What to implement
- Entry point from the main league view (new "Transactions" tab alongside Standings, News, etc.).
- Sport + team picker at top.
- Paginated list of transactions: type (Signed/Released/Traded), player name, position, date, related teams.
- ESPN endpoint: `site.api.espn.com/apis/site/v2/sports/{sport}/{league}/transactions` (no team filter = league-wide)

**Notes:**
- NFL, NBA, NHL, MLB all have transaction data. NCAA and soccer coverage varies.
- Transactions are a natural companion to the injury tab already present in game details.

---

## Phase 5 — Team Favorites

### What to implement
- **Star icon** on team rows (in team browse, standings, team hub header) to toggle favorite status.
- **Favorites section** at top of home screen showing favorite team cards.
- Each card displays:
  - Team name + sport badge
  - If game is live: live score + situation (baseball: pitcher, batter, base runners, count, outs; other sports: period/quarter + clock)
  - Most recent completed game result
  - Next scheduled game (opponent + date)
  - Up to 2 recent news headlines (clickable)
- **Reorder:** Up/Down buttons or keyboard shortcut to change card order. VoiceOver: accessible actions (Move Up / Move Down / Move to Top / Move to Bottom).
- **Persistence:** Favorite team IDs and order saved via Phase 1 settings.
- **Refresh:** Favorite cards refresh on the same cycle as the Live Scores view.

### Dependencies
- Phase 1 (settings persistence)
- Phase 3 (team hub — cards link into team hub)
- Requires fetching live game state per team on refresh; can batch these with existing `get_live_scores_all_sports` logic

---

## Phase 6 — NFL Draft Viewer

### What to implement
- Entry point: new item in NFL league navigation (alongside Standings, News, etc.), visible during and after draft season.
- **Year selector** (dropdown or combobox) — all available draft years (2001–present).
- **Round navigation** — segmented control or tab strip (rounds 1–7).
- **Pick list:** for each pick: overall pick number, team (name + abbreviation), player name, position, college/university, any trade note (e.g., "via trade from Dallas Cowboys").
- **Live draft:** during draft weekend, picks marked TBD until announced; auto-refresh populates them.
- ESPN endpoint: `site.api.espn.com/apis/v2/sports/football/nfl/draft?season={year}`

**Notes:**
- Round 1 is the high-value view; rounds 2–7 follow same format.
- Trade provenance data is available in ESPN's draft payload and worth displaying.

---

## Phase 7 — Golf

Golf is a new sport type and the most structurally different from existing sports (no opposing teams, no play-by-play, leaderboard-centric).

### What to implement

**Golf Hub** (new home screen entry, grouped separately like Soccer):
- PGA Tour
- LPGA Tour

**Tournament View** (per tour):
- Current/featured tournament name and status
- Leaderboard with player name, score (total to par), position, today's round score
- Tabs:
  - **Leaderboard** — current standings
  - **Schedule** — upcoming tournaments with dates, location
  - **Results** — past tournament winners and scores

**Navigation:**
- Previous / Next tournament arrows (by date)
- Jump-to-date calendar picker

**ESPN endpoints:**
- Golf scoreboard: `site.api.espn.com/apis/site/v2/sports/golf/{tour}/scoreboard`
- PGA Tour slug: `pga`; LPGA slug: `lpga`
- Season calendar: ESPN Core API for golf tour schedule

**Notes:**
- Golf leaderboard format is a flat player list, not a team matchup. Will need a new view component (or adapted `accessible_table.py` subclass).
- FedEx Cup and CME Globe season-long standings are bonus additions after the core leaderboard works.
- Golf is lower priority than Phases 1–6 but included for completeness.

---

## Weather Fix (Quick Win)

Weather is already partially wired in the codebase but commented out in `scores.py` around the game info display. Re-enable it:
- ESPN returns `weather` data in game details for outdoor venues when available.
- Display temperature, condition (clear, cloudy, rain, etc.) in the game Info section.
- Suppress gracefully when not present (indoor arenas, no data).

This is a 1–2 hour fix independent of all phases.

---

## Implementation Order Recommendation

```
Phase 1 (Settings)  →  Phase 2 (Home customization + Soccer)
                    →  Phase 3 (Team Hub)  →  Phase 5 (Favorites)
                                           →  Phase 4 (Transactions Hub)
                    →  Phase 6 (NFL Draft)
                    →  Phase 7 (Golf)

Quick win: Weather fix (any time, ~1-2 hours)
```

Phases 3 and 4 share the transactions ESPN endpoint and should be built together. Phase 5 (Favorites) depends on Phase 3 (team hub) for the card → team detail link and Phase 1 for persistence. Everything else is independent.

---

## ESPN API Notes

All endpoints below use base URL `https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/` unless noted.

| Feature | Endpoint |
|---|---|
| Team info | `teams/{id}` |
| Team roster | `teams/{id}/roster` |
| Team news | `teams/{id}/news` |
| Team schedule | `teams/{id}/schedule?season={year}` |
| Transactions (team) | `transactions?team={id}` |
| Transactions (league) | `transactions` |
| NFL Draft | `https://site.api.espn.com/apis/v2/sports/football/nfl/draft?season={year}` |
| Golf scoreboard | `https://site.api.espn.com/apis/site/v2/sports/golf/{pga\|lpga}/scoreboard` |
| Golf schedule | ESPN Core API v2 golf calendar |
