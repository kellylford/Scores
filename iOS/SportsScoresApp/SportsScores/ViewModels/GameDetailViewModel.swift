//
//  GameDetailViewModel.swift
//  SportsScores
//

import Foundation

@MainActor
final class GameDetailViewModel: ObservableObject {
    @Published var gameDetails: GameDetails?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let game: Game
    private let sport: Sport

    init(game: Game, sport: Sport) {
        self.game = game
        self.sport = sport
    }

    func loadDetails() async {
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
