//
//  ScoresViewModel.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

// MARK: - Auto-refresh interval

enum AutoRefreshInterval: Int, CaseIterable, Identifiable {
    case thirtySeconds = 30
    case oneMinute     = 60
    case twoMinutes    = 120
    case manual        = 0

    var id: Int { rawValue }

    var label: String {
        switch self {
        case .thirtySeconds: return "30s"
        case .oneMinute:     return "1m"
        case .twoMinutes:    return "2m"
        case .manual:        return "Manual"
        }
    }
}

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
    /// True while the user is viewing the API-resolved current week.
    @Published var isOnCurrentWeek: Bool = true

    // Auto-refresh
    @Published var autoRefreshInterval: AutoRefreshInterval = .oneMinute

    // MARK: - Sectioned game lists

    var inProgressGames: [Game] { games.filter { $0.status.isLive } }
    var upcomingGames:   [Game] { games.filter { !$0.status.isLive && !$0.status.isCompleted }.sorted { $0.date < $1.date } }
    var completedGames:  [Game] { games.filter { $0.status.isCompleted } }

    // MARK: - Today / current-week state

    /// True when the currently displayed date is calendar today (non-football).
    var isOnToday: Bool { Calendar.current.isDateInToday(currentDate) }

    // MARK: - Formatted date label for display

    var dateLabelText: String {
        let cal = Calendar.current
        if cal.isDateInToday(currentDate)     { return "Today" }
        if cal.isDateInYesterday(currentDate) { return "Yesterday" }
        if cal.isDateInTomorrow(currentDate)  { return "Tmrw" }
        let fmt = DateFormatter()
        fmt.dateFormat = "EEE, MMM d"
        return fmt.string(from: currentDate)
    }

    /// Long-form date string used in VoiceOver announcements and accessibility labels.
    var dateAccessibilityString: String {
        let cal = Calendar.current
        if cal.isDateInToday(currentDate)     { return "Today" }
        if cal.isDateInYesterday(currentDate) { return "Yesterday" }
        if cal.isDateInTomorrow(currentDate)  { return "Tomorrow" }
        let fmt = DateFormatter()
        fmt.dateFormat = "EEEE, MMMM d"
        return fmt.string(from: currentDate)
    }

    // MARK: - Fetch

    private let apiService = ESPNAPIService.shared

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
            isOnCurrentWeek = false
        } else {
            currentDate = Calendar.current.date(byAdding: .day, value: 1, to: currentDate) ?? currentDate
        }
        await fetchGames(for: sport)
    }

    func goBack(for sport: Sport) async {
        if sport.isFootball {
            let prev = (currentWeek ?? 2) - 1
            if prev >= 1 {
                currentWeek = prev
                isOnCurrentWeek = false
            }
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
        isOnCurrentWeek = true
        await fetchGames(for: sport)
    }

    func refresh(for sport: Sport) async {
        await fetchGames(for: sport)
    }
}
