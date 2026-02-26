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
    @State private var showPitchMap = false

    // Audio engine shared across the plays view
    @StateObject private var pitchAudio = PitchAudioEngine()

    var body: some View {
        VStack(spacing: 0) {
            gameHeader
                .padding()
                .background(Color.secondary.opacity(0.1))

            Divider()

            if gameDetails != nil {
                Picker("Section", selection: $selectedSection) {
                    Text("Box Score").tag(0)
                    Text("Plays").tag(1)
                    Text("Leaders").tag(2)
                }
                .pickerStyle(.segmented)
                .padding()
            }

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
                    Button("Retry") { Task { await loadDetails() } }
                        .buttonStyle(.bordered)
                }
                .padding()
                Spacer()
            } else if let details = gameDetails {
                TabView(selection: $selectedSection) {
                    boxScoreTab(details: details).tag(0)
                    playsTab(details: details).tag(1)
                    leadersTab(details: details).tag(2)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
            }
        }
        .navigationTitle("Game Details")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showPitchMap) {
            if let details = gameDetails {
                NavigationStack {
                    PitchMapView(plays: details.plays ?? [])
                        .navigationTitle("Pitch Map")
                        .navigationBarTitleDisplayMode(.inline)
                        .toolbar {
                            ToolbarItem(placement: .confirmationAction) {
                                Button("Done") { showPitchMap = false }
                            }
                        }
                }
            }
        }
        .task { await loadDetails() }
    }

    // MARK: - Game Header

    private var gameHeader: some View {
        VStack(spacing: 12) {
            if game.status.isLive {
                Label(game.status.displayText, systemImage: "circle.fill")
                    .foregroundColor(.red).font(.headline)
            } else if game.status.isCompleted {
                Text("Final").font(.headline).foregroundColor(.secondary)
            } else {
                Text(game.displayTime).font(.headline).foregroundColor(.secondary)
            }
            HStack(spacing: 40) {
                teamColumn(game.awayTeam)
                Text("@").font(.title3).foregroundColor(.secondary)
                teamColumn(game.homeTeam)
            }
        }
    }

    private func teamColumn(_ team: Game.Team) -> some View {
        VStack {
            Text(team.abbreviation).font(.title2).fontWeight(.bold)
            if let score = team.score {
                Text("\(score)")
                    .font(.system(size: 48, weight: .bold, design: .rounded))
                    .monospacedDigit()
            }
            if let record = team.record {
                Text("(\(record))").font(.caption).foregroundColor(.secondary)
            }
        }
    }

    // MARK: - Box Score tab

    private func boxScoreTab(details: GameDetails) -> some View {
        Group {
            if let bs = details.boxscore {
                BoxScoreView(boxscore: bs)
            } else {
                Text("Box score not available")
                    .foregroundColor(.secondary).padding()
            }
        }
    }

    // MARK: - Plays tab

    @ViewBuilder
    private func playsTab(details: GameDetails) -> some View {
        let plays = details.plays ?? []
        if plays.isEmpty {
            Text("Play-by-play not available")
                .foregroundColor(.secondary).padding()
        } else if sport == .mlb {
            VStack(spacing: 0) {
                if plays.contains(where: { $0.isPitch }) {
                    HStack {
                        Spacer()
                        Button {
                            showPitchMap = true
                        } label: {
                            Label("Strike Zone Map", systemImage: "square.grid.2x2")
                                .font(.caption)
                        }
                        .buttonStyle(.bordered)
                        .padding(.horizontal)
                        .padding(.vertical, 4)
                    }
                    .background(Color.secondary.opacity(0.06))
                }
                MLBPlaysView(
                    plays: plays,
                    awayAbbr: game.awayTeam.abbreviation,
                    homeAbbr: game.homeTeam.abbreviation,
                    audio: pitchAudio
                )
            }
        } else {
            GenericPlaysView(
                plays: plays,
                awayAbbr: game.awayTeam.abbreviation,
                homeAbbr: game.homeTeam.abbreviation
            )
        }
    }

    // MARK: - Leaders tab

    private func leadersTab(details: GameDetails) -> some View {
        ScrollView {
            if let leaders = details.leaders, !leaders.isEmpty {
                VStack(spacing: 16) {
                    ForEach(leaders, id: \.name) { category in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(category.displayName)
                                .font(.headline).padding(.horizontal)
                            ForEach(category.leaders, id: \.athlete.displayName) { leader in
                                HStack {
                                    Text(leader.athlete.displayName)
                                    Spacer()
                                    Text(leader.displayValue).fontWeight(.medium)
                                }
                                .padding(.horizontal).padding(.vertical, 4)
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
                    .foregroundColor(.secondary).padding()
            }
        }
    }

    // MARK: - Data Loading

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
                homeTeam: Game.Team(id: "1", name: "Padres", abbreviation: "SD",
                                    displayName: "San Diego Padres", score: 5, record: "82-80", logo: nil),
                awayTeam: Game.Team(id: "2", name: "Dodgers", abbreviation: "LAD",
                                    displayName: "Los Angeles Dodgers", score: 3, record: "95-67", logo: nil),
                venue: nil, broadcasts: ["ESPN"], situation: nil
            ),
            sport: .mlb
        )
    }
}
