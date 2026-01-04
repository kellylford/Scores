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
            let statistics: [Statistic]
            
            struct TeamInfo: Codable {
                let displayName: String
                let abbreviation: String
            }
            
            struct Statistic: Codable {
                let name: String
                let displayValue: String
                let label: String
            }
        }
    }
    
    struct Play: Codable {
        let id: String
        let text: String
        let type: PlayType
        let scoreValue: Int?
        let clock: Clock?
        
        struct PlayType: Codable {
            let text: String
        }
        
        struct Clock: Codable {
            let displayValue: String
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
