//
//  Golf.swift
//  SportsScores
//
//  Domain models for golf tournaments, leaderboards, and schedules.
//  Constructed from GolfAPIModels (the raw Decodable layer).
//

import Foundation

// MARK: - Tournament Schedule Entry

struct GolfCalendarEntry: Identifiable, Equatable {
    let id: String
    let name: String
    let startDate: Date
    let endDate: Date

    var dateRangeText: String {
        let fmt = DateFormatter()
        fmt.dateFormat = "MMM d"
        let start = fmt.string(from: startDate)
        // End date: show month only if different from start month
        let sameMonth = Calendar.current.component(.month, from: startDate) ==
                        Calendar.current.component(.month, from: endDate)
        let endFmt = DateFormatter()
        endFmt.dateFormat = sameMonth ? "d" : "MMM d"
        let end = endFmt.string(from: endDate)
        let yearFmt = DateFormatter()
        yearFmt.dateFormat = "yyyy"
        return "\(start) – \(end), \(yearFmt.string(from: endDate))"
    }
}

// MARK: - Hole Score

struct GolfHole: Identifiable {
    let number: Int           // 1–18
    let strokes: Int
    let relativeScore: String // "+1", "-1", "E", etc.

    var id: Int { number }
}

// MARK: - Round

struct GolfRound: Identifiable {
    let period: Int            // round number 1–4
    let displayScore: String   // par-relative: "-5", "+1", "E"
    let strokes: Int           // raw total e.g. 67
    let holes: [GolfHole]

    var id: Int { period }
    var label: String { "R\(period)" }

    /// Number of holes actually played (strokes > 0) in this round.
    var holesPlayed: Int { holes.filter { $0.strokes > 0 }.count }

    /// True when the full 18 holes are accounted for (uses hole data when available,
    /// falls back to the round-level stroke total for rounds without hole-detail).
    var isComplete: Bool {
        if !holes.isEmpty { return holesPlayed == 18 }
        return strokes > 0
    }

    /// Score for display in a compact table cell, using displayScore.
    var tableCellText: String {
        guard isComplete else { return "--" }
        return displayScore
    }
}

// MARK: - Competitor (leaderboard row)

struct GolfCompetitor: Identifiable {
    let id: String
    let position: Int           // 1-based leaderboard rank
    let playerName: String
    let shortName: String
    let country: String
    let overallScore: String    // "-12", "E", "+5", "CUT", "WD", "DQ"
    let rounds: [GolfRound]

    var isCut: Bool    { overallScore == "CUT" }
    var isWithdrawn: Bool { overallScore == "WD" || overallScore == "DQ" }
    var isActive: Bool { !isCut && !isWithdrawn }

    var positionDisplay: String {
        isCut || isWithdrawn ? overallScore : "\(position)"
    }

    // MARK: Table row helpers

    /// Values for each round column (R1–R4), "--" when not yet played.
    func roundScore(for round: Int) -> String {
        rounds.first(where: { $0.period == round })?.tableCellText ?? "--"
    }

    /// When the tournament is live and this player is mid-round, returns
    /// the (round number, holes completed) pair; otherwise nil.
    var currentRoundProgress: (round: Int, holesPlayed: Int)? {
        guard isActive else { return nil }
        for round in rounds.sorted(by: { $0.period < $1.period }).reversed() {
            let played = round.holesPlayed
            if played > 0 && played < 18 {
                return (round: round.period, holesPlayed: played)
            }
        }
        return nil
    }

    // MARK: Accessible table helpers

    /// Quick-list: "1. Cameron Young (USA)  -12 (thru 12)  67 / 69 / 68 / --"
    var quickListText: String {
        let scores = (1...4).map { roundScore(for: $0) }.joined(separator: " / ")
        let thru = currentRoundProgress.map { " (thru \($0.holesPlayed))" } ?? ""
        return "\(positionDisplay). \(playerName)  \(overallScore)\(thru)  \(scores)"
    }

    /// Full-list (card) description for VoiceOver.
    var fullListText: String {
        var lines = ["Score: \(overallScore)"]
        if let p = currentRoundProgress {
            lines.append("Round \(p.round) in progress, through \(p.holesPlayed) holes")
        }
        for r in rounds where r.isComplete {
            lines.append("Round \(r.period): \(r.displayScore) (\(r.strokes) strokes)")
        }
        return lines.joined(separator: "; ")
    }
}

// MARK: - Tournament

struct GolfTournament: Identifiable {
    let id: String
    let name: String
    let startDate: Date
    let statusState: String    // "pre", "in", "post"
    let statusDescription: String  // "In Progress", "Scheduled", "Final"
    let isCompleted: Bool
    let broadcasts: [String]
    let competitors: [GolfCompetitor]

    var isInProgress: Bool { statusState == "in" }
    var isScheduled: Bool  { statusState == "pre" }

    /// Number of rounds completed or in progress, derived from competitors.
    var currentRound: Int {
        competitors.first?.rounds.filter(\.isComplete).count ?? 0
    }

    /// Human-readable status + round, e.g. "Round 4 · In Progress" or "Final".
    var roundStatusText: String {
        if isScheduled { return statusDescription }
        let r = currentRound
        if r == 0 { return statusDescription }
        let roundLabel = "Round \(r)"
        if isInProgress { return "\(roundLabel) · In Progress" }
        return isCompleted ? (r == 4 ? "Final" : "Complete") : roundLabel
    }

    /// Live broadcast networks, comma-joined.
    var broadcastText: String {
        broadcasts.joined(separator: " · ")
    }

    // MARK: Init from API response

    init(from api: GolfEventAPIResponse, parseDate: (String) -> Date?) {
        id = api.id
        name = api.name
        startDate = parseDate(api.date ?? "") ?? Date()
        statusState = api.status.type.state
        statusDescription = api.status.type.description
        isCompleted = api.status.type.completed

        let competition = api.competitions.first
        broadcasts = competition?.broadcasts?.flatMap(\.names) ?? []

        competitors = (competition?.competitors ?? [])
            .sorted { $0.order < $1.order }
            .map { GolfCompetitor(from: $0) }
    }
}

// MARK: - GolfCompetitor init from API

extension GolfCompetitor {
    init(from api: GolfCompetitorAPIResponse) {
        id = api.id
        position = api.order
        playerName = api.athlete.fullName
        shortName = api.athlete.shortName ?? api.athlete.fullName
        country = api.athlete.flag?.alt ?? ""
        overallScore = api.score ?? "E"

        rounds = (api.linescores ?? []).map { ls in
            let strokes = ls.value.map { Int($0) } ?? 0
            let holes = (ls.linescores ?? []).map { h -> GolfHole in
                GolfHole(
                    number: h.period,
                    strokes: h.value.map { Int($0) } ?? 0,
                    relativeScore: h.scoreType?.displayValue ?? "E"
                )
            }
            return GolfRound(
                period: ls.period,
                displayScore: ls.displayValue ?? "--",
                strokes: strokes,
                holes: holes
            )
        }
    }
}

// MARK: - Result bundle returned from API service

struct GolfTournamentResult {
    let tournament: GolfTournament?
    let calendar: [GolfCalendarEntry]
}
