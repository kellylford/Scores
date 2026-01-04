//
//  ScoresViewModel.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

@MainActor
class ScoresViewModel: ObservableObject {
    @Published var games: [Game] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = ESPNAPIService.shared
    
    func fetchGames(for sport: Sport) async {
        isLoading = true
        errorMessage = nil
        
        do {
            games = try await apiService.fetchGames(for: sport)
        } catch {
            errorMessage = "Failed to load games: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
    
    func refresh(for sport: Sport) async {
        await fetchGames(for: sport)
    }
}
