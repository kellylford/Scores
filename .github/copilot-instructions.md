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

## iOS Accessibility rules — non-negotiable

### Tables must use AccessibleDataTable
Any tabular data (roster, standings, box scores, any grid) MUST use `AccessibleDataTableView` / `AccessibleDataTable` from `AccessibleTableBridge.swift`. This is the UIKit `UIAccessibilityContainerDataTable` bridge that gives VoiceOver proper row/column navigation. Never substitute plain `.accessibilityLabel` loops or `.accessibilityElement(children: .combine)` on rows.

**Correct pattern** (matches `StandingsTableView`):
```swift
visualGrid
    .accessibilityHidden(true)
    .overlay(
        AccessibleDataTable(headers: headers, rows: rows)
            .allowsHitTesting(false)
    )
```
Do NOT use a `ZStack` — the overlay gives `AccessibleDataTable` a real frame; a `ZStack` gives it zero size and VoiceOver can't find it.

### Never put position/index in accessibility labels
Never include "Row N", "Item N", "Column N", or any positional counter in an `accessibilityLabel`. VoiceOver announces position automatically from the data-table protocol. For list modes, use the content itself — e.g. `"Smith, #42, Pitcher, 28"` not `"Row 3: Smith, #42, Pitcher, 28"`.

### Every list row must be a single VoiceOver element
Any `HStack` or compound view used as a list/table row must have:
```swift
.accessibilityElement(children: .ignore)
.accessibilityLabel(/* one combined string */)
```
Without `.accessibilityElement(children: .ignore)`, every sub-view (badge, text, spacer, score) is focusable separately and VoiceOver hits the same game/item 4–5 times.

### Section headers need .isHeader trait
```swift
Text("Section Title")
    .accessibilityAddTraits(.isHeader)
```
This lets VoiceOver users navigate by headings with the rotor.

### Decorative elements must be hidden
Dividers, decorative icons, color swatches, and visual-only separators must have `.accessibilityHidden(true)` so VoiceOver doesn't land on unlabeled elements.

### NavigationStack nesting
Never wrap tab content in its own `NavigationStack` when it lives inside a tab that is already inside an outer `NavigationStack`. Double-stacking creates duplicate nav bars and VoiceOver reads the title twice. Tab views should be plain `View`s; NavigationLinks push onto the single outer stack.
