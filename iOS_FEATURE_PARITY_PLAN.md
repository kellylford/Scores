# iOS App Feature Parity Plan
**Date:** February 25, 2026  
**Status:** Draft — working document  
**Scope:** Full audit of Python app features → gap analysis → implementation roadmap for iOS

---

## Executive Summary

The Python app is a mature, feature-complete product. The iOS app is a skeleton. It has sport selection, a scores list, a mostly-working game detail view, standings (URL just fixed), and the MLB pitch play-by-play system. That's roughly 15% of the feature surface. The remaining 85% includes date navigation, all news features, team schedules, venues, statistics, rankings/polls, drives (NFL), injuries in context, betting odds, live all-sports feed, notifications, and six missing or broken sports. Several things that appear to "work" are actually broken for non-current-day or non-current-season data.

This document is organized as: (1) complete feature inventory by category, (2) current iOS status for each, (3) concerns and open questions, (4) implementation plan with sequencing.

---

## Part 1: Complete Python App Feature Inventory

### Sports / Leagues Supported

| League | Python | iOS | Notes |
|--------|--------|-----|-------|
| MLB | ✅ Full | ✅ Partial | Game detail broken for past games; stats API missing |
| NFL | ✅ Full | ✅ Partial | Drives view missing; week nav missing; past games broken |
| NBA | ✅ Full | ⚠️ Partial | Season year format (year+1) may be wrong |
| NHL | ✅ Full | ⚠️ Partial | OTL in standings missing |
| NCAAF | ✅ Full | ⚠️ Partial | Week nav missing; bowls/playoffs missing; polls missing |
| NCAAM | ✅ Full | ⚠️ Partial | Polls missing |
| NCAAWB | ✅ Full | ⚠️ Partial | Polls missing |
| WNBA | ✅ Full | ❌ Missing | Not in Sport enum at all |
| NCAAH | ✅ Full | ❌ Missing | Not in Sport enum; ESPN data is incomplete anyway |
| NCAAWH | ✅ Full | ❌ Missing | Not in Sport enum |
| Soccer (EPL) | ✅ Basic | ❌ Missing | Python treats it generically; reasonable to defer |

---

### Navigation and Date/Season Control

| Feature | Python | iOS |
|---------|--------|-----|
| Previous Day / Next Day | ✅ | ❌ Missing completely |
| Go to Date (date picker) | ✅ Month/Day/Year picker, Ctrl+G | ❌ Missing |
| Previous Week / Next Week (football) | ✅ | ❌ Missing |
| Current week auto-detect (football) | ✅ Via calendar API | ❌ Missing |
| Season year selector on scores view | ✅ (team schedules) | ❌ Missing |
| Back navigation history | ✅ view_stack list | ✅ NavigationStack |
| Postseason / seasontype switching | ✅ | ❌ Missing — critical bug for past games |

**Critical bug:** The Super Bowl and any past playoff/postseason game fails because the iOS app always requests `seasontype=2` (regular season). The ESPN summary API works fine; the scoreboard request needs `seasontype=3` for postseason. The iOS app has no concept of season type at all.

---

### Scores / Live View

| Feature | Python | iOS |
|---------|--------|-----|
| Live scores — all sports combined view | ✅ `LiveScoresView` | ✅ `LiveScoresView` (exists, unclear quality) |
| Per-sport scores for a given date | ✅ | ✅ `ScoresView` |
| Section headers: LIVE / UPCOMING / COMPLETED | ✅ Color-coded | ⚠️ Partial |
| Per-league sub-headers in live view | ✅ | Unknown |
| Score change monitoring (Alt+M) | ✅ Per-game toggle | ❌ Missing |
| Auto-refresh with interval selector | ✅ 30s/1m/2m/Manual | ⚠️ Unclear |
| Live game situation: base runners, count, outs | ✅ MLB only | ❌ Missing from scores list |
| Live game situation: down/distance/red zone | ✅ NFL only | ❌ Missing from scores list |
| Local notifications on score change | ✅ Windows UIA; `winsound` | ❌ Missing (iOS: UNUserNotificationCenter) |

---

### Game Detail View

| Feature | Python | iOS |
|---------|--------|-----|
| Teams, score, game time, status | ✅ | ✅ |
| Venue (city, state, name) | ✅ | ❌ Not shown |
| Officials list | ✅ Press Enter → dialog | ❌ Missing |
| Betting line, over/under | ✅ | ❌ Missing |
| TV broadcast | ✅ | ❌ Missing |
| Injuries (count → drill-down table) | ✅ | ❌ Missing |
| Box score — batting stats per player | ✅ Player-level | ⚠️ Team-level only |
| Box score — pitching stats per player | ✅ Player-level | ⚠️ Team-level only |
| Leaders (per team, by category) | ✅ | ⚠️ Tab exists, completeness unclear |
| News (game-specific, 🎯 prefix) | ✅ | ❌ Missing |
| Play-by-play — MLB hierarchy | ✅ | ✅ Done (just fixed) |
| Play-by-play — NFL drives | ✅ `QTreeWidget` by quarter/drive | ❌ Missing — NFL plays view is flat |
| Play-by-play — NBA/NHL | ✅ Generic flat | ✅ `GenericPlaysView` |
| Drives view (NFL) | ✅ Full drive tree w/ result emoji | ❌ Missing |
| Win probability (MLB KitchenSink) | ✅ | ❌ Missing |
| Season series (MLB KitchenSink) | ✅ | ❌ Missing |
| Videos (MLB KitchenSink) | ✅ | ❌ Missing |
| Betting ATS / expert picks | ✅ | ❌ Missing |
| Game wrap-up export (HTML) | ✅ Browser | ❌ Missing (iOS: ShareSheet) |
| Configurable fields per league | ✅ `ConfigDialog` | ❌ Missing |
| F5 refresh | ✅ | ❌ Unknown |

---

### News

| Feature | Python | iOS |
|---------|--------|-----|
| League-level headlines list | ✅ `NewsDialog` | ❌ Missing |
| Open article in browser (web URL) | ✅ `webbrowser.open()` | ❌ Missing (iOS: `UIApplication.open` or `SFSafariViewController`) |
| Game-specific news with 🎯 prefix | ✅ | ❌ Missing |
| NBA/NFL/MLB/NHL news endpoint | ✅ All supported | ❌ Missing |

---

### Standings

| Feature | Python | iOS |
|---------|--------|-----|
| Basic W/L/PCT/GB/Streak | ✅ | ✅ (URL fixed) |
| Division tabs (MLB: 6, NFL: 8) | ✅ | ❌ Missing — all teams flat |
| MLB expanded: R/RA/Diff/Home/Road/Playoff%/Magic# | ✅ | ❌ Missing |
| NFL expanded: PF/PA/Diff/Div Rec/Seed/Ties | ✅ | ❌ Missing |
| NBA expanded: PPG/OppPPG/DivW%/Seed | ✅ | ❌ Missing |
| NHL expanded: OTL/Pts/GF/GA/Diff/Seed | ✅ | ❌ Missing |
| Win% with ties (NFL: W+0.5T)/(W+L+T) | ✅ | ❌ Probably wrong |
| NCAAF standings + conferences | ✅ | ⚠️ Unknown |

---

### Team Schedules

| Feature | Python | iOS |
|---------|--------|-----|
| Team schedule view (full season) | ✅ `TeamScheduleDialog` | ❌ Missing |
| Season selector (2001–current) | ✅ `QComboBox` | ❌ Missing |
| Today's game highlighted | ✅ Bold + yellow bg | ❌ Missing |
| Activate game → go to game detail | ✅ | ❌ Missing |
| MLB: 3 season types (pre/regular/post) | ✅ All fetched and merged | ❌ Missing |
| Background loading with progress | ✅ `QThread` | ❌ Missing |
| Press team name in game detail → schedule | ✅ | ❌ Missing |

---

### Venues

| Feature | Python | iOS |
|---------|--------|-----|
| Venues list for a league | ✅ `VenuesDialog` | ❌ Missing |
| Venue detail: type, surface, capacity | ✅ `VenueDetailsDialog` | ❌ Missing |
| Home teams per venue | ✅ | ❌ Missing |
| Interesting facts | ✅ | ❌ Missing |
| Venue shown in game detail | ✅ city/state | ❌ Missing |

---

### Statistics

| Feature | Python | iOS |
|---------|--------|-----|
| Team statistics per league | ✅ `StatisticsChoiceDialog` → categories | ❌ Missing |
| Player statistics per league | ✅ | ❌ Missing |
| Ranked results (1st, 2nd…) | ✅ | ❌ Missing |
| Stat definitions help (Alt+D) | ✅ | ❌ Missing |
| MLB stats: MLB Stats API, 39 categories | ✅ `statsapi.mlb.com` | ❌ Missing |
| NFL/NBA/NHL stats: ESPN API | ✅ | ❌ Missing |
| ThreadPoolExecutor parallel fetch | ✅ 10–15 workers | ❌ Missing |

---

### Rankings / Polls

| Feature | Python | iOS |
|---------|--------|-----|
| NCAAF AP Poll, Coaches Poll | ✅ `PollsDialog` | ❌ Missing |
| NCAAM polls | ✅ | ❌ Missing |
| NCAAWB polls | ✅ | ❌ Missing |
| Rank movement indicators (↑/↓/—/NR) | ✅ | ❌ Missing |

---

### Football-Specific

| Feature | Python | iOS |
|---------|--------|-----|
| Drives view: quarter → drive → plays | ✅ `QTreeWidget` | ❌ Missing |
| Drive result emoji (🏈/🥅/🔄/⚡) | ✅ | ❌ Missing |
| Red zone indicator | ✅ | ❌ Missing |
| Down/distance in score row | ✅ | ❌ Missing |
| NCAAF Bowls & Playoffs tree | ✅ By competition type | ❌ Missing |

---

### Accessibility Features

| Feature | Python | iOS |
|---------|--------|-----|
| Screen reader labels on all UI | ✅ | ✅ Good |
| AccessibleTable (3 view modes: Table/Quick/Full) | ✅ Platform-specific | ⚠️ `DataTableView` component (unclear quality) — iOS needs this for large stat tables |
| Voiceover on standings (with categories) | ⚠️ Partial | ⚠️ Partial |
| MLB pitch VoiceOver (adjust action) | ❌ Windows only | ✅ Done — better than Python |
| Score monitoring announcements | ✅ Windows UIA | ❌ Missing (iOS: post local notification) |
| Breadcrumb window/tab titles | ✅ | ❌ Navigation titles inconsistent |
| HTML export accessibility (ARIA tables) | ✅ | ❌ Missing |

---

## Part 2: Open Questions and Concerns

### 1. Past Game / Postseason Failures (HIGH PRIORITY — fix first)
The Super Bowl fails because the iOS app fetches the scoreboard with only `seasontype=2`. When a game was played in the postseason, it doesn't appear. The ESPN scoreboard API key: `seasontype=1` (preseason), `2` (regular), `3` (postseason). The fix requires:
- Detecting what season type a game belongs to
- Storing `seasontype` alongside `game_id` in the `Game` model
- Passing it through to the summary API fetch (the summary URL itself doesn't need it, but the game must be discoverable)

**Deeper issue:** The iOS app has no way to browse past dates, so past games are inaccessible even if postseason was fixed.

### 2. NFL Drives vs Plays
The Python app has both a drives tree AND a plays tree for NFL. For iOS, the current `GenericPlaysView` shows flat play-by-play. NFL drives deserve a dedicated `NFLDrivesView` that mirrors the MLB hierarchy — Quarter → Drive (result + yards) → individual plays. This is arguably more important for football than the flat plays list.

### 3. Statistics API Split
MLB statistics use `statsapi.mlb.com` (completely separate from ESPN), not ESPN's own API. ESPN's stats endpoint for other sports returns `leaders` data, not full ranked leaderboards. The Python app has separate code paths for each. On iOS, using `URLSession` to `statsapi.mlb.com` is no different technically, but the response model is completely different — it needs its own `Codable` types.

### 4. NBA Season Year Format
NBA and WNBA use year+1 format (2025-26 season = `season=2026`). The current iOS API service may be passing the wrong year. The Python app has a workaround: if early-season standings fail, fall back to teams endpoint. This needs to be replicated.

### 5. Venue Data Latency
The Python app disables enhanced venue details by default because fetching them requires per-game summary calls. On iOS, this should be lazy-loaded: venues list loads fast, tapping a venue kicks off the detail fetch. Not a concern, just needs async thinking.

### 6. Score Change Notifications
Python uses `winsound` + Windows-specific UIA. On iOS this becomes `UNUserNotificationCenter` for when the app is backgrounded, and `accessibilityAnnouncement` via `UIAccessibility.post(notification:)` when foregrounded. The monitoring pattern (Alt+M equivalent) should be a long-press or context menu on a game row.

### 7. Team Schedule Deep Linking
Python allows pressing the team name in game detail to jump to that team's schedule. This is premium UX — makes the app feel like a proper information system. Requires `NavigationLink` passing a `Team` object that triggers schedule fetch.

### 8. WNBA, NCAAH, NCAAWH
These are trivially addable to the `Sport` enum and API paths. NCAAH/NCAAWH have incomplete ESPN data (standings may show 0-0) — same as Python's known limitation. Should be added but not promised to have complete data.

### 9. Config / Per-League Feature Flags
The Python app has a `ConfigDialog` that lets users control which sections appear in game detail. On iOS this maps to Settings (app-level `UserDefaults`). Not critical for initial phases but worth designing the data architecture for from the start.

### 10. Pitch Explorer / Strike Zone Grid
The Python `PitchExplorationDialog` with 3×3 zone buttons is interesting but iOS already has `PitchMapView` which is arguably better. The iOS version should focus on the `PitchMapView` + AudioGraph + VoiceOver adjustable actions already built, rather than porting the 9-button grid literally.

---

## Part 3: Implementation Plan

### Guiding Principles
1. **Fix what's broken before adding new features.** A working app that does less is better than a broken app that does more.
2. **No dead-end UI.** Every screen needs working back navigation and error states.
3. **Data model first, views second.** Get the API models right before building views around them.
4. **Accessibility is not an afterthought.** Every view built without VoiceOver labels is incomplete.
5. **Ship phases, not features.** Each phase must result in a build that is better than the prior one across the board.

---

### Phase 1: Fix the Foundation (What's Broken Now)

These are blocking issues — the app is embarrassingly broken for anything off today's date.

**P1.1 — Date navigation on scores view**
- Add Previous/Next Day buttons to `ScoresView` for non-football sports
- Add Previous/Next Week buttons for NFL and NCAAF
- `ScoresViewModel` must hold a `currentDate: Date` and `currentWeek: Int` state
- For football: call the calendar API to resolve from today's scoreboard `week.number`
- For other sports: `dates=YYYYMMDD` query param

**P1.2 — Season type awareness**
- Add `seasonType: Int` (1/2/3) to the `Game` model
- Scoreboard API: try postseason first when a game isn't found in regular season
- Store `seasonType` in game so it can be passed to any related API calls
- This is the fix for the Super Bowl and all other playoff games

**P1.3 — Date picker modal**
- `DatePickerView` as a sheet: month wheel, day wheel, year wheel (SwiftUI `DatePicker` handles this natively)
- Accessible: `DatePicker` is natively VoiceOver-compatible with the `.graphical` or `.wheels` style

**P1.4 — Fix game detail view for all game states**
- Verify game detail loads for completed regular season, completed postseason, and in-progress games
- All three tabs (Box Score, Plays, Leaders) must not crash on empty data
- NFL plays tab currently shows nothing meaningful — wire it to the drives data at minimum for now

---

### Phase 2: Core Missing Features

**P2.1 — News**
- Add `NewsService.fetchNews(sport:) async throws -> [NewsItem]` to `ESPNAPIService`
- `NewsModel`: `headline`, `description`, `url`, `published`, `byline`
- `NewsView`: List of headlines, tap → `SFSafariViewController` (or opens Safari)
- Add "News" to the sport tab (add a 4th tab in the per-sport view alongside Scores, Standings)
- Game-specific news: add a "News" section within `GameDetailView`

**P2.2 — NFL Drives View**
- `NFLDrivesView` in `PlaysView.swift` or its own file
- Data model: `DriveGroup` (quarter, driveResult, description, yards, plays)
- Hierarchy: Quarter → Drive (collapsible, shows result emoji + yardage) → individual plays
- Drive results: 🏈 Touchdown, 🥅 Field Goal, 🔄 Turnover, ⚡ Punt, ❌ Incomplete
- Use the existing `drives` array from the summary API (it's already fetched, just not rendered)
- VoiceOver: `accessibilityLabel` on drive row = "Drive 3, Touchdown, 65 yards, 8 plays"

**P2.3 — Venue in Game Detail**
- Extract `venue.fullName`, `venue.address.city`, `venue.address.state` from `gameInfo` in summary API response
- Already in the response — just not displayed
- Add to the game header section of `GameDetailView`

**P2.4 — Betting / Broadcast in Game Detail**
- Extract `odds[0].details` (spread), `odds[0].overUnder`, `broadcasts[].names[]` from summary
- Add a collapsible "Game Info" row in `GameDetailView` (below the score header, collapsed by default)

---

### Phase 3: Standings Done Right

The current standings view is a flat list. It needs to match the Python app.

**P3.1 — Division grouping**
- Group standings results into divisions using the `children` array from the v2 standings API
- `StandingsView` becomes a `Picker`-based division selector or expandable division sections
- Divisions per league:
  - MLB: AL East/Central/West, NL East/Central/West (6 tabs)
  - NFL: AFC East/North/South/West, NFC East/North/South/West (8 tabs)
  - NBA: Atlantic/Central/Southeast, Northwest/Pacific/Southwest (6 tabs)
  - NHL: Atlantic/Metropolitan, Central/Pacific (4 tabs)

**P3.2 — Expanded stats columns**
- Toggle between basic (W/L/PCT/GB/Streak) and expanded per-sport columns
- Use the existing `Grid` from `BoxScoreView` for the table — horizontal swipe for overflow columns
- MLB: add R/RA/Diff/Home/Road/Playoff%/Magic#
- NFL: add PF/PA/Diff/Div Rec/Seed/Ties (with correct win% calculation)
- NBA: add PPG/OppPPG/Seed
- NHL: add OTL/Pts/GF/GA/Diff/Seed

---

### Phase 4: Team Schedules

**P4.1 — Team model**
- Add `Team` struct to the app (already partially in `Game.swift` as `TeamScore`)
- Add `TeamService.fetchSchedule(teamId:sport:season:) async throws -> [ScheduleGame]`
- Fetch all 3 season types (pre/regular/post) for MLB; regular only for NFL

**P4.2 — TeamScheduleView**
- Launched by tapping a team name in `GameDetailView`
- Season year picker at top
- List of games: date, opponent, home/away, score/status
- Today's game highlighted
- Tap game → `GameDetailView`

---

### Phase 5: Statistics

**P5.1 — ESPN stats (NFL/NBA/NHL)**
- Use existing leaders data from summary API — it's already being fetched
- `StatisticsView`: category list (left column or picker) → ranked results list
- Tap stat name → definition sheet (hardcode the definitions Python has)

**P5.2 — MLB Stats (MLB Stats API)**
- Separate `MLBStatsService` hitting `statsapi.mlb.com`
- 39 categories across hitting/pitching/fielding
- Parallel fetch using `async let` or `TaskGroup` for all categories at once
- `MLBStatisticsView` with section headers (Hitting / Pitching / Fielding)

---

### Phase 6: Polls and Rankings

**P6.1 — College rankings**
- `RankingsService.fetchRankings(sport:) async throws -> [Poll]`
- Polls endpoint: `{BASE_URL}/football/college-football/rankings`
- `PollsView`: Picker between AP Poll / Coaches Poll; List showing Rank/Team/Record/Points with movement indicators

---

### Phase 7: Additional Sports and Missing Features

**P7.1 — Add WNBA, NCAAH, NCAAWH to Sport enum**
- 3-line addition to `Sport.swift`
- NCAAH/NCAAWH ship with documented caveat: ESPN standings data is incomplete

**P7.2 — Score change notifications**
- `ScoreMonitor`: keeps a dict of watched game IDs → last known score
- On refresh, diff and post `UNUserNotificationCenter` notifications for backgrounded state
- `UIAccessibility.post(notification: .announcement, argument: "...")` for foreground state
- UI: long-press a game row → "Monitor this game" toggle, stored in `UserDefaults`

**P7.3 — Injuries in game detail**
- Extract `injuries[]` from summary response (it's already there in the API call)
- Display count in game detail header; tap → `InjuryDetailView` with player/position/status/type/details

**P7.4 — Officials in game detail**
- Extract `officials[]` from `gameInfo`
- Tap "Officials: N" → sheet showing ordered list of name + position

---

### Phase 8: Power Features

**P8.1 — MLB KitchenSink**
- New tab in `GameDetailView` for completed/live MLB games: "More"
- Sub-sections: Win Probability (chart, accessible as Audio Graph), Season Series, Key Articles

**P8.2 — Game wrap-up / share**
- Build summary string for a completed game (boxscore + plays summary + leaders)
- Share via `ShareLink` or `UIActivityViewController`

---

## Part 4: Files to Create / Modify

| File | Action | Phase |
|------|--------|-------|
| `Models/Sport.swift` | Add WNBA, NCAAH, NCAAWH | P7.1 |
| `Models/Game.swift` | Add `seasonType`, `venue`, `odds`, `broadcasts`, `drives` | P1.2 / P2.2 |
| `Models/News.swift` | Create | P2.1 |
| `Models/Standings.swift` | Add division grouping, expanded stat fields | P3.1 |
| `Services/ESPNAPIService.swift` | Date params, season type, news, drives, injuries, officials | Multiple |
| `Services/MLBStatsService.swift` | Create | P5.2 |
| `ViewModels/ScoresViewModel.swift` | Add `currentDate`, `currentWeek`, `seasonType` | P1.1 |
| `ViewModels/StandingsViewModel.swift` | Division grouping, expanded columns | P3.1 |
| `ViewModels/NewsViewModel.swift` | Create | P2.1 |
| `ViewModels/TeamScheduleViewModel.swift` | Create | P4.1 |
| `ViewModels/StatisticsViewModel.swift` | Create | P5.1 |
| `Views/ScoresView.swift` | Date/week navigation controls | P1.1 |
| `Views/GameDetailView.swift` | Venue, odds, broadcasts, injuries, officials, drives tab | P2 |
| `Views/PlaysView.swift` | `NFLDrivesView` | P2.2 |
| `Views/StandingsView.swift` | Division tabs, expanded columns | P3.1 |
| `Views/NewsView.swift` | Create | P2.1 |
| `Views/TeamScheduleView.swift` | Create | P4.2 |
| `Views/DatePickerView.swift` | Create | P1.3 |
| `Views/StatisticsView.swift` | Create | P5.1 |
| `Views/PollsView.swift` | Create | P6.1 |
| `Views/InjuryDetailView.swift` | Create | P7.3 |
| `Services/ScoreMonitorService.swift` | Create | P7.2 |

---

## Part 5: What Will NOT Be Ported

| Python Feature | Reason |
|----------------|--------|
| `winsound` / Windows UIA notifications | Platform-specific; iOS has better equivalents already called out above |
| HTML Game Wrap Up export | Replace with native `ShareLink` in Phase 8; HTML is browser-specific hack |
| `ESPNTextProcessor` control-char placeholders | ESPN API format; same resolution needed on iOS, but implement inline |
| `KitchenSinkDialog` UI layout | Concept ported; specific PyQt6 tab dialog is non-applicable |
| AccessibleTable 3-mode toggle (Table/Quick/Full) | Evaluate whether iOS SwiftUI `Grid` + `List` already covers this; if VoiceOver users need it, implement as accessibility-only setting |
| Soccer / EPL | Defer until all major sports done |
| `PitchExplorationDialog` 3×3 button grid | `PitchMapView` AudioGraph is already superior for VoiceOver |
| Background `QThread` loading pattern | iOS `async/await` is cleaner; not a port, already the iOS pattern |

---

## Part 6: Risk Register

| Risk | Severity | Mitigation |
|------|----------|------------|
| ESPN API changes / undocumented fields | High | Unit tests against cached API responses (`tests/fixtures/`) |
| statsapi.mlb.com rate limits | Medium | Cache responses 5 min; show stale data with timestamp |
| NFL drives array structure differs from plays | Medium | Audit live NFL game API response before building drive view |
| NBA season year off-by-one | Medium | Verify current season year at launch; store correct year |
| NCAAH standings always show 0-0 | Low | Document in-app; show "Standings unavailable" message |
| Super Bowl / postseason game ID lookup | High | Test manually with Super Bowl game ID; fix season type detection |
| Score monitoring battery drain | Medium | Minimum refresh interval 60s when monitoring; stop timer when app backgrounded and switch to push-style if possible |
| `drives[]` present for NFL but what about empty games? | Medium | Guard all collections; show "No drives available" fallback |

---

## Recommended Execution Order

1. **Phase 1** — Fix the broken stuff. Nothing matters if games don't load.
2. **Phase 2.1** — News. High visibility, relatively simple, makes the app feel real.
3. **Phase 2.2** — NFL Drives. Football is huge; football users need drives, not just flat plays.
4. **Phase 3** — Standings with divisions. The current flat list is embarrassing.
5. **Phase 4** — Team schedules. Deep-link from game detail to team — makes navigation feel connected.
6. **Phase 2 remainder** — Venue, Betting, Game info in detail.
7. **Phase 5** — Statistics. Complex but valuable.
8. **Phase 6** — Polls. NCAAF audience expects rankings.
9. **Phase 7** — Notifications, injuries, officials, missing sports.
10. **Phase 8** — Power features and polish.

Every phase ends with: (a) `xcodegen generate`, (b) full iOS Simulator build, (c) manual VoiceOver spot-check, (d) commit + push.
