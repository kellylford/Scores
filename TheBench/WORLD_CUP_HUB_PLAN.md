# World Cup Hub — Implementation Plan

**Tournament:** 2026 FIFA World Cup  
**Dates:** June 11 – July 19, 2026  
**ESPN API slug:** `soccer/fifa.world`  
**Branch:** iOS  

---

## What ESPN Gives Us

All endpoints confirmed working against the live 2026 API:

| Data                 | Endpoint                                                          | Notes                                                                            |
| -------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Scoreboard (by date) | `site.api.espn.com/…/soccer/fifa.world/scoreboard?dates=YYYYMMDD` | Returns all games on that day                                                    |
| Full phase schedule  | `…?dates=YYYYMMDD-YYYYMMDD`                                       | Range query — fetch 72 group-stage games in one call                             |
| Group standings      | `site.api.espn.com/apis/v2/sports/soccer/fifa.world/standings`    | 12 groups (A–L), 4 teams each; includes GP/W/D/L/GD/Pts + advancement color note |
| News                 | `…/soccer/fifa.world/news?limit=25`                               | World Cup specific feed                                                          |
| Game details         | `…/soccer/fifa.world/summary?event=ID`                            | Play-by-play, lineups — same shape as other sports                               |
| Teams                | `…/soccer/fifa.world/teams?limit=50`                              | 48 teams with logos                                                              |

**Calendar phases returned by the API:**

| Value | Label           | Dates        |
| ----- | --------------- | ------------ |
| 1     | Group Stage     | Jun 11–27    |
| 2     | Round of 32     | Jun 28–Jul 3 |
| 3     | Round of 16     | Jul 4–7      |
| 4     | Quarterfinals   | Jul 9–11     |
| 5     | Semifinals      | Jul 14–15    |
| 6     | 3rd-Place Match | Jul 18       |
| 7     | Final           | Jul 19       |

**Standings stats available:** GP, W, D, L, GF, GA, GD, Points — plus a `note` field with color + "Advance to Round of 32" text.  
**Knockout bracket:** Pre-tournament shows placeholder "RD32", "RD16" etc.; will fill in with actual teams as results come in. Same shape as group-stage events.

---

## Architecture

Following the **Golf hub pattern** (GolfHubView → GolfLeagueView, GolfViewModel) as the closest model. The hub sits on the home page as a conditional row, navigates into a full tabbed view.

### New Files

```
iOS/SportsScoresApp/SportsScores/
├── Models/
│   └── WorldCup.swift              # WorldCupGroup, WorldCupGroupEntry, WorldCupPhase, WorldCupBracketMatch
├── ViewModels/
│   └── WorldCupViewModel.swift     # Loads groups, schedule (by date), news; phase picker state
├── Views/
│   ├── WorldCupHubView.swift       # Tabbed root: Scores · Groups · Bracket · News
│   ├── WorldCupGroupsView.swift    # 12-group standings grid
│   └── WorldCupBracketView.swift   # Knockout rounds (Round of 32 through Final)
```

### Modified Files

| File                             | Change                                                                        |
| -------------------------------- | ----------------------------------------------------------------------------- |
| `Models/Sport.swift`             | Add `case worldCup = "WorldCup"` with `apiPath = "soccer/fifa.world"`         |
| `Services/ESPNAPIService.swift`  | Add `fetchWorldCupStandings()` and `fetchWorldCupScheduleRange(start:end:)`   |
| `Settings/AppSettings.swift`     | Add `worldCupHubEnabled: Bool` (auto-defaults to `true` during Jun 11–Jul 19) |
| `Views/SportSelectionView.swift` | Add World Cup hub row (same pattern as Soccer and Golf rows)                  |

---

## Tab-by-Tab Design

### Tab 1 — Scores (Today's Games)

- Date navigation bar (same ±7 day pattern as SoccerHubView)
- List of games on selected day, grouped by match time
- Each row: team flags/abbr, score or kick-off time, venue, TV/streaming info
- Tap → GameDetailView (reuses existing play-by-play / stats / lineups — the summary endpoint works identically for soccer)
- During group stage: show "Group A" label on each match row
- During knockout: show round label ("Round of 32", "Quarterfinal", etc.)

### Tab 2 — Groups

- Scrollable list of all 12 groups (A–L)
- Each group is a section with a 4-row standings table
- Columns: Team | GP | W | D | L | GD | Pts
- Advancement indicator: colored dot + "Advances" note (data comes from the `note` field in the standings API — green = advance, absent = eliminated)
- After group stage ends (Jun 27): show final standings; groups section stays useful as reference through the tournament

**Accessibility:**
- Each group section header announced: "Group A"
- Each row: "Mexico, 1st, 3 points, 1 win 0 draws 0 losses, goal difference plus 2, advances"
- VoiceOver swipe navigates row-by-row through all groups without needing to enter each section

### Tab 3 — Bracket

- Phase picker across the top: Group Stage | Rd of 32 | Rd of 16 | QF | SF | Final
- **Group Stage selected:** shows the Groups view (reuse Tab 2 content) — compact group tables
- **Knockout phase selected:** shows matches for that round in a list
  - Pre-result: "Winner Group A vs Runner-up Group B" with TBD scores
  - Post-result: actual team names + score + winner highlight
- This is a list-based bracket (not a visual tree diagram) — keeps it clean for VoiceOver

**Accessibility:**
- Phase picker uses `.pickerStyle(.segmented)` — VoiceOver reads "Quarterfinals, 3 of 5"
- Each bracket match row: "Argentina vs France, Argentina wins 2 to 1, Quarterfinal 1"
- TBD slots: "Winner Group A vs Runner-up Group B, Scheduled July 9th"

### Tab 4 — News

- Reuses the existing `NewsView` pattern (already used in GolfLeagueView)
- Fetches from `soccer/fifa.world/news`
- Standard headline list → Safari sheet on tap

---

## Sport.swift Changes

```swift
// Add to enum Sport
case worldCup = "WorldCup"

// apiPath
case .worldCup: return "soccer/fifa.world"

// displayName  
case .worldCup: return "2026 FIFA World Cup"

// icon
case .worldCup: return "WC"

// systemImage
case .worldCup: return "globe.americas.fill"

// isSoccer — worldCup is NOT included in soccerLeagues (separate hub)
// isWorldCup convenience
var isWorldCup: Bool { self == .worldCup }
```

`Sport.allCases` — do NOT add worldCup here (same approach as golf and soccer — it's hub-only, not in the main home page ForEach).

---

## AppSettings Changes

```swift
// New storage key
static let worldCupHubEnabled = "worldCupHubEnabled"

// New published property
@Published var worldCupHubEnabled: Bool { ... }

// In init(): default to true if we're currently within the tournament window
// Jun 11, 2026 – Jul 20, 2026
private static var isWorldCupActive: Bool {
    let now = Date()
    var comps = DateComponents()
    comps.year = 2026; comps.month = 6; comps.day = 11
    let start = Calendar.current.date(from: comps)!
    comps.month = 7; comps.day = 20
    let end = Calendar.current.date(from: comps)!
    return now >= start && now < end
}
```

Setting is user-overridable via Settings → "Show World Cup Hub" toggle (same as Soccer/Golf hub toggles that already exist in SettingsView).

---

## Home Page Row (SportSelectionView)

```swift
// After the Golf hub row, before the section close:
if appSettings.worldCupHubEnabled {
    NavigationLink(destination: WorldCupHubView()) {
        HStack(spacing: 12) {
            Image(systemName: "globe.americas.fill")
                .font(.title2)
                .foregroundColor(.accentColor)
                .frame(width: 36)
            VStack(alignment: .leading, spacing: 2) {
                Text("2026 FIFA World Cup")
                    .font(.headline)
                Text(worldCupSubtitle)   // e.g. "Group Stage · Jun 11–27"
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            Spacer()
            // Live game count badge (same capsule pattern as Soccer hub)
        }
        .padding(.vertical, 4)
    }
    .accessibilityLabel("2026 FIFA World Cup hub")
}
```

---

## ESPNAPIService Additions

```swift
// MARK: - World Cup Group Standings
func fetchWorldCupStandings() async throws -> [WorldCupGroup]

// MARK: - World Cup Schedule (date range)
// Used to load all games in a phase at once (e.g. all 72 group-stage games)
func fetchWorldCupScheduleRange(startDate: Date, endDate: Date) async throws -> [Game]
// Uses existing fetchGames(for:date:) for single-day Scores tab — no new method needed
```

Standings parsing needs a custom response model (different shape from league standings — uses `children` with `standings.entries` + `note` fields). Everything else reuses existing `Game`, `GameDetails`, `NewsItem` models unchanged.

---

## Model: WorldCup.swift

```swift
struct WorldCupGroup: Identifiable {
    let id: String           // "1" through "12"
    let name: String         // "Group A" through "Group L"
    let entries: [WorldCupGroupEntry]
}

struct WorldCupGroupEntry: Identifiable {
    let id: String
    let teamAbbreviation: String
    let teamDisplayName: String
    let gamesPlayed: Int
    let wins: Int
    let draws: Int
    let losses: Int
    let goalsFor: Int
    let goalsAgainst: Int
    let goalDifference: Int
    let points: Int
    let advancementNote: String?   // "Advance to Round of 32" or nil
    let advancementColor: String?  // hex color string from API
}

struct WorldCupPhase: Identifiable {
    let id: String           // "1"–"7"
    let label: String        // "Group Stage", "Round of 32", etc.
    let startDate: Date
    let endDate: Date
}
```

---

## Accessibility Checklist

All existing patterns apply — nothing new to invent:

- [ ] Every interactive element has `.accessibilityLabel` (no bare icons)
- [ ] Date navigation arrows: "Previous Day" / "Next Day" (matches SoccerHubView)
- [ ] Phase picker: `.pickerStyle(.segmented)` — naturally announced by VoiceOver
- [ ] Group table rows: spoken as full sentence with position, team, and key stats
- [ ] Advancement status: spoken inline ("advances to Round of 32") not just color-coded
- [ ] Bracket TBD slots: spoken as "TBD vs TBD" not silent/empty
- [ ] Score badges on home row: `accessibilityHidden(true)` with count in the row label
- [ ] Loading states: `.accessibilityLabel("Loading World Cup data")` on ProgressView
- [ ] Navigation title set on WorldCupHubView: "2026 FIFA World Cup" — gives VoiceOver context

---

## Build Order

1. **`WorldCup.swift`** — models only, no dependencies
2. **`Sport.swift`** — add `worldCup` case (touches existing file minimally)
3. **`ESPNAPIService.swift`** — add `fetchWorldCupStandings()` 
4. **`WorldCupViewModel.swift`** — wraps the API calls, `@Published` state
5. **`WorldCupGroupsView.swift`** — groups tab (can be tested standalone with mock data)
6. **`WorldCupBracketView.swift`** — bracket tab
7. **`WorldCupHubView.swift`** — assembles all tabs
8. **`AppSettings.swift`** — add `worldCupHubEnabled`
9. **`SportSelectionView.swift`** — add hub row
10. **`SettingsView.swift`** — add toggle in Home Page section

Each step compiles independently. Steps 5–6 can be done in parallel.

---

## Out of Scope (for now)

- Visual bracket tree diagram — a list-based bracket is screen-reader-friendly and much simpler to build. A visual tree is a future enhancement.
- Team detail pages — tapping a team in the groups table could navigate to a team page, but that's a separate feature.
- Push notifications for goals — that's an app-level infrastructure change.
- Historical World Cups — ESPN only has 2026 data in the live API; previous tournaments would require different API work.

---

## Open Questions for Kelly

1. **Should the World Cup hub auto-hide after July 19?** (i.e., the home page row disappears when the tournament ends, or leave it visible year-round as a historical record)
Kelly: Turn it on now and leave it on. Make it something the user can turn off/on in the settings like our other sports.

3. **Bracket tab format:** Prefer the list-based bracket described above, or is a more visual left/right bracket worth the extra complexity?  
	  
	Kelly: List based. Making a visual bracket is really tough.  
	  

4. **Scores tab scope:** Show only World Cup games, or also surface the "Live Soccer" entry so users can cross-check with other leagues?  
	  
	Kelly: HJust World Cup. Don’t turn off any of the other soccer but this should be specific to this event.  

5. **Women's World Cup:** 2027 Women's World Cup is in Brazil. Slot same structure for `soccer/fifa.wwc`? Worth plumbing the `worldCupWomens` case now while this is being built.
Kelly: Yes, please.  
  
One other reminder, where possible, use our three formats for lists, table, quick list and full list.