//
//  FantasyCheatsheet.swift
//  SportsScores
//
//  Fantasy football cheatsheet models. Backed by ESPN's fantasy player universe
//  (lm-api-reads.fantasy.espn.com …/players?view=kona_player_info), which — unlike
//  the public site/core APIs — exposes real draft data: average draft position
//  (ADP), auction values, PPR/Standard consensus ranks, and season projections.
//
//  The cheatsheet is a "good starting point" draft board, not a full draft app:
//  it ranks by ESPN's published rank/ADP and shows projected points for the
//  chosen scoring format. Team defenses (D/ST) come from the same feed, so a
//  single struct represents both players and defenses.
//

import Foundation

// MARK: - Fantasy Position

/// Fantasy-relevant NFL positions, including a synthetic D/ST row per team.
enum FantasyPosition: String, CaseIterable, Identifiable, Hashable {
    case qb  = "QB"
    case rb  = "RB"
    case wr  = "WR"
    case te  = "TE"
    case k   = "K"
    case dst = "D/ST"

    var id: String { rawValue }
    var displayName: String { rawValue }

    /// Maps ESPN's `defaultPositionId` to a fantasy position.
    /// Returns nil for non-fantasy positions (IDL, LB, DB, P, etc.).
    static func from(positionId: Int) -> FantasyPosition? {
        switch positionId {
        case 1:  return .qb
        case 2:  return .rb
        case 3:  return .wr
        case 4:  return .te
        case 5:  return .k
        case 16: return .dst
        default: return nil
        }
    }
}

// MARK: - Scoring format

/// The three common scoring formats. ESPN publishes separate PPR and Standard
/// rank boards + projections; Half-PPR is derived from the PPR board with the
/// reception value halved.
enum ScoringPreset: String, CaseIterable, Identifiable, Codable {
    case standard = "Standard"
    case halfPPR  = "Half-PPR"
    case ppr      = "PPR"

    var id: String { rawValue }

    /// Points awarded per reception in this format.
    var pointsPerReception: Double {
        switch self {
        case .standard: return 0.0
        case .halfPPR:  return 0.5
        case .ppr:      return 1.0
        }
    }
}

// MARK: - Pro team map

/// ESPN `proTeamId` → team abbreviation. These ids are stable and match the
/// team ids used elsewhere in ESPN's APIs. `0` denotes a free agent.
enum NFLProTeams {
    static let abbreviations: [Int: String] = [
        1: "ATL",  2: "BUF",  3: "CHI",  4: "CIN",  5: "CLE",  6: "DAL",
        7: "DEN",  8: "DET",  9: "GB",  10: "TEN", 11: "IND", 12: "KC",
        13: "LV",  14: "LAR", 15: "MIA", 16: "MIN", 17: "NE",  18: "NO",
        19: "NYG", 20: "NYJ", 21: "PHI", 22: "ARI", 23: "PIT", 24: "LAC",
        25: "SF",  26: "SEA", 27: "TB",  28: "WSH", 29: "CAR", 30: "JAX",
        33: "BAL", 34: "HOU"
    ]

    static func abbreviation(for id: Int) -> String { abbreviations[id] ?? "FA" }
}

// MARK: - Cheatsheet Player (also represents D/ST)

/// A single row on the cheatsheet — an offensive player or a team defense.
/// All the draft-relevant values come pre-computed from the fantasy feed, so
/// switching scoring format only re-derives points/rank locally (no refetch).
struct CheatsheetPlayer: Identifiable, Hashable {
    let id: String                  // ESPN athlete id, or "dst-<proTeamId>"
    let fullName: String            // players: name; defenses: "<Team> D/ST"
    let position: FantasyPosition
    let proTeamId: Int
    let teamAbbreviation: String
    /// Injury designation ("QUESTIONABLE", "OUT", …). Nil when active/unknown.
    let injuryStatus: String?
    /// Average draft position. Nil when the player is effectively undrafted.
    let adp: Double?
    /// Average auction dollar value. Nil when none is published.
    let auctionValue: Double?
    let pprRank: Int?
    let standardRank: Int?
    /// Projected fantasy points EXCLUDING receptions, computed from ESPN's raw
    /// projected stat line (passing/rushing/receiving yards + TDs, turnovers).
    /// Reception points are added per scoring format in `projectedPoints(for:)`.
    /// Nil when there is no reliable projection — kickers and D/ST, whose ESPN
    /// `appliedTotal` values are corrupted (e.g. ~23,000) and unusable.
    let projectedPointsBase: Double?
    /// Projected receptions — added at the chosen format's per-reception value.
    let projectedReceptions: Double
    let headshotURL: URL?

    var isDST: Bool { position == .dst }

    /// Display name. Team defenses already arrive as "<Team> D/ST" from the feed.
    var displayName: String { fullName }

    /// Published rank for the chosen format. Half-PPR reuses the PPR board
    /// (ESPN publishes no separate Half-PPR ranks).
    func rank(for preset: ScoringPreset) -> Int? {
        preset == .standard ? standardRank : pprRank
    }

    /// Projected fantasy points for the chosen format: the non-reception base
    /// plus receptions valued at the format's per-reception rate.
    func projectedPoints(for preset: ScoringPreset) -> Double? {
        guard let base = projectedPointsBase else { return nil }
        return base + projectedReceptions * preset.pointsPerReception
    }

    /// One-decimal projected-points string, or "—" when no projection exists.
    func projectedPointsString(for preset: ScoringPreset) -> String {
        guard let pts = projectedPoints(for: preset) else { return "—" }
        return String(format: "%.1f", pts)
    }

    /// ADP string ("—" when undrafted).
    var adpString: String {
        guard let adp, adp > 0, adp < 300 else { return "—" }
        return String(format: "%.1f", adp)
    }

    /// Auction value string ("—" when none), e.g. "$42".
    var auctionString: String {
        guard let auctionValue, auctionValue > 0 else { return "—" }
        return "$\(Int(auctionValue.rounded()))"
    }
}

// MARK: - Draft State

/// Tracks which players have been marked taken in the user's live draft.
/// Persisted in UserDefaults keyed by player id so it survives app restarts.
struct DraftState: Codable, Equatable {
    /// Player ids (athlete id or "dst-<proTeamId>") marked taken.
    var takenIds: Set<String> = []

    mutating func toggleTaken(_ id: String) {
        if takenIds.contains(id) { takenIds.remove(id) }
        else { takenIds.insert(id) }
    }

    func isTaken(_ id: String) -> Bool { takenIds.contains(id) }
}

// MARK: - Sort Category

/// Columns the cheatsheet can be sorted by. All map to draft data the fantasy
/// feed provides directly.
enum CheatsheetSort: String, CaseIterable, Identifiable {
    case rank            = "ESPN Rank"
    case adp             = "ADP"
    case auctionValue    = "Auction Value"
    case projectedPoints = "Projected Points"

    var id: String { rawValue }
}
