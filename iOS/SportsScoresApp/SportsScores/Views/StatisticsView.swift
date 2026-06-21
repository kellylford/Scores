//
//  StatisticsView.swift
//  SportsScores
//
//  Phase 5 — League leaders / season statistics.
//  Two tabs: Players (individual leaders) and Teams (team-level leaders).
//  Each category shows the top 10 with a "View All" link to the full list.
//

import SwiftUI

private enum StatsTab: String, CaseIterable {
    case players = "Players"
    case teams   = "Teams"
}

struct StatisticsView: View {
    let sport: Sport
    @StateObject private var viewModel = StatisticsViewModel()
    @State private var viewMode: ViewMode = .quickList
    @State private var statsTab: StatsTab = .players

    var body: some View {
        VStack(spacing: 0) {
            Picker("Stats Type", selection: $statsTab) {
                ForEach(StatsTab.allCases, id: \.self) { tab in
                    Text(tab.rawValue).tag(tab)
                }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)
            .padding(.top, 8)
            .padding(.bottom, 4)

            Group {
                switch statsTab {
                case .players: playerContent
                case .teams:   teamContent
                }
            }
        }
        .task { await viewModel.fetchLeaders(for: sport) }
        .refreshable { await viewModel.refresh(for: sport) }
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                ViewModeMenuButton(currentMode: $viewMode)
            }
        }
    }

    // MARK: - Tab content

    @ViewBuilder
    private var playerContent: some View {
        if viewModel.isLoadingPlayers {
            ProgressView("Loading statistics…")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if let error = viewModel.playerError {
            errorState(message: error) { Task { await viewModel.fetchLeaders(for: sport) } }
        } else if viewModel.playerCategories.isEmpty {
            emptyState(icon: "chart.bar.xaxis", text: "No player statistics available")
        } else {
            categoryScrollList(viewModel.playerCategories)
        }
    }

    @ViewBuilder
    private var teamContent: some View {
        if viewModel.isLoadingTeams {
            ProgressView("Loading team statistics…")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if let error = viewModel.teamError {
            errorState(message: error) { Task { await viewModel.fetchLeaders(for: sport) } }
        } else if viewModel.teamCategories.isEmpty {
            emptyState(icon: "building.2", text: "No team statistics available")
        } else {
            categoryScrollList(viewModel.teamCategories)
        }
    }

    // MARK: - Category scroll list

    private func categoryScrollList(_ categories: [LeagueLeaderCategory]) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                ForEach(categories) { category in
                    VStack(alignment: .leading, spacing: 0) {
                        LeaderCategorySection(category: category, viewMode: viewMode)

                        // View All button — shown when we hit the fetch limit (likely more data exists)
                        if category.leaders.count >= 10 {
                            NavigationLink {
                                StatLeaderDetailView(
                                    category: category,
                                    sport: sport,
                                    initialViewMode: viewMode
                                )
                            } label: {
                                HStack(spacing: 4) {
                                    Spacer()
                                    Text("View All \(category.displayName)")
                                        .font(.subheadline)
                                        .foregroundColor(.accentColor)
                                    Image(systemName: "chevron.right")
                                        .font(.caption2)
                                        .foregroundColor(.accentColor)
                                    Spacer()
                                }
                                .padding(.vertical, 8)
                                .accessibilityLabel("View all \(category.displayName) leaders")
                            }
                        }
                    }
                }
            }
            .padding()
        }
    }

    // MARK: - States

    private func errorState(message: String, retry: @escaping () -> Void) -> some View {
        ErrorStateView(message: message, retryAction: retry)
    }

    private func emptyState(icon: String, text: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text(text)
                .font(.headline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// MARK: - Shared category section view

/// Renders a single stat category (header + leader rows) in the current view mode.
/// Used by both StatisticsView (summary) and StatLeaderDetailView (full list).
struct LeaderCategorySection: View {
    let category: LeagueLeaderCategory
    let viewMode: ViewMode

    private var hasTeams: Bool {
        category.leaders.contains { !$0.teamAbbreviation.isEmpty }
    }

    /// Column headers: "Team" replaces "Player" for team-stat categories.
    private var entityHeader: String { category.isTeamCategory ? "Team" : "Player" }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(category.displayName)
                .font(.headline)
                .foregroundColor(.primary)
                .accessibilityAddTraits(.isHeader)

            switch viewMode {
            case .table:
                tableSection
            case .quickList:
                quickListSection
            case .fullList:
                fullListSection
            }
        }
    }

    // MARK: Table

    @ViewBuilder
    private var tableSection: some View {
        let headers  = hasTeams ? ["Rank", entityHeader, "Team", "Value"] : ["Rank", entityHeader, "Value"]
        let rows = category.leaders.map { entry -> [String] in
            hasTeams
                ? ["\(entry.rank)", entry.athleteName, entry.teamAbbreviation, entry.displayValue]
                : ["\(entry.rank)", entry.athleteName, entry.displayValue]
        }

        VStack(spacing: 0) {
            HStack(spacing: 0) {
                Text("Rank")
                    .font(.caption.bold()).foregroundColor(.secondary)
                    .frame(width: 50, alignment: .trailing)
                Text(entityHeader)
                    .font(.caption.bold()).foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading).padding(.leading, 12)
                if hasTeams {
                    Text("Team")
                        .font(.caption.bold()).foregroundColor(.secondary)
                        .frame(width: 60, alignment: .center)
                }
                Text("Value")
                    .font(.caption.bold()).foregroundColor(.secondary)
                    .frame(width: 70, alignment: .trailing)
            }
            .padding(.horizontal, 12).padding(.vertical, 6)
            .background(Color.secondary.opacity(0.12))
            .accessibilityHidden(true)

            ForEach(Array(category.leaders.enumerated()), id: \.element.id) { idx, entry in
                HStack(spacing: 0) {
                    Text("\(entry.rank)")
                        .font(.caption.bold()).monospacedDigit()
                        .frame(width: 50, alignment: .trailing)
                        .foregroundColor(rankColor(entry.rank))
                    Text(entry.athleteName)
                        .font(.subheadline)
                        .frame(maxWidth: .infinity, alignment: .leading).padding(.leading, 12)
                        .lineLimit(1)
                    if hasTeams {
                        Text(entry.teamAbbreviation)
                            .font(.caption).foregroundColor(.secondary)
                            .frame(width: 60, alignment: .center)
                    }
                    Text(entry.displayValue)
                        .font(.subheadline.bold()).monospacedDigit()
                        .frame(width: 70, alignment: .trailing)
                }
                .padding(.horizontal, 12).padding(.vertical, 6)
                .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
                .accessibilityHidden(true)
            }
        }
        .background(Color.secondary.opacity(0.04))
        .cornerRadius(8)
        .accessibilityHidden(true)
        .overlay(
            AccessibleDataTable(headers: headers, rows: rows)
                .allowsHitTesting(false)
        )
    }

    // MARK: Quick list

    private var quickListSection: some View {
        VStack(alignment: .leading, spacing: 2) {
            ForEach(Array(category.leaders.enumerated()), id: \.element.id) { idx, entry in
                HStack {
                    Text("#\(entry.rank)")
                        .font(.caption.bold()).foregroundColor(.secondary)
                        .monospacedDigit().frame(width: 36, alignment: .trailing)
                    Text(entry.athleteName)
                        .font(.subheadline)
                    if hasTeams {
                        Text(entry.teamAbbreviation)
                            .font(.caption).foregroundColor(.secondary)
                    }
                    Spacer()
                    Text(entry.displayValue)
                        .font(.subheadline.bold()).monospacedDigit()
                }
                .padding(.horizontal, 12).padding(.vertical, 5)
                .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(
                    "#\(entry.rank) \(entry.athleteName)\(hasTeams ? " \(entry.teamAbbreviation)" : "") — \(entry.displayValue)"
                )
            }
        }
        .background(Color.secondary.opacity(0.04))
        .cornerRadius(8)
    }

    // MARK: Full list
    // Visually identical to Quick List. The only difference is the VoiceOver
    // accessibility label includes label words ("Rank N, Player: Name, Value: .350")
    // so users who need that context get it without a different visual layout.

    private var fullListSection: some View {
        VStack(alignment: .leading, spacing: 2) {
            ForEach(Array(category.leaders.enumerated()), id: \.element.id) { idx, entry in
                HStack {
                    Text("#\(entry.rank)")
                        .font(.caption.bold()).foregroundColor(.secondary)
                        .monospacedDigit().frame(width: 36, alignment: .trailing)
                    Text(entry.athleteName)
                        .font(.subheadline)
                    if hasTeams {
                        Text(entry.teamAbbreviation)
                            .font(.caption).foregroundColor(.secondary)
                    }
                    Spacer()
                    Text(entry.displayValue)
                        .font(.subheadline.bold()).monospacedDigit()
                }
                .padding(.horizontal, 12).padding(.vertical, 5)
                .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(
                    "Rank \(entry.rank), \(entityHeader): \(entry.athleteName)\(hasTeams ? ", Team: \(entry.teamAbbreviation)" : ""), Value: \(entry.displayValue)"
                )
            }
        }
        .background(Color.secondary.opacity(0.04))
        .cornerRadius(8)
    }

    // MARK: Helpers

    private func rankColor(_ rank: Int) -> Color {
        switch rank {
        case 1:  return .yellow
        case 2:  return Color(.systemGray2)
        case 3:  return .orange
        default: return .secondary
        }
    }
}

#Preview {
    NavigationStack {
        StatisticsView(sport: .mlb)
            .navigationTitle("MLB Statistics")
    }
}
