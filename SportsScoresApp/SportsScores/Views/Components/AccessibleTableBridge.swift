//
//  AccessibleTableBridge.swift
//  SportsScores
//
//  A thin UIKit bridge that gives VoiceOver proper data-table navigation for
//  standings and box-score grids.
//
//  VoiceOver will announce "row 2, column 3 of 6" when users swipe through
//  cells — something SwiftUI.Grid cannot provide on its own.
//
//  Usage (inside a ZStack, overlaying the visual grid which is
//  .accessibilityHidden(true)):
//
//      ZStack(alignment: .topLeading) {
//          visualGrid
//              .accessibilityHidden(true)
//          AccessibleDataTable(headers: headers, rows: rows)
//              .allowsHitTesting(false)
//      }
//

import SwiftUI
import UIKit

// MARK: - Cell element

/// A single logical cell in the accessibility table.
///
/// Implements `UIAccessibilityContainerDataTableCell` so VoiceOver can
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
/// `UIAccessibilityContainerDataTable` tree to VoiceOver.
///
/// Set `allowsHitTesting(false)` in SwiftUI so touches pass through to the
/// visual layer underneath.
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
        accessibilityContainerType = .dataTable
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
        // Column 0 (Team / Stat name) gets 40% of width; rest split equally.
        let totalW      = max(1, bounds.width)
        let totalH      = max(1, bounds.height)
        let col0W       = totalW * 0.40
        let otherColW   = ncols > 1 ? (totalW - col0W) / CGFloat(ncols - 1) : 0
        let rowH        = totalH / CGFloat(nrows + 1) // +1 for header

        func xOffset(col: Int) -> CGFloat {
            col == 0 ? 0 : col0W + CGFloat(col - 1) * otherColW
        }
        func colWidth(col: Int) -> CGFloat {
            col == 0 ? col0W : otherColW
        }

        func screenFrame(row: Int, col: Int) -> CGRect {
            let localFrame = CGRect(
                x: xOffset(col: col),
                y: CGFloat(row) * rowH,
                width: colWidth(col: col),
                height: rowH
            )
            return UIAccessibility.convertToScreenCoordinates(localFrame, in: self)
        }

        // Header row (accessibility row 0)
        headerElements = columnHeaders.enumerated().map { col, title in
            let el = DataTableCellElement(
                container: self,
                label: title,
                traits: .header,
                row: 0,
                col: col
            )
            el.accessibilityFrame = screenFrame(row: 0, col: col)
            return el
        }

        // Data rows (accessibility rows 1…n)
        rowElements = dataRows.enumerated().map { row, cols in
            cols.enumerated().map { col, label in
                let el = DataTableCellElement(
                    container: self,
                    label: label,
                    traits: .staticText,
                    row: row + 1,
                    col: col
                )
                el.accessibilityFrame = screenFrame(row: row + 1, col: col)
                return el
            }
        }
    }

    // MARK: UIAccessibilityContainerDataTable

    @objc func accessibilityRowCount() -> Int {
        dataRows.count + 1 // data rows + header row
    }

    @objc func accessibilityColumnCount() -> Int {
        columnHeaders.count
    }

    @objc func accessibilityHeaderElements(forColumn column: Int) -> [Any]? {
        guard column < headerElements.count else { return nil }
        return [headerElements[column]]
    }

    @objc func accessibilityDataTableCellElement(forRow row: Int, column: Int) -> (any UIAccessibilityContainerDataTableCell)? {
        if row == 0 {
            return column < headerElements.count ? headerElements[column] : nil
        }
        let dataRow = row - 1
        guard dataRow < rowElements.count,
              column < rowElements[dataRow].count else { return nil }
        return rowElements[dataRow][column]
    }

    // Standard accessibility traversal (used by VoiceOver for swipe navigation)
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

/// SwiftUI wrapper for `AccessibleDataTableView`.
///
/// Example:
/// ```swift
/// ZStack(alignment: .topLeading) {
///     visualGridView
///         .accessibilityHidden(true)
///     AccessibleDataTable(headers: headers, rows: rows)
///         .allowsHitTesting(false)
/// }
/// ```
struct AccessibleDataTable: UIViewRepresentable {
    let headers: [String]
    let rows: [[String]]

    func makeUIView(context: Context) -> AccessibleDataTableView {
        AccessibleDataTableView()
    }

    func updateUIView(_ uiView: AccessibleDataTableView, context: Context) {
        // Guard against redundant rebuilds
        guard uiView.columnHeaders != headers || uiView.dataRows != rows else { return }
        uiView.columnHeaders = headers
        uiView.dataRows      = rows
    }
}
