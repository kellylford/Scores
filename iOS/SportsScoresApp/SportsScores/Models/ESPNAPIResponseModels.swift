//
//  ESPNAPIResponseModels.swift
//  SportsScores
//
//  Raw API response types decoded in ESPNAPIService, plus the display models
//  for league leaders and polls that are consumed by view models.
//

import Foundation

// MARK: - Team Stats Ranking

/// One row in the Team Stats tab: where this team ranks in a given stat category.
struct TeamStatRanking: Identifiable {
    let id = UUID()
    let sectionName: String          // "Batting", "Pitching", etc.
    let categoryDisplayName: String  // "ERA", "Home Runs"
    let teamValue: String            // "3.58"
    let leagueRank: Int             // numeric rank, used for color coding
    let rankDisplay: String          // ESPN display string: "2nd", "Tied-9th"
}

// MARK: - Core API Team Statistics Response
// Used by ESPNAPIService.fetchTeamStatRankings.
// URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/seasons/{year}/types/{type}/teams/{id}/statistics

struct CoreTeamStatisticsResponse: Codable {
    let splits: Splits?

    struct Splits: Codable {
        let categories: [StatCategory]?

        struct StatCategory: Codable {
            let name: String?
            let displayName: String?
            let stats: [Stat]?

            struct Stat: Codable {
                let name: String?
                let displayName: String?
                let value: Double?
                let displayValue: String?
                let rank: Int?
                let rankDisplayValue: String?
            }
        }
    }
}

// MARK: - League Leaders Models

struct LeagueLeaderCategory: Identifiable {
    let id = UUID()
    let name: String
    let displayName: String
    let leaders: [LeagueLeaderEntry]
    /// True when every entry represents a team rather than an individual player.
    let isTeamCategory: Bool

    struct LeagueLeaderEntry: Identifiable {
        let id = UUID()
        let rank: Int
        let displayValue: String
        /// Player name for player categories; team abbreviation for team categories.
        let athleteName: String
        /// Team abbreviation for player categories; empty for team categories.
        let teamAbbreviation: String
    }

    init(name: String, displayName: String, leaders: [LeagueLeaderEntry], isTeamCategory: Bool = false) {
        self.name = name
        self.displayName = displayName
        self.leaders = leaders
        self.isTeamCategory = isTeamCategory
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
            /// The raw numeric stat value (e.g. 0.331 for BA, 4.0 for HR count).
            /// Use this instead of displayValue for MLB, whose displayValue is a
            /// full stats-line string like "9-17, 4 HR, 2B, 6 RBI, 7 R, 3 BB, 4 K".
            let value: Double?
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

// MARK: - Scoreboard Response

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
