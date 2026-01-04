//
//  Sport.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

enum Sport: String, CaseIterable, Identifiable {
    case mlb = "MLB"
    case nfl = "NFL"
    case nba = "NBA"
    case nhl = "NHL"
    case ncaaf = "NCAAF"
    case ncaam = "NCAAM"
    case ncaawb = "NCAAWB"
    
    var id: String { rawValue }
    
    var displayName: String {
        switch self {
        case .mlb: return "MLB Baseball"
        case .nfl: return "NFL Football"
        case .nba: return "NBA Basketball"
        case .nhl: return "NHL Hockey"
        case .ncaaf: return "NCAA Football"
        case .ncaam: return "NCAA Men's Basketball"
        case .ncaawb: return "NCAA Women's Basketball"
        }
    }
    
    var apiPath: String {
        switch self {
        case .mlb: return "baseball/mlb"
        case .nfl: return "football/nfl"
        case .nba: return "basketball/nba"
        case .nhl: return "hockey/nhl"
        case .ncaaf: return "football/college-football"
        case .ncaam: return "basketball/mens-college-basketball"
        case .ncaawb: return "basketball/womens-college-basketball"
        }
    }
    
    var icon: String {
        switch self {
        case .mlb: return "MLB"
        case .nfl: return "NFL"
        case .nba, .ncaam, .ncaawb: return "NBA"
        case .nhl: return "NHL"
        case .ncaaf: return "NCAAF"
        }
    }
}
