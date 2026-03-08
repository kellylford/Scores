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
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                ForEach(viewModel.categories) { category in
                    categorySection(category)
                }
            }
            .padding()
        }
    }
    
    private func categorySection(_ category: LeagueLeaderCategory) -> some View {
        let headers = ["Rank", "Player", "Team", "Value"]
        let rows = category.leaders.map { entry in
            [
                "\(entry.rank)",
                entry.athleteName,
                entry.teamAbbreviation,
                entry.displayValue
            ]
        }
        
        return VStack(alignment: .leading, spacing: 8) {
            Text(category.displayName)
                .font(.headline)
                .foregroundColor(.primary)
                .accessibilityAddTraits(.isHeader)
            
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
                    Text("Team")
                        .font(.caption.bold())
                        .foregroundColor(.secondary)
                        .frame(width: 60, alignment: .center)
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
                        Text(entry.teamAbbreviation)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .frame(width: 60, alignment: .center)
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
