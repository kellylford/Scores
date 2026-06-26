//
//  Sport.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

enum Sport: String, CaseIterable, Identifiable, Codable {
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

    // ── Golf tours (appear in Golf hub, not the main home page list) ─────────
    case pga  = "PGA"
    case lpga = "LPGA"

    // ── Canadian Football League (separate data source; toggled like a hub) ──
    // Not in `allCases` — it's sourced from CFLAPIService, not ESPN, so it must
    // stay out of the ESPN-driven home/standings/news loops. It has its own
    // home-page row (see SportSelectionView) and appears in Team Hub.
    case cfl = "CFL"

    // ── Auto racing (appear in Racing hub, not the main home page list) ──
    case formulaOne = "F1"
    case indyCar    = "IndyCar"
    case nascarCup  = "NASCAR"

    // ── World Cup hubs (separate from the Soccer hub; appear on the home page when enabled) ──
    case worldCup        = "WorldCup"
    case worldCupWomens  = "WorldCupWomens"

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

    /// All golf tour cases. Feed these to the Golf hub.
    static var golfTours: [Sport] { [.pga, .lpga] }

    /// All auto racing series. Feed these to the Racing hub.
    static var racingSeries: [Sport] { [.formulaOne, .indyCar, .nascarCup] }

    /// Sports available in Team Hub (main sports plus CFL — no soccer or golf).
    static var teamHubSports: [Sport] { allCases + [.cfl] }

    var isRacing: Bool { Sport.racingSeries.contains(self) }

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
        case .formulaOne:       return "Formula 1"
        case .indyCar:          return "IndyCar Series"
        case .nascarCup:        return "NASCAR Cup Series"
        case .worldCup:        return "2026 FIFA World Cup"
        case .worldCupWomens:  return "2027 FIFA Women's World Cup"
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
        case .pga:              return "PGA Tour"
        case .lpga:             return "LPGA Tour"
        case .cfl:              return "CFL Football"
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
        case .worldCup:        return "soccer/fifa.world"
        case .worldCupWomens:  return "soccer/fifa.wwc"
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
        case .pga:              return "golf/pga"
        case .lpga:             return "golf/lpga"
        case .formulaOne:       return "racing/f1"
        case .indyCar:          return "racing/irl"
        case .nascarCup:        return "racing/nascar-premier"
        // CFL is not served by ESPN; CFLAPIService ignores this path. Kept for completeness.
        case .cfl:              return "football/cfl"
        }
    }

    /// True for the Canadian Football League, which is sourced from
    /// `CFLAPIService` (the cfl.ca scoreboard feed) rather than ESPN.
    /// Callers branch on this to route fetches and to hide ESPN-only tabs
    /// (News, Stats) and the historical-season picker.
    var usesCFLSource: Bool { self == .cfl }

    /// True for World Cup hub cases.
    var isWorldCup: Bool {
        self == .worldCup || self == .worldCupWomens
    }

    /// True for sports that navigate by week instead of calendar date.
    var isFootball: Bool {
        self == .nfl || self == .ncaaf
    }

    /// True for sports whose Scores screen navigates by week/round rather than
    /// by calendar day. NFL/NCAAF use ESPN week navigation; CFL uses round-based
    /// navigation from the cfl.ca feed. (CFL has games spread Thu–Sun, so day
    /// navigation would surface mostly empty days.)
    var usesWeekNavigation: Bool {
        isFootball || usesCFLSource
    }

    /// True for soccer league cases (not World Cup — those are hub-only).
    var isSoccer: Bool {
        Sport.soccerLeagues.contains(self)
    }

    /// True for golf tour cases.
    var isGolf: Bool {
        Sport.golfTours.contains(self)
    }

    /// True for college sports — Team Hub shows a conference picker before the team list.
    var isCollegeSport: Bool {
        switch self {
        case .ncaaf, .ncaam, .ncaawb, .ncaah, .ncaawh: return true
        default: return false
        }
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

    // MARK: - Season navigation helpers

    /// Earliest season year available in the ESPN API for this sport.
    var earliestSeason: Int {
        switch self {
        case .ncaaf:         return 2005
        case .ncaah, .ncaawh: return 2012
        default:             return 2001
        }
    }

    /// All season years available for display in the season picker, newest first.
    var availableSeasonYears: [Int] {
        let currentYear = Calendar.current.component(.year, from: Date())
        return Array((earliestSeason...currentYear).reversed())
    }

    /// Human-readable season label for the given API year.
    ///
    /// - For year+1 sports (NBA, NHL, NCAAM, …):  2023 → "2022-23"
    /// - For single-year sports (MLB, NFL, WNBA): 2023 → "2023"
    func seasonDisplayName(year: Int) -> String {
        // WNBA runs within a single calendar year even though usesNextYearFormat = true
        // for the ESPN API convention. Show as plain year to avoid "2025-26" confusion.
        if self == .wnba {
            return String(year - 1)
        }
        if usesNextYearFormat {
            let shortYear = String(year).suffix(2)
            return "\(year - 1)-\(shortYear)"
        }
        return String(year)
    }

    /// The date to jump to when the user selects a historical season via the picker
    /// for non-football sports. Returns an approximate regular-season opening date.
    ///
    /// `year` is the **ESPN API season year** (i.e. the value you would pass as
    /// `season=` to the API), which for `usesNextYearFormat` sports is one more
    /// than the calendar year the season starts in.
    func approximateSeasonStartDate(year: Int) -> Date {
        var comps = DateComponents()
        switch self {
        case .mlb:
            // Regular season opens ~late March / early April
            comps.year = year; comps.month = 4; comps.day = 1
        case .wnba:
            // WNBA opens ~mid May (API year = year, not year+1 for display)
            // When the user picks display year N, API year = N+1; we show May of N.
            comps.year = year - 1; comps.month = 5; comps.day = 14
        case .nba, .ncaam:
            // Season starts ~mid October of the prior calendar year
            comps.year = year - 1; comps.month = 10; comps.day = 18
        case .ncaawb:
            comps.year = year - 1; comps.month = 11; comps.day = 5
        case .nhl:
            comps.year = year - 1; comps.month = 10; comps.day = 8
        case .ncaah, .ncaawh:
            comps.year = year - 1; comps.month = 10; comps.day = 15
        default:
            // Soccer leagues and others: default to January of the display year
            comps.year = year; comps.month = 1; comps.day = 1
        }
        return Calendar.current.date(from: comps) ?? Date()
    }

    var icon: String {
        switch self {
        case .formulaOne: return "F1"
        case .indyCar:    return "IC"
        case .nascarCup:  return "NAC"
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
        case .pga:    return "PGA"
        case .lpga:   return "LPGA"
        case .cfl:    return "CFL"
        case .worldCup:       return "WC"
        case .worldCupWomens: return "WWC"
        default:      return "SOC"
        }
    }

    /// SF Symbol name suitable for a tab or list icon.
    var systemImage: String {
        switch self {
        case .formulaOne, .indyCar, .nascarCup: return "flag.checkered"
        case .mlb:                              return "figure.baseball"
        case .nfl, .ncaaf, .cfl:                return "figure.american.football"
        case .nba, .ncaam, .ncaawb, .wnba:     return "figure.basketball"
        case .nhl, .ncaah, .ncaawh:            return "figure.hockey"
        case .pga, .lpga:                       return "figure.golf"
        case .worldCup, .worldCupWomens:        return "globe.americas.fill"
        default:                                return "figure.soccer"
        }
    }
}
