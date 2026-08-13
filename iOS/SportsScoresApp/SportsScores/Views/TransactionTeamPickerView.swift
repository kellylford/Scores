//
//  TransactionTeamPickerView.swift
//  SportsScores
//
//  Shows an "All" option plus individual team rows for a given sport.
//

import SwiftUI

struct TransactionTeamPickerView: View {
    let sport: Sport
    @StateObject private var viewModel: TransactionViewModel

    init(sport: Sport) {
        self.sport = sport
        _viewModel = StateObject(wrappedValue: TransactionViewModel(sport: sport))
    }

    var body: some View {
        List {
            // "All" — every transaction league-wide
            Section {
                NavigationLink(destination: TransactionListView(sport: sport, team: nil)) {
                    HStack(spacing: 14) {
                        Image(systemName: sport.systemImage)
                            .font(.title2)
                            .foregroundColor(.accentColor)
                            .frame(width: 34)
                        VStack(alignment: .leading, spacing: 2) {
                            Text("All \(sport.displayName)").font(.headline)
                            Text("Every transaction across the league").font(.caption).foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 4)
                }
                .accessibilityLabel("All \(sport.displayName). Every transaction across the league.")
            }

            // Per-team rows
            if viewModel.isLoading {
                Section {
                    HStack {
                        Spacer()
                        ProgressView()
                        Spacer()
                    }
                    .accessibilityLabel("Loading teams")
                }
            } else if !viewModel.teams.isEmpty {
                Section {
                    ForEach(viewModel.teams) { team in
                        NavigationLink(destination: TransactionListView(sport: sport, team: team)) {
                            HStack(spacing: 12) {
                                Circle()
                                    .fill(colorFromHex(team.color))
                                    .frame(width: 12, height: 12)
                                Text(team.displayName).font(.body)
                            }
                            .padding(.vertical, 2)
                        }
                        .accessibilityLabel(team.displayName)
                    }
                } header: {
                    Text("Teams")
                }
            } else if let error = viewModel.errorMessage {
                Section {
                    Text(error).foregroundColor(.secondary)
                }
            }
        }
        .navigationTitle(sport.displayName)
        .task { await viewModel.loadTeams() }
    }

    // MARK: - Helpers

    private func colorFromHex(_ hex: String?) -> Color {
        guard let hex = hex, hex.count == 6,
              let value = UInt64(hex, radix: 16) else {
            return Color.accentColor
        }
        let r = Double((value >> 16) & 0xFF) / 255
        let g = Double((value >> 8)  & 0xFF) / 255
        let b = Double( value        & 0xFF) / 255
        return Color(red: r, green: g, blue: b)
    }
}

#Preview {
    NavigationStack { TransactionTeamPickerView(sport: .mlb) }
}
