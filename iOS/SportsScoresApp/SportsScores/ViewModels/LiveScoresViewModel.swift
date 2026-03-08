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

        // Today's date boundaries for filtering
        let calendar = Calendar.current
        let now = Date()
        let startOfToday = calendar.startOfDay(for: now)
        let endOfToday = calendar.date(byAdding: .day, value: 1, to: startOfToday)!

        // Fetch all sports in parallel. Football uses the week-based endpoint;
        // all other sports use the date-based endpoint.
        let results: [(Sport, [Game])] = await withTaskGroup(of: (Sport, [Game]).self) { group in
            for sport in Sport.allCases {
                group.addTask {
                    do {
                        let games: [Game]
                        if sport.isFootball {
                            // Football is organised by week, not calendar date.
                            let result = try await self.apiService.fetchFootballGames(for: sport)
                            games = result.games
                        } else {
                            games = try await self.apiService.fetchGames(for: sport)
                        }
                        return (sport, games)
                    } catch {
                        print("Failed to fetch games for \(sport.rawValue): \(error)")
                        return (sport, [])
                    }
                }
            }
            var collected: [(Sport, [Game])] = []
            for await pair in group { collected.append(pair) }
            // Restore consistent ordering (Sport.allCases order)
            return collected.sorted { Sport.allCases.firstIndex(of: $0.0)! < Sport.allCases.firstIndex(of: $1.0)! }
        }

        var live: [SportGames] = []
        var completed: [SportGames] = []
        var upcoming: [SportGames] = []

        for (sport, games) in results {
            // Football: keep all games returned (week-based, not date-filtered).
            // Other sports: restrict to today.
            let relevantGames: [Game]
            if sport.isFootball {
                relevantGames = games
            } else {
                relevantGames = games.filter { $0.date >= startOfToday && $0.date < endOfToday }
            }

            let liveGamesForSport     = relevantGames.filter { $0.status.isLive }
            let completedGamesForSport = relevantGames.filter { $0.status.isCompleted }
            let upcomingGamesForSport  = relevantGames.filter { !$0.status.isLive && !$0.status.isCompleted }

            if !liveGamesForSport.isEmpty     { live.append(SportGames(sport: sport, games: liveGamesForSport)) }
            if !completedGamesForSport.isEmpty { completed.append(SportGames(sport: sport, games: completedGamesForSport)) }
            if !upcomingGamesForSport.isEmpty  { upcoming.append(SportGames(sport: sport, games: upcomingGamesForSport)) }
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
