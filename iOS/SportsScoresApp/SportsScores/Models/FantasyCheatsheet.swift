//
//  FantasyCheatsheet.swift
//  SportsScores
//
//  Fantasy football cheatsheet models. Pulls player identity/position from the
//  ESPN site roster endpoint and per-player statistical splits from the Core
//  API athlete-statistics endpoint, then computes a fantasy-points column from
//  user-configurable ScoringSettings.
//
//  ESPN does NOT expose an official fantasy-points value, ADP, or projections —
//  only raw past-season / season-to-date stats. The cheatsheet therefore ranks
//  by a stats-derived points value, not by consensus rank or ADP.
//

import Foundation

// MARK: - Fantasy Position

/// Fantasy-relevant NFL positions. Defensive players are grouped under a
/// synthetic "D/ST" row per team (derived, not from the roster) so the cheatsheet
/// matches a standard fantasy draft board.
enum FantasyPosition: String, CaseIterable, Identifiable, Hashable {
    case qb = "QB"
    case rb = "RB"
    case wr = "WR"
    case te = "TE"
    case k  = "K"
    case dst = "D/ST"

    var id: String { rawValue }

    /// Display label used in the filter chips and column headers.
    var displayName: String { rawValue }

    /// Maps an ESPN roster position abbreviation to a fantasy position.
    /// Returns nil for positions that aren't fantasy-relevant (OL, LS, etc.).
    static func from(espnAbbr: String) -> FantasyPosition? {
        switch espnAbbr.uppercased() {
        case "QB": return .qb
        case "RB": return .rb
        case "FB": return .rb   // fullbacks pool with RBs
        case "WR": return .wr
        case "TE": return .te
        case "K", "PK": return .k
        default:  return nil
        }
    }
}

// MARK: - Cheatsheet Player

/// A single row in the cheatsheet. Holds identity + the raw stat splits needed
/// to compute fantasy points. The computed `fantasyPoints` value is derived
/// from `stats` + `ScoringSettings` at view time so changing settings re-ranks
/// instantly without refetching.
struct CheatsheetPlayer: Identifiable, Hashable {
    let id: String                 // ESPN athlete id
    let fullName: String
    let shortName: String
    let teamAbbreviation: String
    let teamId: String
    let position: FantasyPosition
    let jersey: String
    let experienceYears: Int?
    let isRookie: Bool
    let headshotURL: URL?
    /// Raw named stats keyed by ESPN stat name (e.g. "passingYards").
    /// Populated lazily from the Core API statistics/0 endpoint.
    var stats: [String: Double]

    /// Cached fantasy-points total for the current scoring settings.
    /// Nil until first computed.
    var computedPoints: Double?
}

// MARK: - Cheatsheet Team Defense (D/ST)

/// A derived D/ST row — one per NFL team. Defense stats come from the team
/// statistics endpoint rather than an individual athlete.
struct CheatsheetTeamDefense: Identifiable, Hashable {
    /// Team id prefixed to avoid colliding with athlete ids.
    let id: String
    let teamAbbreviation: String
    let teamDisplayName: String
    let teamId: String
    /// Raw team defensive stats (sacks, interceptions, fumbles recovered, etc.)
    var stats: [String: Double]
    var computedPoints: Double?

    init(teamId: String, abbreviation: String, displayName: String, stats: [String: Double] = [:]) {
        self.id = "dst-\(teamId)"
        self.teamId = teamId
        self.teamAbbreviation = abbreviation
        self.teamDisplayName = displayName
        self.stats = stats
    }
}

// MARK: - Draft State

/// Tracks whether a player has been drafted (taken) in the user's live draft.
/// Persisted in UserDefaults keyed by player id so it survives app restarts.
struct DraftState: Codable, Equatable {
    /// Player ids (athlete id or "dst-<teamId>") that have been marked taken.
    var takenIds: Set<String> = []

    mutating func toggleTaken(_ id: String) {
        if takenIds.contains(id) { takenIds.remove(id) }
        else { takenIds.insert(id) }
    }

    func isTaken(_ id: String) -> Bool { takenIds.contains(id) }
}

// MARK: - Sort Category

/// Columns the cheatsheet can be sorted by.
enum CheatsheetSort: String, CaseIterable, Identifiable {
    case fantasyPoints = "Fantasy Points"
    case passingYards = "Pass Yds"
    case passingTDs = "Pass TD"
    case rushingYards = "Rush Yds"
    case rushingTDs = "Rush TD"
    case receivingYards = "Rec Yds"
    case receivingTDs = "Rec TD"
    case receptions = "Receptions"
    case totalTDs = "Total TD"

    var id: String { rawValue }

    /// The ESPN stat name this sort maps to. Nil for the computed fantasy
    /// points column (which is derived, not a raw stat).
    var statKey: String? {
        switch self {
        case .fantasyPoints: return nil
        case .passingYards: return "passingYards"
        case .passingTDs: return "passingTouchdowns"
        case .rushingYards: return "rushingYards"
        case .rushingTDs: return "rushingTouchdowns"
        case .receivingYards: return "receivingYards"
        case .receivingTDs: return "receivingTouchdowns"
        case .receptions: return "receptions"
        case .totalTDs: return "totalTouchdowns"
        }
    }
}