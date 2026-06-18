//
//  CFLAPIService.swift
//  SportsScores
//
//  Data client for the Canadian Football League.
//
//  ESPN does not carry live CFL game data (its `football/cfl` scoreboard is
//  frozen at the 2022 season), so CFL is sourced from the public scoreboard
//  widget feed behind cfl.ca, which is powered by Genius Sports:
//
//    https://cflscoreboard.cfl.ca/json/scoreboard/rounds.json   — full season
//    https://cflscoreboard.cfl.ca/json/scoreboard/squads.json   — teams + records
//
//  This feed is unofficial and undocumented, so it can change without notice.
//  It provides scores, schedule, live status, and win/loss records — but no
//  play-by-play, rosters, news, or statistics. The app degrades gracefully
//  where those are unavailable.
//
//  The two JSON documents describe the entire season in one fetch each, so a
//  short in-memory cache keeps date navigation and auto-refresh cheap.
//

import Foundation

final class CFLAPIService {
    static let shared = CFLAPIService()

    private let roundsURL = URL(string: "https://cflscoreboard.cfl.ca/json/scoreboard/rounds.json")!
    private let squadsURL = URL(string: "https://cflscoreboard.cfl.ca/json/scoreboard/squads.json")!
    private let session: URLSession

    /// Cache lifetime. Short enough that live scores update on auto-refresh,
    /// long enough that navigating between days doesn't re-fetch repeatedly.
    private let cacheTTL: TimeInterval = 25

    private var cachedFeed: Feed?
    private var cacheTimestamp: Date?

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        // Always pull a fresh copy when the cache has expired rather than a
        // stale CDN-cached response.
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        self.session = URLSession(configuration: config)
    }

    // MARK: - Division layout (East / West)

    /// CFL division membership keyed by team abbreviation (the feed's `shortName`).
    private static let eastTeams: Set<String> = ["HAM", "MTL", "OTT", "TOR"]
    private static let westTeams: Set<String> = ["BC", "CGY", "EDM", "SSK", "WPG"]

    private static func divisionName(for abbreviation: String) -> String {
        westTeams.contains(abbreviation) ? "West Division" : "East Division"
    }

    // MARK: - Public API

    /// Games taking place on the given calendar day (local time), grouped exactly
    /// like every other sport so `ScoresView` can render them unchanged.
    func fetchGames(on date: Date) async throws -> [Game] {
        let feed = try await loadFeed()
        let cal = Calendar.current
        return feed.allTournaments()
            .filter { cal.isDate($0.tournament.parsedDate, inSameDayAs: date) }
            .map { makeGame(from: $0.tournament, seasonType: $0.seasonType, records: feed.recordMap) }
            .sorted { $0.date < $1.date }
    }

    /// Number of games scheduled on the given day — for the home-page badge.
    func gameCount(on date: Date) async -> Int {
        (try? await fetchGames(on: date))?.count ?? 0
    }

    /// East / West standings built from each team's win-loss-draw record.
    func fetchStandings() async throws -> [StandingsGroup] {
        let feed = try await loadFeed()
        var buckets: [String: [StandingsEntry]] = ["East Division": [], "West Division": []]

        for squad in feed.squads where squad.id != 0 {
            let division = Self.divisionName(for: squad.abbreviation)
            buckets[division, default: []].append(standingsEntry(from: squad))
        }

        // Order East before West; sort each by win% then wins, and assign ranks.
        return ["East Division", "West Division"].compactMap { name in
            guard var entries = buckets[name], !entries.isEmpty else { return nil }
            entries.sort {
                $0.stats.winPercent != $1.stats.winPercent
                    ? $0.stats.winPercent > $1.stats.winPercent
                    : $0.stats.wins > $1.stats.wins
            }
            let ranked = entries.enumerated().map { idx, entry in
                StandingsEntry(rank: idx + 1, team: entry.team, stats: entry.stats)
            }
            return StandingsGroup(name: name, entries: ranked)
        }
    }

    /// All teams, sorted by name — for the Team Hub team picker.
    func fetchTeams() async throws -> [TransactionTeam] {
        let feed = try await loadFeed()
        return feed.squads
            .filter { $0.id != 0 }
            .map {
                TransactionTeam(
                    id: String($0.id),
                    location: nil,
                    name: nil,
                    abbreviation: $0.abbreviation,
                    displayName: $0.name,
                    color: nil,
                    logos: nil
                )
            }
            .sorted { $0.displayName < $1.displayName }
    }

    /// Every game a team plays this season, oldest first — for the Team Hub schedule tab.
    func fetchSchedule(teamId: String) async throws -> [ScheduleGame] {
        let feed = try await loadFeed()
        return feed.allTournaments()
            .filter { String($0.tournament.homeSquad.id) == teamId || String($0.tournament.awaySquad.id) == teamId }
            .map { makeScheduleGame(from: $0.tournament, seasonType: $0.seasonType) }
            .sorted { $0.date < $1.date }
    }

    /// Team Hub Info-tab summary: record, division standing, and next game.
    func fetchTeamInfo(teamId: String) async throws -> TeamHubTeamInfo {
        let feed = try await loadFeed()
        guard let squad = feed.squads.first(where: { String($0.id) == teamId }) else {
            throw APIError.invalidResponse
        }

        // Division rank from the computed standings.
        let standings = try await fetchStandings()
        var standingSummary: String?
        for group in standings {
            if let idx = group.entries.firstIndex(where: { $0.team.id == teamId }) {
                standingSummary = "\(ordinal(idx + 1)) in \(group.name)"
                break
            }
        }

        // Next scheduled game.
        let schedule = try await fetchSchedule(teamId: teamId)
        let now = Date()
        var nextGame: TeamHubNextGame?
        if let upcoming = schedule.first(where: { !$0.isCompleted && !$0.isInProgress && $0.date > now }) {
            let isHome = upcoming.homeTeam.id == teamId
            let opponent = isHome ? upcoming.awayTeam : upcoming.homeTeam
            nextGame = TeamHubNextGame(
                gameId: upcoming.id,
                date: upcoming.date,
                opponentDisplayName: opponent.displayName,
                opponentAbbreviation: opponent.abbreviation,
                isHome: isHome
            )
        }

        return TeamHubTeamInfo(
            teamId: teamId,
            displayName: squad.name,
            abbreviation: squad.abbreviation,
            location: squad.name,
            color: nil,
            alternateColor: nil,
            primaryLogoURL: nil,
            overallRecord: squad.recordString,
            homeRecord: nil,
            awayRecord: nil,
            standingSummary: standingSummary,
            venueName: nil,
            venueCity: nil,
            coachName: nil,
            nextGame: nextGame
        )
    }

    // MARK: - Feed loading + cache

    private func loadFeed() async throws -> Feed {
        if let cached = cachedFeed, let stamp = cacheTimestamp,
           Date().timeIntervalSince(stamp) < cacheTTL {
            return cached
        }

        // Both documents fetch concurrently; decode once each is in.
        async let roundsData = fetch(roundsURL)
        async let squadsData = fetch(squadsURL)
        let rounds = try JSONDecoder().decode([CFLRound].self, from: try await roundsData)
        let squads = try JSONDecoder().decode([CFLSquad].self, from: try await squadsData)

        let feed = Feed(rounds: rounds, squads: squads)
        cachedFeed = feed
        cacheTimestamp = Date()
        return feed
    }

    private func fetch(_ url: URL) async throws -> Data {
        var request = URLRequest(url: url)
        // The feed only serves browser-like clients reliably.
        request.setValue("Mozilla/5.0", forHTTPHeaderField: "User-Agent")
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        return data
    }

    // MARK: - Mapping helpers

    private func makeGame(from t: CFLTournament, seasonType: Int, records: [Int: String]) -> Game {
        let status = gameStatus(for: t)
        let suppressScores = status.state == "pre"

        func team(_ squad: CFLSquadScore) -> Game.Team {
            Game.Team(
                id: String(squad.id),
                name: squad.name,
                abbreviation: squad.shortName,
                displayName: squad.name,
                score: suppressScores ? nil : squad.score,
                record: records[squad.id],
                logo: nil
            )
        }

        return Game(
            id: String(t.id),
            name: "\(t.awaySquad.name) at \(t.homeSquad.name)",
            shortName: "\(t.awaySquad.shortName) @ \(t.homeSquad.shortName)",
            date: t.parsedDate,
            status: status,
            homeTeam: team(t.homeSquad),
            awayTeam: team(t.awaySquad),
            venue: nil,
            broadcasts: [],
            situation: nil,
            seasonType: seasonType
        )
    }

    private func gameStatus(for t: CFLTournament) -> Game.GameStatus {
        switch t.status {
        case "complete":
            return Game.GameStatus(state: "post", detail: "Final", period: nil, clock: nil, name: "STATUS_FINAL")
        case "playing":
            var detail = "In Progress"
            if let period = t.activePeriod {
                detail = "Q\(period)"
                if let clock = t.clock, !clock.isEmpty { detail += " \(clock)" }
            } else if let clock = t.clock, !clock.isEmpty {
                detail = clock
            }
            return Game.GameStatus(state: "in", detail: detail, period: t.activePeriod,
                                   clock: t.clock, name: "STATUS_IN_PROGRESS")
        default: // "scheduled"
            return Game.GameStatus(state: "pre", detail: "Scheduled", period: nil, clock: nil, name: "STATUS_SCHEDULED")
        }
    }

    private func makeScheduleGame(from t: CFLTournament, seasonType: Int) -> ScheduleGame {
        let statusType: String
        let statusText: String
        switch t.status {
        case "complete": statusType = "STATUS_FINAL";       statusText = "Final"
        case "playing":  statusType = "STATUS_IN_PROGRESS"; statusText = "In Progress"
        default:         statusType = "STATUS_SCHEDULED";   statusText = "Scheduled"
        }
        let played = t.status != "scheduled"
        return ScheduleGame(
            id: String(t.id),
            date: t.parsedDate,
            name: "\(t.awaySquad.name) at \(t.homeSquad.name)",
            awayTeam: ScheduleGame.ScheduleTeam(
                id: String(t.awaySquad.id),
                abbreviation: t.awaySquad.shortName,
                displayName: t.awaySquad.name,
                score: played ? t.awaySquad.score : nil
            ),
            homeTeam: ScheduleGame.ScheduleTeam(
                id: String(t.homeSquad.id),
                abbreviation: t.homeSquad.shortName,
                displayName: t.homeSquad.name,
                score: played ? t.homeSquad.score : nil
            ),
            statusText: statusText,
            statusType: statusType,
            seasonType: seasonType,
            venueName: nil
        )
    }

    private func standingsEntry(from squad: CFLSquad) -> StandingsEntry {
        let games = squad.wins + squad.loss + squad.draw
        let winPercent = games > 0 ? (Double(squad.wins) + 0.5 * Double(squad.draw)) / Double(games) : 0
        let stats = StandingsEntry.StandingsStats(
            wins: squad.wins,
            losses: squad.loss,
            winPercent: winPercent,
            gamesBack: "-",
            streak: "-",
            record: squad.recordString,
            pointsFor: nil,
            pointsAgainst: nil,
            ties: squad.draw > 0 ? squad.draw : nil,
            otLosses: nil,
            nhlPoints: nil,
            avgPointsFor: nil,
            avgPointsAgainst: nil,
            homeRecord: nil,
            roadRecord: nil,
            lastTenRecord: nil,
            divisionRecord: nil,
            playoffSeed: nil,
            differential: nil
        )
        let team = StandingsEntry.TeamInfo(
            id: String(squad.id),
            name: squad.name,
            abbreviation: squad.abbreviation,
            displayName: squad.name,
            logo: nil
        )
        // Rank is assigned after sorting in fetchStandings().
        return StandingsEntry(rank: 0, team: team, stats: stats)
    }

    private func ordinal(_ n: Int) -> String {
        switch n {
        case 1: return "1st"
        case 2: return "2nd"
        case 3: return "3rd"
        default: return "\(n)th"
        }
    }

    // MARK: - Decoded feed

    private struct Feed {
        let rounds: [CFLRound]
        let squads: [CFLSquad]

        /// Maps a season-type label (PRE/REG/POST) to the ESPN season-type
        /// convention used throughout the app (1 pre / 2 regular / 3 post).
        private static func seasonType(for roundType: String) -> Int {
            switch roundType {
            case "PRE":  return 1
            case "POST": return 3
            default:     return 2
            }
        }

        /// Flattened (tournament, seasonType) pairs across every round.
        func allTournaments() -> [(tournament: CFLTournament, seasonType: Int)] {
            rounds.flatMap { round in
                round.tournaments
                    .filter { !($0.isHidden ?? false) }
                    .map { ($0, Feed.seasonType(for: round.type)) }
            }
        }

        /// Team id → "W-L" (or "W-L-D") record string, from squads.
        var recordMap: [Int: String] {
            Dictionary(uniqueKeysWithValues: squads.map { ($0.id, $0.recordString) })
        }
    }
}

// MARK: - Raw JSON models

private struct CFLRound: Decodable {
    let name: String
    let type: String        // "PRE" | "REG" | "POST"
    let number: Int?
    let tournaments: [CFLTournament]
}

private struct CFLTournament: Decodable {
    let id: Int
    let date: String
    let status: String      // "scheduled" | "playing" | "complete"
    let homeSquad: CFLSquadScore
    let awaySquad: CFLSquadScore
    let activePeriod: Int?
    let clock: String?
    let winner: Int?
    let isHidden: Bool?

    /// Parsed kickoff time. The feed uses ISO-8601 with an explicit offset,
    /// e.g. "2026-06-12T00:30:00+00:00".
    var parsedDate: Date {
        let fmt = DateFormatter()
        fmt.locale = Locale(identifier: "en_US_POSIX")
        let formats = [
            "yyyy-MM-dd'T'HH:mm:ssZZZZZ",
            "yyyy-MM-dd'T'HH:mmZZZZZ",
            "yyyy-MM-dd'T'HH:mm:ss'Z'"
        ]
        for f in formats {
            fmt.dateFormat = f
            if let d = fmt.date(from: date) { return d }
        }
        return ISO8601DateFormatter().date(from: date) ?? Date()
    }
}

private struct CFLSquadScore: Decodable {
    let id: Int
    let name: String
    let shortName: String
    let score: Int?
}

private struct CFLSquad: Decodable {
    let id: Int
    let name: String
    let abbreviation: String
    let wins: Int
    let draw: Int
    let loss: Int

    /// "W-L" or "W-L-D" when there are draws.
    var recordString: String {
        draw > 0 ? "\(wins)-\(loss)-\(draw)" : "\(wins)-\(loss)"
    }
}
