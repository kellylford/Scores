//
//  Transaction.swift
//  SportsScores
//

import Foundation

// MARK: - Transactions list response

struct TransactionResponse: Codable {
    let season: TransactionSeason?
    let count: Int
    let pageIndex: Int
    let pageSize: Int
    let pageCount: Int
    let transactions: [TransactionItem]
}

struct TransactionSeason: Codable {
    let year: Int
    let type: Int?
    let displayName: String
}

struct TransactionItem: Codable, Identifiable {
    /// Synthetic stable id — team id + date + first 40 chars of description
    var id: String { "\(team.id)-\(dateString)-\(description.prefix(40))" }

    let dateString: String
    let description: String
    let team: TransactionTeam

    enum CodingKeys: String, CodingKey {
        case dateString = "date"
        case description
        case team
    }
}

struct TransactionTeam: Codable, Identifiable {
    let id: String
    let location: String?
    let name: String?
    let abbreviation: String
    let displayName: String
    let color: String?
    let logos: [TransactionTeamLogo]?

    /// URL of the default (light) team logo.
    var primaryLogoURL: URL? {
        let defaultLogo = logos?.first(where: { $0.rel?.contains("default") == true })
        return (defaultLogo ?? logos?.first)?.href.flatMap { URL(string: $0) }
    }
}

struct TransactionTeamLogo: Codable {
    let href: String?
    let width: Int?
    let height: Int?
    let rel: [String]?
}

// MARK: - Teams endpoint response (used by the team picker)

struct TeamsAPIResponse: Codable {
    let sports: [TeamsSport]
}

struct TeamsSport: Codable {
    let leagues: [TeamsLeague]
}

struct TeamsLeague: Codable {
    let teams: [TeamsTeamWrapper]
}

struct TeamsTeamWrapper: Codable {
    let team: TransactionTeam
}
