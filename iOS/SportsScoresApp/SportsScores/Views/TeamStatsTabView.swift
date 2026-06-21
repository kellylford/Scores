//
//  TeamStatsTabView.swift
//  SportsScores
//
//  Stats tab for the Team Hub. Two sub-tabs:
//    Players — leaders on this team in each stat category (no View All needed)
//    Team    — this team's rank in each league-wide stat category
//

import SwiftUI

struct TeamStatsTabView: View {
    let teamId: String
    let teamAbbreviation: String
    let sport: Sport

    @StateObject private var viewModel = TeamStatsViewModel()
    @State private var viewMode: ViewMode = .quickList
    @State private var subTab: SubTab = .players

    private enum SubTab: String, CaseIterable {
        case players = "Players"
        case team    = "Team"
    }

    var body: some View {
        VStack(spacing: 0) {
            Picker("Stats Type", selection: $subTab) {
                ForEach(SubTab.allCases, id: \.self) { t in
                    Text(t.rawValue).tag(t)
                }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)
            .padding(.top, 8)
            .padding(.bottom, 4)

            Group {
                switch subTab {
                case .players: playerContent
                case .team:    teamContent
                }
            }
        }
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                if subTab == .players {
                    ViewModeMenuButton(currentMode: $viewMode)
                }
            }
        }
        .task { await viewModel.load(teamId: teamId, teamAbbreviation: teamAbbreviation, sport: sport) }
    }

    // MARK: - Player sub-tab

    @ViewBuilder
    private var playerContent: some View {
        if viewModel.isLoadingPlayers {
            ProgressView("Loading player stats…")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if let error = viewModel.playerError {
            ErrorStateView(message: error) {
                Task { await viewModel.load(teamId: teamId, teamAbbreviation: teamAbbreviation, sport: sport) }
            }
        } else if viewModel.playerCategories.isEmpty {
            emptyState(icon: "chart.bar.xaxis", text: "No player statistics available")
        } else {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    ForEach(viewModel.playerCategories) { category in
                        LeaderCategorySection(category: category, viewMode: viewMode)
                    }
                }
                .padding()
            }
        }
    }

    // MARK: - Team sub-tab

    @ViewBuilder
    private var teamContent: some View {
        if viewModel.isLoadingTeamRankings {
            ProgressView("Loading team stats…")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if let error = viewModel.teamError {
            ErrorStateView(message: error) {
                Task { await viewModel.load(teamId: teamId, teamAbbreviation: teamAbbreviation, sport: sport) }
            }
        } else if viewModel.teamRankings.isEmpty {
            emptyState(icon: "building.2", text: "No team statistics available")
        } else {
            teamRankingsList
        }
    }

    private var teamRankingsList: some View {
        // Group by sectionName (Batting / Pitching / etc.)
        let sections = Dictionary(grouping: viewModel.teamRankings, by: \.sectionName)
        let sectionOrder = viewModel.teamRankings.map(\.sectionName).reduce(into: [String]()) {
            if !$0.contains($1) { $0.append($1) }
        }

        return ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                ForEach(sectionOrder, id: \.self) { section in
                    let rankings = sections[section] ?? []
                    let rows = rankings.map { r in [r.categoryDisplayName, r.teamValue, r.rankDisplay] }
                    let headers = ["Category", "Value", "Rank"]

                    VStack(alignment: .leading, spacing: 0) {
                        Text(section)
                            .font(.headline)
                            .padding(.bottom, 6)
                            .accessibilityAddTraits(.isHeader)

                        VStack(spacing: 0) {
                            // Column header
                            HStack(spacing: 0) {
                                Text("Category")
                                    .font(.caption.bold()).foregroundColor(.secondary)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                Text("Value")
                                    .font(.caption.bold()).foregroundColor(.secondary)
                                    .frame(width: 70, alignment: .trailing)
                                Text("Rank")
                                    .font(.caption.bold()).foregroundColor(.secondary)
                                    .frame(width: 80, alignment: .trailing)
                            }
                            .padding(.horizontal, 12).padding(.vertical, 6)
                            .background(Color.secondary.opacity(0.12))
                            .accessibilityHidden(true)

                            ForEach(Array(rankings.enumerated()), id: \.element.id) { idx, ranking in
                                HStack(spacing: 0) {
                                    Text(ranking.categoryDisplayName)
                                        .font(.subheadline)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                    Text(ranking.teamValue)
                                        .font(.subheadline.bold()).monospacedDigit()
                                        .frame(width: 70, alignment: .trailing)
                                    Text(ranking.rankDisplay)
                                        .font(.subheadline)
                                        .foregroundColor(rankColor(ranking.leagueRank))
                                        .frame(width: 80, alignment: .trailing)
                                }
                                .padding(.horizontal, 12).padding(.vertical, 7)
                                .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
                                .accessibilityElement(children: .ignore)
                                .accessibilityLabel("\(ranking.categoryDisplayName): \(ranking.teamValue), \(ranking.rankDisplay)")
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
                }
            }
            .padding()
        }
    }

    // MARK: - Helpers

    private func rankColor(_ rank: Int) -> Color {
        if rank <= 8  { return .green }
        if rank <= 20 { return .primary }
        return Color(.systemRed)
    }

    private func emptyState(icon: String, text: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 48)).foregroundColor(.secondary)
            Text(text)
                .font(.headline).foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
