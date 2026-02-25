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
    private let session: URLSession
    
    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)
    }
    
    // MARK: - Fetch Games
    func fetchGames(for sport: Sport) async throws -> [Game] {
        let urlString = "\(baseURL)/\(sport.apiPath)/scoreboard"
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
        let apiResponse = try decoder.decode(ScoreboardResponse.self, from: data)
        
        return try apiResponse.events.map { try Game(from: $0) }
    }
    
    // MARK: - Fetch Standings
    func fetchStandings(for sport: Sport) async throws -> [StandingsGroup] {
        let urlString = "\(baseURL)/\(sport.apiPath)/standings"
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
        
        return try apiResponse.children.map { try StandingsGroup(from: $0) }
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
}

// MARK: - API Response Models
struct ScoreboardResponse: Codable {
    let events: [APIGame]
}

struct GameDetails: Codable {
    let boxscore: Boxscore?
    let plays: [Play]?
    let leaders: [Leader]?
    
    struct Boxscore: Codable {
        let teams: [TeamStats]
        
        struct TeamStats: Codable {
            let team: TeamInfo
            // ESPN returns statistics as named categories (batting, pitching, etc.)
            // each containing a "stats" array of individual stat items.
            let statistics: [StatCategory]
            
            struct TeamInfo: Codable {
                let displayName: String
                let abbreviation: String
            }
            
            /// Top-level stat grouping (e.g. "batting", "pitching", "fielding")
            struct StatCategory: Codable {
                let name: String
                let displayName: String
                let stats: [StatItem]
                
                struct StatItem: Codable {
                    let name: String
                    let displayName: String
                    let abbreviation: String
                    let displayValue: String
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
        let name: String
        let displayName: String
        let leaders: [PlayerLeader]
        
        struct PlayerLeader: Codable {
            let displayValue: String
            let athlete: Athlete
            
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
