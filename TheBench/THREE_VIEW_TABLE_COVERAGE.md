# Three-View Table Coverage — iOS App

All views that support the Table / Quick List / Full List accessible table system.

---

## Core Infrastructure

| File | Role |
|---|---|
| `SportsScores/Utilities/ViewMode.swift` | `ViewMode` enum, `ViewModePicker`, `ViewModeToggleButton` (with VoiceOver announcement on mode change) |
| `SportsScores/Views/Components/AccessibleTableBridge.swift` | `AccessibleDataTable` — UIKit overlay that exposes `UIAccessibilityContainerDataTable` to VoiceOver in Table mode |
| `SportsScores/Views/Components/DataTableView.swift` | `DataTableView` generic three-view component; `StandingsTableView` (standings-specific with expand/collapse) |

---

## Views with Full Three-View Support

### Originally Implemented

| View | File | Data | Notes |
|---|---|---|---|
| Golf Leaderboard | `Views/GolfLeaderboardView.swift` | Tournament leaderboard | First implementation; reference design |
| Standings | `Views/StandingsView.swift` + `Components/DataTableView.swift` | League standings (MLB/NFL/NBA/NHL) | Expand/collapse button for advanced columns; NavigationLink to team schedule per row |

### Added April 2026

| View | File | Data | Default Mode | Table Columns |
|---|---|---|---|---|
| Scores | `Views/ScoresView.swift` | Games grouped by status (In Progress / Upcoming / Completed / Postponed) | Quick List | Away, Home, Status |
| Live Scores | `Views/LiveScoresView.swift` | Multi-sport games grouped by status and sport | Table | Away, Home, Status |
| Team Schedule | `Views/TeamScheduleView.swift` | Season schedule grouped by month | Table | Date, Opp, Result |
| Statistics | `Views/StatisticsView.swift` | League leaders by category | Table | Rank, Player, Team, Value |
| Polls / Rankings | `Views/PollsView.swift` | College rankings (AP Top 25, Coaches Poll, etc.) | Table | Rank, Team, Record, Pts |
| Golf Schedule | `Views/GolfScheduleView.swift` | Golf tour tournament calendar | Table | Tournament, Dates, Status |
| Soccer Live | `Views/SoccerLiveView.swift` | Soccer-only live scores grouped by league | Table | Away, Home, Status |
| Box Score | `Views/BoxScoreView.swift` | Player stats and team stats (all sports, per tab) | Table | Varies by sport/stat group |

---

## View-by-View Detail

### ScoresView
- **Default mode**: Quick List (preserves familiar list experience)
- **Table**: 3-column compact grid (Away | Home | Status) per status section with `AccessibleDataTable` overlay
- **Quick List**: Single-line text per game, e.g. `NYY 5 @ BOS 3 — Final`
- **Full List**: Rich `GameRow` cards with score rows, broadcast chip, venue, live situation
- **Mode picker**: Inline `ViewModePicker` above game list; `ViewModeToggleButton` in toolbar (visible only when games are loaded)

### LiveScoresView
- Table/Quick List/Full List applied per sport block within each status section
- **Full List**: Existing `CompactGameRow` cards
- `ViewModePicker` sits at the top of the scroll content; `ViewModeToggleButton` in toolbar

### TeamScheduleView
- Sections grouped by month in all three modes
- **Table**: Date | Opp | Result with NavigationLink per row and `AccessibleDataTable` overlay
- **Quick List**: `Mon Jan 8 vs LAD — W 5-3`, NavigationLink to `GameDetailView`
- **Full List**: Existing rich schedule rows with venue, today highlight, W/L color
- Year picker and `ViewModeToggleButton` both in toolbar (visible only when games are loaded)

### StatisticsView
- Previously: visual grid + `AccessibleDataTable` overlay only (no mode switching)
- **Table**: Existing visual grid with rank-color highlights + overlay
- **Quick List**: Compact HStack rows (rank · name · team · value)
- **Full List**: Per-leader cards with labeled header-value pairs
- `ViewModePicker` embedded inside `leadersList`; `ViewModeToggleButton` in toolbar

### PollsView
- **Table**: Rank | Team | Record | Pts grid with `AccessibleDataTable` overlay
- **Quick List**: `#1 Alabama 12-0 — 1550 pts`
- **Full List**: Existing `RankingRow` list with movement indicators
- Poll selector segmented control shown below content (unchanged)

### GolfScheduleView
- **Table**: Tournament | Dates | Status grid; button tap navigates to leaderboard
- **Quick List**: `Masters — Apr 8–14 [Active]`
- **Full List**: Existing grouped list with status dot, selection checkmark
- `ViewModePicker` at top of non-empty content

### SoccerLiveView
- Same architecture as `LiveScoresView`; table/quick list applied per league block
- **Full List**: Existing `CompactGameRow` cards

### BoxScoreView
- Previously: visual grid + `AccessibleDataTable` overlay only (no mode switching)
- `ViewModePicker` sits between the page tab bar and the scroll area; mode persists across tab switches
- Three page types each support all three modes:
  - **Player group** (batting, pitching, skaters, etc.): Table = horizontal scroll grid + overlay; Quick List = player name + stat pairs per row; Full List = per-player cards with each stat labeled
  - **MLB team stats** (side-by-side categories): Table = stat rows with team columns + overlay; Quick List = stat name + `ABB: value` inline; Full List = per-stat cards
  - **Flat team stats** (NFL/NBA/NHL): same three-mode pattern as MLB team stats

---

## Excluded Views (intentional)

| View | Reason |
|---|---|
| `PlaysView` / `MLBPlaysView` | Four-level hierarchy (inning → half → at-bat → pitch); not a flat table |
| `GolfHubView` | 2–3 static navigation items; no tabular data |
| `SportSelectionView` | Navigation-only list; no tabular data |
| `NewsView` | Article headlines are not naturally tabular; excluded by design |
