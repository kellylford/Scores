//
//  LiveScoresViewModel.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

@MainActor
class LiveScoresViewModel: ObservableObject {
    @Published var liveGames: [SportGames] = []
    @Published var completedGames: [SportGames] = []
    @Published var upcomingGames: [SportGames] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = ESPNAPIService.shared
    
    struct SportGames: Identifiable {
        let id = UUID()
        let sport: Sport
        let games: [Game]
    }
    
    func fetchAllGames() async {
        isLoading = true
        errorMessage = nil
        
        var live: [SportGames] = []
        var completed: [SportGames] = []
        var upcoming: [SportGames] = []
        
        // Get today's date range (midnight to midnight in local timezone)
        let calendar = Calendar.current
        let now = Date()
        let startOfToday = calendar.startOfDay(for: now)
        let endOfToday = calendar.date(byAdding: .day, value: 1, to: startOfToday)!
        
        // Fetch games for all sports
        for sport in Sport.allCases {
            do {
                let games = try await apiService.fetchGames(for: sport)
                
                // Filter to only today's games
                let todaysGames = games.filter { game in
                    game.date >= startOfToday && game.date < endOfToday
                }
                
                // Further filter into categories
                let liveGamesForSport = todaysGames.filter { $0.status.isLive }
                let completedGamesForSport = todaysGames.filter { $0.status.isCompleted }
                let upcomingGamesForSport = todaysGames.filter { !$0.status.isLive && !$0.status.isCompleted }
                
                if !liveGamesForSport.isEmpty {
                    live.append(SportGames(sport: sport, games: liveGamesForSport))
                }
                if !completedGamesForSport.isEmpty {
                    completed.append(SportGames(sport: sport, games: completedGamesForSport))
                }
                if !upcomingGamesForSport.isEmpty {
                    upcoming.append(SportGames(sport: sport, games: upcomingGamesForSport))
                }
            } catch {
                // Continue with other sports even if one fails
                print("Failed to fetch games for \(sport.rawValue): \(error)")
            }
        }
        
        liveGames = live
        completedGames = completed
        upcomingGames = upcoming
        
        if live.isEmpty && completed.isEmpty && upcoming.isEmpty {
            errorMessage = "No games scheduled today"
        }
        
        isLoading = false
    }
    
    func refresh() async {
        await fetchAllGames()
    }
}
