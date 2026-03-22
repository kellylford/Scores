//
//  TeamScheduleViewModel.swift
//  SportsScores
//
//  Created on 2/26/26.
//

import Foundation

@MainActor
class TeamScheduleViewModel: ObservableObject {
    @Published var games: [ScheduleGame] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedYear: Int

    private let apiService = ESPNAPIService.shared
    private let teamId: String
    private let sport: Sport

    // Available years to display in the picker (current year and 4 prior)
    let availableYears: [Int]

    init(teamId: String, sport: Sport) {
        self.teamId = teamId
        self.sport = sport
        let year = Self.defaultSeasonYear(for: sport)
        self.selectedYear = year
        self.availableYears = (0..<5).map { year - $0 }
    }

    /// Returns the season year to request from ESPN for a given sport.
    /// MLB spring training runs Feb–March; during that window request the
    /// current year (spring data) rather than last year's completed season.
    /// For sports where ESPN uses year+1 (NBA, WNBA) adjust accordingly.
    /// Football seasons (NFL, NCAAF) start in Aug/Sep and end in Jan/Feb of
    /// the following year — so Jan–Jul still belong to the prior season year.
    static func defaultSeasonYear(for sport: Sport) -> Int {
        let cal = Calendar.current
        let now = Date()
        let year = cal.component(.year, from: now)
        let month = cal.component(.month, from: now)

        if sport.usesNextYearFormat {
            // NBA/WNBA 2025-26 season → pass 2026
            return month >= 10 ? year + 1 : year
        }

        // Football seasons start in Aug/Sep and run into Jan/Feb of the next
        // calendar year. During Jan–Jul we're still in last year's season.
        if sport.isFootball && month < 8 {
            return year - 1
        }

        // For all other sports the season year matches the calendar year.
        return year
    }

    /// Season types to fetch for a given sport and year.
    /// MLB: pre (spring training) + regular + postseason.
    /// Football: preseason + regular + postseason (bowls/playoffs).
    /// All other sports: regular + postseason so playoff games appear.
    private var seasonTypesToFetch: [Int] {
        if sport == .mlb { return [1, 2, 3] }
        if sport.isFootball { return [1, 2, 3] }
        return [2, 3]
    }

    func fetchSchedule() async {
        isLoading = true
        errorMessage = nil
        var allGames: [ScheduleGame] = []

        await withTaskGroup(of: [ScheduleGame].self) { group in
            for st in seasonTypesToFetch {
                group.addTask { [self] in
                    (try? await self.apiService.fetchTeamSchedule(
                        teamId: self.teamId,
                        sport: self.sport,
                        season: self.selectedYear,
                        seasonType: st
                    )) ?? []
                }
            }
            for await result in group {
                allGames.append(contentsOf: result)
            }
        }

        if allGames.isEmpty {
            errorMessage = "No schedule data available for \(selectedYear)."
        }
        games = allGames.sorted { $0.date < $1.date }
        isLoading = false
    }

    func changeYear(_ year: Int) async {
        selectedYear = year
        await fetchSchedule()
    }
}
