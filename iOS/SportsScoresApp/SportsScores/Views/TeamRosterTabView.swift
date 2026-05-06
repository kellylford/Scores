//
//  TeamRosterTabView.swift
//  SportsScores
//
//  Roster tab for Team Hub — accessible table of players.
//

import SwiftUI

struct TeamRosterTabView: View {
    @ObservedObject var viewModel: TeamHubViewModel
    @EnvironmentObject private var appSettings: AppSettings

    private let headers = ["#", "Name", "Position", "Age"]

    private var rows: [[String]] {
        viewModel.roster.map { player in
            [player.jerseyNumber, player.displayName, player.positionAbbreviation, player.age]
        }
    }

    var body: some View {
        Group {
            if viewModel.isLoadingRoster {
                ProgressView("Loading roster…")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = viewModel.errorRoster, viewModel.roster.isEmpty {
                errorState(message: error)
            } else if viewModel.roster.isEmpty {
                emptyState
            } else {
                DataTableView(headers: headers, rows: rows)
                    .environmentObject(appSettings)
            }
        }
        .navigationTitle("Roster")
        .navigationBarTitleDisplayMode(.inline)
        .task { await viewModel.loadRoster() }
    }

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "person.3")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("No roster available")
                .font(.headline)
                .foregroundColor(.secondary)
        }
    }

    private func errorState(message: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 40))
                .foregroundColor(.secondary)
            Text(message)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            Button("Retry") { Task { await viewModel.loadRoster() } }
                .buttonStyle(.borderedProminent)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
