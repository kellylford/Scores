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
        let rows = viewModel.teamRankings.map { r in
            [r.categoryDisplayName, r.teamValue, ordinal(r.leagueRank)]
        }
        let headers = ["Category", "Value", "Rank"]

        return ScrollView {
            VStack(spacing: 0) {
                // Header row
                HStack(spacing: 0) {
                    Text("Category")
                        .font(.caption.bold()).foregroundColor(.secondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    Text("Value")
                        .font(.caption.bold()).foregroundColor(.secondary)
                        .frame(width: 70, alignment: .trailing)
                    Text("Rank")
                        .font(.caption.bold()).foregroundColor(.secondary)
                        .frame(width: 60, alignment: .trailing)
                }
                .padding(.horizontal, 16).padding(.vertical, 8)
                .background(Color.secondary.opacity(0.12))
                .accessibilityHidden(true)

                ForEach(Array(viewModel.teamRankings.enumerated()), id: \.element.id) { idx, ranking in
                    HStack(spacing: 0) {
                        Text(ranking.categoryDisplayName)
                            .font(.subheadline)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Text(ranking.teamValue)
                            .font(.subheadline.bold()).monospacedDigit()
                            .frame(width: 70, alignment: .trailing)
                        Text(ordinal(ranking.leagueRank))
                            .font(.subheadline)
                            .foregroundColor(rankColor(ranking.leagueRank, of: ranking.totalTeams))
                            .frame(width: 60, alignment: .trailing)
                    }
                    .padding(.horizontal, 16).padding(.vertical, 8)
                    .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
                    .accessibilityElement(children: .ignore)
                    .accessibilityLabel("\(ranking.categoryDisplayName): \(ranking.teamValue), ranked \(ordinal(ranking.leagueRank))")
                }
            }
            .padding()
            .accessibilityHidden(true)
            .overlay(
                AccessibleDataTable(headers: headers, rows: rows)
                    .allowsHitTesting(false)
            )
        }
    }

    // MARK: - Helpers

    private func ordinal(_ n: Int) -> String {
        let ones = n % 10, tens = n % 100
        let suffix: String
        if tens >= 11 && tens <= 13    { suffix = "th" }
        else if ones == 1              { suffix = "st" }
        else if ones == 2              { suffix = "nd" }
        else if ones == 3              { suffix = "rd" }
        else                           { suffix = "th" }
        return "\(n)\(suffix)"
    }

    private func rankColor(_ rank: Int, of total: Int) -> Color {
        guard total > 0 else { return .primary }
        let third = max(1, total / 3)
        if rank <= third             { return .green }
        if rank > total - third      { return Color(.systemRed) }
        return .primary
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
