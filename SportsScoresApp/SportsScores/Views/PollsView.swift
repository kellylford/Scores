//
//  PollsView.swift
//  SportsScores
//
//  Phase 6 — College rankings: AP Top 25, Coaches Poll, etc.
//  Shows for: NCAAF, NCAAM, NCAAWB
//

import SwiftUI

struct PollsView: View {
    let sport: Sport
    @StateObject private var viewModel = PollsViewModel()

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading rankings…")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = viewModel.errorMessage {
                errorState(message: error)
            } else if viewModel.polls.isEmpty {
                emptyState
            } else {
                pollsContent
            }
        }
        .task { await viewModel.fetchRankings(for: sport) }
        .refreshable { await viewModel.refresh(for: sport) }
    }

    // MARK: - Main Content

    private var pollsContent: some View {
        VStack(spacing: 0) {
            if viewModel.polls.count > 1 {
                pollPicker
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                Divider()
            }

            if let poll = viewModel.selectedPoll {
                rankingList(poll: poll)
            }
        }
    }

    // MARK: - Poll picker

    private var pollPicker: some View {
        Picker("Poll", selection: $viewModel.selectedPollIndex) {
            ForEach(viewModel.polls.indices, id: \.self) { idx in
                Text(viewModel.polls[idx].shortName).tag(idx)
            }
        }
        .pickerStyle(.segmented)
        .accessibilityLabel("Select poll")
    }

    // MARK: - Ranking list

    private func rankingList(poll: RankingsPoll) -> some View {
        List {
            if let lastUpdated = poll.lastUpdated, !lastUpdated.isEmpty {
                Section {
                    Text("Updated \(lastUpdated)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            Section {
                ForEach(poll.ranks) { entry in
                    RankingRow(entry: entry)
                }
            } header: {
                HStack {
                    Text("Rank").frame(width: 36, alignment: .leading)
                    Text("Team")
                    Spacer()
                    Text("Record").frame(width: 52, alignment: .trailing)
                    Text("Pts").frame(width: 44, alignment: .trailing)
                }
                .font(.caption.bold())
                .foregroundColor(.secondary)
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
            Button("Retry") { Task { await viewModel.fetchRankings(for: sport) } }
                .buttonStyle(.bordered)
        }
        .padding()
    }

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "list.number")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("No rankings available")
                .font(.headline)
                .foregroundColor(.secondary)
            Text("Rankings are published weekly during the season.")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
    }
}

// MARK: - Ranking Row

private struct RankingRow: View {
    let entry: RankingsPoll.RankEntry

    var body: some View {
        HStack(spacing: 10) {
            // Current rank
            Text("\(entry.current)")
                .font(.title3.bold())
                .monospacedDigit()
                .frame(width: 28, alignment: .trailing)

            // Movement indicator
            Text(entry.movementText)
                .font(.caption.bold())
                .foregroundColor(movementColor)
                .frame(width: 28, alignment: .leading)

            // Team name
            VStack(alignment: .leading, spacing: 1) {
                Text(entry.teamDisplayName)
                    .font(.subheadline)
                if let record = entry.recordSummary {
                    Text(record)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()

            // Points
            if let pts = entry.points {
                Text(String(format: pts >= 100 ? "%.0f" : "%.1f", pts))
                    .font(.caption.bold())
                    .monospacedDigit()
                    .foregroundColor(.secondary)
                    .frame(width: 44, alignment: .trailing)
            }
        }
        .padding(.vertical, 2)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityLabel)
    }

    private var movementColor: Color {
        if entry.movementDirection > 0 { return .green }
        if entry.movementDirection < 0 { return .red }
        return .secondary
    }

    private var accessibilityLabel: String {
        var parts: [String] = []
        parts.append("Ranked \(entry.current)")
        parts.append(entry.teamDisplayName)
        if let record = entry.recordSummary { parts.append(record) }

        let mov = entry.movementDirection
        if mov > 0 { parts.append("Up \(mov)") }
        else if mov < 0 { parts.append("Down \(abs(mov))") }
        else if entry.previous == nil || entry.previous == 0 { parts.append("New to rankings") }
        else { parts.append("No change") }

        if let pts = entry.points {
            parts.append("\(Int(pts)) points")
        }
        return parts.joined(separator: ", ")
    }
}

#Preview {
    NavigationStack {
        PollsView(sport: .ncaaf)
            .navigationTitle("NCAAF Rankings")
    }
}
