//
//  ScoresViewModel.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

@MainActor
class ScoresViewModel: ObservableObject {

    // MARK: - Published state

    @Published var games: [Game] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    // Date navigation (non-football sports)
    @Published var currentDate: Date = Calendar.current.startOfDay(for: Date())

    // Week navigation (football)
    @Published var currentWeek: Int?
    @Published var currentSeasonType: Int = 2            // 1 pre / 2 regular / 3 post
    @Published var weekLabel: String = ""

    // ─────────────────────────────────────────────────────────────────────
    private let apiService = ESPNAPIService.shared

    // MARK: - Formatted date label for display

    var dateLabelText: String {
        let cal = Calendar.current
        if cal.isDateInToday(currentDate) { return "Today" }
        if cal.isDateInYesterday(currentDate) { return "Yesterday" }
        if cal.isDateInTomorrow(currentDate) { return "Tomorrow" }
        let fmt = DateFormatter()
        fmt.dateFormat = "EEE, MMM d"
        return fmt.string(from: currentDate)
    }

    // MARK: - Fetch

    func fetchGames(for sport: Sport) async {
        isLoading = true
        errorMessage = nil

        do {
            if sport.isFootball {
                let result = try await apiService.fetchFootballGames(
                    for: sport,
                    week: currentWeek,
                    seasonType: currentSeasonType
                )
                games            = result.games
                currentWeek      = result.week
                weekLabel        = result.weekLabel
                currentSeasonType = result.seasonType
            } else {
                games = try await apiService.fetchGames(for: sport, date: currentDate)
            }
            // Check watched games for score changes after every refresh
            ScoreMonitorService.shared.checkForChanges(games: games)
        } catch {
            errorMessage = "Failed to load games: \(error.localizedDescription)"
        }

        isLoading = false
    }

    // MARK: - Navigation

    func goForward(for sport: Sport) async {
        if sport.isFootball {
            currentWeek = (currentWeek ?? 1) + 1
        } else {
            currentDate = Calendar.current.date(byAdding: .day, value: 1, to: currentDate) ?? currentDate
        }
        await fetchGames(for: sport)
    }

    func goBack(for sport: Sport) async {
        if sport.isFootball {
            let prev = (currentWeek ?? 2) - 1
            if prev >= 1 { currentWeek = prev }
        } else {
            currentDate = Calendar.current.date(byAdding: .day, value: -1, to: currentDate) ?? currentDate
        }
        await fetchGames(for: sport)
    }

    func goToDate(_ date: Date, for sport: Sport) async {
        currentDate = Calendar.current.startOfDay(for: date)
        await fetchGames(for: sport)
    }

    func goToToday(for sport: Sport) async {
        currentDate = Calendar.current.startOfDay(for: Date())
        currentWeek = nil   // nil → API resolves to current week
        await fetchGames(for: sport)
    }

    func refresh(for sport: Sport) async {
        await fetchGames(for: sport)
    }
}
