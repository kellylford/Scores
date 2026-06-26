//
//  Racing.swift
//  SportsScores
//
//  Domain models for auto racing: race events, competitors, and championship standings.
//  Covers Formula 1 (racing/f1), IndyCar (racing/irl), and NASCAR Cup (racing/nascar-premier).
//

import Foundation

// MARK: - Race Competitor

struct RaceCompetitor: Identifiable {
    let id: String
    let position: Int          // finishing order; 1 = winner
    let driverName: String
    let shortName: String      // e.g. "K. Antonelli"
    let nationality: String    // country name from flag.alt, may be empty
}

// MARK: - Race Event

struct RaceEvent: Identifiable {
    let id: String
    let name: String
    let date: Date
    let statusState: String        // "pre", "in", "post"
    let statusDescription: String  // "Scheduled", "In Progress", "Final"
    let broadcasts: [String]
    let competitors: [RaceCompetitor]

    var isScheduled: Bool  { statusState == "pre" }
    var isInProgress: Bool { statusState == "in" }
    var isCompleted: Bool  { statusState == "post" }

    var broadcastText: String {
        broadcasts.isEmpty ? "" : broadcasts.joined(separator: " · ")
    }

    var winner: RaceCompetitor? {
        competitors.first { $0.position == 1 }
    }
}

// MARK: - Standings Entry

struct RacingStandingsEntry: Identifiable {
    let id: String
    let rank: Int
    let name: String          // driver display name or constructor name
    let shortName: String     // abbreviated; e.g. "K. Antonelli", "MER"
    let nationality: String   // driver nationality; empty for constructor entries
    let points: String        // formatted championship points, e.g. "156"
}

// MARK: - Standings Group

struct RacingStandingsGroup: Identifiable {
    let id: String            // "drivers" or "constructors"
    let name: String          // "Driver Standings", "Constructor Standings", "Standings"
    let entries: [RacingStandingsEntry]
}
