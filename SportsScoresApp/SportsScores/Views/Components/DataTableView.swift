//
//  DataTableView.swift
//  SportsScores
//
//  Created on 1/4/26.
//
//  Revolutionary three-view-mode table component
//  Supports: Table View, Quick List, Full List

import SwiftUI

struct DataTableView: View {
    let headers: [String]
    let rows: [[String]]
    @State private var viewMode: ViewMode = .table
    
    var body: some View {
        VStack(spacing: 0) {
            // View Mode Picker
            ViewModePicker(selectedMode: $viewMode)
                .padding(.vertical, 8)
            
            Divider()
            
            // Content based on view mode
            ScrollView {
                switch viewMode {
                case .table:
                    tableView
                case .quickList:
                    quickListView
                case .fullList:
                    fullListView
                }
            }
        }
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                ViewModeToggleButton(currentMode: $viewMode)
            }
        }
    }
    
    // MARK: - Table View
    private var tableView: some View {
        VStack(spacing: 0) {
            // Header Row
            HStack(spacing: 0) {
                ForEach(headers, id: \.self) { header in
                    Text(header)
                        .font(.caption)
                        .fontWeight(.bold)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(Color.secondary.opacity(0.2))
                }
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Table headers: \(headers.joined(separator: ", "))")
            
            Divider()
            
            // Data Rows
            ForEach(Array(rows.enumerated()), id: \.offset) { index, row in
                HStack(spacing: 0) {
                    ForEach(Array(row.enumerated()), id: \.offset) { colIndex, value in
                        Text(value)
                            .font(.caption)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 8)
                            .background(index % 2 == 0 ? Color.clear : Color.secondary.opacity(0.05))
                            .accessibilityLabel("\(headers[colIndex]): \(value)")
                    }
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel(createAccessibilityLabel(for: row, at: index))
                
                if index < rows.count - 1 {
                    Divider()
                }
            }
        }
    }
    
    // MARK: - Quick List View
    private var quickListView: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(Array(rows.enumerated()), id: \.offset) { index, row in
                VStack(alignment: .leading, spacing: 4) {
                    Text(row.joined(separator: ", "))
                        .font(.body)
                        .padding(.vertical, 8)
                        .padding(.horizontal, 12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(index % 2 == 0 ? Color.clear : Color.secondary.opacity(0.05))
                        .cornerRadius(6)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Row \(index + 1): \(row.joined(separator: ", "))")
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
    
    // MARK: - Full List View
    private var fullListView: some View {
        VStack(alignment: .leading, spacing: 16) {
            ForEach(Array(rows.enumerated()), id: \.offset) { index, row in
                VStack(alignment: .leading, spacing: 6) {
                    Text("Item \(index + 1)")
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    ForEach(Array(row.enumerated()), id: \.offset) { colIndex, value in
                        HStack(alignment: .top) {
                            Text("\(headers[colIndex]):")
                                .font(.caption)
                                .fontWeight(.semibold)
                                .foregroundColor(.secondary)
                                .frame(width: 100, alignment: .leading)
                            
                            Text(value)
                                .font(.caption)
                                .foregroundColor(.primary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                }
                .padding(12)
                .background(Color.secondary.opacity(0.05))
                .cornerRadius(8)
                .accessibilityElement(children: .combine)
                .accessibilityLabel(createFullAccessibilityLabel(for: row, at: index))
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
    
    // MARK: - Accessibility Helpers
    private func createAccessibilityLabel(for row: [String], at index: Int) -> String {
        let pairs = zip(headers, row).map { "\($0): \($1)" }
        return "Row \(index + 1). " + pairs.joined(separator: "; ")
    }
    
    private func createFullAccessibilityLabel(for row: [String], at index: Int) -> String {
        let pairs = zip(headers, row).map { "\($0): \($1)" }
        return "Item \(index + 1). " + pairs.joined(separator: "; ")
    }
}

// MARK: - Standings-Specific Table View
struct StandingsTableView: View {
    let standingsGroups: [StandingsGroup]
    let sport: Sport
    @State private var viewMode: ViewMode = .table
    @State private var showExpanded = false

    // MARK: Column definitions

    private var basicHeaders: [String] { ["Team", "W", "L", "PCT", "GB", "Streak"] }

    private var expandedHeaders: [String] {
        switch sport {
        case .mlb:  return ["Team", "W", "L", "PCT", "GB", "R", "RA", "Diff", "Home", "Road", "L10"]
        case .nfl:  return ["Team", "W", "L", "T", "PCT", "PF", "PA", "Diff", "Div", "Seed"]
        case .nba:  return ["Team", "W", "L", "PCT", "GB", "PPG", "Opp", "Diff", "Seed"]
        case .nhl:  return ["Team", "W", "L", "OTL", "PTS", "GF", "GA", "Diff", "Seed"]
        default:    return basicHeaders
        }
    }

    private var activeHeaders: [String] { showExpanded ? expandedHeaders : basicHeaders }

    private func rowData(for entry: StandingsEntry) -> [String] {
        let s = entry.stats
        if !showExpanded {
            return [entry.team.abbreviation,
                    "\(s.wins)", "\(s.losses)",
                    s.displayWinPercent, s.gamesBack, s.streak]
        }
        switch sport {
        case .mlb:
            return [entry.team.abbreviation,
                    "\(s.wins)", "\(s.losses)", s.displayWinPercent, s.gamesBack,
                    "\(s.pointsFor ?? 0)", "\(s.pointsAgainst ?? 0)",
                    s.differential ?? "-",
                    s.homeRecord ?? "-", s.roadRecord ?? "-", s.lastTenRecord ?? "-"]
        case .nfl:
            return [entry.team.abbreviation,
                    "\(s.wins)", "\(s.losses)", "\(s.ties ?? 0)", s.displayWinPercent,
                    "\(s.pointsFor ?? 0)", "\(s.pointsAgainst ?? 0)",
                    s.differential ?? "-",
                    s.divisionRecord ?? "-",
                    s.playoffSeed.map { "\($0)" } ?? "-"]
        case .nba:
            return [entry.team.abbreviation,
                    "\(s.wins)", "\(s.losses)", s.displayWinPercent, s.gamesBack,
                    String(format: "%.1f", s.avgPointsFor ?? 0),
                    String(format: "%.1f", s.avgPointsAgainst ?? 0),
                    s.differential ?? "-",
                    s.playoffSeed.map { "\($0)" } ?? "-"]
        case .nhl:
            return [entry.team.abbreviation,
                    "\(s.wins)", "\(s.losses)", "\(s.otLosses ?? 0)",
                    "\(s.nhlPoints ?? 0)",
                    "\(s.pointsFor ?? 0)", "\(s.pointsAgainst ?? 0)",
                    s.differential ?? "-",
                    s.playoffSeed.map { "\($0)" } ?? "-"]
        default:
            return [entry.team.abbreviation,
                    "\(s.wins)", "\(s.losses)",
                    s.displayWinPercent, s.gamesBack, s.streak]
        }
    }

    /// Same as `rowData(for:)` but uses the full team display name in column 0
    /// — used by the UIKit accessibility table overlay so VoiceOver speaks the
    /// full name ("Los Angeles Dodgers") rather than the abbreviation ("LAD").
    private func accessibleRowData(for entry: StandingsEntry) -> [String] {
        var cols = rowData(for: entry)
        if !cols.isEmpty { cols[0] = entry.team.displayName }
        return cols
    }

    var body: some View {
        VStack(spacing: 0) {
            ViewModePicker(selectedMode: $viewMode)
                .padding(.vertical, 8)

            Divider()

            // Single vertical ScrollView — NO nested vertical scroll views
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 0, pinnedViews: [.sectionHeaders]) {
                    ForEach(standingsGroups) { group in
                        Section {
                            switch viewMode {
                            case .table:
                                // Horizontal scroll only in expanded mode
                                if showExpanded {
                                    ScrollView(.horizontal, showsIndicators: true) {
                                        standingsTableSection(for: group)
                                    }
                                } else {
                                    standingsTableSection(for: group)
                                }
                            case .quickList:
                                quickListSection(for: group)
                            case .fullList:
                                fullListSection(for: group)
                            }
                        } header: {
                            Text(group.name)
                                .font(.headline)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(.horizontal)
                                .padding(.vertical, 8)
                                .background(Color(uiColor: .systemBackground))
                                .accessibilityAddTraits(.isHeader)
                        }
                    }
                }
            }
        }
        .toolbar {
            ToolbarItemGroup(placement: .navigationBarTrailing) {
                if viewMode == .table {
                    Button {
                        withAnimation { showExpanded.toggle() }
                    } label: {
                        Label(showExpanded ? "Basic" : "Expand",
                              systemImage: showExpanded ? "arrow.down.right.and.arrow.up.left" : "arrow.up.left.and.arrow.down.right")
                        .labelStyle(.iconOnly)
                    }
                    .accessibilityLabel(showExpanded ? "Show basic columns" : "Show expanded columns")
                }
                ViewModeToggleButton(currentMode: $viewMode)
            }
        }
    }

    // MARK: - Table mode

    private func standingsTableSection(for group: StandingsGroup) -> some View {
        VStack(spacing: 0) {
            // Header row — derived from activeHeaders
            HStack(spacing: 0) {
                Text(activeHeaders[0])     // "Team" — flexible width
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

            ForEach(Array(group.entries.enumerated()), id: \.element.id) { idx, entry in
                let cols = rowData(for: entry)
                HStack(spacing: 0) {
                    Text(cols[0])   // Team abbreviation — flexible
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
                // Row is hidden from VoiceOver; AccessibleDataTable overlay
                // handles all accessibility navigation for the table view.
                .accessibilityHidden(true)

                if idx < group.entries.count - 1 {
                    Divider().padding(.leading, 8)
                }
            }
        }
        .accessibilityHidden(true) // UIKit overlay handles VoiceOver for table mode
        .overlay(
            AccessibleDataTable(
                headers: activeHeaders,
                rows: group.entries.map { accessibleRowData(for: $0) }
            )
            .allowsHitTesting(false)
        )
        .padding(.bottom, 16)
    }

    // MARK: - Quick List mode

    private func quickListSection(for group: StandingsGroup) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            ForEach(group.entries) { entry in
                Text(entry.quickListText)
                    .font(.subheadline)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 6)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .accessibilityLabel(entry.quickListText)
            }
        }
        .padding(.bottom, 16)
    }

    // MARK: - Full List mode

    private func fullListSection(for group: StandingsGroup) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            ForEach(group.entries) { entry in
                VStack(alignment: .leading, spacing: 4) {
                    Text(entry.team.displayName)
                        .font(.headline)
                    Text(entry.fullListText)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.secondary.opacity(0.05))
                .cornerRadius(8)
                .padding(.horizontal, 12)
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(entry.fullListText)
            }
        }
        .padding(.bottom, 16)
    }
}

// MARK: - Preview
#Preview {
    NavigationView {
        DataTableView(
            headers: ["Rank", "Team", "W", "L"],
            rows: [
                ["1", "LAD", "95", "67"],
                ["2", "ARI", "84", "78"],
                ["3", "SD", "82", "80"]
            ]
        )
        .navigationTitle("Example Table")
    }
}
