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
    }

    // MARK: - Leaders list

    private var leadersList: some View {
        List {
            ForEach(viewModel.categories) { category in
                Section {
                    ForEach(category.leaders) { entry in
                        LeaderRow(rank: entry.rank,
                                  athleteName: entry.athleteName,
                                  teamAbbr: entry.teamAbbreviation,
                                  value: entry.displayValue)
                    }
                } header: {
                    Text(category.displayName)
                        .font(.headline)
                        .foregroundColor(.primary)
                        .accessibilityAddTraits(.isHeader)
                }
            }
        }
        .listStyle(.insetGrouped)
    }

    // MARK: - States

    private func errorState(message: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 48))
                .foregroundColor(.orange)
            Text(message)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
            Button("Retry") { Task { await viewModel.fetchLeaders(for: sport) } }
                .buttonStyle(.bordered)
        }
        .padding()
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

// MARK: - Leader Row

private struct LeaderRow: View {
    let rank: Int
    let athleteName: String
    let teamAbbr: String
    let value: String

    var body: some View {
        HStack(spacing: 12) {
            // Rank badge
            Text("\(rank)")
                .font(.caption.bold())
                .monospacedDigit()
                .frame(width: 24, alignment: .trailing)
                .foregroundColor(rankColor)

            // Name + team
            VStack(alignment: .leading, spacing: 1) {
                Text(athleteName)
                    .font(.subheadline)
                if !teamAbbr.isEmpty {
                    Text(teamAbbr)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()

            // Stat value
            Text(value)
                .font(.subheadline.bold())
                .monospacedDigit()
                .foregroundColor(.primary)
        }
        .padding(.vertical, 2)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(rank). \(athleteName)\(teamAbbr.isEmpty ? "" : ", \(teamAbbr)"), \(value)")
    }

    private var rankColor: Color {
        switch rank {
        case 1: return .yellow
        case 2: return Color(.systemGray2)
        case 3: return .orange
        default: return .secondary
        }
    }
}

#Preview {
    NavigationStack {
        StatisticsView(sport: .nfl)
            .navigationTitle("NFL Leaders")
    }
}
