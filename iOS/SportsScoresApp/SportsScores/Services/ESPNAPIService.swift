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
        
        // Process categories: resolve $ref URLs for athletes/teams in parallel
        var resolvedCategories: [LeagueLeaderCategory] = []
        
        for category in apiResponse.categories ?? [] {
            var resolvedLeaders: [LeagueLeaderCategory.LeagueLeaderEntry] = []
            
            for (index, leader) in (category.leaders ?? []).enumerated() {
                let athleteName: String
                let teamAbbr: String
                
                // Resolve athlete $ref if present
                if let athleteRef = leader.athlete?.ref {
                    if let athlete = try? await fetchReference(url: athleteRef, as: CoreAthleteResponse.self) {
                        athleteName = athlete.displayName ?? "Unknown"
                    } else {
                        athleteName = "Unknown"
                    }
                } else if let teamRef = leader.team?.ref {
                    if let team = try? await fetchReference(url: teamRef, as: CoreTeamResponse.self) {
                        athleteName = team.displayName ?? "Unknown"
                    } else {
                        athleteName = "Unknown"
                    }
                } else {
                    athleteName = "Unknown"
                }
                
                // Resolve team $ref if present
                if let teamRef = leader.team?.ref {
                    if let team = try? await fetchReference(url: teamRef, as: CoreTeamResponse.self) {
                        teamAbbr = team.abbreviation ?? ""
                    } else {
                        teamAbbr = ""
                    }
                } else {
                    teamAbbr = ""
                }
                
                resolvedLeaders.append(LeagueLeaderCategory.LeagueLeaderEntry(
                    rank: index + 1,
                    displayValue: leader.displayValue ?? "-",
                    athleteName: athleteName,
                    teamAbbreviation: teamAbbr
                ))
            }
            
            resolvedCategories.append(LeagueLeaderCategory(
                name: category.name ?? "",
                displayName: category.displayName ?? "",
                leaders: resolvedLeaders
            ))
        }
        
        return resolvedCategories
    }
    
    private func fetchReference<T: Decodable>(url: String, as type: T.Type) async throws -> T {
        guard let refURL = URL(string: url) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: refURL)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        return try JSONDecoder().decode(T.self, from: data)
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

// MARK: - League Leaders Models

struct LeagueLeaderCategory: Identifiable {
    let id = UUID()
    let name: String
    let displayName: String
    let leaders: [LeagueLeaderEntry]

    struct LeagueLeaderEntry: Identifiable {
        let id = UUID()
        let rank: Int
        let displayValue: String
        let athleteName: String
        let teamAbbreviation: String
    }
    
    // Direct init for Core API
    init(name: String, displayName: String, leaders: [LeagueLeaderEntry]) {
        self.name = name
        self.displayName = displayName
        self.leaders = leaders
    }
}

// MARK: - Core API Response Models

struct CoreLeadersAPIResponse: Codable {
    let categories: [CoreCategory]?
    
    struct CoreCategory: Codable {
        let name: String?
        let displayName: String?
        let leaders: [CoreLeader]?
        
        struct CoreLeader: Codable {
            let displayValue: String?
            let athlete: Reference?
            let team: Reference?
            
            struct Reference: Codable {
                let ref: String?

                enum CodingKeys: String, CodingKey {
                    case ref = "$ref"
                }
            }
        }
    }
}

struct CoreAthleteResponse: Codable {
    let displayName: String?
}

struct CoreTeamResponse: Codable {
    let displayName: String?
    let abbreviation: String?
}

// MARK: - Rankings / Polls Models

struct RankingsPoll: Identifiable {
    let id = UUID()
    let name: String
    let shortName: String
    let lastUpdated: String?
    let ranks: [RankEntry]

    struct RankEntry: Identifiable {
        let id = UUID()
        let current: Int
        let previous: Int?
        let trend: String?
        let points: Double?
        let firstPlaceVotes: Int?
        let teamDisplayName: String
        let teamAbbreviation: String
        let recordSummary: String?

        var movementText: String {
            guard let prev = previous, prev > 0 else { return "NR" }
            let diff = prev - current
            if diff > 0 { return "↑\(diff)" }
            if diff < 0 { return "↓\(abs(diff))" }
            return "—"
        }

        var movementDirection: Int {
            guard let prev = previous, prev > 0 else { return 0 }
            return prev - current
        }
    }

    init(from api: RankingsAPIResponse.APIPoll) {
        self.name = api.name ?? api.shortName ?? "Poll"
        self.shortName = api.shortName ?? api.name ?? "Poll"
        self.lastUpdated = api.lastUpdated
        self.ranks = (api.ranks ?? []).map { r in
            RankEntry(
                current: r.current ?? 0,
                previous: r.previous,
                trend: r.trend,
                points: r.points,
                firstPlaceVotes: r.firstPlaceVotes,
                teamDisplayName: r.team?.displayName ?? "Unknown",
                teamAbbreviation: r.team?.abbreviation ?? "—",
                recordSummary: r.record?.summary ?? r.team?.record?.summary
            )
        }
    }
}

struct RankingsAPIResponse: Codable {
    let rankings: [APIPoll]

    struct APIPoll: Codable {
        let name: String?
        let shortName: String?
        let headline: String?
        let lastUpdated: String?
        let ranks: [APIRank]?

        struct APIRank: Codable {
            let current: Int?
            let previous: Int?
            let trend: String?
            let points: Double?
            let firstPlaceVotes: Int?
            let record: APIRecord?
            let team: APITeam?

            struct APIRecord: Codable {
                let summary: String?
            }
            struct APITeam: Codable {
                let displayName: String?
                let abbreviation: String?
                let record: APIRecord?
            }
        }
    }
}

// MARK: - API Response Models
struct ScoreboardResponse: Codable {
    let events: [APIGame]
    /// Present for football sports — describes the current week.
    let week: APIWeek?
    /// Describes the current season being served.
    let season: APISeason?

    struct APIWeek: Codable {
        let number: Int?
        let text: String?
    }

    struct APISeason: Codable {
        let year: Int?
        let type: Int?
    }
}

struct GameDetails: Codable {
    let boxscore: Boxscore?
    let plays: [Play]?
    let leaders: [Leader]?
    /// NFL/NCAAF only — drive-by-drive breakdown.
    let drives: DrivesContainer?
    /// Venue, officials, odds, injuries from the summary API.
    let gameInfo: GameInfo?
    let odds: [OddsEntry]?
    let injuries: [InjuryTeam]?
    /// Win probability timeline (MLB, per play).
    let winprobability: [WinProbEntry]?
    /// Season series breakdown (MLB — current series, regular season, preseason).
    let seasonseries: [SeasonSeriesEntry]?
    /// Game-specific news articles embedded in summary response.
    let news: GameNewsContainer?

    // MARK: - Win Probability

    struct WinProbEntry: Codable {
        let homeWinPercentage: Double
        let tiePercentage: Double
        let playId: String
    }

    // MARK: - Season Series

    struct SeasonSeriesEntry: Codable {
        let type: String?
        let title: String?
        let summary: String?
        let completed: Bool?
        let totalCompetitions: Int?
        let seriesScore: String?

        // Prefer "Regular Season Series" and "Current Series" for display
        var displayOrder: Int {
            switch type {
            case "current":  return 0
            case "season":   return 1
            case "preseason": return 2
            default:         return 3
            }
        }
    }

    // MARK: - Game News

    struct GameNewsContainer: Codable {
        let articles: [GameArticle]?

        struct GameArticle: Codable, Identifiable {
            let id: Int?
            let headline: String?
            let description: String?
            let type: String?
            let links: ArticleLinks?

            struct ArticleLinks: Codable {
                let web: WebLink?
                struct WebLink: Codable {
                    let href: String?
                }
            }

            var webURL: URL? {
                links?.web?.href.flatMap { URL(string: $0) }
            }
        }
    }

    // ── Game-info sub-models ──────────────────────────────────────────────

    struct GameInfo: Codable {
        let officials: [Official]?

        struct Official: Codable {
            let fullName: String?
            let position: OfficialPosition?

            struct OfficialPosition: Codable {
                let displayName: String?
            }
        }
    }

    struct OddsEntry: Codable {
        let details: String?         // spread text e.g. "KC -6.5"
        let overUnder: Double?
        let provider: OddsProvider?

        struct OddsProvider: Codable {
            let name: String?
        }
    }

    struct InjuryTeam: Codable {
        let team: InjuryTeamInfo?
        let injuries: [PlayerInjury]?

        struct InjuryTeamInfo: Codable {
            let displayName: String?
            let abbreviation: String?
        }

        struct PlayerInjury: Codable {
            let athlete: InjuryAthlete?
            let type: InjuryType?
            let status: String?

            struct InjuryAthlete: Codable {
                let displayName: String?
                let position: AthletePosition?

                struct AthletePosition: Codable {
                    let abbreviation: String?
                }
            }

            struct InjuryType: Codable {
                let description: String?
            }
        }
    }

    // ── Drives container (NFL / NCAAF) ────────────────────────────────────

    struct DrivesContainer: Codable {
        let current: Drive?
        let previous: [Drive]?

        /// All drives in chronological order (current drive appended at end if present).
        var all: [Drive] {
            var list = previous ?? []
            if let cur = current { list.append(cur) }
            return list
        }
    }

    struct Drive: Codable, Identifiable {
        let id: String
        let description: String?
        let yards: Int?
        let offensivePlays: Int?
        /// Short abbreviation ("FG", "PUNT", "TD"). Use `displayResult` for the
        /// human-readable version that drives the emoji mapping.
        let result: String?
        /// Human-readable result e.g. "Field Goal", "Punt", "Touchdown".
        let displayResult: String?
        let isScore: Bool?
        let team: DriveTeam?
        let start: DrivePosition?
        let end: DrivePosition?
        let plays: [DrivePlay]?

        /// Drive result mapped to an emoji. Uses `displayResult` (e.g. "Field Goal")
        /// because `result` contains abbreviations ("FG") which don't match a simple switch.
        var resultEmoji: String {
            switch displayResult?.lowercased() {
            case "touchdown":                               return "🏈"
            case "field goal":                             return "🥅"
            case "punt":                                   return "⚡"
            case "fumble", "interception",
                 "turnover on downs":                      return "🔄"
            case "missed field goal", "missed fg":        return "❌"
            case "end of half", "end of game",
                 "end of quarter":                         return "🕒"
            default:
                // Fallback: use the short abbreviation
                switch result?.uppercased() {
                case "TD":   return "🏈"
                case "FG":   return "🥅"
                case "PUNT": return "⚡"
                default:     return "•"
                }
            }
        }

        /// ESPN period number for the drive start (1-4, plus 5+ for OT).
        var quarterNumber: Int { start?.period?.number ?? 1 }

        struct DriveTeam: Codable {
            let id: String?
            let abbreviation: String?
            let displayName: String?
        }

        struct DrivePosition: Codable {
            let period: DrivePeriod?
            let yardLine: Int?
            let text: String?

            struct DrivePeriod: Codable {
                let number: Int?
            }
        }

        struct DrivePlay: Codable, Identifiable {
            let id: String
            let text: String?
            let statYardage: Int?
            let type: PlayType?
            let clock: PlayClock?
            let period: DrivePeriod?

            struct PlayType: Codable {
                let text: String?
                let type: String?
            }

            struct PlayClock: Codable {
                let displayValue: String?
            }

            struct DrivePeriod: Codable {
                let number: Int?
            }
        }
    }
    
    struct Boxscore: Codable {
        let teams: [TeamStats]
        let players: [TeamPlayers]?
        
        struct TeamStats: Codable {
            let team: TeamInfo
            // ESPN returns statistics in two different shapes depending on sport:
            //   MLB  → [{name, displayName, stats:[{name,displayName,...}]}]  (nested categories)
            //   NFL/NBA/NHL → [{name, label, abbreviation?, displayValue}]     (flat rows)
            let statistics: [StatEntry]
            
            struct TeamInfo: Codable {
                let displayName: String
                let abbreviation: String
            }
            
            /// One element of the statistics array.
            /// Use `isNested` to distinguish MLB category format from NFL/NBA/NHL flat format.
            struct StatEntry: Codable {
                // Present in every format
                let name: String
                // MLB nested: category label (e.g. "Batting")
                let displayName: String?
                // NFL/NBA/NHL flat: row label (e.g. "1st Downs")
                let label: String?
                // NHL flat rows include an abbreviation
                let abbreviation: String?
                // Flat formats carry the displayValue directly
                let displayValue: String?
                // MLB only: nested stat rows under this category
                let stats: [StatItem]?
                
                /// Human-readable title for this entry (works for all formats).
                var groupTitle: String { displayName ?? label ?? name }
                
                /// True when this entry is an MLB-style category wrapping nested stats.
                var isNested: Bool { stats != nil }
                
                struct StatItem: Codable {
                    let name: String
                    let displayName: String
                    let shortDisplayName: String?
                    let description: String?
                    let abbreviation: String?
                    let displayValue: String
                }
            }
        }
        
        struct TeamPlayers: Codable {
            let team: TeamInfo
            let statistics: [PlayerStatGroup]
            
            struct TeamInfo: Codable {
                let displayName: String
                let abbreviation: String
            }
            
            struct PlayerStatGroup: Codable {
                let type: String
                let names: [String]?
                let keys: [String]?
                let athletes: [AthleteStats]
                
                var groupTitle: String { type.capitalized }
                
                struct AthleteStats: Codable {
                    let athlete: AthleteInfo
                    let stats: [String]
                    let active: Bool?
                    
                    var isActive: Bool { active ?? true }
                    
                    struct AthleteInfo: Codable {
                        let displayName: String
                        let position: Position?
                        let headshot: Headshot?
                        
                        struct Position: Codable {
                            let name: String?
                            let abbreviation: String?
                        }
                        
                        struct Headshot: Codable {
                            let href: String?
                            let alt: String?
                        }
                    }
                }
            }
        }
    }
    
    struct Play: Codable {
        let id: String
        // text is absent on some play types (e.g. inning-start markers in MLB)
        let text: String?
        let type: PlayType
        let scoreValue: Int?
        // ESPN uses "period" (with a displayValue) rather than a "clock" key for most sports
        let period: Period?
        // Cumulative score after this play (present in NBA/NCAAB, absent in MLB/NFL/NHL)
        let awayScore: Int?
        let homeScore: Int?
        // Game-clock time remaining at time of play (NBA, NFL)
        let clock: PlayClock?
        /// MLB play classification: I=inning-header, A=at-bat-header, P=pitch, N=result-note
        let summaryType: String?
        // Default init values let callers (e.g. previews) omit optional fields
        init(id: String, text: String?, type: PlayType, scoreValue: Int?,
             period: Period?, awayScore: Int? = nil, homeScore: Int? = nil,
             clock: PlayClock? = nil, summaryType: String? = nil,
             pitchCoordinate: PitchCoordinate? = nil,
             pitchType: PitchTypeInfo? = nil, pitchVelocity: Int? = nil,
             bats: BatterHand? = nil, atBatId: String? = nil,
             atBatPitchNumber: Int? = nil, resultCount: PitchCount? = nil,
             outs: Int? = nil) {
            self.id = id; self.text = text; self.type = type
            self.scoreValue = scoreValue; self.period = period
            self.awayScore = awayScore; self.homeScore = homeScore
            self.clock = clock; self.summaryType = summaryType
            self.pitchCoordinate = pitchCoordinate; self.pitchType = pitchType
            self.pitchVelocity = pitchVelocity; self.bats = bats
            self.atBatId = atBatId; self.atBatPitchNumber = atBatPitchNumber
            self.resultCount = resultCount; self.outs = outs
        }
        
        // ── Pitch-specific fields (MLB / baseball only) ──────────────────────
        /// Pixel coordinates in ESPN's 256×256 strike-zone space.
        let pitchCoordinate: PitchCoordinate?
        /// Pitch classification (Four-seam FB, Curveball, etc.).
        let pitchType: PitchTypeInfo?
        /// Pitch speed in mph.
        let pitchVelocity: Int?
        /// Batter handedness ("L" / "R").
        let bats: BatterHand?
        /// The at-bat this pitch belongs to.
        let atBatId: String?
        /// Pitch number within the at-bat.
        let atBatPitchNumber: Int?
        /// Balls/strikes count *after* this pitch.
        let resultCount: PitchCount?
        /// Outs at time of pitch.
        let outs: Int?
        
        var isPitch: Bool { pitchCoordinate != nil }
        
        struct PlayType: Codable {
            let text: String
            /// ESPN play-type slug: "ball", "called-strike", "foul", "in-play-out", etc.
            let type: String?
        }
        
        struct Period: Codable {
            let displayValue: String
            /// "Top" or "Bottom" (MLB half-inning), quarter/period name for other sports
            let type: String?
            /// Inning or period number
            let number: Int?
        }
        
        struct PlayClock: Codable {
            let displayValue: String
        }
        
        struct PitchCoordinate: Codable {
            let x: Int
            let y: Int
        }
        
        struct PitchTypeInfo: Codable {
            let text: String
            let abbreviation: String
        }
        
        struct BatterHand: Codable {
            let abbreviation: String  // "L" or "R"
        }
        
        struct PitchCount: Codable {
            let balls: Int
            let strikes: Int
        }
        
        // ── Derived helpers ──────────────────────────────────────────────────
        
        /// Single-character result label for display (B / K / F / O / H / R / •)
        var pitchResultLabel: String {
            switch type.type {
            case "ball":           return "B"
            case "called-strike":  return "K"
            case "swinging-strike": return "K"
            case "foul":           return "F"
            case "in-play-out":    return "O"
            case "in-play-score":  return "R"
            case "in-play-no-out": return "H"
            default:               return "•"
            }
        }
        
        /// Color name for the pitch result dot.
        var pitchResultColorName: String {
            switch type.type {
            case "ball":                       return "blue"
            case "called-strike", "swinging-strike": return "red"
            case "foul":                       return "orange"
            case "in-play-out":                return "gray"
            case "in-play-score":              return "green"
            case "in-play-no-out":             return "green"
            default:                           return "secondary"
            }
        }
        
        /// Human-readable zone description matching the Python app's logic.
        func locationDescription(batterHand: String?) -> String {
            guard let coord = pitchCoordinate else { return "Unknown" }
            let xNorm = Double(coord.x) / 255.0
            let isLeft = (batterHand ?? bats?.abbreviation) == "L"
            
            let horizontal: String
            if isLeft {
                horizontal = xNorm < 0.2 ? "way outside" : xNorm < 0.4 ? "outside" :
                             xNorm < 0.6 ? "over plate"  : xNorm < 0.8 ? "inside"  : "way inside"
            } else {
                horizontal = xNorm < 0.2 ? "way inside" : xNorm < 0.4 ? "inside" :
                             xNorm < 0.6 ? "over plate"  : xNorm < 0.8 ? "outside" : "way outside"
            }
            let yNorm = Double(coord.y) / 255.0
            let vertical = yNorm < 0.33 ? "high" : yNorm < 0.66 ? "middle" : "low"
            return "\(vertical) \(horizontal)"
        }
    }
    
    struct Leader: Codable {
        // NBA wraps categories under a {team, leaders} envelope;
        // MLB/NFL/NHL put {name, displayName} at the top level.
        // Make everything optional so a mismatch in one sport doesn't
        // blow up decoding for another.
        let name: String?
        let displayName: String?
        let leaders: [PlayerLeader]?

        // NBA adds a team reference; ignore it for display purposes.
        // let team: …  (not decoded)

        struct PlayerLeader: Codable {
            // For MLF/NFL/NHL: flat player entry
            let displayValue: String?
            let athlete: Athlete?
            // For NBA: this struct doubles as a category container with its own leaders
            let name: String?
            let displayName: String?
            let leaders: [PlayerLeader]?

            struct Athlete: Codable {
                let displayName: String
            }
        }
    }
}

// MARK: - Error Types
enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case decodingError
    case networkError(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid response from server"
        case .decodingError:
            return "Failed to decode response"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        }
    }
}
