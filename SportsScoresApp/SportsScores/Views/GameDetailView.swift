//
//  GameDetailView.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI

struct GameDetailView: View {
    let game: Game
    let sport: Sport
    @State private var gameDetails: GameDetails?
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var selectedSection = 0
    
    /// Whether this sport produces per-pitch coordinate data.
    private var hasPitches: Bool { sport == .mlb }
    
    var body: some View {
        VStack(spacing: 0) {
            // Game Header
            gameHeader
                .padding()
                .background(Color.secondary.opacity(0.1))
            
            Divider()
            
            // Section Picker (show only when details have loaded)
            if gameDetails != nil {
                Picker("Section", selection: $selectedSection) {
                    Text("Box Score").tag(0)
                    Text("Plays").tag(1)
                    Text("Leaders").tag(2)
                    if hasPitches {
                        Text("Pitches 🎵").tag(3)
                    }
                }
                .pickerStyle(.segmented)
                .padding()
            }
            
            // Content
            if isLoading {
                Spacer()
                ProgressView("Loading details...")
                Spacer()
            } else if let error = errorMessage {
                Spacer()
                VStack(spacing: 16) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 48))
                        .foregroundColor(.orange)
                    Text(error)
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)
                    Button("Retry") {
                        Task {
                            await loadDetails()
                        }
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
                Spacer()
            } else if let details = gameDetails {
                TabView(selection: $selectedSection) {
                    boxScoreView(details: details)
                        .tag(0)
                    
                    playsView(details: details)
                        .tag(1)
                    
                    leadersView(details: details)
                        .tag(2)
                    
                    if hasPitches {
                        PitchMapView(plays: details.plays ?? [])
                            .tag(3)
                    }
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
            }
        }
        .navigationTitle("Game Details")
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await loadDetails()
        }
    }
    
    private var gameHeader: some View {
        VStack(spacing: 12) {
            // Status
            if game.status.isLive {
                Label(game.status.displayText, systemImage: "circle.fill")
                    .foregroundColor(.red)
                    .font(.headline)
            } else if game.status.isCompleted {
                Text("Final")
                    .font(.headline)
                    .foregroundColor(.secondary)
            } else {
                Text(game.displayTime)
                    .font(.headline)
                    .foregroundColor(.secondary)
            }
            
            // Teams and Scores
            HStack(spacing: 40) {
                VStack {
                    Text(game.awayTeam.abbreviation)
                        .font(.title2)
                        .fontWeight(.bold)
                    if let score = game.awayTeam.score {
                        Text("\(score)")
                            .font(.system(size: 48, weight: .bold, design: .rounded))
                            .monospacedDigit()
                    }
                    if let record = game.awayTeam.record {
                        Text("(\(record))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Text("@")
                    .font(.title3)
                    .foregroundColor(.secondary)
                
                VStack {
                    Text(game.homeTeam.abbreviation)
                        .font(.title2)
                        .fontWeight(.bold)
                    if let score = game.homeTeam.score {
                        Text("\(score)")
                            .font(.system(size: 48, weight: .bold, design: .rounded))
                            .monospacedDigit()
                    }
                    if let record = game.homeTeam.record {
                        Text("(\(record))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
    }
    
    private func boxScoreView(details: GameDetails) -> some View {
        ScrollView {
            if let boxscore = details.boxscore {
                VStack(spacing: 20) {
                    ForEach(boxscore.teams, id: \.team.displayName) { team in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(team.team.displayName)
                                .font(.headline)
                                .padding(.horizontal)
                            
                            // Each category (batting, pitching, etc.) contains individual stats
                            ForEach(team.statistics, id: \.name) { category in
                                Text(category.displayName)
                                    .font(.subheadline)
                                    .fontWeight(.semibold)
                                    .foregroundColor(.secondary)
                                    .padding(.horizontal)
                                    .padding(.top, 4)
                                ForEach(category.stats, id: \.name) { stat in
                                    HStack {
                                        Text(stat.displayName)
                                            .foregroundColor(.secondary)
                                        Spacer()
                                        Text(stat.displayValue)
                                            .fontWeight(.medium)
                                    }
                                    .padding(.horizontal)
                                    .padding(.vertical, 2)
                                }
                            }
                        }
                        .padding(.vertical, 8)
                        .background(Color.secondary.opacity(0.05))
                        .cornerRadius(8)
                    }
                }
                .padding()
            } else {
                Text("Box score not available")
                    .foregroundColor(.secondary)
                    .padding()
            }
        }
    }
    
    private func playsView(details: GameDetails) -> some View {
        ScrollView {
            if let plays = details.plays, !plays.isEmpty {
                LazyVStack(alignment: .leading, spacing: 12) {
                    ForEach(plays, id: \.id) { play in
                        VStack(alignment: .leading, spacing: 4) {
                            if let period = play.period {
                                Text(period.displayValue)
                                    .font(.caption)
                                    .fontWeight(.semibold)
                                    .foregroundColor(.blue)
                            }
                            
                            if let text = play.text {
                                Text(text)
                                    .font(.body)
                            }
                            
                            Text(play.type.text)
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                        .padding()
                        .background(Color.secondary.opacity(0.05))
                        .cornerRadius(8)
                    }
                }
                .padding()
            } else {
                Text("Play-by-play not available")
                    .foregroundColor(.secondary)
                    .padding()
            }
        }
    }
    
    private func leadersView(details: GameDetails) -> some View {
        ScrollView {
            if let leaders = details.leaders, !leaders.isEmpty {
                VStack(spacing: 16) {
                    ForEach(leaders, id: \.name) { category in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(category.displayName)
                                .font(.headline)
                                .padding(.horizontal)
                            
                            ForEach(category.leaders, id: \.athlete.displayName) { leader in
                                HStack {
                                    Text(leader.athlete.displayName)
                                        .foregroundColor(.primary)
                                    Spacer()
                                    Text(leader.displayValue)
                                        .fontWeight(.medium)
                                }
                                .padding(.horizontal)
                                .padding(.vertical, 4)
                            }
                        }
                        .padding(.vertical, 8)
                        .background(Color.secondary.opacity(0.05))
                        .cornerRadius(8)
                    }
                }
                .padding()
            } else {
                Text("Leaders not available")
                    .foregroundColor(.secondary)
                    .padding()
            }
        }
    }
    
    private func loadDetails() async {
        isLoading = true
        errorMessage = nil
        
        do {
            gameDetails = try await ESPNAPIService.shared.fetchGameDetails(for: game.id, sport: sport)
        } catch {
            errorMessage = "Failed to load details: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
}

#Preview {
    NavigationStack {
        GameDetailView(
            game: Game(
                id: "1",
                name: "Sample Game",
                shortName: "LAD @ SD",
                date: Date(),
                status: Game.GameStatus(state: "post", detail: "Final", period: nil, clock: nil),
                homeTeam: Game.Team(id: "1", name: "Padres", abbreviation: "SD", displayName: "San Diego Padres", score: 5, record: "82-80", logo: nil),
                awayTeam: Game.Team(id: "2", name: "Dodgers", abbreviation: "LAD", displayName: "Los Angeles Dodgers", score: 3, record: "95-67", logo: nil),
                venue: nil,
                broadcasts: ["ESPN"],
                situation: nil
            ),
            sport: .mlb
        )
    }
}
