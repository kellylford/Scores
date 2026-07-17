//
//  FantasyCheatsheetService.swift
//  SportsScores
//
//  Fetches the player universe + per-player stats that back the fantasy
//  cheatsheet. Built on the same ESPN endpoints the rest of the app uses:
//    • site/v2  …/nfl/teams  → all 32 team ids
//    • site/v2  …/teams/{id}/roster → per-team players (identity + position)
//    • core/v2  …/seasons/{y}/types/2/athletes/{id}/statistics/0 → raw splits
//    • core/v2  …/seasons/{y}/types/2/leaders → top-N boards (for quick fills)
//  ESPN does NOT expose fantasy points, ADP, or projections — only raw past
//  stats. Points are computed client-side from FantasyScoringSettings.
//

import Foundation

/// Lightweight team record used to seed the player pool.
struct NFLTeamInfo: Identifiable, Hashable, Codable {
    let id: String
    let abbreviation: String
    let displayName: String
}

/// A resolved athlete from the Core API (position, name, headshot).
struct CoreAthleteDetail: Decodable {
    let id: String?
    let fullName: String?
    let shortName: String?
    let jersey: String?
    let experience: Experience?
    let status: Status?
    let position: Position?
    let team: Reference?

    struct Experience: Decodable { let years: Int? }
    struct Status: Decodable {
        let id: String?
        let name: String?
        let type: String?
    }
    struct Position: Decodable {
        let id: String?
        let name: String?
        let abbreviation: String?
    }
    struct Reference: Decodable {
        let ref: String?
        enum CodingKeys: String, CodingKey { case ref = "$ref" }
    }
}

/// The Core API athlete-statistics response: a single "splits" object holding
/// named categories, each with named stats. We flatten to `[String: Double]`.
struct CoreAthleteStatistics: Decodable {
    let splits: Splits?

    struct Splits: Decodable {
        let categories: [Category]?
        struct Category: Decodable {
            let name: String?
            let stats: [Stat]?
            struct Stat: Decodable {
                let name: String?
                let value: Double?
            }
        }
    }

    /// Flattened stat-name → value dictionary.
    var flatStats: [String: Double] {
        guard let categories = splits?.categories else { return [:] }
        var dict = [String: Double]()
        for category in categories {
            for stat in category.stats ?? [] {
                if let name = stat.name, let value = stat.value {
                    dict[name] = value
                }
            }
        }
        return dict
    }
}

/// The site API team roster response (grouped by offense/defense/special teams).
struct GroupedRosterResponse: Decodable {
    let athletes: [PositionGroup]?
    let team: TeamRef?

    struct PositionGroup: Decodable {
        let position: String?
        let items: [RosterAthlete]?
    }

    struct RosterAthlete: Decodable {
        let id: String
        let fullName: String?
        let shortName: String?
        let jersey: String?
        let position: Position?
        let experience: Experience?
        let status: Status?
        let headshot: Headshot?

        struct Position: Decodable {
            let abbreviation: String?
        }
        struct Experience: Decodable { let years: Int? }
        struct Status: Decodable {
            let name: String?
            let type: String?
        }
        struct Headshot: Decodable { let href: String? }
    }

    struct TeamRef: Decodable {
        let id: String?
        let abbreviation: String?
        let displayName: String?
    }
}

/// The site API /teams list response (nested sports > leagues > teams).
struct NFLTeamsListResponse: Decodable {
    let sports: [Sport]?
    struct Sport: Decodable {
        let leagues: [League]?
        struct League: Decodable {
            let teams: [TeamEntry]?
            struct TeamEntry: Decodable {
                let team: Team?
                struct Team: Decodable {
                    let id: String
                    let abbreviation: String?
                    let displayName: String?
                }
            }
        }
    }

    var allTeams: [NFLTeamInfo] {
        (sports ?? []).flatMap { sport in
            (sport.leagues ?? []).flatMap { league in
                (league.teams ?? []).compactMap { entry -> NFLTeamInfo? in
                    guard let t = entry.team else { return nil }
                    return NFLTeamInfo(
                        id: t.id,
                        abbreviation: t.abbreviation ?? "",
                        displayName: t.displayName ?? t.id
                    )
                }
            }
        }
    }
}

// MARK: - Service

/// Reads-only API layer for the fantasy cheatsheet. Uses ESPNAPIService's
/// session via the shared instance's helpers where possible, but keeps its
/// own decode models so it doesn't bloat the core response types.
final class FantasyCheatsheetService {
    static let shared = FantasyCheatsheetService()

    private let siteBase = "https://site.api.espn.com/apis/site/v2/sports"
    private let coreBase = "https://sports.core.api.espn.com/v2/sports"
    private let session: URLSession

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 120
        self.session = URLSession(configuration: config)
    }

    // MARK: - NFL season resolution

    /// Returns the most recent completed NFL regular season year. In
    /// Feb–June the season is the prior calendar year; July+ uses the same
    /// prior year until the new season starts in September.
    func statsSeason() -> Int {
        let cal = Calendar.current
        let now = Date()
        let year = cal.component(.year, from: now)
        let month = cal.component(.month, from: now)
        // NFL season N spans Sept(year)–Feb(year+1). Stats for "last season"
        // are complete by ~mid-February. Before the new season starts (month < 9)
        // use year-1; from September onward use current year (the new season).
        return month < 9 ? year - 1 : year
    }

    // MARK: - Teams

    /// Fetches all 32 NFL teams in one call.
    func fetchAllNFLTeams() async throws -> [NFLTeamInfo] {
        let urlString = "\(siteBase)/football/nfl/teams?limit=40"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        let resp = try JSONDecoder().decode(NFLTeamsListResponse.self, from: data)
        return resp.allTeams.sorted { $0.abbreviation < $1.abbreviation }
    }

    // MARK: - Roster (player universe)

    /// Fetches a single team's roster and returns fantasy-relevant players
    /// (QB/RB/WR/TE/K). Defensive players are excluded — D/ST is derived
    /// separately from team statistics.
    func fetchRoster(teamId: String) async throws -> [CheatsheetPlayer] {
        let urlString = "\(siteBase)/football/nfl/teams/\(teamId)/roster"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        let resp = try JSONDecoder().decode(GroupedRosterResponse.self, from: data)
        let teamAbbr = resp.team?.abbreviation ?? ""
        var players: [CheatsheetPlayer] = []
        for group in resp.athletes ?? [] {
            for a in group.items ?? [] {
                guard let posAbbr = a.position?.abbreviation,
                      let fantasyPos = FantasyPosition.from(espnAbbr: posAbbr),
                      a.status?.type != "inactive" || a.status?.name == "Active" else { continue }
                // Skip inactive/IR players from the draftable pool.
                if let statusType = a.status?.type?.lowercased(),
                   statusType == "inactive" || statusType == "ir" || statusType == "pup" || statusType == "suspended" {
                    continue
                }
                players.append(CheatsheetPlayer(
                    id: a.id,
                    fullName: a.fullName ?? "Unknown",
                    shortName: a.shortName ?? a.fullName ?? "Unknown",
                    teamAbbreviation: teamAbbr,
                    teamId: teamId,
                    position: fantasyPos,
                    jersey: a.jersey ?? "–",
                    experienceYears: a.experience?.years,
                    isRookie: (a.experience?.years ?? 1) == 0,
                    headshotURL: a.headshot?.href.flatMap { URL(string: $0) },
                    stats: [:]
                ))
            }
        }
        return players
    }

    // MARK: - Per-player statistics (Core API)

    /// Fetches the raw stat splits for a single athlete and returns the
    /// flattened name→value dictionary. Returns empty on failure so a single
    /// player error doesn't break the whole pool.
    func fetchAthleteStats(athleteId: String, season: Int) async -> [String: Double] {
        // Regular season = type 2. Try that first, fall back to type 3 (postseason).
        for seasonType in [2, 3] {
            let urlString = "\(coreBase)/football/leagues/nfl/seasons/\(season)/types/\(seasonType)/athletes/\(athleteId)/statistics/0"
            guard let url = URL(string: urlString) else { continue }
            do {
                let (data, response) = try await session.data(from: url)
                guard let http = response as? HTTPURLResponse, http.statusCode == 200 else { continue }
                let stats = try JSONDecoder().decode(CoreAthleteStatistics.self, from: data)
                let flat = stats.flatStats
                if !flat.isEmpty { return flat }
            } catch {
                continue
            }
        }
        return [:]
    }

    // MARK: - Leaders (quick top-N fill)

    /// A leader entry resolved with athlete name + team abbreviation + id.
    struct ResolvedLeader {
        let athleteId: String
        let fullName: String
        let teamAbbreviation: String
        let statName: String
        let statValue: Double
    }

    /// Fetches the league leaders board and resolves athlete/team refs.
    /// Used to seed the top of the cheatsheet with players who have real stats
    /// before the full roster pool is enriched.
    func fetchLeaders(season: Int, limit: Int = 40) async throws -> [ResolvedLeader] {
        let urlString = "\(coreBase)/football/leagues/nfl/seasons/\(season)/types/2/leaders?limit=\(limit)"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }

        // Decode the same shape ESPNAPIService already understands.
        struct LeadersResponse: Decodable {
            let categories: [Category]?
            struct Category: Decodable {
                let name: String?
                let leaders: [Leader]?
                struct Leader: Decodable {
                    let value: Double?
                    let athlete: Ref?
                    let team: Ref?
                    struct Ref: Decodable {
                        let ref: String?
                        enum CodingKeys: String, CodingKey { case ref = "$ref" }
                    }
                }
            }
        }

        let resp = try JSONDecoder().decode(LeadersResponse.self, from: data)

        // Collect refs to resolve in parallel.
        var athleteRefs = Set<String>()
        var teamRefs = Set<String>()
        for cat in resp.categories ?? [] {
            for leader in cat.leaders ?? [] {
                if let r = leader.athlete?.ref { athleteRefs.insert(secure(r)) }
                if let r = leader.team?.ref { teamRefs.insert(secure(r)) }
            }
        }

        // Freeze into immutable constants before concurrent capture (Swift 6).
        let frozenAthleteRefs = athleteRefs
        let frozenTeamRefs = teamRefs
        async let athletesTask = resolveRefs(frozenAthleteRefs, as: CoreAthleteDetail.self)
        async let teamsTask = resolveRefs(frozenTeamRefs, as: CoreTeamInfo.self)
        let (athletes, teams) = await (athletesTask, teamsTask)

        var resolved: [ResolvedLeader] = []
        for cat in resp.categories ?? [] {
            guard let statName = cat.name else { continue }
            for leader in cat.leaders ?? [] {
                guard let value = leader.value,
                      let athleteRef = leader.athlete?.ref,
                      let athlete = athletes[secure(athleteRef)],
                      let aid = athlete.id ?? athleteIdFromRef(athleteRef) else { continue }
                let teamAbbr = leader.team?.ref.flatMap { teams[secure($0)]?.abbreviation } ?? ""
                resolved.append(ResolvedLeader(
                    athleteId: aid,
                    fullName: athlete.fullName ?? "Unknown",
                    teamAbbreviation: teamAbbr,
                    statName: statName,
                    statValue: value
                ))
            }
        }
        return resolved
    }

    // MARK: - Helpers

    private func secure(_ ref: String) -> String {
        ref.hasPrefix("http://") ? "https://" + ref.dropFirst(7) : ref
    }

    /// Extract the trailing numeric athlete id from a Core API $ref URL.
    private func athleteIdFromRef(_ ref: String) -> String? {
        var trimmed = ref
        if let q = trimmed.firstIndex(of: "?") { trimmed = String(trimmed[..<q]) }
        return trimmed.split(separator: "/").last.map(String.init)
    }

    private func resolveRefs<T: Decodable & Sendable>(
        _ refs: Set<String>, as type: T.Type
    ) async -> [String: T] {
        var cache = [String: T]()
        await withTaskGroup(of: (String, T?).self) { group in
            for ref in refs {
                group.addTask {
                    guard let url = URL(string: ref) else { return (ref, nil) }
                    do {
                        let (data, response) = try await self.session.data(from: url)
                        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                            return (ref, nil)
                        }
                        return (ref, try? JSONDecoder().decode(T.self, from: data))
                    } catch {
                        return (ref, nil)
                    }
                }
            }
            for await (ref, value) in group {
                if let value { cache[ref] = value }
            }
        }
        return cache
    }
}

/// Minimal team info resolved from the Core API team $ref.
private struct CoreTeamInfo: Decodable {
    let abbreviation: String?
    let displayName: String?
}