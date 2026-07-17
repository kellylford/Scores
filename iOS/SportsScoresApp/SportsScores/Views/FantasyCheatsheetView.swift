//
//  FantasyCheatsheetView.swift
//  SportsScores
//
//  NFL fantasy football cheatsheet. Lists fantasy-relevant players + team
//  defenses, sortable by several stat categories, filterable by position,
//  with a taken/available toggle for live drafts and user-configurable
//  scoring settings that re-rank instantly.
//
//  Three view modes (Quick List / Full List / Table) per DESIGN_PRINCIPLES.md.
//  Table mode uses AccessibleDataTable for VoiceOver row/column navigation.
//
//  Data note: ranks by a stats-derived points value (last completed season),
//  NOT by ADP or expert consensus — ESPN's public API exposes no ADP/projections.
//

import SwiftUI

struct FantasyCheatsheetView: View {
    @StateObject private var viewModel = FantasyCheatsheetViewModel()
    @State private var viewMode: ViewMode = .quickList
    @State private var showingSettings = false

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading fantasy data…")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = viewModel.errorMessage {
                ErrorStateView(message: error) { Task { await viewModel.loadAll() } }
            } else {
                content
            }
        }
        .navigationTitle("Fantasy Cheatsheet")
        .navigationBarTitleDisplayMode(.inline)
        .searchable(text: $viewModel.searchQuery, prompt: "Search player or team")
        .task { if viewModel.offensivePlayers.isEmpty { await viewModel.loadAll() } }
        .toolbar {
            ToolbarItemGroup(placement: .navigationBarTrailing) {
                Menu {
                    Picker("Sort", selection: $viewModel.selectedSort) {
                        ForEach(CheatsheetSort.allCases) { sort in
                            Text(sort.rawValue).tag(sort)
                        }
                    }
                } label: {
                    Label("Sort", systemImage: "arrow.up.arrow.down")
                }

                Button {
                    showingSettings = true
                } label: {
                    Image(systemName: "slider.horizontal.3")
                }
                .accessibilityLabel("Scoring settings")

                ViewModeMenuButton(currentMode: $viewMode)
            }
        }
        .sheet(isPresented: $showingSettings) {
            NavigationStack {
                ScoringSettingsView(viewModel: viewModel)
            }
        }
    }

    // MARK: - Content

    private var content: some View {
        VStack(spacing: 0) {
            positionFilterBar
            seasonBanner
            Divider()
            if viewModel.displayedRows.isEmpty {
                emptyState
            } else {
                cheatsheetBody
            }
        }
    }

    // MARK: - Position filter chips

    private var positionFilterBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(FantasyPosition.allCases) { pos in
                    positionChip(pos)
                }
                Divider().frame(height: 18).padding(.horizontal, 4)
                Button {
                    viewModel.selectAllPositions()
                } label: {
                    Text("All")
                        .font(.caption.bold())
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Capsule().fill(Color.accentColor.opacity(0.12)))
                }
                .accessibilityLabel("Select all positions")
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
        }
    }

    private func positionChip(_ pos: FantasyPosition) -> some View {
        let selected = viewModel.selectedPositions.contains(pos)
        return Button {
            viewModel.togglePosition(pos)
        } label: {
            Text(pos.displayName)
                .font(.caption.bold())
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(
                    Capsule().fill(selected ? Color.accentColor.opacity(0.18) : Color.secondary.opacity(0.10))
                )
                .foregroundColor(selected ? .accentColor : .primary)
        }
        .accessibilityLabel("\(pos.displayName) filter")
        .accessibilityValue(selected ? "on" : "off")
    }

    // MARK: - Season banner

    private var seasonBanner: some View {
        HStack {
            Image(systemName: "info.circle")
                .foregroundColor(.secondary)
            Text("Based on \(viewModel.statsSeason) NFL regular-season stats")
                .font(.caption)
                .foregroundColor(.secondary)
            Spacer()
            Toggle("Hide taken", isOn: $viewModel.hideTaken)
                .toggleStyle(.switch)
                .labelsHidden()
                .accessibilityLabel("Hide drafted players")
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 6)
    }

    // MARK: - Body (view mode switch)

    @ViewBuilder
    private var cheatsheetBody: some View {
        switch viewMode {
        case .table:     tableView
        case .quickList: listView(fullLabels: false)
        case .fullList:  listView(fullLabels: true)
        }
    }

    // MARK: - List modes (Quick / Full)

    private func listView(fullLabels: Bool) -> some View {
        List {
            ForEach(viewModel.displayedRows) { row in
                listRow(row, fullLabels: fullLabels)
                    .swipeActions(edge: .trailing) {
                        Button {
                            viewModel.toggleTaken(row)
                        } label: {
                            Label(viewModel.isTaken(row) ? "Available" : "Taken",
                                   systemImage: viewModel.isTaken(row) ? "checkmark.circle" : "checkmark.circle.fill")
                        }
                        .tint(viewModel.isTaken(row) ? .green : .gray)
                    }
                    .accessibilityAction(named: viewModel.isTaken(row) ? "Mark available" : "Mark taken") {
                        viewModel.toggleTaken(row)
                    }
            }
        }
        .listStyle(.plain)
        .overlay {
            if viewModel.isEnriching {
                VStack {
                    ProgressView("Enriching top players…")
                        .padding(12)
                        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 10))
                    Spacer()
                }
                .padding(.top, 12)
            }
        }
    }

    private func listRow(_ row: CheatsheetRow, fullLabels: Bool) -> some View {
        HStack(spacing: 12) {
            // Taken indicator
            Image(systemName: viewModel.isTaken(row) ? "checkmark.circle.fill" : "circle")
                .foregroundColor(viewModel.isTaken(row) ? .green : .secondary)
                .accessibilityHidden(true)

            VStack(alignment: .leading, spacing: 2) {
                Text(row.displayName)
                    .font(.subheadline.weight(.medium))
                    .strikethrough(viewModel.isTaken(row), color: .secondary)
                Text("\(row.positionLabel) · \(row.teamAbbreviation)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()

            Text(row.pointsString(settings: viewModel.scoringSettings))
                .font(.system(.subheadline, design: .monospaced).bold())
                .foregroundColor(.accentColor)
        }
        .padding(.vertical, 4)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(listVoiceOverLabel(row, fullLabels: fullLabels))
    }

    private func listVoiceOverLabel(_ row: CheatsheetRow, fullLabels: Bool) -> String {
        let taken = viewModel.isTaken(row) ? ", taken" : ""
        let pts = row.pointsString(settings: viewModel.scoringSettings)
        let name = row.displayName
        let pos = row.positionLabel
        let team = row.teamAbbreviation

        if fullLabels {
            return "Player: \(name), Position: \(pos), Team: \(team), Points: \(pts)\(taken)"
        } else {
            return "\(name) \(pos) \(team) — \(pts)\(taken)"
        }
    }

    // MARK: - Table mode

    private var tableView: some View {
        let rows = viewModel.displayedRows
        let headers = ["Rank", "Player", "Pos", "Team", "Pts"]

        return ScrollView {
            VStack(spacing: 0) {
                // Column header row
                HStack(spacing: 0) {
                    Text("Rank").frame(width: 44, alignment: .trailing)
                    Text("Player").frame(maxWidth: .infinity, alignment: .leading).padding(.leading, 12)
                    Text("Pos").frame(width: 44, alignment: .center)
                    Text("Team").frame(width: 50, alignment: .leading)
                    Text("Pts").frame(width: 56, alignment: .trailing)
                }
                .font(.caption.bold())
                .foregroundColor(.secondary)
                .padding(.vertical, 6)
                .padding(.horizontal, 16)
                .background(Color.secondary.opacity(0.10))

                Divider()

                VStack(spacing: 0) {
                    ForEach(Array(rows.enumerated()), id: \.element.id) { idx, row in
                        tableEntryRow(row, rank: idx + 1)
                        if idx < rows.count - 1 {
                            Divider().padding(.leading, 16)
                        }
                    }
                }
                .accessibilityHidden(true)
                .overlay(
                    AccessibleDataTable(
                        headers: headers,
                        rows: rows.enumerated().map { i, row in
                            [String(i + 1), row.displayName, row.positionLabel, row.teamAbbreviation, row.pointsString(settings: viewModel.scoringSettings)]
                        }
                    )
                    .allowsHitTesting(false)
                )
            }
        }
    }

    private func tableEntryRow(_ row: CheatsheetRow, rank: Int) -> some View {
        HStack(spacing: 0) {
            Text("\(rank)")
                .font(.system(.body, design: .monospaced))
                .frame(width: 44, alignment: .trailing)

            Text(row.displayName)
                .font(.body)
                .lineLimit(1)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.leading, 12)
                .strikethrough(viewModel.isTaken(row), color: .secondary)

            Text(row.positionLabel)
                .font(.caption)
                .frame(width: 44, alignment: .center)
                .foregroundColor(.secondary)

            Text(row.teamAbbreviation)
                .font(.caption)
                .frame(width: 50, alignment: .leading)
                .foregroundColor(.secondary)

            Text(row.pointsString(settings: viewModel.scoringSettings))
                .font(.system(.body, design: .monospaced).bold())
                .frame(width: 56, alignment: .trailing)
                .foregroundColor(.accentColor)
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 16)
        .background(rank % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
        .accessibilityHidden(true)  // exposed via AccessibleDataTable overlay
    }

    // MARK: - Empty state

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "american.football")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("No players match the current filters")
                .font(.headline)
                .foregroundColor(.secondary)
            if viewModel.totalPlayerCount > 0 {
                Text("\(viewModel.totalPlayerCount) players loaded · \(viewModel.displayedCount) shown")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

#Preview {
    NavigationStack { FantasyCheatsheetView() }
}