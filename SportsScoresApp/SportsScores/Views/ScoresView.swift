//
//  ScoresView.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI

struct ScoresView: View {
    let sport: Sport
    @StateObject private var viewModel = ScoresViewModel()
    @State private var selectedTab = 0
    
    var body: some View {
        VStack(spacing: 0) {
            // Tab Selector
            Picker("View", selection: $selectedTab) {
                Text("Scores").tag(0)
                Text("Standings").tag(1)
            }
            .pickerStyle(.segmented)
            .padding()
            
            // Content
            TabView(selection: $selectedTab) {
                scoresTab
                    .tag(0)
                
                StandingsView(sport: sport)
                    .tag(1)
            }
            .tabViewStyle(.page(indexDisplayMode: .never))
        }
        .navigationTitle(sport.displayName)
        .task {
            await viewModel.fetchGames(for: sport)
        }
        .refreshable {
            await viewModel.refresh(for: sport)
        }
    }
    
    private var scoresTab: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading games...")
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
                            await viewModel.fetchGames(for: sport)
                        }
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
            } else if viewModel.games.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "calendar.badge.exclamationmark")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text("No games scheduled")
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
            } else {
                gamesList
            }
        }
    }
    
    private var gamesList: some View {
        List {
            ForEach(viewModel.games) { game in
                NavigationLink(destination: GameDetailView(game: game, sport: sport)) {
                    GameRow(game: game)
                }
            }
        }
        .listStyle(.plain)
    }
}

struct GameRow: View {
    let game: Game
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Status and Time
            HStack {
                if game.status.isLive {
                    Label(game.status.displayText, systemImage: "circle.fill")
                        .foregroundColor(.red)
                        .font(.caption)
                        .fontWeight(.semibold)
                } else if game.status.isCompleted {
                    Text("Final")
                        .font(.caption)
                        .foregroundColor(.secondary)
                } else {
                    Text(game.displayTime)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                if !game.broadcasts.isEmpty {
                    Text(game.broadcasts.first ?? "")
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.blue.opacity(0.2))
                        .cornerRadius(4)
                }
            }
            
            // Teams and Scores
            VStack(alignment: .leading, spacing: 4) {
                TeamScoreRow(team: game.awayTeam, isHome: false)
                TeamScoreRow(team: game.homeTeam, isHome: true)
            }
            
            // Venue
            if let venue = game.venue {
                Text(venue.fullName)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(createAccessibilityLabel())
    }
    
    private func createAccessibilityLabel() -> String {
        var label = ""
        
        if game.status.isLive {
            label = "Live: "
        } else if game.status.isCompleted {
            label = "Final: "
        }
        
        label += "\(game.awayTeam.displayName) \(game.awayTeam.score ?? 0), "
        label += "\(game.homeTeam.displayName) \(game.homeTeam.score ?? 0)"
        
        if !game.status.isLive && !game.status.isCompleted {
            label += ", \(game.displayTime)"
        }
        
        return label
    }
}

struct TeamScoreRow: View {
    let team: Game.Team
    let isHome: Bool
    
    var body: some View {
        HStack {
            Text(isHome ? "vs" : "@")
                .font(.caption)
                .foregroundColor(.secondary)
                .frame(width: 20)
            
            Text(team.abbreviation)
                .font(.body)
                .fontWeight(.medium)
            
            if let record = team.record {
                Text("(\(record))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            if let score = team.score {
                Text("\(score)")
                    .font(.title3)
                    .fontWeight(.bold)
                    .monospacedDigit()
            }
        }
    }
}

#Preview {
    NavigationStack {
        ScoresView(sport: .mlb)
    }
}
