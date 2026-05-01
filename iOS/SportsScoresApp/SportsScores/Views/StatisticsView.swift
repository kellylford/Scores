//
//  StatisticsView.swift
//  SportsScores
//
//  Phase 5 — League leaders / season statistics.
//  Shows current-season stat leaders per category for any sport.
//

import SwiftUI

struct StatisticsView: View {
    let sport: Sport
    @StateObject private var viewModel = StatisticsViewModel()
    @State private var viewMode: ViewMode = .table

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading statistics…")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = viewModel.errorMessage {
                errorState(message: error)
            } else if viewModel.categories.isEmpty {
                emptyState
            } else {
                leadersList
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

    // MARK: - Leaders list

    private var leadersList: some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    ForEach(viewModel.categories) { category in
                        categorySection(category)
                    }
                }
                .padding()
            }
        }
    }
    
    private func categorySection(_ category: LeagueLeaderCategory) -> some View {
        let hasTeams = category.leaders.contains { !$0.teamAbbreviation.isEmpty }
        let headers  = hasTeams ? ["Rank", "Player", "Team", "Value"] : ["Rank", "Player", "Value"]
        let rows = category.leaders.map { entry -> [String] in
            hasTeams
                ? ["\(entry.rank)", entry.athleteName, entry.teamAbbreviation, entry.displayValue]
                : ["\(entry.rank)", entry.athleteName, entry.displayValue]
        }

        return VStack(alignment: .leading, spacing: 8) {
            Text(category.displayName)
                .font(.headline)
                .foregroundColor(.primary)
                .accessibilityAddTraits(.isHeader)

            switch viewMode {
            case .table:
                statsTableSection(category: category, headers: headers, rows: rows, hasTeams: hasTeams)
            case .quickList:
                statsQuickListSection(category: category, hasTeams: hasTeams)
            case .fullList:
                statsFullListSection(category: category, hasTeams: hasTeams)
            }
        }
    }

    @ViewBuilder
    private func statsTableSection(category: LeagueLeaderCategory, headers: [String], rows: [[String]], hasTeams: Bool) -> some View {
        VStack(spacing: 0) {
            // Header row
            HStack(spacing: 0) {
                Text("Rank")
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
                    .frame(width: 50, alignment: .trailing)
                Text("Player")
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.leading, 12)
                if hasTeams {
                    Text("Team")
                        .font(.caption.bold())
                        .foregroundColor(.secondary)
                        .frame(width: 60, alignment: .center)
                }
                Text("Value")
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
                    .frame(width: 70, alignment: .trailing)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(Color.secondary.opacity(0.12))
            .accessibilityHidden(true)

            // Data rows
            ForEach(Array(category.leaders.enumerated()), id: \.element.id) { idx, entry in
                HStack(spacing: 0) {
                    Text("\(entry.rank)")
                        .font(.caption.bold())
                        .monospacedDigit()
                        .frame(width: 50, alignment: .trailing)
                        .foregroundColor(rankColor(entry.rank))
                    Text(entry.athleteName)
                        .font(.subheadline)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.leading, 12)
                        .lineLimit(1)
                    if hasTeams {
                        Text(entry.teamAbbreviation)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .frame(width: 60, alignment: .center)
                    }
                    Text(entry.displayValue)
                        .font(.subheadline.bold())
                        .monospacedDigit()
                        .frame(width: 70, alignment: .trailing)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
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

    @ViewBuilder
    private func statsQuickListSection(category: LeagueLeaderCategory, hasTeams: Bool) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            ForEach(Array(category.leaders.enumerated()), id: \.element.id) { idx, entry in
                HStack {
                    Text("#\(entry.rank)")
                        .font(.caption.bold())
                        .foregroundColor(.secondary)
                        .monospacedDigit()
                        .frame(width: 36, alignment: .trailing)
                    Text(entry.athleteName)
                        .font(.subheadline)
                    if hasTeams {
                        Text(entry.teamAbbreviation)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    Spacer()
                    Text(entry.displayValue)
                        .font(.subheadline.bold())
                        .monospacedDigit()
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 5)
                .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
                .accessibilityLabel("#\(entry.rank) \(entry.athleteName)\(hasTeams ? " \(entry.teamAbbreviation)" : "") — \(entry.displayValue)")
            }
        }
        .background(Color.secondary.opacity(0.04))
        .cornerRadius(8)
    }

    @ViewBuilder
    private func statsFullListSection(category: LeagueLeaderCategory, hasTeams: Bool) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            ForEach(category.leaders) { entry in
                VStack(alignment: .leading, spacing: 4) {
                    Text(entry.athleteName)
                        .font(.headline)
                    HStack(alignment: .top) {
                        Text("Rank:")
                            .font(.caption.bold())
                            .foregroundColor(.secondary)
                            .frame(width: 80, alignment: .leading)
                        Text("#\(entry.rank)")
                            .font(.caption)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    if hasTeams {
                        HStack(alignment: .top) {
                            Text("Team:")
                                .font(.caption.bold())
                                .foregroundColor(.secondary)
                                .frame(width: 80, alignment: .leading)
                            Text(entry.teamAbbreviation)
                                .font(.caption)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                    HStack(alignment: .top) {
                        Text("Value:")
                            .font(.caption.bold())
                            .foregroundColor(.secondary)
                            .frame(width: 80, alignment: .leading)
                        Text(entry.displayValue)
                            .font(.caption)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
                .padding(12)
                .background(Color.secondary.opacity(0.05))
                .cornerRadius(8)
                .accessibilityElement(children: .combine)
                .accessibilityLabel("#\(entry.rank) \(entry.athleteName)\(hasTeams ? ", \(entry.teamAbbreviation)" : ""), \(entry.displayValue)")
            }
        }
    }

    
    private func rankColor(_ rank: Int) -> Color {
        switch rank {
        case 1: return .yellow
        case 2: return Color(.systemGray2)
        case 3: return .orange
        default: return .secondary
        }
    }

    // MARK: - States

    private func errorState(message: String) -> some View {
        ErrorStateView(message: message) { Task { await viewModel.fetchLeaders(for: sport) } }
    }

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "chart.bar.xaxis")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("No statistics available")
                .font(.headline)
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    NavigationStack {
        StatisticsView(sport: .nfl)
            .navigationTitle("NFL Leaders")
    }
}
