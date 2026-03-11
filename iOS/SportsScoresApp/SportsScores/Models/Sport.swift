//
//  Sport.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

enum Sport: String, CaseIterable, Identifiable {
    // ── Main sports (appear on the home page) ─────────────────────────────
    case mlb    = "MLB"
    case nfl    = "NFL"
    case nba    = "NBA"
    case nhl    = "NHL"
    case ncaaf  = "NCAAF"
    case ncaam  = "NCAAM"
    case ncaawb = "NCAAWB"
    case wnba   = "WNBA"
    case ncaah  = "NCAAH"   // NCAA Men's Hockey — ESPN data is often incomplete
    case ncaawh = "NCAAWH"  // NCAA Women's Hockey — same caveat

    // ── Soccer leagues (appear in Soccer hub + Live Scores, not the main home page list) ──
    case soccerEPL        = "EPL"
    case soccerMLS        = "MLS"
    case soccerNWSL       = "NWSL"
    case soccerLaLiga     = "LaLiga"
    case soccerBundesliga = "Bundesliga"
    case soccerSerieA     = "SerieA"
    case soccerLigue1     = "Ligue1"
    case soccerUCL        = "UCL"
    case soccerUEL        = "UEL"
    case soccerLigaMX     = "LigaMX"
    case soccerCONCACAF   = "CONCACAF-CC"

    var id: String { rawValue }

    // Override CaseIterable synthesis so ForEach(Sport.allCases) on the home
    // page only shows the main (non-soccer) sports. Soccer has its own hub.
    static var allCases: [Sport] {
        [.mlb, .nfl, .nba, .nhl, .ncaaf, .ncaam, .ncaawb, .wnba, .ncaah, .ncaawh]
    }

    /// All soccer league cases. Feed these to the Soccer hub and Live Scores.
    static var soccerLeagues: [Sport] {
        [.soccerEPL, .soccerMLS, .soccerNWSL, .soccerLaLiga, .soccerBundesliga,
         .soccerSerieA, .soccerLigue1, .soccerUCL, .soccerUEL, .soccerLigaMX, .soccerCONCACAF]
    }

    var displayName: String {
        switch self {
        case .mlb:              return "MLB Baseball"
        case .nfl:              return "NFL Football"
        case .nba:              return "NBA Basketball"
        case .nhl:              return "NHL Hockey"
        case .ncaaf:            return "NCAA Football"
        case .ncaam:            return "NCAA Men's Basketball"
        case .ncaawb:           return "NCAA Women's Basketball"
        case .wnba:             return "WNBA Basketball"
        case .ncaah:            return "NCAA Men's Hockey"
        case .ncaawh:           return "NCAA Women's Hockey"
        case .soccerEPL:        return "Premier League"
        case .soccerMLS:        return "MLS"
        case .soccerNWSL:       return "NWSL"
        case .soccerLaLiga:     return "La Liga"
        case .soccerBundesliga: return "Bundesliga"
        case .soccerSerieA:     return "Serie A"
        case .soccerLigue1:     return "Ligue 1"
        case .soccerUCL:        return "Champions League"
        case .soccerUEL:        return "Europa League"
        case .soccerLigaMX:     return "Liga MX"
        case .soccerCONCACAF:   return "CONCACAF Champions Cup"
        }
    }

    var apiPath: String {
        switch self {
        case .mlb:              return "baseball/mlb"
        case .nfl:              return "football/nfl"
        case .nba:              return "basketball/nba"
        case .nhl:              return "hockey/nhl"
        case .ncaaf:            return "football/college-football"
        case .ncaam:            return "basketball/mens-college-basketball"
        case .ncaawb:           return "basketball/womens-college-basketball"
        case .wnba:             return "basketball/wnba"
        case .ncaah:            return "hockey/mens-college-hockey"
        case .ncaawh:           return "hockey/womens-college-hockey"
        case .soccerEPL:        return "soccer/eng.1"
        case .soccerMLS:        return "soccer/usa.1"
        case .soccerNWSL:       return "soccer/usa.nwsl"
        case .soccerLaLiga:     return "soccer/esp.1"
        case .soccerBundesliga: return "soccer/ger.1"
        case .soccerSerieA:     return "soccer/ita.1"
        case .soccerLigue1:     return "soccer/fra.1"
        case .soccerUCL:        return "soccer/uefa.champions"
        case .soccerUEL:        return "soccer/uefa.europa"
        case .soccerLigaMX:     return "soccer/mex.1"
        case .soccerCONCACAF:   return "soccer/concacaf.champions"
        }
    }

    /// True for sports that navigate by week instead of calendar date.
    var isFootball: Bool {
        self == .nfl || self == .ncaaf
    }

    /// True for soccer league cases.
    var isSoccer: Bool {
        Sport.soccerLeagues.contains(self)
    }

    /// True for sports where the season year uses year+1 (NBA, WNBA, NHL and NCAA basketball/hockey).
    var usesNextYearFormat: Bool {
        switch self {
        case .nba, .wnba, .nhl, .ncaam, .ncaawb, .ncaah, .ncaawh: return true
        default: return false
        }
    }

    /// True for sports that publish weekly polls/rankings.
    var hasPolls: Bool {
        self == .ncaaf || self == .ncaam || self == .ncaawb
    }

    var icon: String {
        switch self {
        case .mlb:    return "MLB"
        case .nfl:    return "NFL"
        case .nba:    return "NBA"
        case .nhl:    return "NHL"
        case .ncaaf:  return "NCAAF"
        case .ncaam:  return "NCAAM"
        case .ncaawb: return "NCAAWB"
        case .wnba:   return "WNBA"
        case .ncaah:  return "NCAAH"
        case .ncaawh: return "NCAAWH"
        default:      return "⚽"
        }
    }

    /// SF Symbol name suitable for a tab or list icon.
    var systemImage: String {
        switch self {
        case .mlb:                              return "figure.baseball"
        case .nfl, .ncaaf:                      return "figure.american.football"
        case .nba, .ncaam, .ncaawb, .wnba:     return "figure.basketball"
        case .nhl, .ncaah, .ncaawh:            return "figure.hockey"
        default:                                return "figure.soccer"
        }
    }
}
