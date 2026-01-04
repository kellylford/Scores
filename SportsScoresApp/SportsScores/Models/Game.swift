//
//  Game.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

struct Game: Identifiable, Codable {
    let id: String
    let name: String
    let shortName: String
    let date: Date
    let status: GameStatus
    let homeTeam: Team
    let awayTeam: Team
    let venue: Venue?
    let broadcasts: [String]
    
    var displayTime: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "EEE M/d h:mm a"
        return formatter.string(from: date)
    }
    
    var scoreDisplay: String {
        if status.state == "pre" {
            return displayTime
        } else {
            return "\(awayTeam.score ?? 0) - \(homeTeam.score ?? 0)"
        }
    }
    
    struct Team: Codable {
        let id: String
        let name: String
        let abbreviation: String
        let displayName: String
        let score: Int?
        let record: String?
        let logo: String?
        
        var displayText: String {
            if let score = score, let record = record {
                return "\(abbreviation) (\(record)) - \(score)"
            } else if let record = record {
                return "\(abbreviation) (\(record))"
            } else if let score = score {
                return "\(abbreviation) - \(score)"
            } else {
                return abbreviation
            }
        }
    }
    
    struct GameStatus: Codable {
        let state: String // "pre", "in", "post"
        let detail: String
        let period: Int?
        let clock: String?
        
        var displayText: String {
            if state == "in", let period = period, let clock = clock {
                return "\(detail) - \(clock)"
            }
            return detail
        }
        
        var isLive: Bool {
            state == "in"
        }
        
        var isCompleted: Bool {
            state == "post"
        }
    }
    
    struct Venue: Codable {
        let name: String
        let city: String?
        let state: String?
        
        var fullName: String {
            if let city = city, let state = state {
                return "\(name), \(city), \(state)"
            } else if let city = city {
                return "\(name), \(city)"
            }
            return name
        }
    }
}

// MARK: - API Response Models
extension Game {
    init(from apiResponse: APIGame) throws {
        self.id = apiResponse.id
        self.name = apiResponse.name
        self.shortName = apiResponse.shortName
        
        // Parse date
        let formatter = ISO8601DateFormatter()
        self.date = formatter.date(from: apiResponse.date) ?? Date()
        
        // Parse status
        self.status = GameStatus(
            state: apiResponse.status.type.state,
            detail: apiResponse.status.type.detail,
            period: apiResponse.status.period,
            clock: apiResponse.status.displayClock
        )
        
        // Parse teams
        let competitions = apiResponse.competitions.first
        let homeCompetitor = competitions?.competitors.first(where: { $0.homeAway == "home" })
        let awayCompetitor = competitions?.competitors.first(where: { $0.homeAway == "away" })
        
        self.homeTeam = Team(
            id: homeCompetitor?.team.id ?? "",
            name: homeCompetitor?.team.name ?? "",
            abbreviation: homeCompetitor?.team.abbreviation ?? "",
            displayName: homeCompetitor?.team.displayName ?? "",
            score: Int(homeCompetitor?.score ?? "0"),
            record: homeCompetitor?.records?.first?.summary,
            logo: homeCompetitor?.team.logo
        )
        
        self.awayTeam = Team(
            id: awayCompetitor?.team.id ?? "",
            name: awayCompetitor?.team.name ?? "",
            abbreviation: awayCompetitor?.team.abbreviation ?? "",
            displayName: awayCompetitor?.team.displayName ?? "",
            score: Int(awayCompetitor?.score ?? "0"),
            record: awayCompetitor?.records?.first?.summary,
            logo: awayCompetitor?.team.logo
        )
        
        // Parse venue
        if let venueData = competitions?.venue {
            self.venue = Venue(
                name: venueData.fullName,
                city: venueData.address?.city,
                state: venueData.address?.state
            )
        } else {
            self.venue = nil
        }
        
        // Parse broadcasts
        self.broadcasts = competitions?.broadcasts?.map { $0.names.first ?? "" } ?? []
    }
}

// MARK: - ESPN API Response Structure
struct APIGame: Codable {
    let id: String
    let name: String
    let shortName: String
    let date: String
    let status: APIStatus
    let competitions: [APICompetition]
    
    struct APIStatus: Codable {
        let type: APIStatusType
        let period: Int?
        let displayClock: String?
        
        struct APIStatusType: Codable {
            let state: String
            let detail: String
        }
    }
    
    struct APICompetition: Codable {
        let competitors: [APICompetitor]
        let venue: APIVenue?
        let broadcasts: [APIBroadcast]?
        
        struct APICompetitor: Codable {
            let homeAway: String
            let team: APITeam
            let score: String?
            let records: [APIRecord]?
            
            struct APITeam: Codable {
                let id: String
                let name: String
                let abbreviation: String
                let displayName: String
                let logo: String?
            }
            
            struct APIRecord: Codable {
                let summary: String
            }
        }
        
        struct APIVenue: Codable {
            let fullName: String
            let address: APIAddress?
            
            struct APIAddress: Codable {
                let city: String?
                let state: String?
            }
        }
        
        struct APIBroadcast: Codable {
            let names: [String]
        }
    }
}
