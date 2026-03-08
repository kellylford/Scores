//
//  ESPNAPIResponseModels.swift
//  SportsScores
//
//  Raw API response types decoded in ESPNAPIService, plus the display models
//  for league leaders and polls that are consumed by view models.
//

import Foundation

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
