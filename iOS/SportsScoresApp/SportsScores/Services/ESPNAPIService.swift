//
//  ESPNAPIService.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

class ESPNAPIService {
    static let shared = ESPNAPIService()
    
    private let baseURL = "https://site.api.espn.com/apis/site/v2/sports"
    /// Standings uses a different ESPN API base path (v2, not site/v2)
    private let standingsBaseURL = "https://site.api.espn.com/apis/v2/sports"
    /// Core API for leaders/statistics
    private let coreAPIBaseURL = "https://sports.core.api.espn.com/v2/sports"
    private let session: URLSession
    
    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)
    }
    
    // MARK: - Fetch Games (non-football, optional date)

    func fetchGames(for sport: Sport, date: Date? = nil) async throws -> [Game] {
        var urlString = "\(baseURL)/\(sport.apiPath)/scoreboard"
        if let date = date {
            let fmt = DateFormatter()
            fmt.dateFormat = "yyyyMMdd"
            urlString += "?dates=\(fmt.string(from: date))"
        }
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }

        let (data, response) = try await session.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else { throw APIError.invalidResponse }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let apiResponse = try decoder.decode(ScoreboardResponse.self, from: data)
        let seasonType = apiResponse.season?.type ?? 2
        return try apiResponse.events.map { try Game(from: $0, seasonType: seasonType) }
    }

    // MARK: - Fetch Football Games (week-based navigation)

    struct FootballScoreboardResult {
        let games: [Game]
        let week: Int
        let weekLabel: String
        let seasonType: Int
        let season: Int
    }

    func fetchFootballGames(for sport: Sport,
                            week: Int? = nil,
                            season: Int? = nil,
                            seasonType: Int = 2) async throws -> FootballScoreboardResult {
        var components: [String] = []
        components.append("seasontype=\(seasonType)")
        if let w = week { components.append("week=\(w)") }
        if let s = season { components.append("season=\(s)") }
        let query = components.isEmpty ? "" : "?" + components.joined(separator: "&")
        let urlString = "\(baseURL)/\(sport.apiPath)/scoreboard\(query)"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }

        let (data, response) = try await session.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else { throw APIError.invalidResponse }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let apiResponse = try decoder.decode(ScoreboardResponse.self, from: data)
        let resolvedSeasonType = apiResponse.season?.type ?? seasonType
        let resolvedSeason = apiResponse.season?.year ?? season ?? Calendar.current.component(.year, from: Date())
        let resolvedWeek = apiResponse.week?.number ?? week ?? 1
        let weekLabel = apiResponse.week?.text ?? "Week \(resolvedWeek)"
        let games = try apiResponse.events.map { try Game(from: $0, seasonType: resolvedSeasonType) }
        return FootballScoreboardResult(
            games: games,
            week: resolvedWeek,
            weekLabel: weekLabel,
            seasonType: resolvedSeasonType,
            season: resolvedSeason
        )
    }

    // MARK: - Fetch News

    func fetchNews(for sport: Sport, limit: Int = 25) async throws -> [NewsItem] {
        let urlString = "\(baseURL)/\(sport.apiPath)/news?limit=\(limit)"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }

        let (data, response) = try await session.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else { throw APIError.invalidResponse }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let apiResponse = try decoder.decode(NewsAPIResponse.self, from: data)
        return apiResponse.articles.map { NewsItem(from: $0) }
    }
    
    // MARK: - Fetch Standings
    func fetchStandings(for sport: Sport) async throws -> [StandingsGroup] {
        let urlString = "\(standingsBaseURL)/\(sport.apiPath)/standings"
        guard let url = URL(string: urlString) else {
            throw APIError.invalidURL
        }

        let (data, response) = try await session.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let apiResponse = try decoder.decode(APIStandingsResponse.self, from: data)

        // If the sport has a division mapper, sub-divide the flat conference entries
        // into proper divisions (e.g. "AL East", "AFC North").  Otherwise fall back
        // to the conference-level groupings from the API.
        if DivisionMapper.hasDivisions(sport) {
            return groupByDivision(apiResponse.children, sport: sport)
        } else {
            return try apiResponse.children.map { try StandingsGroup(from: $0) }
        }
    }

    /// Collect all entries from every conference child, assign each to a division
    /// via DivisionMapper, then produce a sorted [StandingsGroup].
    private func groupByDivision(_ children: [APIStandingsGroup], sport: Sport) -> [StandingsGroup] {
        // Bucket entries by division name
        var buckets: [String: [StandingsEntry]] = [:]

        for child in children {
            for apiEntry in child.standings.entries {
                let abbr = apiEntry.team.abbreviation
                let divisionName = DivisionMapper.division(for: sport, abbreviation: abbr)
                                   ?? child.name   // fallback to conference name
                let entry = StandingsEntry(fromAPIEntry: apiEntry)
                buckets[divisionName, default: []].append(entry)
            }
        }

        // Sort entries within each division by win% descending, then wins descending
        for key in buckets.keys {
            buckets[key]?.sort {
                if $0.stats.winPercent != $1.stats.winPercent {
                    return $0.stats.winPercent > $1.stats.winPercent
                }
                return $0.stats.wins > $1.stats.wins
            }
        }

        // Sort division groups by predefined order, unknown divisions appended last
        let order = DivisionMapper.divisionOrder(for: sport)
        var groups: [StandingsGroup] = []
        for divName in order {
            if let entries = buckets[divName], !entries.isEmpty {
                groups.append(StandingsGroup(name: divName, entries: entries))
            }
        }
        // Append any unmapped divisions alphabetically
        let unknown = buckets.keys.filter { !order.contains($0) }.sorted()
        for divName in unknown {
            if let entries = buckets[divName] {
                groups.append(StandingsGroup(name: divName, entries: entries))
            }
        }
        return groups
    }
    
    // MARK: - Fetch Game Details
    func fetchGameDetails(for gameId: String, sport: Sport) async throws -> GameDetails {
        let urlString = "\(baseURL)/\(sport.apiPath)/summary?event=\(gameId)"
        guard let url = URL(string: urlString) else {
            throw APIError.invalidURL
        }
        
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let details = try decoder.decode(GameDetails.self, from: data)
        
        return details
    }

    // MARK: - Fetch Team Schedule

    /// Fetch the schedule for a single team and season type.
    func fetchTeamSchedule(teamId: String, sport: Sport, season: Int, seasonType: Int) async throws -> [ScheduleGame] {
        let urlString = "\(baseURL)/\(sport.apiPath)/teams/\(teamId)/schedule?season=\(season)&seasontype=\(seasonType)"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }

        let (data, response) = try await session.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }

        let apiResponse = try JSONDecoder().decode(TeamScheduleAPIResponse.self, from: data)
        return apiResponse.events.compactMap { $0.toScheduleGame() }
    }

    // MARK: - Fetch League Leaders (Phase 5)

    func fetchLeagueLeaders(for sport: Sport) async throws -> [LeagueLeaderCategory] {
        // Extract league from apiPath (e.g., "basketball/nba" → "nba")
        let league = sport.apiPath.components(separatedBy: "/").last ?? sport.rawValue.lowercased()
        let sportType = sport.apiPath.components(separatedBy: "/").first ?? "unknown"
        
        // Get current season year (NBA/WNBA use year+1 format)
        let currentYear = Calendar.current.component(.year, from: Date())
        let seasonYear = sport.usesNextYearFormat ? currentYear + 1 : currentYear
        
        // Get season types to try (MLB spring training in Feb-March uses type 1)
        let seasonTypes = getSeasonTypes(for: sport)
        
        // Try current season with all season types, then fallback to previous seasons
        let seasonsToTry = [seasonYear, seasonYear - 1, seasonYear - 2]
        
        for season in seasonsToTry {
            for seasonType in seasonTypes {
                do {
                    let categories = try await fetchLeadersForSeason(
                        sportType: sportType,
                        league: league,
                        season: season,
                        seasonType: seasonType
                    )
                    if !categories.isEmpty {
                        return categories
                    }
                } catch {
                    // Continue to next season/type combination
                    continue
                }
            }
        }
        
        // No data found for any season
        return []
    }
    
    private func getSeasonTypes(for sport: Sport) -> [Int] {
        let now = Date()
        let calendar = Calendar.current
        let month = calendar.component(.month, from: now)
        
        // MLB: Spring training (type 1) in Feb-March, regular season (type 2) otherwise
        if sport == .mlb {
            if month >= 2 && month <= 3 {
                return [1, 2, 3] // Try spring training, then regular, then postseason
            }
            return [2, 3, 1] // Try regular, then postseason, then spring training
        }
        
        // Other sports: Regular season (2) first, then postseason (3)
        return [2, 3, 1]
    }
    
    private func fetchLeadersForSeason(
        sportType: String,
        league: String,
        season: Int,
        seasonType: Int
    ) async throws -> [LeagueLeaderCategory] {
        let urlString = "\(coreAPIBaseURL)/\(sportType)/leagues/\(league)/seasons/\(season)/types/\(seasonType)/leaders?limit=10"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse else { throw APIError.invalidResponse }
        
        // Return empty for 404 (no data for this season/type) so we can try next one
        if http.statusCode == 404 {
            return []
        }
        
        guard http.statusCode == 200 else { throw APIError.invalidResponse }
        
        let apiResponse = try JSONDecoder().decode(CoreLeadersAPIResponse.self, from: data)
        let categories = apiResponse.categories ?? []
        
        // Collect all unique $ref URLs across all categories so we can resolve
        // them all in parallel (one TaskGroup), not sequentially per leader.
        // Sequential resolution for MLB (20 cats × 10 leaders × 2 refs = 400 calls)
        // would exceed the 30-second URLSession timeout. Parallel cuts this to ~1-2s.
        var athleteRefs = Set<String>()
        var teamRefs    = Set<String>()
        for category in categories {
            for leader in category.leaders ?? [] {
                if let ref = leader.athlete?.ref { athleteRefs.insert(ref) }
                if let ref = leader.team?.ref    { teamRefs.insert(ref) }
            }
        }
        
        // Resolve all unique refs in parallel
        async let athleteTask = resolveRefs(athleteRefs, as: CoreAthleteResponse.self)
        async let teamTask    = resolveRefs(teamRefs,    as: CoreTeamResponse.self)
        let (athletes, teams) = await (athleteTask, teamTask)
        
        // Build results using the resolved caches
        return categories.map { category in
            let leaders = (category.leaders ?? []).enumerated().map { index, leader -> LeagueLeaderCategory.LeagueLeaderEntry in
                let athleteName: String
                if let ref = leader.athlete?.ref, let ath = athletes[ref] {
                    athleteName = ath.displayName ?? "Unknown"
                } else if let ref = leader.team?.ref, let team = teams[ref] {
                    athleteName = team.displayName ?? "Unknown"
                } else {
                    athleteName = "Unknown"
                }
                let teamAbbr = leader.team?.ref.flatMap { teams[$0]?.abbreviation } ?? ""
                return LeagueLeaderCategory.LeagueLeaderEntry(
                    rank: index + 1,
                    displayValue: leader.displayValue ?? "-",
                    athleteName: athleteName,
                    teamAbbreviation: teamAbbr
                )
            }
            return LeagueLeaderCategory(
                name: category.name ?? "",
                displayName: category.displayName ?? "",
                leaders: leaders
            )
        }
    }

    /// Resolve a set of Core API $ref URLs in parallel. Returns a dictionary
    /// mapping each original ref URL string to the decoded response object.
    /// Failed resolutions are silently dropped rather than failing the whole batch.
    private func resolveRefs<T: Decodable & Sendable>(
        _ refs: Set<String>,
        as type: T.Type
    ) async -> [String: T] {
        var cache = [String: T]()
        await withTaskGroup(of: (String, T?).self) { group in
            for ref in refs {
                group.addTask {
                    guard let url = URL(string: ref) else { return (ref, nil) }
                    let result = try? await {
                        let (data, response) = try await self.session.data(from: url)
                        guard let http = response as? HTTPURLResponse,
                              http.statusCode == 200 else { return nil as T? }
                        return try? JSONDecoder().decode(T.self, from: data)
                    }()
                    return (ref, result)
                }
            }
            for await (ref, result) in group {
                if let result { cache[ref] = result }
            }
        }
        return cache
    }

    // MARK: - Fetch Rankings / Polls (Phase 6)

    func fetchRankings(for sport: Sport) async throws -> [RankingsPoll] {
        let urlString = "\(baseURL)/\(sport.apiPath)/rankings"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else { throw APIError.invalidResponse }
        let apiResponse = try JSONDecoder().decode(RankingsAPIResponse.self, from: data)
        return apiResponse.rankings.map { RankingsPoll(from: $0) }
    }
}
