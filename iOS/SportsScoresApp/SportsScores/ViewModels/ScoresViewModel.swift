//
//  ScoresViewModel.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

// MARK: - Auto-refresh interval

enum AutoRefreshInterval: Int, CaseIterable, Identifiable {
    case oneMinute     = 60
    case twoMinutes    = 120
    case fiveMinutes   = 300
    case manual        = 0

    var id: Int { rawValue }

    var label: String {
        switch self {
        case .oneMinute:     return "1m"
        case .twoMinutes:    return "2m"
        case .fiveMinutes:   return "5m"
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
    /// Set to a specific season year when the user picks a historical season.
    /// `nil` means "let the ESPN API resolve to the current season."
    @Published var currentSeason: Int?
    /// The API-resolved season year (used for the UI label).
    @Published var resolvedSeason: Int = Calendar.current.component(.year, from: Date())

    /// Available season types for the currently selected historical football season.
    /// Empty when viewing the current (live) season — ESPN handles type resolution automatically.
    @Published var availableSeasonTypes: [SeasonTypeInfo] = []

    // MARK: - Private football calendar state

    /// Calendar loaded from the ESPN Core API for the current historical season.
    private var footballCalendar: SeasonCalendar?

    // MARK: - Computed helpers

    /// Week number bounds for the current season type, derived from the fetched calendar.
    /// `nil` when viewing the live (current) season — no hard bounds are enforced there.
    var currentWeekBounds: (min: Int, max: Int)? {
        guard let cal = footballCalendar else { return nil }
        let count = cal.weekCount(for: currentSeasonType)
        guard count > 0 else { return nil }
        return (min: 1, max: count)
    }

    /// True when the current week is the first week of the active season type
    /// and a calendar is loaded (i.e. the back arrow should be disabled).
    var isAtWeekStart: Bool {
        guard let bounds = currentWeekBounds else { return false }
        return (currentWeek ?? 1) <= bounds.min
    }

    /// True when the current week is the last week of the active season type
    /// and a calendar is loaded (i.e. the forward arrow should be disabled).
    var isAtWeekEnd: Bool {
        guard let bounds = currentWeekBounds else { return false }
        return (currentWeek ?? 1) >= bounds.max
    }

    // MARK: - Sectioned game lists

    var inProgressGames: [Game] { games.filter { $0.status.isLive } }
    var upcomingGames:   [Game] { games.filter { !$0.status.isLive && !$0.status.isCompleted }.sorted { $0.date < $1.date } }
    var completedGames:  [Game] { games.filter { $0.status.isCompleted && !$0.status.isPostponed && !$0.status.isCancelled } }
    /// Games that were postponed, cancelled, or otherwise did not take place.
    var postponedGames:  [Game] { games.filter { $0.status.isPostponed || $0.status.isCancelled } }

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

    /// The logical season display year for the currently visible date for non-football sports.
    /// Accounts for the year+1 API convention (e.g. NBA Oct 2022 → display year 2023).
    func displaySeasonYear(for sport: Sport) -> Int {
        let cal  = Calendar.current
        let year  = cal.component(.year,  from: currentDate)
        let month = cal.component(.month, from: currentDate)
        if sport.usesNextYearFormat {
            // Season starts ~October; Oct–Dec belong to the next year's season.
            return month >= 10 ? year + 1 : year
        }
        return year
    }

    // MARK: - Fetch

    private let apiService = ESPNAPIService.shared

    func fetchGames(for sport: Sport) async {
        isLoading = true
        errorMessage = nil

        do {
            if sport.isFootball {
                if let season = currentSeason {
                    // Historical season: fetch via Core API date ranges.
                    let week = currentWeek ?? 1
                    let result = try await apiService.fetchFootballWeek(
                        sport: sport,
                        season: season,
                        seasonType: currentSeasonType,
                        week: week
                    )
                    games             = result.games
                    currentWeek       = result.week
                    weekLabel         = result.weekLabel
                    currentSeasonType = result.seasonType
                    resolvedSeason    = result.season
                } else {
                    // Current (live) season: let ESPN resolve the week automatically.
                    let result = try await apiService.fetchFootballGames(
                        for: sport,
                        week: currentWeek,
                        season: nil,
                        seasonType: currentSeasonType
                    )
                    games             = result.games
                    currentWeek       = result.week
                    weekLabel         = result.weekLabel
                    currentSeasonType = result.seasonType
                    resolvedSeason    = result.season
                }
            } else {
                games = try await apiService.fetchGames(for: sport, date: currentDate)
            }
        } catch {
            errorMessage = "Failed to load games: \(error.localizedDescription)"
        }

        isLoading = false
    }

    // MARK: - Navigation

    func goForward(for sport: Sport) async {
        if sport.isFootball {
            let nextWeek = (currentWeek ?? 1) + 1
            // Respect bounds when we have a loaded calendar.
            if let bounds = currentWeekBounds, nextWeek > bounds.max { return }
            currentWeek = nextWeek
            isOnCurrentWeek = false
        } else {
            currentDate = Calendar.current.date(byAdding: .day, value: 1, to: currentDate) ?? currentDate
        }
        await fetchGames(for: sport)
    }

    func goBack(for sport: Sport) async {
        if sport.isFootball {
            let prevWeek = (currentWeek ?? 2) - 1
            if prevWeek < 1 { return }
            // Respect bounds when we have a loaded calendar.
            if let bounds = currentWeekBounds, prevWeek < bounds.min { return }
            currentWeek = prevWeek
            isOnCurrentWeek = false
        } else {
            currentDate = Calendar.current.date(byAdding: .day, value: -1, to: currentDate) ?? currentDate
        }
        await fetchGames(for: sport)
    }

    func goToDate(_ date: Date, for sport: Sport) async {
        currentDate = Calendar.current.startOfDay(for: date)
        await fetchGames(for: sport)
    }

    /// Navigate to a historical (or current) season.
    ///
    /// - Football: fetches the season calendar from the Core API to discover
    ///   available season types and week counts, then loads week 1 regular season.
    /// - Non-football: jumps to the approximate opening date for the season.
    func goToSeason(_ year: Int, for sport: Sport) async {
        if sport.isFootball {
            // If the user tapped the year that's already the live season,
            // treat it as a "go back to current" action.
            let isLiveSeason = (currentSeason == nil && year == resolvedSeason)
            if isLiveSeason {
                await goToToday(for: sport)
                return
            }

            // Switch to historical mode.
            currentSeason       = year
            currentWeek         = nil
            currentSeasonType   = 2
            isOnCurrentWeek     = false
            footballCalendar    = nil
            availableSeasonTypes = []

            // Load the season calendar: which types exist and how many weeks?
            if let cal = try? await apiService.fetchFootballCalendar(sport: sport, season: year) {
                footballCalendar     = cal
                availableSeasonTypes = cal.seasonTypes
                // Default to regular season week 1; fall back to whatever is available.
                if cal.hasSeasonType(2) {
                    currentSeasonType = 2
                } else if let first = cal.seasonTypes.first {
                    currentSeasonType = first.type
                }
                currentWeek = 1
            } else {
                // Calendar fetch failed — still try week 1 regular season.
                currentWeek = 1
            }
        } else {
            // Non-football: jump to the approximate start of that season.
            currentDate = sport.approximateSeasonStartDate(year: year)
        }
        await fetchGames(for: sport)
    }

    /// Switch to a different season type within the current historical football season.
    /// No-op if the type isn't in the loaded calendar or if no calendar is loaded.
    func goToSeasonType(_ type: Int, for sport: Sport) async {
        guard let cal = footballCalendar, cal.hasSeasonType(type) else { return }
        currentSeasonType = type
        currentWeek       = 1
        await fetchGames(for: sport)
    }

    func goToToday(for sport: Sport) async {
        currentDate          = Calendar.current.startOfDay(for: Date())
        currentWeek          = nil
        currentSeason        = nil   // nil → ESPN resolves to current season
        currentSeasonType    = 2
        isOnCurrentWeek      = true
        footballCalendar     = nil
        availableSeasonTypes = []
        await fetchGames(for: sport)
    }

    func refresh(for sport: Sport) async {
        await fetchGames(for: sport)
    }
}

