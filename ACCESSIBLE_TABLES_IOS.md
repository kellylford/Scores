# Proper Accessible Data Tables on iOS
### How to give VoiceOver users the same table navigation experience as the web — and why almost everyone gets it wrong

---

## Executive Summary

Every major accessibility framework — web, Windows, macOS — provides a way for screen reader users to navigate a table by row and column. When a VoiceOver user moves to a cell, the screen reader automatically reads the column header ("Wins") and the row header ("Baltimore Orioles") as context, so the user always knows where they are in the table without having to navigate back and look it up.

iOS has had this capability since iOS 11. Almost no apps implement it correctly. Instead, developers — including those at large financial institutions — resort to a workaround: stuffing the full context into every cell's spoken label, so every cell sounds like *"Baltimore Orioles, Wins, 82, row 4, column 3 of 6."* That works but it is not a table. It is a list of sentences. Users cannot navigate by column. They cannot ask "what is the header for this column?" There is no structure — just text.

This project demonstrates that the correct implementation is achievable, requires no special hardware or software beyond what iOS already ships, and produces behavior identical to a properly marked-up web table. The same approach applies directly to financial tables — portfolio holdings, account statements, transaction histories, options chains — anywhere a sighted user reads a grid and a VoiceOver user deserves the same experience.

---

## The Problem, Plainly Stated

Imagine a standings table:

|        | W  | L  | PCT  | GB  |
|--------|----|----|------|-----|
| BAL    | 82 | 58 | .586 | —   |
| BOS    | 78 | 62 | .557 | 4.0 |
| NYY    | 75 | 65 | .536 | 7.0 |

A sighted user sees the whole grid at once. They know instantly that 82 is Wins for Baltimore. They can scan down the GB column to compare teams.

A VoiceOver user moving cell by cell needs the same information delivered through audio. The correct experience:

> *"Baltimore Orioles — row header"* → *"Wins — 82"* → *"Losses — 58"* → *"Win Percent — point five eight six"*

The common wrong implementation:

> *"Baltimore Orioles"* → *"Baltimore Orioles, Wins, 82"* → *"Baltimore Orioles, Losses, 58"* → *"Baltimore Orioles, Win Percent, point five eight six"*

The wrong version reads the team name five times per row, is slower to navigate, and provides no actual table structure. Users cannot jump by column.

---

## Why Companies Get This Wrong

### The belief that it cannot be done

SwiftUI — Apple's modern UI framework, which most iOS teams have been building in since 2019 — does not expose a native API for this behavior. When developers build a table in SwiftUI, they reach for `Grid` and `GridRow`. These work visually. But they are layout-only constructs with no accessibility model behind them. Placing accessibility modifiers on a `GridRow` has no effect. VoiceOver sees a flat list of cells with no row or column relationship.

When teams investigate, they find no SwiftUI solution. They conclude the platform cannot do it — and they resort to the long-string workaround.

### The belief that UIKit is too old or too costly

The correct implementation lives in UIKit, Apple's older framework that SwiftUI runs on top of. It is not deprecated. It exposes `UIAccessibilityContainerDataTable`, a protocol that provides full table semantics. Most modern iOS teams have limited UIKit expertise and are reluctant to use it. The integration requires a specific bridging pattern that is not widely documented.

---

## The Solution

The implementation has three components.

### 1. The accessibility model (UIKit)

An invisible `UIView` subclass — zero pixels, pass-through for touches — implements two Apple protocols:

**`UIAccessibilityContainerDataTable`** tells iOS this view contains a data table, and provides the cell structure:
- How many rows and columns exist
- What element is at each (row, column) position
- Which elements are column headers (read when navigating down a column)
- Which elements are row headers (read when navigating across a row)

**`UIAccessibilityContainerDataTableCell`** is implemented by each individual cell element. It reports which row and column it occupies, which is how VoiceOver announces "row 3, column 2 of 6."

The critical method that almost everyone omits is `accessibilityHeaderElements(forRow:)`. This is the direct equivalent of `<th scope="row">` in an HTML table — it designates the first column of each data row as a row header. Without it, VoiceOver has no way to associate the team name with the data in that row as you navigate across. With it, VoiceOver reads the team name automatically as context, exactly once, at the right moment.

### 2. The visual layer (SwiftUI)

A normal SwiftUI view renders the table visually — fonts, colors, alternating row backgrounds, dividers. This is hidden from VoiceOver entirely using `.accessibilityHidden(true)`. VoiceOver users never touch it.

### 3. The bridge

The invisible UIKit overlay is placed on top of the visual SwiftUI table using `UIViewRepresentable`, SwiftUI's standard bridge to UIKit components. The overlay is sized to match the visual table exactly so that VoiceOver focus rectangles appear in the right place on screen — sighted users and VoiceOver users are looking at the same visual cells, just navigated differently.

---

## How It Behaves for a VoiceOver User

**Swipe right through cells in a row:**
> "AL East — row header" → "Baltimore Orioles — row 2, column 1 of 6" → "82 — row 2, column 2 of 6, Wins, Baltimore Orioles" → "58 — row 2, column 3 of 6, Losses, Baltimore Orioles"

The team name is read automatically as context on every cell in that row — not stuffed into the cell label, but provided by the table structure.

**Swipe down through a column:**
> "82 — row 2, column 2 of 6, Wins, Baltimore Orioles" → "78 — row 3, column 2 of 6, Wins, Boston Red Sox" → "75 — row 4, column 2 of 6, Wins, New York Yankees"

The column header "Wins" is read automatically as context. Users can navigate an entire column without losing track of what statistic they are comparing.

**VoiceOver rotor (column navigation mode):**
Users can use the VoiceOver rotor to jump directly to the next or previous cell in the same column — moving through all teams' win totals in sequence, for example — without traversing every cell in between.

---

## Why This Matters for Financial Tables

A brokerage portfolio table and a sports standings table are structurally identical from an accessibility standpoint:

| Context | Row Header | Column Headers |
|---------|-----------|----------------|
| Standings | Team name | W, L, PCT, GB |
| Portfolio | Ticker / Security name | Price, Change, Value, % of Portfolio |
| Account statement | Transaction date | Description, Amount, Balance |
| Options chain | Strike price | Bid, Ask, Volume, Open Interest, IV |

The implementation is the same in every case. The row header associates the security name with all its data values. Column headers associate the statistic name with all values in that column. Users navigate both dimensions freely.

Financial companies that have told customers this is not achievable are mistaken. It is achievable with the platform APIs that shipped in iOS 11 in 2017.

---

## Deep Technical Reference

### Protocols involved

```
UIAccessibilityContainerDataTable       (on the container UIView)
UIAccessibilityContainerDataTableCell   (on each cell UIAccessibilityElement)
```

Both must be implemented. Implementing only the container gives you cell position announcements but no header context. Implementing only the cell protocol gives you nothing — iOS will not call the cell methods without the container declaring `.dataTable` as its `accessibilityContainerType`.

### Critical: traits on row-header cells

Row-header cells (column 0 of each data row) must use `UIAccessibilityTraits.staticText`. Do **not** assign `.header` to them. The `.header` trait signals a heading in the document outline — it makes VoiceOver say "heading" and the VoiceOver rotor presents these cells as outline headings rather than table headers. The association between a cell and its role *as a row header* is established entirely through `accessibilityHeaderElements(forRow:)`, not through traits.

Column-header cells (row 0) correctly use `.header` because they are genuinely column headers.

### Why GridRow does not work

In SwiftUI, `GridRow` is a layout directive — it has no underlying `UIView` in the accessibility tree:

```
SwiftUI Grid
├── GridRow          ← no view node; children appear as direct children of Grid
│   ├── Text "BAL"  ← VoiceOver sees this as a sibling of the Grid cells, not a child of GridRow
│   ├── Text "82"
│   └── Text "58"
```

`.accessibilityElement(children: .ignore)` placed on a `GridRow` has no container to be set on because `GridRow` is not a view container. The modifier is silently ignored. Children remain individually navigable and the row-level combined label fires in addition to each child — producing triple-read behavior.

`HStack` is a real `UIView` container. The same modifier on an `HStack` works correctly: children are suppressed and the `HStack` element is the single accessibility node.

### Why the long-string workaround is not a table

```swift
// Common workaround — generates a sentence, not a table cell
.accessibilityLabel("Baltimore Orioles, Wins, 82, row 4, column 3 of 6")
```

This approach:
- Provides no actual column structure — VoiceOver rotor cannot navigate by column
- Reads the team name on every cell in the row (4–6× per row)
- Provides no relationship between cells that VoiceOver can reason about
- Cannot be navigated with the table navigation commands in the VoiceOver rotor
- Is not a table in any technical sense — it is a list of descriptive strings

### Platform availability

| API | Available since |
|-----|----------------|
| `UIAccessibilityContainerDataTable` | iOS 11 (2017) |
| `UIAccessibilityContainerDataTableCell` | iOS 11 (2017) |
| `accessibilityHeaderElements(forColumn:)` | iOS 11 (2017) |
| `accessibilityHeaderElements(forRow:)` | iOS 11 (2017) |
| `accessibilityContainerType = .dataTable` | iOS 11 (2017) |

Everything used here has been available for eight years. There is no technical reason for any app shipping today to use the workaround instead.

---

## The Exact Production Code

The following is the complete, unmodified code shipping in this app. It is reproduced here so it can be copied directly into any Swift project.

### File 1 of 2 — `AccessibleTableBridge.swift`

This is the entire accessibility engine. Drop this file into any SwiftUI project as-is.

```swift
//
//  AccessibleTableBridge.swift
//
//  A thin UIKit bridge that gives VoiceOver proper data-table navigation.
//
//  VoiceOver announces "row 2, column 3 of 6" when users swipe through cells
//  and automatically reads the row-header (team/security name) as context when
//  navigating across a row — the same behaviour as <th scope="row"> in HTML.
//
//  Key protocol hooks:
//    • accessibilityHeaderElements(forColumn:) — column header for each col
//    • accessibilityHeaderElements(forRow:)    — row header (col-0 cell) for
//                                               each data row; this is the
//                                               hook that makes VoiceOver read
//                                               the row label automatically
//    • accessibilityDataTableCellElement(forRow:column:) — individual cells
//
//  Column-0 data cells carry .staticText traits (NOT .header — that would make
//  VoiceOver say "heading" and break navigation). They are associated as
//  row headers purely through accessibilityHeaderElements(forRow:).
//
//  Usage (overlay the visual SwiftUI table, which is .accessibilityHidden(true)):
//
//      visualTableVStack
//          .accessibilityHidden(true)
//          .overlay(
//              AccessibleDataTable(headers: headers, rows: rows)
//                  .allowsHitTesting(false)
//          )
//

import SwiftUI
import UIKit

// MARK: - Cell element

/// A single logical cell in the accessibility table.
/// Implements UIAccessibilityContainerDataTableCell so VoiceOver can
/// announce the cell's position ("row 2, column 3 of 6").
final class DataTableCellElement: UIAccessibilityElement,
                                  UIAccessibilityContainerDataTableCell {
    private let _row: Int
    private let _col: Int

    init(container: AccessibleDataTableView,
         label: String,
         traits: UIAccessibilityTraits = .none,
         row: Int,
         col: Int) {
        self._row = row
        self._col = col
        super.init(accessibilityContainer: container)
        accessibilityLabel = label
        accessibilityTraits = traits
    }

    @objc func accessibilityRowRange() -> NSRange {
        NSRange(location: _row, length: 1)
    }

    @objc func accessibilityColumnRange() -> NSRange {
        NSRange(location: _col, length: 1)
    }
}

// MARK: - Container view

/// An invisible UIKit view whose sole purpose is to expose a proper
/// UIAccessibilityContainerDataTable tree to VoiceOver.
/// Set allowsHitTesting(false) in SwiftUI so touches pass through.
final class AccessibleDataTableView: UIView,
                                     UIAccessibilityContainerDataTable {

    // MARK: Public inputs
    var columnHeaders: [String] = [] { didSet { rebuild() } }
    var dataRows: [[String]] = []    { didSet { rebuild() } }

    // MARK: Private state
    private var headerElements: [DataTableCellElement] = []
    private var rowElements:    [[DataTableCellElement]] = []

    // MARK: Init

    override init(frame: CGRect) {
        super.init(frame: frame)
        accessibilityContainerType = .dataTable   // REQUIRED — without this, nothing works
        isUserInteractionEnabled = false
        backgroundColor = .clear
    }

    required init?(coder: NSCoder) { fatalError("init(coder:) not implemented") }

    // MARK: Layout

    override func layoutSubviews() {
        super.layoutSubviews()
        rebuild()
    }

    // MARK: Build elements

    private func rebuild() {
        guard !columnHeaders.isEmpty else {
            headerElements = []
            rowElements    = []
            return
        }

        let ncols = columnHeaders.count
        let nrows = dataRows.count

        // Divide the view bounds into a logical grid for focus-rectangle placement.
        // Column 0 (row-header column) gets 40% of width; remaining columns split equally.
        let totalW    = max(1, bounds.width)
        let totalH    = max(1, bounds.height)
        let col0W     = totalW * 0.40
        let otherColW = ncols > 1 ? (totalW - col0W) / CGFloat(ncols - 1) : 0
        let rowH      = totalH / CGFloat(nrows + 1)  // +1 for the column-header row

        func xOffset(col: Int) -> CGFloat {
            col == 0 ? 0 : col0W + CGFloat(col - 1) * otherColW
        }
        func colWidth(col: Int) -> CGFloat {
            col == 0 ? col0W : otherColW
        }
        func screenFrame(row: Int, col: Int) -> CGRect {
            let local = CGRect(x: xOffset(col: col),
                               y: CGFloat(row) * rowH,
                               width: colWidth(col: col),
                               height: rowH)
            return UIAccessibility.convertToScreenCoordinates(local, in: self)
        }

        // Column header row (accessibility row 0).
        // .header trait = VoiceOver announces "header" and reads this cell
        // as context when the user navigates down a column.
        headerElements = columnHeaders.enumerated().map { col, title in
            let el = DataTableCellElement(container: self, label: title,
                                          traits: .header, row: 0, col: col)
            el.accessibilityFrame = screenFrame(row: 0, col: col)
            return el
        }

        // Data rows (accessibility rows 1…n).
        // Column-0 cells are the row headers. They use .staticText traits —
        // NOT .header, which would make VoiceOver say "heading" and break
        // table navigation. Their role as row headers is communicated entirely
        // through accessibilityHeaderElements(forRow:) below.
        rowElements = dataRows.enumerated().map { row, cols in
            cols.enumerated().map { col, label in
                let el = DataTableCellElement(container: self, label: label,
                                              traits: .staticText,
                                              row: row + 1, col: col)
                el.accessibilityFrame = screenFrame(row: row + 1, col: col)
                return el
            }
        }
    }

    // MARK: UIAccessibilityContainerDataTable

    @objc func accessibilityRowCount() -> Int {
        dataRows.count + 1  // data rows + column-header row
    }

    @objc func accessibilityColumnCount() -> Int {
        columnHeaders.count
    }

    /// Column header for each column.
    /// VoiceOver calls this when the user navigates down a column so it can
    /// announce "Wins" (or "Price", or "Amount") as persistent context.
    @objc func accessibilityHeaderElements(forColumn column: Int) -> [Any]? {
        guard column < headerElements.count else { return nil }
        return [headerElements[column]]
    }

    /// Row header for each data row — the column-0 cell (team name, ticker, etc.).
    /// THIS IS THE METHOD ALMOST EVERYONE OMITS.
    /// It is the direct equivalent of <th scope="row"> in HTML.
    /// VoiceOver calls this when the user navigates across a row so it can
    /// announce "Baltimore Orioles" (or "AAPL") as persistent context for
    /// every data cell in that row — without the app having to stuff the name
    /// into every cell's label string.
    @objc func accessibilityHeaderElements(forRow row: Int) -> [Any]? {
        guard row > 0 else { return nil }  // row 0 is the column-header row; no row-header for it
        let dataRow = row - 1
        guard dataRow < rowElements.count,
              !rowElements[dataRow].isEmpty else { return nil }
        return [rowElements[dataRow][0]]   // column-0 cell IS the row header
    }

    /// Cell element at an explicit (row, column) position.
    /// Used by VoiceOver's table-navigation rotor commands (next/previous in column, etc.).
    @objc func accessibilityDataTableCellElement(
        forRow row: Int, column: Int
    ) -> (any UIAccessibilityContainerDataTableCell)? {
        if row == 0 {
            return column < headerElements.count ? headerElements[column] : nil
        }
        let dataRow = row - 1
        guard dataRow < rowElements.count,
              column < rowElements[dataRow].count else { return nil }
        return rowElements[dataRow][column]
    }

    /// Linear element order for standard VoiceOver swipe navigation.
    override var accessibilityElements: [Any]? {
        get {
            var all: [Any] = headerElements
            rowElements.forEach { all.append(contentsOf: $0) }
            return all
        }
        set {}
    }
}

// MARK: - SwiftUI representable

/// SwiftUI wrapper — drop this onto any visual table using .overlay().
///
///     visualTableVStack
///         .accessibilityHidden(true)
///         .overlay(
///             AccessibleDataTable(headers: headers, rows: rows)
///                 .allowsHitTesting(false)
///         )
///
/// headers  — column labels including the col-0 row-header column label ("Team", "Security", etc.)
/// rows     — one array per data row; rows[n][0] is the row-header value (full name, not abbreviation)
struct AccessibleDataTable: UIViewRepresentable {
    let headers: [String]
    let rows: [[String]]

    func makeUIView(context: Context) -> AccessibleDataTableView {
        AccessibleDataTableView()
    }

    func updateUIView(_ uiView: AccessibleDataTableView, context: Context) {
        guard uiView.columnHeaders != headers || uiView.dataRows != rows else { return }
        uiView.columnHeaders = headers
        uiView.dataRows      = rows
    }
}
```

### File 2 of 2 — How it is called from SwiftUI (`StandingsTableView`, table-mode section)

This is the exact SwiftUI side that wires the visual table to the accessibility overlay. The pattern is the same for any table — replace the standings-specific `rowData` / `accessibleRowData` functions with whatever data your table holds.

```swift
private func standingsTableSection(for group: StandingsGroup) -> some View {
    VStack(spacing: 0) {

        // ── Visual column header row ──────────────────────────────────────
        HStack(spacing: 0) {
            Text(activeHeaders[0])           // "Team" — flexible width
                .font(.caption.bold())
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 8)
            ForEach(activeHeaders.dropFirst(), id: \.self) { col in
                Text(col)
                    .font(.caption.bold())
                    .frame(width: 44)
            }
        }
        .padding(.vertical, 6)
        .background(Color.secondary.opacity(0.15))

        Divider()

        // ── Visual data rows ──────────────────────────────────────────────
        ForEach(Array(group.entries.enumerated()), id: \.element.id) { idx, entry in
            let cols = rowData(for: entry)   // uses abbreviation in col 0 for display
            HStack(spacing: 0) {
                Text(cols[0])
                    .font(.subheadline.bold())
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 8)
                ForEach(Array(cols.dropFirst().enumerated()), id: \.offset) { _, value in
                    Text(value)
                        .font(.caption.monospacedDigit())
                        .frame(width: 44)
                }
            }
            .padding(.vertical, 7)
            .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.05))
            .accessibilityHidden(true)    // VoiceOver never sees visual rows

            if idx < group.entries.count - 1 {
                Divider().padding(.leading, 8)
            }
        }
    }
    // The entire visual VStack is hidden from VoiceOver.
    // The AccessibleDataTable overlay IS what VoiceOver sees.
    .accessibilityHidden(true)
    .overlay(
        AccessibleDataTable(
            headers: activeHeaders,
            // accessibleRowData() uses the full display name ("Los Angeles Dodgers")
            // in column 0 instead of the abbreviation ("LAD") so VoiceOver speaks
            // the full name as the row header.
            rows: group.entries.map { accessibleRowData(for: $0) }
        )
        .allowsHitTesting(false)   // touches pass through to the visual layer
    )
}

// Column 0 for accessibility uses full name; visual table uses abbreviation.
private func accessibleRowData(for entry: StandingsEntry) -> [String] {
    var cols = rowData(for: entry)
    if !cols.isEmpty { cols[0] = entry.team.displayName }
    return cols
}
```

**The only thing that changes when adapting this to a financial table** is `rowData()` and `accessibleRowData()` — the functions that produce the string arrays. The `AccessibleDataTable` struct, `AccessibleDataTableView`, and `DataTableCellElement` are completely generic and reusable as-is.

---

## Summary of What Correct Implementation Requires

1. A `UIView` subclass with `accessibilityContainerType = .dataTable`
2. Implementation of `UIAccessibilityContainerDataTable` on that view, including **both** `accessibilityHeaderElements(forColumn:)` and `accessibilityHeaderElements(forRow:)`
3. Individual cell elements conforming to `UIAccessibilityContainerDataTableCell`, reporting their row and column ranges
4. Column-0 data cells designated as row-header elements via `accessibilityHeaderElements(forRow:)` — with `.staticText` traits, **not `.header`**
5. The visual table hidden from VoiceOver (`accessibilityHidden(true)`); the UIKit overlay on top via `.overlay()` with `.allowsHitTesting(false)`
6. A `UIViewRepresentable` bridge (`AccessibleDataTable`) connecting SwiftUI to the UIKit container

None of these steps is optional. Omitting any one of them degrades to partial or no table navigation. The most commonly omitted step is #2 (`accessibilityHeaderElements(forRow:)`) — and it is the step that makes the entire experience work like a real table rather than a list.
