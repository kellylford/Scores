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
    let situation: Situation?
    /// ESPN season type — 1 preseason, 2 regular, 3 postseason (default 2).
    let seasonType: Int
    
    var displayTime: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "EEE M/d h:mm a"
        formatter.timeZone = TimeZone.current
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
            if state == "in", period != nil, let clock = clock {
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
    
    struct Situation: Codable {
        let lastPlay: String?
        let down: Int?
        let distance: Int?
        let possessionText: String?
        let shortDownDistanceText: String?
        // Baseball live situation
        let onFirst: Bool?
        let onSecond: Bool?
        let onThird: Bool?
        let outs: Int?
        let balls: Int?
        let strikes: Int?

        var displayText: String? {
            if let lastPlay = lastPlay, !lastPlay.isEmpty {
                return lastPlay
            }
            return shortDownDistanceText
        }

        /// Non-nil for live baseball games — e.g. "1st & 3rd, 3-2, 1 out"
        var baseballSituationText: String? {
            guard balls != nil || outs != nil || onFirst != nil else { return nil }
            var parts: [String] = []
            // Bases
            let firstOn  = onFirst  ?? false
            let secondOn = onSecond ?? false
            let thirdOn  = onThird  ?? false
            if firstOn || secondOn || thirdOn {
                var bases: [String] = []
                if firstOn  { bases.append("1st") }
                if secondOn { bases.append("2nd") }
                if thirdOn  { bases.append("3rd") }
                parts.append(bases.joined(separator: " & "))
            } else {
                parts.append("Bases empty")
            }
            // Count
            if let b = balls, let s = strikes { parts.append("\(b)-\(s)") }
            // Outs
            if let o = outs { parts.append("\(o) \(o == 1 ? "out" : "outs")") }
            return parts.joined(separator: ", ")
        }
    }
}

// MARK: - API Response Models
extension Game {
    init(from apiResponse: APIGame, seasonType: Int = 2) throws {
        self.id = apiResponse.id
        self.name = apiResponse.name
        self.shortName = apiResponse.shortName
        self.seasonType = seasonType
        
        // Parse date - ESPN returns dates in ISO8601 format (e.g., "2026-01-05T01:20Z")
        let dateFormatter = DateFormatter()
        dateFormatter.locale = Locale(identifier: "en_US_POSIX")
        dateFormatter.timeZone = TimeZone(secondsFromGMT: 0)
        
        // ESPN returns several ISO-8601 variants; try most common first
        let dateFormats = [
            "yyyy-MM-dd'T'HH:mm:ss'Z'",   // most common: 2026-01-05T01:20:00Z
            "yyyy-MM-dd'T'HH:mm'Z'",       // compact: 2026-01-05T01:20Z
            "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'" // with milliseconds
        ]
        var parsedDate: Date?
        for fmt in dateFormats {
            dateFormatter.dateFormat = fmt
            if let d = dateFormatter.date(from: apiResponse.date) {
                parsedDate = d
                break
            }
        }
        self.date = parsedDate ?? Date()
        
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
            // flatMap returns nil when score is nil or non-numeric (e.g. pre-game "")
            score: homeCompetitor?.score.flatMap({ Int($0) }),
            record: homeCompetitor?.records?.first?.summary,
            logo: homeCompetitor?.team.logo
        )
        
        self.awayTeam = Team(
            id: awayCompetitor?.team.id ?? "",
            name: awayCompetitor?.team.name ?? "",
            abbreviation: awayCompetitor?.team.abbreviation ?? "",
            displayName: awayCompetitor?.team.displayName ?? "",
            score: awayCompetitor?.score.flatMap({ Int($0) }),
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
        
        // Parse situation (last play, down & distance for football; bases/count/outs for baseball)
        if let situationData = competitions?.situation {
            self.situation = Situation(
                lastPlay: situationData.lastPlay?.text,
                down: situationData.down,
                distance: situationData.distance,
                possessionText: situationData.possessionText,
                shortDownDistanceText: situationData.shortDownDistanceText,
                onFirst: situationData.onFirst,
                onSecond: situationData.onSecond,
                onThird: situationData.onThird,
                outs: situationData.outs,
                balls: situationData.balls,
                strikes: situationData.strikes
            )
        } else {
            self.situation = nil
        }
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
        let situation: APISituation?
        
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
        
        struct APISituation: Codable {
            let lastPlay: APILastPlay?
            let down: Int?
            let distance: Int?
            let possessionText: String?
            let shortDownDistanceText: String?
            // Baseball live fields
            let onFirst: Bool?
            let onSecond: Bool?
            let onThird: Bool?
            let outs: Int?
            let balls: Int?
            let strikes: Int?

            struct APILastPlay: Codable {
                let text: String?
            }
        }
    }
}
