# Sports Scores iOS App — Design Principles

This is the living design reference for the Sports Scores iOS app. It captures the canonical structure, screen contracts, accessibility rules, and naming conventions. When implementing any change to display or accessibility behavior, consult this document first. When making a design decision that isn't covered here, add it here before implementing.

---

## Three View Modes

Every list or table screen in the app offers three presentation modes, selectable via `ViewModeMenuButton` (a toolbar `Menu` wrapping an inline `Picker`). The default is **Quick List**.

| Mode | Visual layout | VoiceOver label style |
|---|---|---|
| **Quick List** | Compact rows — rank / name / value on one line | Terse: `"#1 Aaron Judge NYY — .350"` — no label words |
| **Full List** | **Same visual rows as Quick List** | Verbose: `"Rank 1, Player: Aaron Judge, Team: NYY, Value: .350"` — includes field names |
| **Table** | Grid with visible column headers (Rank / Player / Team / Value) | `AccessibleDataTable` overlay handles VoiceOver |

**Critical rule:** Quick List and Full List must be visually identical. The only difference is in the `.accessibilityLabel` string attached to each row. Full List adds label words so VoiceOver users who need that context ("Rank 1, Player: …") get it; Quick List omits them for faster scanning. Table is the only mode with a different visual layout.

### Implementation pattern

- `ViewMode` enum and `ViewModeMenuButton` live in `Utilities/ViewMode.swift`.
- The shared player-leaders renderer is `LeaderCategorySection` (defined at the bottom of `Views/StatisticsView.swift`). It is reused by `StatisticsView`, `StatLeaderDetailView`, and the player sub-tab of `TeamStatsTabView`.
- Team ranking rows (in `TeamStatsTabView`) have their own three-mode rendering functions: `teamQuickList`, `teamTable`, `teamFullList`.
- Default `@State` is always `.quickList`. Views do **not** persist viewMode across sessions via `@AppStorage` — each navigation push resets to Quick List.

### Accessibility label formats

Player/leader rows (Quick List): `"#\(rank) \(athleteName)\(team) — \(value)"`  
Player/leader rows (Full List): `"Rank \(rank), \(entityHeader): \(athleteName)\(, Team: \(team)), Value: \(value)"`  
Team stat rows (Quick List): `"\(categoryName): \(value), \(rankDisplay)"`  
Team stat rows (Full List): `"Category: \(categoryName), Value: \(value), Rank: \(rankDisplay)"`

---

## Three-Screen Model

The app has exactly three canonical screen types:

| Screen | View | Status |
|---|---|---|
| **Sport Selection** | `SportSelectionView` | Stable — home screen |
| **Sport Screen** | `ScoresView` | Needs structural work |
| **Game Detail** | `GameDetailView` | Design in progress |

`LiveScoresView` is not a fourth screen. It is a projection of the Sport Screen concept applied simultaneously across all sports.

---

## Sport Screen Standard Layout

### Scores Tab

Every sport's Scores tab must have exactly three sections, in this order, each with a visible heading that is also a VoiceOver accessibility header:

1. **In Progress** — games currently live
2. **Upcoming** — games not yet started
3. **Completed** — games finished

Empty sections are omitted entirely. Do not show "No games" or "None" placeholders inside a section — either show games or omit the section heading entirely.

**Current state:** `ScoresView` does not implement these sections. The scores tab is an unsorted flat list. This is the highest-priority structural gap.

### Time Period Concept by Sport

| Sport type | Grouping period | Navigation unit |
|---|---|---|
| All non-football | Day | ±1 day |
| NFL, NCAAF | Week | ±1 week, using ESPN-resolved week label |

When displaying NFL or NCAAF, section headings should name the week (e.g. "Wild Card Week", "Week 14") rather than a calendar date.

### Other Tabs on the Sport Screen

The `ScoresView` segmented tab picker has these tabs (in order):

| Tab | Available |
|---|---|
| Scores | All sports |
| Standings | All sports |
| News | All sports |
| Stats | All sports |
| Polls | NCAAF, NCAAM, NCAAWB only |

#### Stats tab data sources

The Stats tab has a Players / Teams switch, and the two halves come from
different ESPN endpoints:

| Sub-tab | Endpoint | Notes |
|---|---|---|
| Players | Core API `…/types/{type}/leaders` | Individual leaders, top 10 per category |
| Teams | Web API `…/statistics/byteam` | Real team aggregates for every team |

The Core API `leaders` endpoint **only ever returns individual players** — its
`groups=50` "team" parameter is silently ignored, which once made the Teams
sub-tab show player numbers labelled with team abbreviations. Team statistics
must come from `statistics/byteam`.

Which stats appear, in what order, and which direction ranks best-first is
declared per sport in `Models/TeamStatCatalog.swift` (ESPN returns 100+ raw
columns per team). The Players / Teams switch is hidden entirely for sports
where ESPN publishes no team statistics — soccer, golf, racing, college hockey
and CFL (`Sport.hasTeamStats`).

---

## Live Scores View

`LiveScoresView` shows all sports on a single screen. Its section structure mirrors the Sport Screen sections, with sport headings acting as sub-headings within each status group:

```
IN PROGRESS            ← VoiceOver header trait
  NFL                  ← VoiceOver header trait
    game row
    game row
  MLB                  ← VoiceOver header trait
    game row
UPCOMING               ← VoiceOver header trait
  ...
COMPLETED              ← VoiceOver header trait
  ...
```

Sports with no games in a given status bucket are omitted entirely — no empty sport heading.

**Football in Live Scores is day-only.** `LiveScoresView` has no week navigation and always shows the current calendar day. For NFL and NCAAF this means only games on today's calendar date appear, unlike the full `ScoresView` which shows the whole week. This is intentional — the Live Scores view is a real-time snapshot, not a week planner.

**Current state:** `CompactGameRow` (used only in `LiveScoresView`) has no combined accessibility element. VoiceOver cycles through each sub-element individually. This must be fixed to match the `GameRow` pattern.

---

## Date and Week Navigation

### Where it applies

- Sport Selection home screen
- All Sport Screens

### Where it does not apply

- Game Detail — no date navigation inside a game
- Live Scores — always today, no navigation

### Control Layout

The navigation bar hosts these controls:

```
[← Previous]  [Date / Week label]  [→ Next]  [Today]
```

- **Previous / Next buttons** — labeled `"Previous Day"` / `"Next Day"` or `"Previous Week"` / `"Next Week"` depending on sport
- **Date / Week label** — center element; tappable to open date picker
- **Today button** — appears only when not already on today/current week; disappears when on today

### VoiceOver Pattern (from FastWeather)

The date/week label in the toolbar uses `.accessibilityAdjustableAction` so that when VoiceOver is focused on it, the user can swipe up/down to step through days (or weeks) without navigating focus away to the arrow buttons.

```swift
Text(dateDisplayString)
    .accessibilityLabel("Currently viewing \(accessibilityDateString)")
    .accessibilityAddTraits(.isButton)
    .accessibilityHint("Swipe up for next day, swipe down for previous day")
    .accessibilityAdjustableAction { direction in
        switch direction {
        case .increment: navigateToNextDay()
        case .decrement: navigateToPreviousDay()
        @unknown default: break
        }
    }
```

As a belt-and-suspenders fallback, named custom actions are also added to the screen container:

```swift
.accessibilityAction(named: "Previous Day") { navigateToPreviousDay() }
.accessibilityAction(named: "Next Day") { navigateToNextDay() }
```

Each navigation action should:
1. Call `UINotificationFeedbackGenerator().notificationOccurred(.success)` for haptic feedback
2. Post `UIAccessibility.post(notification: .announcement, argument: "Viewing [sport] for \(accessibilityDateString)")` so VoiceOver announces the new date without requiring focus to move

Date label display strings (visual vs VoiceOver are different):

| Offset | Visual | VoiceOver |
|---|---|---|
| −1 | Yesterday | Yesterday |
| 0 | Today | Today |
| +1 | Tmrw | Tomorrow |
| other | Mon, Mar 2 | Monday, March 2 |

### Future Dates

The date picker **must allow future dates** up to a reasonable lookahead (suggest 7 days). ESPN publishes future schedules; blocking navigation to tomorrow is a defect. Remove the `in: ...Date()` cap from `DatePickerView`.

**Current state:** `DatePickerView` blocks all future dates. This is a bug.

---

## Team Name Display Principle

The `Game.Team` struct carries four fields: `abbreviation`, `name`, `displayName`, `shortName`. Use them as follows:

| Context | Field | Example |
|---|---|---|
| Game row — visual | `abbreviation` | MIL |
| Game detail header — visual | `abbreviation` | MIL |
| Box score column headers | `abbreviation` | MIL |
| Standings row — visual | `abbreviation` | MIL |
| Game row — VoiceOver label | user preference (see below) | Milwaukee Brewers |
| Game detail team tap target — VoiceOver | user preference | Milwaukee Brewers |
| Standings row — VoiceOver | user preference | Milwaukee Brewers |
| Leader row (`LeaderRow`) — VoiceOver | user preference | Milwaukee Brewers |
| News, polls, rankings | user preference | Milwaukee Brewers |
| Team schedule navigation title | user preference | Milwaukee Brewers |
| Sport / section headings | `sport.displayName` | MLB |

**Rule:** Abbreviations are sufficient on screen because visual context (sport, layout, score columns) is available. VoiceOver users lack that ambient context — a VoiceOver accessibility label should never use an abbreviation unless the user has explicitly chosen that preference.

**Rule:** The user controls how team names are announced in VoiceOver via the App Settings (see below). Visual display always uses `abbreviation` regardless of this setting.

### Team Name Preference

Users set one of four modes in Settings → Team Name Announcement:

| Mode | Field / computation | Example (professional) | Example (college) |
|---|---|---|---|
| Full Name | `displayName` | Milwaukee Brewers | Wisconsin Badgers |
| Mascot / Nickname | `name` | Brewers | Badgers |
| City / School | `displayName` stripped of `name` suffix | Milwaukee | Wisconsin |
| Abbreviation | `abbreviation` | MIL | WIS |

The `Game.Team` extension provides `voiceOverName(for:)` to compute the right string given the active preference. Default is **Full Name**.

**Judgment notes:**
- College teams often have a school name where "city" is really the school ("Wisconsin", "Duke", "Ohio State"). The city/school mode uses the same computation (strip `name` from `displayName`) and is correct for both cases.
- Some team names have no city component (`displayName == name`, e.g. a hypothetical one-word name). In that case city/school mode falls back to `displayName`.
- The preference applies uniformly across all sports. There is no per-sport override at this time.

---

## VoiceOver Redundancy Principle

A game row should not repeat information that the section heading already communicates.

| Section | Words to omit from row labels |
|---|---|
| In Progress | "Live", "In progress" |
| Upcoming | "Upcoming", "Scheduled" |
| Completed | "Final", "Complete", "Finished" |

The visual status chip (e.g. a "FINAL" badge, "LIVE" dot) should be marked `.accessibilityHidden(true)` when inside a section whose heading already conveys that status. The section heading itself must have `.accessibilityAddTraits(.isHeader)`.

For **In Progress** rows, the meaningful VoiceOver content is the period, clock, and situation text — not the word "Live." For example:

> "Milwaukee Brewers 4, Chicago Cubs 2. Bottom 7th, one out, runner on second."

Not:

> "Live. Final. Milwaukee Brewers 4, Chicago Cubs 2."

---

## App Settings

The app has a single `AppSettings` object (`ObservableObject`) injected into the SwiftUI environment at the root. All views read preferences from it via `@EnvironmentObject`.

Settings are persisted via `@AppStorage` (backed by `UserDefaults`). No iCloud sync at this time.

### Settings Screen

Accessed via the gear icon in the `SportSelectionView` navigation bar. Opens as a modal sheet.

### Team Name Announcement

Key: `teamNamePreference` — type `TeamNamePreference` (String-backed enum, default `.full`).

Surfaces in SettingsView as a grouped `Picker` with an example preview row beneath. The example always shows how the Milwaukee Brewers (professional) example would be spoken so the user can hear the difference immediately.

### Future Settings (placeholder, not implemented)

- Auto-refresh default interval (currently reset to 1 min every navigation)
- Default sport on launch
- Time zone display preference

---

## Play-by-Play Information Order

**Applies to:** all timed sports (NBA, NHL, NFL, NCAAB, NCAAF, NCAAH). Not baseball — baseball has no game clock.

Every play row must present information in this order:

1. **What happened** — the play description (e.g. "Giannis Antetokounmpo makes running layup")
2. **When** — the game clock at that moment (e.g. "10:53")
3. **Impact** — cumulative score after the play (e.g. "BOS 4 – MIL 0")

Rationale: the most meaningful fact is what happened. Context (when, score) provides supporting detail and should come after. Both the visual layout and the VoiceOver accessibility label must follow this order. Screen-reading order matches visual reading order.

**Visual layout:** play text on top line; clock and score on a smaller secondary line below.

**VoiceOver label:** `"<play text>. <clock>. <away> <score>, <home> <score>."`  
Example: `"Giannis Antetokounmpo makes running layup. 10:53. BOS 0, MIL 4."`

---

## Game Detail Screen

Design is still being worked out. Decisions not yet made:

- Whether box score should be player-level (Python app) or team-aggregate (current iOS)
- Final tab order and tab naming
- How the game header adapts between pre-game, live, and final states

Current tab structure for reference:

| Tab | Available |
|---|---|
| Box Score | All |
| Drives (football) / Plays (other sports) | All |
| Info (leaders, injuries, officials, news) | All |
| More (win probability, season series) | MLB only |

---

## Known Design Debt

These are inconsistencies in the current codebase that violate the principles above. Each should be addressed in priority order.

| # | Issue | File(s) | Principle violated |
|---|---|---|---|
| 1 | `ScoresView` Scores tab is a flat unsorted list — no In Progress / Upcoming / Completed sections | `ScoresView.swift`, `ScoresViewModel.swift` | Sport Screen Standard Layout |
| 2 | `CompactGameRow` (used in `LiveScoresView`) has no `.accessibilityElement(children: .combine)` — VoiceOver reads sub-elements individually | `LiveScoresView.swift` | VoiceOver Redundancy |
| 3 | `DatePickerView` caps at `Date()` — future dates unreachable | `DatePickerView.swift` | Date Navigation |
| 4 | `autoRefreshInterval` is not shared — resets to 1 min when navigating between `ScoresView` and `LiveScoresView` | Both view files | General UX consistency |
| 5 | Status words ("Final", "Live") appear in VoiceOver labels regardless of section context | `ScoresView.swift`, `LiveScoresView.swift` | VoiceOver Redundancy |
| 6 | Date label in toolbar does not use `.accessibilityAdjustableAction` | `ScoresView.swift` | Date Navigation |
| 7 | `Sport.icon` returns a raw text string (`"MLB"`) not an image or SF Symbol | `Sport.swift` | Visual consistency |
| 8 | NBA/WNBA `usesNextYearFormat` not applied to standings/leaders API calls — only applied in `TeamScheduleViewModel` | `ESPNAPIService.swift`, `StandingsViewModel.swift` | Data correctness |
| 9 | `LiveScoresView` uses `fetchGames(for:)` for football instead of `fetchFootballGames` — may return wrong-week data | `LiveScoresViewModel.swift` | Live Scores: day-only is intentional, but the call should still use the correct ESPN `seasontype` parameter |
| 10 | `AppSettings`/`TeamNamePreference` not yet threaded into all VoiceOver label sites — only `GameRow` and `CompactGameRow` initially covered | Multiple view files | Team Name Display Principle |

---

## Pending Decisions

- **Game Detail player-level box score:** Port the Python app's per-player batting/pitching lines to iOS or keep team-aggregate? (Python app is the source of truth for feature intent.)
- **Date navigation on Sport Selection (home):** Should the home screen's "Today's Games" / `LiveScoresView` entry point also show a date, or is it always today only?
- **Auto-refresh persistence:** Should the refresh interval be persisted in `UserDefaults` and shared across all views?
- **Score monitoring toggle in Live Scores:** `ScoresView` has swipe/context actions to monitor a game for score changes; `LiveScoresView` does not. Should it?
