//
//  FantasyScoringSettings.swift
//  SportsScores
//
//  User-configurable league scoring rules. Persisted via @AppStorage. The
//  points engine maps raw ESPN stat names to a fantasy point total so that
//  changing a setting re-ranks the cheatsheet instantly without refetching.
//
//  Standard NFL fantasy scoring is the default; PPR (point-per-reception) is
//  a single toggle that bumps receptions to 1.0. All values are stored as
//  Double so fractional points (e.g. 0.1 per passing yard) are supported.
//

import Foundation

// MARK: - Scoring Settings

struct FantasyScoringSettings: Codable, Equatable {
    // Passing
    var passingYardsPerPoint: Double = 25.0   // 1 pt per 25 yards
    var passingTD: Double = 4.0
    var passingInterception: Double = -2.0
    // Rushing
    var rushingYardsPerPoint: Double = 10.0   // 1 pt per 10 yards
    var rushingTD: Double = 6.0
    var rushingFumble: Double = -2.0
    // Receiving
    var receivingYardsPerPoint: Double = 10.0
    var receivingTD: Double = 6.0
    var receptions: Double = 0.0              // 0 = standard, 1.0 = PPR, 0.5 = half-PPR
    // Kicking
    var fieldGoalMade: Double = 3.0
    var extraPointMade: Double = 1.0
    // Defense
    var defenseSack: Double = 1.0
    var defenseInterception: Double = 2.0
    var defenseFumbleRecovered: Double = 2.0
    var defenseSafety: Double = 2.0
    var defenseTD: Double = 6.0
    // Points-against bonus/penalty (applied to team defense only)
    var pointsAllowed0: Double = 10.0
    var pointsAllowed1_6: Double = 7.0
    var pointsAllowed7_13: Double = 4.0
    var pointsAllowed14_20: Double = 1.0
    var pointsAllowed21_27: Double = 0.0
    var pointsAllowed28_34: Double = -1.0
    var pointsAllowed35Plus: Double = -4.0

    /// True when receptions are worth 1.0 (full PPR). Convenience for the UI.
    var isPPR: Bool { receptions == 1.0 }

    static let standard = FantasyScoringSettings()
    static let ppr = FantasyScoringSettings(receptions: 1.0)
    static let halfPPR = FantasyScoringSettings(receptions: 0.5)
}

// MARK: - Points Engine

enum FantasyPointsEngine {

    /// Computes fantasy points for an offensive player from raw ESPN stats.
    static func points(for player: CheatsheetPlayer, settings: FantasyScoringSettings) -> Double {
        var pts: Double = 0
        let s = player.stats
        func get(_ key: String) -> Double { s[key] ?? 0 }

        // Passing
        pts += get("passingYards") / settings.passingYardsPerPoint
        pts += get("passingTouchdowns") * settings.passingTD
        pts += get("interceptions") * settings.passingInterception
        // Rushing
        pts += get("rushingYards") / settings.rushingYardsPerPoint
        pts += get("rushingTouchdowns") * settings.rushingTD
        pts += get("rushingFumbles") * settings.rushingFumble
        // Receiving
        pts += get("receivingYards") / settings.receivingYardsPerPoint
        pts += get("receivingTouchdowns") * settings.receivingTD
        pts += get("receptions") * settings.receptions
        // Kicking
        pts += get("fieldGoalsMade") * settings.fieldGoalMade
        pts += get("extraPointsMade") * settings.extraPointMade
        // Two-point conversions (small bonus across the board)
        pts += get("twoPointPassConvs") * 2.0
        pts += get("twoPointRushConvs") * 2.0
        pts += get("twoPointRecConvs") * 2.0

        return roundDouble(pts)
    }

    /// Computes fantasy points for a team defense from raw team defensive stats.
    static func points(for defense: CheatsheetTeamDefense, settings: FantasyScoringSettings) -> Double {
        var pts: Double = 0
        let s = defense.stats
        func get(_ key: String) -> Double { s[key] ?? 0 }

        pts += get("sacks") * settings.defenseSack
        pts += get("interceptions") * settings.defenseInterception
        pts += get("fumblesRecovered") * settings.defenseFumbleRecovered
        pts += get("safeties") * settings.defenseSafety
        // Defensive / special-teams TDs
        pts += (get("interceptionTouchdowns") + get("kickoffReturnTouchdowns")
                + get("fumblesTouchdowns")) * settings.defenseTD

        // Points-against tier (only if the API returned pointsAllowed)
        if let pointsAllowed = s["pointsAllowed"], pointsAllowed > 0 {
            pts += pointsAllowedBonus(pointsAllowed: pointsAllowed, settings: settings)
        }

        return roundDouble(pts)
    }

    /// Maps an absolute points-allowed figure to a bonus/penalty per the settings.
    static func pointsAllowedBonus(pointsAllowed: Double, settings: FantasyScoringSettings) -> Double {
        switch pointsAllowed {
        case 0:                       return settings.pointsAllowed0
        case 1...6:                   return settings.pointsAllowed1_6
        case 7...13:                  return settings.pointsAllowed7_13
        case 14...20:                 return settings.pointsAllowed14_20
        case 21...27:                 return settings.pointsAllowed21_27
        case 28...34:                 return settings.pointsAllowed28_34
        default:                      return settings.pointsAllowed35Plus
        }
    }

    /// Rounds to one decimal place for display.
    static func roundDouble(_ v: Double) -> Double {
        (v * 10).rounded() / 10
    }
}