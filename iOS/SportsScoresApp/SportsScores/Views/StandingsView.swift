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
                ErrorStateView(message: error) {
                    Task { await viewModel.fetchStandings(for: sport) }
                }
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
