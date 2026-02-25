//
//  Standings.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

struct StandingsGroup: Identifiable {
    let id = UUID()
    let name: String
    let entries: [StandingsEntry]
}

struct StandingsEntry: Identifiable {
    let id = UUID()
    let rank: Int
    let team: TeamInfo
    let stats: StandingsStats
    
    struct TeamInfo {
        let id: String
        let name: String
        let abbreviation: String
        let displayName: String
        let logo: String?
    }
    
    struct StandingsStats {
        let wins: Int
        let losses: Int
        let winPercent: Double
        let gamesBack: String
        let streak: String
        let record: String
        let pointsFor: Int?
        let pointsAgainst: Int?
        
        var displayWinPercent: String {
            String(format: "%.3f", winPercent)
        }
    }
    
    // For table view display
    var tableRow: [String] {
        [
            "\(rank)",
            team.abbreviation,
            "\(stats.wins)",
            "\(stats.losses)",
            stats.displayWinPercent,
            stats.gamesBack,
            stats.streak,
            stats.record
        ]
    }
    
    // For quick list display
    var quickListText: String {
        "\(team.abbreviation), \(stats.wins)-\(stats.losses), \(stats.displayWinPercent), GB: \(stats.gamesBack)"
    }
    
    // For full list display
    var fullListText: String {
        """
        Rank: \(rank); Team: \(team.displayName); Wins: \(stats.wins); Losses: \(stats.losses); \
        Win%: \(stats.displayWinPercent); Games Back: \(stats.gamesBack); Streak: \(stats.streak); Record: \(stats.record)
        """
    }
}

// MARK: - API Response Models
extension StandingsGroup {
    init(from apiResponse: APIStandingsGroup) throws {
        self.name = apiResponse.name
        self.entries = apiResponse.standings.entries.map { apiEntry in
            let team = apiEntry.team
            let stats = apiEntry.stats
            
            return StandingsEntry(
                rank: Int(stats.first(where: { $0.name == "rank" })?.value ?? 0),
                team: StandingsEntry.TeamInfo(
                    id: team.id,
                    name: team.name,
                    abbreviation: team.abbreviation,
                    displayName: team.displayName,
                    logo: team.logos?.first?.href
                ),
                stats: StandingsEntry.StandingsStats(
                    wins: Int(stats.first(where: { $0.name == "wins" })?.value ?? 0),
                    losses: Int(stats.first(where: { $0.name == "losses" })?.value ?? 0),
                    winPercent: stats.first(where: { $0.name == "winPercent" })?.value ?? 0,
                    gamesBack: stats.first(where: { $0.name == "gamesBehind" })?.displayValue ?? "0",
                    streak: stats.first(where: { $0.name == "streak" })?.displayValue ?? "-",
                    record: stats.first(where: { $0.name == "overall" })?.displayValue ?? "-",
                    pointsFor: Int(stats.first(where: { $0.name == "pointsFor" })?.value ?? 0),
                    pointsAgainst: Int(stats.first(where: { $0.name == "pointsAgainst" })?.value ?? 0)
                )
            )
        }
    }
}

struct APIStandingsGroup: Codable {
    let name: String
    let standings: APIStandings
    
    struct APIStandings: Codable {
        let entries: [APIStandingsEntry]
        
        struct APIStandingsEntry: Codable {
            let team: APITeam
            let stats: [APIStat]
            
            struct APITeam: Codable {
                let id: String
                let name: String
                let abbreviation: String
                let displayName: String
                let logos: [APILogo]?
                
                struct APILogo: Codable {
                    let href: String
                }
            }
            
            struct APIStat: Codable {
                let name: String
                let displayName: String
                let value: Double
                let displayValue: String
            }
        }
    }
}

struct APIStandingsResponse: Codable {
    let children: [APIStandingsGroup]
}
