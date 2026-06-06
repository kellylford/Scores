//
//  WorldCupViewModel.swift
//  SportsScores
//
//  Manages all state for the World Cup hub:
//    • Groups tab  — group standings
//    • Scores tab  — games for the selected date (±7 days from today)
//    • Bracket tab — games for the selected tournament phase
//

import Foundation

@MainActor
final class WorldCupViewModel: ObservableObject {

    // MARK: - Published state

    @Published var groups: [WorldCupGroup] = []
    @Published var isLoadingGroups = false
    @Published var groupsError: String? = nil

    @Published var games: [Game] = []
    @Published var isLoadingGames = false
    @Published var gamesError: String? = nil
    @Published var selectedDate: Date

    @Published var bracketGames: [Game] = []
    @Published var isLoadingBracket = false
    @Published var bracketError: String? = nil
    @Published var selectedPhaseId: String

    // MARK: - Configuration

    let sport: Sport
    let phases: [WorldCupPhase]

    // MARK: - Private

    private let api = ESPNAPIService.shared
    private let navRange = 7   // days either side of today for date nav

    // MARK: - Init

    init(sport: Sport) {
        self.sport = sport
        self.phases = sport == .worldCup ? WorldCupPhase.wc2026 : WorldCupPhase.wwc2027
        self.selectedDate = Calendar.current.startOfDay(for: Date())

        // Pre-select the currently active phase, or the first phase.
        let now = Date()
        let active = phases.first(where: { now >= $0.startDate && now <= $0.endDate })
                  ?? phases.last
        self.selectedPhaseId = active?.id ?? phases.first?.id ?? "1"
    }

    // MARK: - Load all

    func loadAll() async {
        async let g: () = loadGroups()
        async let s: () = loadGamesForDate()
        _ = await (g, s)
    }

    // MARK: - Groups

    func loadGroups() async {
        isLoadingGroups = true
        groupsError = nil
        do {
            groups = try await api.fetchWorldCupStandings(for: sport)
        } catch {
            groupsError = "Could not load group standings."
        }
        isLoadingGroups = false
    }

    // MARK: - Scores (date-based)

    func loadGamesForDate() async {
        isLoadingGames = true
        gamesError = nil
        do {
            games = try await api.fetchGames(for: sport, date: selectedDate)
        } catch {
            gamesError = "Could not load games."
        }
        isLoadingGames = false
    }

    // MARK: - Date navigation

    private var navStart: Date {
        Calendar.current.date(byAdding: .day, value: -navRange,
                              to: Calendar.current.startOfDay(for: Date())) ?? Date()
    }
    private var navEnd: Date {
        Calendar.current.date(byAdding: .day, value: navRange,
                              to: Calendar.current.startOfDay(for: Date())) ?? Date()
    }

    var canNavigateBackward: Bool { selectedDate > navStart }
    var canNavigateForward:  Bool { selectedDate < navEnd }
    var isOnToday: Bool { Calendar.current.isDateInToday(selectedDate) }

    var dateHeaderText: String {
        if Calendar.current.isDateInToday(selectedDate) { return "Today's Matches" }
        let fmt = DateFormatter()
        fmt.dateFormat = "EEEE"
        return "\(fmt.string(from: selectedDate))'s Matches"
    }

    var dateAccessibilityText: String {
        if Calendar.current.isDateInToday(selectedDate) { return "Today" }
        if Calendar.current.isDateInYesterday(selectedDate) { return "Yesterday" }
        if Calendar.current.isDateInTomorrow(selectedDate) { return "Tomorrow" }
        let fmt = DateFormatter()
        fmt.dateFormat = "EEEE, MMMM d"
        return fmt.string(from: selectedDate)
    }

    func goBack() async {
        guard canNavigateBackward else { return }
        selectedDate = Calendar.current.date(byAdding: .day, value: -1, to: selectedDate) ?? selectedDate
        await loadGamesForDate()
    }

    func goForward() async {
        guard canNavigateForward else { return }
        selectedDate = Calendar.current.date(byAdding: .day, value: 1, to: selectedDate) ?? selectedDate
        await loadGamesForDate()
    }

    func goToToday() async {
        selectedDate = Calendar.current.startOfDay(for: Date())
        await loadGamesForDate()
    }

    // MARK: - Bracket (phase-based)

    var selectedPhase: WorldCupPhase? {
        phases.first(where: { $0.id == selectedPhaseId })
    }

    func loadBracket(for phase: WorldCupPhase) async {
        selectedPhaseId = phase.id
        guard phase.id != "1" else { return } // Group Stage shows the groups view, no game list needed
        isLoadingBracket = true
        bracketError = nil
        do {
            bracketGames = try await api.fetchGamesRange(for: sport,
                                                         startDate: phase.startDate,
                                                         endDate: phase.endDate)
        } catch {
            bracketError = "Could not load bracket matches."
        }
        isLoadingBracket = false
    }

    // MARK: - Game grouping helpers (used by Scores tab)

    var inProgressGames: [Game]  { games.filter { $0.status.isLive } }
    var upcomingGames: [Game]    { games.filter { !$0.status.isLive && !$0.status.isCompleted
                                                  && !$0.status.isPostponed && !$0.status.isCancelled } }
    var completedGames: [Game]   { games.filter { $0.status.isCompleted } }
    var postponedGames: [Game]   { games.filter { $0.status.isPostponed || $0.status.isCancelled } }
}
