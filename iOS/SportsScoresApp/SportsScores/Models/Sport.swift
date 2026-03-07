//
//  Sport.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

enum Sport: String, CaseIterable, Identifiable {
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

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .mlb:    return "MLB Baseball"
        case .nfl:    return "NFL Football"
        case .nba:    return "NBA Basketball"
        case .nhl:    return "NHL Hockey"
        case .ncaaf:  return "NCAA Football"
        case .ncaam:  return "NCAA Men's Basketball"
        case .ncaawb: return "NCAA Women's Basketball"
        case .wnba:   return "WNBA Basketball"
        case .ncaah:  return "NCAA Men's Hockey"
        case .ncaawh: return "NCAA Women's Hockey"
        }
    }

    var apiPath: String {
        switch self {
        case .mlb:    return "baseball/mlb"
        case .nfl:    return "football/nfl"
        case .nba:    return "basketball/nba"
        case .nhl:    return "hockey/nhl"
        case .ncaaf:  return "football/college-football"
        case .ncaam:  return "basketball/mens-college-basketball"
        case .ncaawb: return "basketball/womens-college-basketball"
        case .wnba:   return "basketball/wnba"
        case .ncaah:  return "hockey/mens-college-hockey"
        case .ncaawh: return "hockey/womens-college-hockey"
        }
    }

    /// True for sports that navigate by week instead of calendar date.
    var isFootball: Bool {
        self == .nfl || self == .ncaaf
    }

    /// True for sports where the season year uses year+1 (NBA, WNBA, NHL).
    var usesNextYearFormat: Bool {
        self == .nba || self == .wnba || self == .nhl
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
        }
    }

    /// SF Symbol name suitable for a tab or list icon.
    var systemImage: String {
        switch self {
        case .mlb:              return "figure.baseball"
        case .nfl, .ncaaf:      return "figure.american.football"
        case .nba, .ncaam, .ncaawb, .wnba: return "figure.basketball"
        case .nhl, .ncaah, .ncaawh:        return "figure.hockey"
        }
    }
}
