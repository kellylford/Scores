//
//  TeamStatCatalog.swift
//  SportsScores
//
//  Curated list of league-wide team statistics per sport.
//
//  ESPN's `statistics/byteam` endpoint returns every team's full stat line
//  (100+ values for football). Showing all of them would bury the interesting
//  numbers, so each sport gets a hand-picked list in a sensible reading order
//  (offense → defense → special teams), together with the sort direction that
//  makes "#1" mean "best" rather than merely "largest".
//

import Foundation

/// One team-stat category to build from the `byteam` payload.
struct TeamStatSpec {
    /// Which half of the payload the value comes from. ESPN reports each
    /// category twice: the team's own production (`splitId` 0) and what its
    /// opponents did against it (`splitId` 900) — the latter is how "yards
    /// allowed" and "opponent points" are expressed.
    enum Split {
        case own
        case opponent
    }

    let split: Split
    /// ESPN category name, e.g. "batting", "passing", "offensive".
    let section: String
    /// ESPN stat name within that category, e.g. "homeRuns", "avgPoints".
    let stat: String
    /// Heading shown to the user. ESPN's own display names collide across
    /// categories (batting and pitching both have "Strikeouts"), so titles
    /// are spelled out here rather than taken from the feed.
    let title: String
    /// True when a larger value ranks first (points scored); false when a
    /// smaller value does (ERA, turnovers, points allowed).
    let higherIsBetter: Bool

    init(_ split: Split, _ section: String, _ stat: String, _ title: String, higherIsBetter: Bool = true) {
        self.split = split
        self.section = section
        self.stat = stat
        self.title = title
        self.higherIsBetter = higherIsBetter
    }

    /// The team's own production — the common case.
    init(_ section: String, _ stat: String, _ title: String, higherIsBetter: Bool = true) {
        self.init(.own, section, stat, title, higherIsBetter: higherIsBetter)
    }

    /// Stable identifier used as the category name so "View All" can re-find
    /// this category after a second fetch.
    var key: String {
        "\(split == .opponent ? "opponent." : "")\(section).\(stat)"
    }
}

enum TeamStatCatalog {

    /// Specs for a sport, or an empty array when ESPN publishes no team
    /// statistics for it (soccer, golf, racing, college hockey, CFL).
    static func specs(for sport: Sport) -> [TeamStatSpec] {
        switch sport {
        case .mlb:
            return baseball
        case .nfl, .ncaaf:
            return football
        case .nba, .wnba, .ncaam, .ncaawb:
            return basketball
        case .nhl:
            return hockey
        default:
            return []
        }
    }

    // MARK: - Baseball

    private static let baseball: [TeamStatSpec] = [
        // Batting
        TeamStatSpec("batting", "runs", "Runs"),
        TeamStatSpec("batting", "homeRuns", "Home Runs"),
        TeamStatSpec("batting", "avg", "Batting Average"),
        TeamStatSpec("batting", "onBasePct", "On Base Percentage"),
        TeamStatSpec("batting", "slugAvg", "Slugging Percentage"),
        TeamStatSpec("batting", "OPS", "OPS"),
        TeamStatSpec("batting", "hits", "Hits"),
        TeamStatSpec("batting", "doubles", "Doubles"),
        TeamStatSpec("batting", "triples", "Triples"),
        TeamStatSpec("batting", "walks", "Walks Drawn"),
        TeamStatSpec("batting", "stolenBases", "Stolen Bases"),
        TeamStatSpec("batting", "strikeouts", "Fewest Batter Strikeouts", higherIsBetter: false),
        // Pitching
        TeamStatSpec("pitching", "ERA", "Earned Run Average", higherIsBetter: false),
        TeamStatSpec("pitching", "WHIP", "WHIP", higherIsBetter: false),
        TeamStatSpec("pitching", "opponentAvg", "Opponent Batting Average", higherIsBetter: false),
        TeamStatSpec("pitching", "strikeouts", "Pitching Strikeouts"),
        TeamStatSpec("pitching", "qualityStarts", "Quality Starts"),
        TeamStatSpec("pitching", "saves", "Saves"),
        TeamStatSpec("pitching", "shutouts", "Shutouts"),
        TeamStatSpec("pitching", "homeRuns", "Fewest Home Runs Allowed", higherIsBetter: false),
        TeamStatSpec("pitching", "walks", "Fewest Walks Allowed", higherIsBetter: false),
        // Fielding
        TeamStatSpec("fielding", "fieldingPct", "Fielding Percentage"),
        TeamStatSpec("fielding", "errors", "Fewest Errors", higherIsBetter: false),
    ]

    // MARK: - Football
    //
    // NFL publishes a superset of the college feed; specs missing from the
    // college payload (turnover differential, takeaways) are skipped silently.

    private static let football: [TeamStatSpec] = [
        // Scoring and total offense
        TeamStatSpec("passing", "totalPointsPerGame", "Points Per Game"),
        TeamStatSpec(.opponent, "passing", "totalPointsPerGame", "Fewest Points Allowed Per Game", higherIsBetter: false),
        TeamStatSpec("passing", "yardsPerGame", "Total Yards Per Game"),
        TeamStatSpec(.opponent, "passing", "yardsPerGame", "Fewest Total Yards Allowed Per Game", higherIsBetter: false),
        // Passing
        TeamStatSpec("passing", "passingYardsPerGame", "Passing Yards Per Game"),
        TeamStatSpec(.opponent, "passing", "passingYardsPerGame", "Fewest Passing Yards Allowed Per Game", higherIsBetter: false),
        TeamStatSpec("passing", "passingTouchdowns", "Passing Touchdowns"),
        TeamStatSpec("passing", "completionPct", "Completion Percentage"),
        TeamStatSpec("passing", "QBRating", "Passer Rating"),
        // Rushing
        TeamStatSpec("rushing", "rushingYardsPerGame", "Rushing Yards Per Game"),
        TeamStatSpec(.opponent, "rushing", "rushingYardsPerGame", "Fewest Rushing Yards Allowed Per Game", higherIsBetter: false),
        TeamStatSpec("rushing", "rushingTouchdowns", "Rushing Touchdowns"),
        TeamStatSpec("rushing", "yardsPerRushAttempt", "Yards Per Rush"),
        // Situational
        TeamStatSpec("miscellaneous", "firstDowns", "First Downs"),
        TeamStatSpec("miscellaneous", "thirdDownConvPct", "Third Down Percentage"),
        TeamStatSpec("miscellaneous", "fourthDownConvPct", "Fourth Down Percentage"),
        TeamStatSpec("miscellaneous", "turnOverDifferential", "Turnover Differential"),
        TeamStatSpec("miscellaneous", "totalTakeaways", "Takeaways"),
        TeamStatSpec("miscellaneous", "totalGiveaways", "Fewest Giveaways", higherIsBetter: false),
        TeamStatSpec("miscellaneous", "totalPenaltyYards", "Fewest Penalty Yards", higherIsBetter: false),
        // Defense (the defense's production shows up in the opponent split)
        TeamStatSpec(.opponent, "passing", "sacks", "Sacks"),
        TeamStatSpec(.opponent, "passing", "interceptions", "Interceptions"),
        // Special teams
        TeamStatSpec("kicking", "fieldGoalPct", "Field Goal Percentage"),
        TeamStatSpec("punting", "netAvgPuntYards", "Net Punting Average"),
    ]

    // MARK: - Basketball

    private static let basketball: [TeamStatSpec] = [
        TeamStatSpec("offensive", "avgPoints", "Points Per Game"),
        TeamStatSpec(.opponent, "offensive", "avgPoints", "Fewest Points Allowed Per Game", higherIsBetter: false),
        TeamStatSpec("differential", "avgPointsDifferential", "Scoring Margin"),
        TeamStatSpec("offensive", "fieldGoalPct", "Field Goal Percentage"),
        TeamStatSpec(.opponent, "offensive", "fieldGoalPct", "Opponent Field Goal Percentage", higherIsBetter: false),
        TeamStatSpec("offensive", "threePointFieldGoalPct", "3-Point Percentage"),
        TeamStatSpec("offensive", "avgThreePointFieldGoalsMade", "3-Pointers Made Per Game"),
        TeamStatSpec("offensive", "freeThrowPct", "Free Throw Percentage"),
        TeamStatSpec("offensive", "avgAssists", "Assists Per Game"),
        TeamStatSpec("general", "avgRebounds", "Rebounds Per Game"),
        TeamStatSpec("offensive", "avgOffensiveRebounds", "Offensive Rebounds Per Game"),
        TeamStatSpec("defensive", "avgDefensiveRebounds", "Defensive Rebounds Per Game"),
        TeamStatSpec("defensive", "avgSteals", "Steals Per Game"),
        TeamStatSpec("defensive", "avgBlocks", "Blocks Per Game"),
        TeamStatSpec("general", "assistTurnoverRatio", "Assist To Turnover Ratio"),
        TeamStatSpec("offensive", "avgTurnovers", "Fewest Turnovers Per Game", higherIsBetter: false),
        TeamStatSpec("general", "avgFouls", "Fewest Fouls Per Game", higherIsBetter: false),
    ]

    // MARK: - Hockey

    private static let hockey: [TeamStatSpec] = [
        TeamStatSpec("offensive", "avgGoals", "Goals For Per Game"),
        TeamStatSpec("defensive", "avgGoalsAgainst", "Goals Against Average", higherIsBetter: false),
        TeamStatSpec("offensive", "goals", "Goals"),
        TeamStatSpec("offensive", "assists", "Assists"),
        TeamStatSpec("offensive", "powerPlayPct", "Power Play Percentage"),
        TeamStatSpec("defensive", "penaltyKillPct", "Penalty Kill Percentage"),
        TeamStatSpec("offensive", "powerPlayGoals", "Power Play Goals"),
        TeamStatSpec("offensive", "shortHandedGoals", "Short Handed Goals"),
        TeamStatSpec("offensive", "shotsTotal", "Shots"),
        TeamStatSpec("offensive", "shootingPct", "Shooting Percentage"),
        TeamStatSpec("defensive", "savePct", "Save Percentage"),
        TeamStatSpec("defensive", "saves", "Saves"),
        TeamStatSpec("defensive", "shutouts", "Shutouts"),
        TeamStatSpec("defensive", "shotsAgainst", "Fewest Shots Against", higherIsBetter: false),
        TeamStatSpec("penalties", "penaltyMinutes", "Fewest Penalty Minutes", higherIsBetter: false),
        TeamStatSpec("general", "wins", "Wins"),
    ]
}
