//
//  WorldCupPathDetailViewModel.swift
//  SportsScores
//
//  Loads a team's group-stage games for the "tournament history" section of the
//  Path to the Cup detail screen. Knockout history comes from the already-loaded
//  bracket; only the group-stage games need a separate fetch.
//

import Foundation

@MainActor
final class WorldCupPathDetailViewModel: ObservableObject {

    @Published var groupGames: [Game] = []
    @Published var isLoading = false

    let teamId: String
    let sport: Sport
    let phases: [WorldCupPhase]

    private let api = ESPNAPIService.shared
    private var loaded = false

    init(teamId: String, sport: Sport, phases: [WorldCupPhase]) {
        self.teamId = teamId
        self.sport  = sport
        self.phases = phases
    }

    /// Group stage is phase id "1" — fetch its games once and keep this team's.
    func load() async {
        guard !loaded, let groupPhase = phases.first(where: { $0.id == "1" }) ?? phases.first else { return }
        isLoading = true
        let games = (try? await api.fetchGamesRange(
            for: sport, startDate: groupPhase.startDate, endDate: groupPhase.endDate)) ?? []
        groupGames = games
            .filter { $0.homeTeam.id == teamId || $0.awayTeam.id == teamId }
            .sorted { $0.date < $1.date }
        loaded = true
        isLoading = false
    }
}
