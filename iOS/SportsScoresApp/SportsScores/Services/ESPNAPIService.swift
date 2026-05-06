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
    /// Core API for leaders/statistics and week calendar data
    private let coreAPIBaseURL = "https://sports.core.api.espn.com/v2/sports"
    private let session: URLSession

    // MARK: - Caches (historical season data)

    /// Keyed by "{SportRawValue}-{season}" → SeasonCalendar
    private var seasonCalendarCache: [String: SeasonCalendar] = [:]
    /// Keyed by "{SportRawValue}-{season}-{seasonType}-{week}" → (start, end, label)
    private var weekDateRangeCache: [String: (start: Date, end: Date, text: String)] = [:]

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)
    }

    // MARK: - Core API league name helper

    /// Returns the ESPN Core API league identifier for a football sport.
    private func coreLeagueName(for sport: Sport) -> String {
        sport == .nfl ? "nfl" : "college-football"
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

    // MARK: - Historical Football Calendar (Core API)

    /// Fetches the season calendar from the ESPN Core API for a specific football
    /// season year.  Returns a `SeasonCalendar` describing which season types
    /// (preseason / regular / postseason) exist and how many weeks each has.
    ///
    /// Results are cached in memory so repeated calls for the same sport+season
    /// cost nothing after the first fetch.
    func fetchFootballCalendar(sport: Sport, season: Int) async throws -> SeasonCalendar {
        let cacheKey = "\(sport.rawValue)-\(season)"
        if let cached = seasonCalendarCache[cacheKey] { return cached }

        let league = coreLeagueName(for: sport)

        // Fetch week counts for all three season types in parallel.
        async let preCount  = fetchWeekCount(league: league, season: season, seasonType: 1)
        async let regCount  = fetchWeekCount(league: league, season: season, seasonType: 2)
        async let postCount = fetchWeekCount(league: league, season: season, seasonType: 3)

        let (pre, reg, post) = await (preCount, regCount, postCount)

        var types: [SeasonTypeInfo] = []
        if pre  > 0 { types.append(SeasonTypeInfo(type: 1, weekCount: pre)) }
        if reg  > 0 { types.append(SeasonTypeInfo(type: 2, weekCount: reg)) }
        if post > 0 { types.append(SeasonTypeInfo(type: 3, weekCount: post)) }

        let calendar = SeasonCalendar(sport: sport, season: season, seasonTypes: types)
        seasonCalendarCache[cacheKey] = calendar
        return calendar
    }

    /// Returns the number of weeks in a given season type, or 0 on error / missing data.
    private func fetchWeekCount(league: String, season: Int, seasonType: Int) async -> Int {
        let urlString = "\(coreAPIBaseURL)/football/leagues/\(league)/seasons/\(season)/types/\(seasonType)/weeks?limit=100"
        guard let url = URL(string: urlString) else { return 0 }
        guard let (data, response) = try? await session.data(from: url),
              let http = response as? HTTPURLResponse, http.statusCode == 200 else { return 0 }
        struct WeeksResponse: Decodable { let count: Int? }
        return (try? JSONDecoder().decode(WeeksResponse.self, from: data))?.count ?? 0
    }

    // MARK: - Historical Football Week Games (Core API + date-range scoreboard)

    /// Fetches games for a specific week of a **historical** football season.
    ///
    /// Because the site scoreboard endpoint rejects `season=YEAR` params for past
    /// seasons, this method:
    /// 1. Gets the week's `startDate`/`endDate` from the Core API.
    /// 2. Fetches the site scoreboard with `?dates=YYYYMMDD-YYYYMMDD`.
    ///
    /// Both the week date range and the scoreboard result are cached so that
    /// navigating back and forth between weeks is cheap.
    func fetchFootballWeek(
        sport: Sport,
        season: Int,
        seasonType: Int,
        week: Int
    ) async throws -> FootballScoreboardResult {
        // Step 1 — get the date range for this week (cached after first fetch).
        let weekCacheKey = "\(sport.rawValue)-\(season)-\(seasonType)-\(week)"
        let weekRange: (start: Date, end: Date, text: String)

        if let cached = weekDateRangeCache[weekCacheKey] {
            weekRange = cached
        } else {
            let league = coreLeagueName(for: sport)
            let weekURLString = "\(coreAPIBaseURL)/football/leagues/\(league)/seasons/\(season)/types/\(seasonType)/weeks/\(week)"
            guard let weekURL = URL(string: weekURLString) else { throw APIError.invalidURL }

            let (weekData, weekResponse) = try await session.data(from: weekURL)
            guard let weekHttp = weekResponse as? HTTPURLResponse,
                  weekHttp.statusCode == 200 else { throw APIError.invalidResponse }

            struct CoreWeek: Decodable {
                let number: Int
                let startDate: String
                let endDate: String
                let text: String?
            }
            let coreWeek = try JSONDecoder().decode(CoreWeek.self, from: weekData)
            let start = parseESPNDateString(coreWeek.startDate) ?? Date()
            let end   = parseESPNDateString(coreWeek.endDate)   ?? Date()
            let text  = coreWeek.text ?? "Week \(week)"
            weekRange = (start: start, end: end, text: text)
            weekDateRangeCache[weekCacheKey] = weekRange
        }

        // Step 2 — fetch the scoreboard using the date range.
        let fmt = DateFormatter()
        fmt.dateFormat = "yyyyMMdd"
        let startStr = fmt.string(from: weekRange.start)
        let endStr   = fmt.string(from: weekRange.end)
        let scoreboardURLString = "\(baseURL)/\(sport.apiPath)/scoreboard?dates=\(startStr)-\(endStr)"
        guard let scoreboardURL = URL(string: scoreboardURLString) else { throw APIError.invalidURL }

        let (data, response) = try await session.data(from: scoreboardURL)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let apiResponse = try decoder.decode(ScoreboardResponse.self, from: data)
        let games = try apiResponse.events.map { try Game(from: $0, seasonType: seasonType) }

        return FootballScoreboardResult(
            games: games,
            week: week,
            weekLabel: weekRange.text,
            seasonType: seasonType,
            season: season
        )
    }

    /// Parse an ESPN date string that may be formatted with or without seconds.
    /// ESPN typically returns `"2022-09-08T07:00Z"` (no seconds).
    private func parseESPNDateString(_ s: String) -> Date? {
        let formats = [
            "yyyy-MM-dd'T'HH:mm:ssZ",
            "yyyy-MM-dd'T'HH:mm'Z'",
            "yyyy-MM-dd'T'HH:mmZ",
            "yyyy-MM-dd"
        ]
        let df = DateFormatter()
        df.locale = Locale(identifier: "en_US_POSIX")
        for fmt in formats {
            df.dateFormat = fmt
            if let d = df.date(from: s) { return d }
        }
        return nil
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
        // NOTE: ESPN Core API $refs use http://, which iOS ATS blocks. Upgrade to https://.
        var athleteRefs = Set<String>()
        var teamRefs    = Set<String>()
        for category in categories {
            for leader in category.leaders ?? [] {
                if let ref = leader.athlete?.ref { athleteRefs.insert(secureURL(ref)) }
                if let ref = leader.team?.ref    { teamRefs.insert(secureURL(ref)) }
            }
        }
        
        // Copy to immutable constants before concurrent use (Swift 6: var capture in async let is an error)
        let frozenAthleteRefs = athleteRefs
        let frozenTeamRefs    = teamRefs
        
        // Resolve all unique refs in parallel
        async let athleteTask = resolveRefs(frozenAthleteRefs, as: CoreAthleteResponse.self)
        async let teamTask    = resolveRefs(frozenTeamRefs,    as: CoreTeamResponse.self)
        let (athletes, teams) = await (athleteTask, teamTask)
        
        // Build results using the resolved caches
        return categories.map { category in
            let leaders = (category.leaders ?? []).enumerated().map { index, leader -> LeagueLeaderCategory.LeagueLeaderEntry in
                let athleteName: String
                // Look up athlete/team using the https-upgraded ref to match the cache keys
                if let ref = leader.athlete?.ref, let ath = athletes[secureURL(ref)] {
                    athleteName = ath.displayName ?? "—"
                } else if let ref = leader.team?.ref, let team = teams[secureURL(ref)] {
                    athleteName = team.displayName ?? "—"
                } else {
                    athleteName = "—"
                }
                let teamAbbr = leader.team?.ref.flatMap { teams[secureURL($0)]?.abbreviation } ?? ""
                // MLB displayValue is a full stats-line (e.g. "9-17, 4 HR, 2B, 6 RBI...").
                // Use the numeric value field with smart formatting instead.
                let statDisplay: String
                if let v = leader.value {
                    statDisplay = formatLeaderStatValue(v)
                } else {
                    statDisplay = leader.displayValue ?? "-"
                }
                return LeagueLeaderCategory.LeagueLeaderEntry(
                    rank: index + 1,
                    displayValue: statDisplay,
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

    /// Upgrade a Core API $ref URL from http:// to https:// so iOS ATS allows the connection.
    private func secureURL(_ ref: String) -> String {
        ref.hasPrefix("http://") ? "https://" + ref.dropFirst(7) : ref
    }

    /// Format a raw numeric stat value for display in the leaders table.
    ///  - Values < 1.0  → 3-decimal batting-average style  (e.g. 0.331 → ".331")
    ///  - Whole numbers  → integer counting stat            (e.g. 4.0  → "4")
    ///  - Decimal ≥ 1   → 2-decimal rate stat              (e.g. 2.75 → "2.75")
    private func formatLeaderStatValue(_ value: Double) -> String {
        if value < 1.0 {
            // batting average / OBP / SLG / OPS-under-1 style
            let s = String(format: "%.3f", value)
            return s.hasPrefix("0.") ? String(s.dropFirst()) : s  // ".333" not "0.333"
        } else if value == floor(value) {
            // counting stat: HR, RBI, K, SB, W, etc.
            return "\(Int(value))"
        } else {
            // rate stat ≥ 1: ERA, WHIP, etc.
            return String(format: "%.2f", value)
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

    // MARK: - Fetch Golf Tournament / Schedule

    /// Fetches the current or date-specific golf tournament for PGA or LPGA.
    ///
    /// - `startDate` nil → returns the currently featured tournament (no `?dates` param).
    /// - `startDate` provided → fetches the scoreboard for that date, which ESPN returns
    ///   the tournament active during that week.
    ///
    /// Always returns the full season calendar from `leagues[0].calendar` regardless
    /// of whether a tournament is active.
    func fetchGolfTournament(for sport: Sport, startDate: Date? = nil) async throws -> GolfTournamentResult {
        var urlString = "\(baseURL)/\(sport.apiPath)/scoreboard"
        if let date = startDate {
            let fmt = DateFormatter()
            fmt.dateFormat = "yyyyMMdd"
            urlString += "?dates=\(fmt.string(from: date))"
        }
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }

        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }

        let decoder = JSONDecoder()
        // Golf date strings omit seconds ("2026-04-09T04:00Z") — use lenient parser
        let apiResponse = try decoder.decode(GolfScoreboardResponse.self, from: data)

        let calendar = apiResponse.leagues.first?.calendar.compactMap { entry -> GolfCalendarEntry? in
            guard let start = parseESPNDateString(entry.startDate),
                  let end   = parseESPNDateString(entry.endDate) else { return nil }
            return GolfCalendarEntry(id: entry.id, name: entry.label, startDate: start, endDate: end)
        } ?? []

        let tournament = apiResponse.events.first.map {
            GolfTournament(from: $0, parseDate: { [weak self] s in self?.parseESPNDateString(s) })
        }

        return GolfTournamentResult(tournament: tournament, calendar: calendar)
    }

    // MARK: - NFL Draft

    func fetchDraft(year: Int) async throws -> DraftResponse {
        let urlString = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/draft?season=\(year)"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        return try JSONDecoder().decode(DraftResponse.self, from: data)
    }

    // MARK: - Transactions

    /// Fetches paginated transactions for a sport.
    /// - Parameters:
    ///   - sport: The sport/league to query.
    ///   - page: 1-based page index (default 1).
    ///   - limit: Transactions per page (default 25).
    ///   - dateRange: Optional `(start, end)` strings in `"yyyyMMdd"` format for `?dates=` filtering.
    func fetchTransactions(
        sport: Sport,
        page: Int = 1,
        limit: Int = 25,
        dateRange: (start: String, end: String)? = nil
    ) async throws -> TransactionResponse {
        var urlString = "\(baseURL)/\(sport.apiPath)/transactions?limit=\(limit)&page=\(page)"
        if let range = dateRange {
            urlString += "&dates=\(range.start)-\(range.end)"
        }
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        return try JSONDecoder().decode(TransactionResponse.self, from: data)
    }

    /// Fetches all teams for a sport, sorted by display name.
    func fetchTeamsForSport(sport: Sport) async throws -> [TransactionTeam] {
        let urlString = "\(baseURL)/\(sport.apiPath)/teams"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        let parsed = try JSONDecoder().decode(TeamsAPIResponse.self, from: data)
        return parsed.sports.first?.leagues.first?.teams.map(\.team) ?? []
    }

    /// Fetches conferences with their member teams for college sports.
    /// Uses the standings endpoint which groups teams by conference.
    /// Returns an empty array if the sport has no usable conference structure
    /// (caller should fall back to fetchTeamsForSport).
    func fetchConferencesWithTeams(for sport: Sport) async throws -> [ConferenceGroup] {
        let urlString = "\(standingsBaseURL)/\(sport.apiPath)/standings"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        let decoded = try JSONDecoder().decode(ConferencesAPIResponse.self, from: data)

        // Build a helper to convert a raw entry's team into TransactionTeam
        func toTeam(_ t: ConferencesAPIResponse.APIConference.APIStandings.APIEntry.APITeam) -> TransactionTeam {
            let logos = t.logos?.map { logo in
                TransactionTeamLogo(href: logo.href, width: nil, height: nil, rel: logo.rel)
            }
            return TransactionTeam(
                id: t.id,
                location: t.location,
                name: t.name,
                abbreviation: t.abbreviation,
                displayName: t.displayName,
                color: t.color,
                logos: logos
            )
        }

        // Extract teams from a conference node, flattening sub-divisions (e.g. Sun Belt)
        func teamsFrom(_ conf: ConferencesAPIResponse.APIConference) -> [TransactionTeam] {
            var teams = conf.standings?.entries.map { toTeam($0.team) } ?? []
            for sub in conf.children ?? [] {
                teams += sub.standings?.entries.map { toTeam($0.team) } ?? []
            }
            return teams.sorted { $0.displayName < $1.displayName }
        }

        // Top-level conference children → one ConferenceGroup each
        if let conferences = decoded.children, !conferences.isEmpty {
            let groups = conferences.compactMap { conf -> ConferenceGroup? in
                let teams = teamsFrom(conf)
                guard !teams.isEmpty else { return nil }
                return ConferenceGroup(id: conf.id ?? conf.name, name: conf.name, teams: teams)
            }
            // Only return conference groups if we have a meaningful number of teams.
            // Sports like NCAAH have conference structure but near-empty standings data —
            // in that case return [] so the caller falls back to fetchTeamsForSport.
            let totalTeams = groups.reduce(0) { $0 + $1.teams.count }
            if totalTeams >= 20 { return groups }
        }

        // No usable conference data — caller will fall back to a flat team list.
        return []
    }

    // MARK: - Team Hub: Team Info

    /// Fetches team detail (colors, record, venue, next game, standing summary).
    func fetchTeamHubInfo(teamId: String, sport: Sport) async throws -> TeamHubTeamInfo {
        let urlString = "\(baseURL)/\(sport.apiPath)/teams/\(teamId)"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        let api = try JSONDecoder().decode(TeamInfoAPIResponse.self, from: data)
        let t = api.team

        // Primary logo: prefer rel "default", fall back to first
        let logoURL: URL? = t.logos?
            .first(where: { $0.rel?.contains("default") == true })
            .flatMap { URL(string: $0.href) }
            ?? t.logos?.first.flatMap { URL(string: $0.href) }

        // Record items
        let items = t.record?.items ?? []
        func recordSummary(matching description: String) -> String? {
            items.first(where: { $0.description?.lowercased().contains(description) == true })?.summary
        }
        let overallRecord = recordSummary(matching: "overall")
        let homeRecord = recordSummary(matching: "home")
        let awayRecord = recordSummary(matching: "away") ?? recordSummary(matching: "road")

        // Venue from franchise
        let venue = t.franchise?.venue
        let venueName = venue?.fullName
        let venueCity = venue?.address?.city

        // Next game from nextEvent[0]
        var nextGame: TeamHubNextGame?
        if let ev = t.nextEvent?.first,
           let comp = ev.competitions?.first {
            // Identify which competitor is the opponent (not our team)
            let opponent = comp.competitors?.first(where: { $0.team?.id != teamId })
            let isHome = comp.competitors?.first(where: { $0.team?.id == teamId })?.homeAway == "home"
            if let opp = opponent?.team {
                let parsedDate = parseESPNDate(ev.date)
                if let parsedDate = parsedDate {
                    nextGame = TeamHubNextGame(
                        gameId: ev.id,
                        date: parsedDate,
                        opponentDisplayName: opp.displayName ?? opp.abbreviation ?? "Opponent",
                        opponentAbbreviation: opp.abbreviation ?? "?",
                        isHome: isHome
                    )
                }
            }
        }

        return TeamHubTeamInfo(
            teamId: t.id,
            displayName: t.displayName,
            abbreviation: t.abbreviation,
            location: t.location ?? t.displayName,
            color: t.color,
            alternateColor: t.alternateColor,
            primaryLogoURL: logoURL,
            overallRecord: overallRecord,
            homeRecord: homeRecord,
            awayRecord: awayRecord,
            standingSummary: t.standingSummary,
            venueName: venueName,
            venueCity: venueCity,
            coachName: nil,  // populated by fetchTeamRoster
            nextGame: nextGame
        )
    }

    // MARK: - Team Hub: Roster

    /// Fetches the current roster for a team, flattening position groups.
    /// Also returns the head coach name (first coach in the response).
    func fetchTeamRoster(teamId: String, sport: Sport) async throws -> (players: [RosterPlayer], coachName: String?) {
        let urlString = "\(baseURL)/\(sport.apiPath)/teams/\(teamId)/roster"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }

        func coachNameFrom(_ coaches: [RosterAPIResponse.RosterCoach]?) -> String? {
            coaches?.first.flatMap { c in
                let name = [c.firstName, c.lastName].compactMap { $0 }.joined(separator: " ")
                return name.isEmpty ? nil : name
            }
        }

        func makePlayer(id: String, displayName: String?, jersey: String?,
                        positionAbbr: String?, age: Int?) -> RosterPlayer {
            RosterPlayer(
                id: id,
                jerseyNumber: jersey ?? "–",
                displayName: displayName ?? "Unknown",
                positionAbbreviation: positionAbbr ?? "–",
                age: age.map { String($0) } ?? "–"
            )
        }

        // Try grouped format first (MLB, NFL, NHL, NBA)
        if let api = try? JSONDecoder().decode(RosterAPIResponse.self, from: data) {
            let grouped: [RosterPlayer] = (api.athletes ?? []).flatMap { group in
                (group.items ?? []).map { a in
                    makePlayer(id: a.id, displayName: a.displayName,
                               jersey: a.jersey, positionAbbr: a.position?.abbreviation, age: a.age)
                }
            }
            if !grouped.isEmpty {
                return (grouped, coachNameFrom(api.coach))
            }
        }

        // Fall back to flat format (college sports — athletes is a direct array of players)
        if let flat = try? JSONDecoder().decode(FlatRosterAPIResponse.self, from: data) {
            let players: [RosterPlayer] = (flat.athletes ?? []).map { a in
                makePlayer(id: a.id, displayName: a.displayName,
                           jersey: a.jersey, positionAbbr: a.position?.abbreviation, age: a.age)
            }
            return (players, coachNameFrom(flat.coach))
        }

        return ([], nil)
    }

    // MARK: - Team Hub: News (team-filtered, falls back to league)

    /// Fetches news filtered to a specific team; falls back to league news if none returned.
    func fetchTeamNews(teamId: String, sport: Sport, limit: Int = 25) async throws -> [NewsItem] {
        let urlString = "\(baseURL)/\(sport.apiPath)/news?team=\(teamId)&limit=\(limit)"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let apiResponse = try decoder.decode(NewsAPIResponse.self, from: data)
        let articles = apiResponse.articles.map { NewsItem(from: $0) }
        if !articles.isEmpty { return articles }
        // Fall back to league-wide news
        return try await fetchNews(for: sport, limit: limit)
    }

    // MARK: - Team Hub: Schedule (current season, for Info + Schedule tabs)

    /// Fetches the current season schedule for a team. Returns games sorted by date.
    func fetchTeamHubSchedule(teamId: String, sport: Sport) async throws -> [ScheduleGame] {
        // Compute current season year (mirrors TeamScheduleViewModel.defaultSeasonYear)
        let cal = Calendar.current
        let now = Date()
        let year = cal.component(.year, from: now)
        let month = cal.component(.month, from: now)
        let season: Int
        if sport.usesNextYearFormat {
            season = month >= 10 ? year + 1 : year
        } else if sport.isFootball && month < 8 {
            season = year - 1
        } else {
            season = year
        }
        let seasonTypes: [Int]
        if sport == .mlb {
            seasonTypes = [1, 2, 3]
        } else if sport.isFootball {
            seasonTypes = [1, 2, 3]
        } else {
            seasonTypes = [2, 3]
        }
        var allGames: [ScheduleGame] = []
        await withTaskGroup(of: [ScheduleGame].self) { group in
            for st in seasonTypes {
                group.addTask { [self] in
                    (try? await self.fetchTeamSchedule(
                        teamId: teamId,
                        sport: sport,
                        season: season,
                        seasonType: st
                    )) ?? []
                }
            }
            for await result in group {
                allGames.append(contentsOf: result)
            }
        }
        return allGames.sorted { $0.date < $1.date }
    }

    // MARK: - Multi-format date parser

    private func parseESPNDate(_ string: String) -> Date? {
        // Try full ISO8601 with seconds first, then without
        let formatsToTry = ["yyyy-MM-dd'T'HH:mmZ", "yyyy-MM-dd'T'HH:mm:ssZ"]
        let fmt = DateFormatter()
        fmt.locale = Locale(identifier: "en_US_POSIX")
        for format in formatsToTry {
            fmt.dateFormat = format
            if let d = fmt.date(from: string) { return d }
        }
        return ISO8601DateFormatter().date(from: string)
    }
}
