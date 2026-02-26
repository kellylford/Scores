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
                    Text(sport.isFootball ? "Drives" : "Plays").tag(1)
                    Text("Info").tag(2)
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
                    gameInfoTab(details: details).tag(2)
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

            // Venue information
            if let venue = game.venue {
                HStack(spacing: 4) {
                    Image(systemName: "mappin.circle")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(venue.fullName)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Venue: \(venue.fullName)")
            }

            // Broadcast networks
            let activeBroadcasts = game.broadcasts.filter { !$0.isEmpty }
            if !activeBroadcasts.isEmpty {
                HStack(spacing: 4) {
                    Image(systemName: "tv")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(activeBroadcasts.joined(separator: ", "))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .accessibilityLabel("TV: \(activeBroadcasts.joined(separator: ", "))")
            }

            // Odds (when available from summary API)
            if let odds = gameDetails?.odds?.first {
                HStack(spacing: 12) {
                    if let spread = odds.details, !spread.isEmpty {
                        Text("Line: \(spread)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    if let ou = odds.overUnder {
                        Text("O/U: \(String(format: "%.1f", ou))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .accessibilityLabel({
                    var parts: [String] = []
                    if let s = odds.details { parts.append("Line: \(s)") }
                    if let o = odds.overUnder { parts.append("Over/under: \(o)") }
                    return parts.joined(separator: ". ")
                }())
            }
        }
    }

    private func teamColumn(_ team: Game.Team) -> some View {
        NavigationLink(destination: TeamScheduleView(team: team, sport: sport)) {
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
            .foregroundColor(.primary)
        }
        .accessibilityLabel("\(team.displayName) — tap for schedule")
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

    // MARK: - Plays / Drives tab

    @ViewBuilder
    private func playsTab(details: GameDetails) -> some View {
        // Football: prefer drives view; fall back to flat plays if no drives data.
        if sport.isFootball {
            let allDrives = details.drives?.all ?? []
            if !allDrives.isEmpty {
                NFLDrivesView(
                    drives: allDrives,
                    awayAbbr: game.awayTeam.abbreviation,
                    homeAbbr: game.homeTeam.abbreviation
                )
            } else {
                let plays = details.plays ?? []
                if plays.isEmpty {
                    Text("Drives not available")
                        .foregroundColor(.secondary).padding()
                } else {
                    GenericPlaysView(
                        plays: plays,
                        awayAbbr: game.awayTeam.abbreviation,
                        homeAbbr: game.homeTeam.abbreviation
                    )
                }
            }
        } else {
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
    }

    // MARK: - Leaders tab

    // MARK: - Game Info tab (Leaders + Injuries + Officials)

    private func gameInfoTab(details: GameDetails) -> some View {
        ScrollView {
            VStack(spacing: 20) {
                leadersSection(details: details)

                if let injuries = details.injuries, !injuries.isEmpty {
                    injuriesSection(injuries)
                }

                if let officials = details.gameInfo?.officials, !officials.isEmpty {
                    officialsSection(officials)
                }
            }
            .padding()
        }
    }

    // MARK: - Leaders section

    private func leadersSection(details: GameDetails) -> some View {
        let sections: [(String, [(String, String)])] = {
            guard let raw = details.leaders, !raw.isEmpty else { return [] }
            var result: [(String, [(String, String)])] = []

            for entry in raw {
                if let catName = entry.displayName ?? entry.name {
                    // Direct category (MLB/NFL/NHL)
                    let players: [(String, String)] = (entry.leaders ?? []).compactMap { pl in
                        guard let name = pl.athlete?.displayName, let val = pl.displayValue else { return nil }
                        return (name, val)
                    }
                    if !players.isEmpty { result.append((catName, players)) }
                } else {
                    // NBA: team-wrapper, inner leaders are categories
                    for inner in entry.leaders ?? [] {
                        let catName = inner.displayName ?? inner.name ?? "Leaders"
                        let players: [(String, String)] = (inner.leaders ?? []).compactMap { pl in
                            guard let name = pl.athlete?.displayName, let val = pl.displayValue else { return nil }
                            return (name, val)
                        }
                        if !players.isEmpty { result.append((catName, players)) }
                    }
                }
            }
            return result
        }()

        return Group {
            if !sections.isEmpty {
                sectionCard(title: "Leaders") {
                    ForEach(sections, id: \.0) { catName, players in
                        Text(catName)
                            .font(.subheadline.bold())
                            .foregroundColor(.secondary)
                            .padding(.top, 4)
                        ForEach(players, id: \.0) { playerName, value in
                            HStack {
                                Text(playerName)
                                    .font(.subheadline)
                                Spacer()
                                Text(value)
                                    .font(.subheadline.bold())
                            }
                            .padding(.vertical, 2)
                            .accessibilityLabel("\(catName): \(playerName), \(value)")
                        }
                    }
                }
            }
        }
    }

    // MARK: - Injuries section

    private func injuriesSection(_ teams: [GameDetails.InjuryTeam]) -> some View {
        sectionCard(title: "Injuries") {
            ForEach(Array(teams.enumerated()), id: \.offset) { _, team in
                if let injuries = team.injuries, !injuries.isEmpty {
                    Text(team.team?.displayName ?? "")
                        .font(.subheadline.bold())
                        .foregroundColor(.secondary)
                        .padding(.top, 4)
                    ForEach(Array(injuries.enumerated()), id: \.offset) { _, injury in
                        HStack(spacing: 8) {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(injury.athlete?.displayName ?? "")
                                    .font(.subheadline)
                                Text(injury.athlete?.position?.abbreviation ?? "")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            Spacer()
                            Text(injury.status ?? "")
                                .font(.caption.bold())
                                .padding(.horizontal, 7)
                                .padding(.vertical, 3)
                                .background(injuryColor(for: injury.status ?? "").opacity(0.15))
                                .foregroundColor(injuryColor(for: injury.status ?? ""))
                                .cornerRadius(6)
                        }
                        .padding(.vertical, 3)
                        .accessibilityLabel(
                            "\(injury.athlete?.displayName ?? ""), \(injury.athlete?.position?.abbreviation ?? ""), status: \(injury.status ?? "")"
                        )
                    }
                }
            }
        }
    }

    private func injuryColor(for status: String) -> Color {
        switch status.lowercased() {
        case "out":  return .red
        case "questionable": return .orange
        case "doubtful": return .orange
        case "injured reserve", "ir": return .red
        default: return .secondary
        }
    }

    // MARK: - Officials section

    private func officialsSection(_ officials: [GameDetails.GameInfo.Official]) -> some View {
        sectionCard(title: "Officials") {
            ForEach(Array(officials.enumerated()), id: \.offset) { _, official in
                HStack {
                    Text(official.fullName ?? "")
                        .font(.subheadline)
                    Spacer()
                    Text(official.position?.displayName ?? "")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 3)
                .accessibilityLabel("\(official.fullName ?? ""), \(official.position?.displayName ?? "")")
            }
        }
    }

    // MARK: - Shared card container

    private func sectionCard<Content: View>(title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title)
                .font(.headline)
                .accessibilityAddTraits(.isHeader)
            content()
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(Color.secondary.opacity(0.07))
        .cornerRadius(12)
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
                venue: nil, broadcasts: ["ESPN"], situation: nil, seasonType: 2
            ),
            sport: .mlb
        )
    }
}
