//
//  StandingsViewModel.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

@MainActor
class StandingsViewModel: ObservableObject {
    @Published var standingsGroups: [StandingsGroup] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = ESPNAPIService.shared
    
    func fetchStandings(for sport: Sport) async {
        isLoading = true
        errorMessage = nil
        
        do {
            standingsGroups = try await apiService.fetchStandings(for: sport)
        } catch {
            errorMessage = "Failed to load standings: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
    
    func refresh(for sport: Sport) async {
        await fetchStandings(for: sport)
    }
}
