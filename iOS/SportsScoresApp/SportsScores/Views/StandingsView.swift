//
//  StandingsView.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI

struct StandingsView: View {
    let sport: Sport
    @StateObject private var viewModel = StandingsViewModel()
    
    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading standings...")
            } else if let error = viewModel.errorMessage {
                VStack(spacing: 16) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 48))
                        .foregroundColor(.orange)
                    Text(error)
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)
                    Button("Retry") {
                        Task {
                            await viewModel.fetchStandings(for: sport)
                        }
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
            } else if viewModel.standingsGroups.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "list.bullet.clipboard")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text("No standings available")
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
            } else {
                StandingsTableView(standingsGroups: viewModel.standingsGroups, sport: sport)
            }
        }
        .task {
            await viewModel.fetchStandings(for: sport)
        }
        .refreshable {
            await viewModel.refresh(for: sport)
        }
    }
}

#Preview {
    NavigationStack {
        StandingsView(sport: .mlb)
            .navigationTitle("MLB Standings")
    }
}
