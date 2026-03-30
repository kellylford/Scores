//
//  StatisticsViewModel.swift
//  SportsScores
//
//  Phase 5 — League-wide stat leaders.
//  Fetches the ESPN leaders endpoint for the current sport/season.
//

import Foundation

@MainActor
class StatisticsViewModel: ObservableObject {
    @Published var categories: [LeagueLeaderCategory] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiService = ESPNAPIService.shared

    func fetchLeaders(for sport: Sport) async {
        isLoading = categories.isEmpty
        errorMessage = nil

        do {
            categories = try await apiService.fetchLeagueLeaders(for: sport)
        } catch {
            errorMessage = "Failed to load statistics: \(error.localizedDescription)"
        }

        isLoading = false
    }

    func refresh(for sport: Sport) async {
        await fetchLeaders(for: sport)
    }
}
