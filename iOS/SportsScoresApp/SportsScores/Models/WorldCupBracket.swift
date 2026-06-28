//
//  WorldCupBracket.swift
//  SportsScores
//
//  A model of the World Cup knockout bracket that can resolve ESPN's
//  "Round of 32 N Winner" placeholders into the actual teams that feed a match.
//
//  ESPN populates later-round matchups with placeholder competitors whose
//  displayName is e.g. "Round of 32 1 Winner", "Quarterfinal 2 Winner",
//  "Semifinal 1 Loser". Within a round the matches are numbered 1…K in event-id
//  order. This engine parses those placeholders and walks the bracket so we can:
//
//    • show the real teams feeding an undetermined match
//      ("Winner of RSA/CAN vs Winner of NED/MAR") — used inline, capped so a
//      reader never has to track more than four teams at once, and
//    • compute every team's status and forward "path to the Cup".
//
//  Everything is dynamic: as matches complete, ESPN fills the winner into the
//  next round, so placeholders collapse to real teams on their own. We also use
//  the `isWinner` flag to resolve completed feeders, so the projection shrinks
//  the moment a result is in — even before ESPN propagates it forward.
//

import Foundation

// MARK: - Rounds

/// A knockout round, ordered shallow (Round of 32) → deep (Final).
enum KnockoutRound: Int, Comparable, CaseIterable {
    case roundOf32 = 0
    case roundOf16
    case quarterfinals
    case semifinals
    case thirdPlace
    case final

    /// Maps ESPN's `season.slug` to a round.
    init?(slug: String) {
        switch slug {
        case "round-of-32":     self = .roundOf32
        case "round-of-16":     self = .roundOf16
        case "quarterfinals":   self = .quarterfinals
        case "semifinals":      self = .semifinals
        case "3rd-place-match": self = .thirdPlace
        case "final":           self = .final
        default:                return nil
        }
    }

    /// Maps the round word inside a placeholder ("Round of 32 1 Winner") to a round.
    /// Only the rounds that can *feed* a later match appear as placeholder sources.
    init?(placeholderWord word: String) {
        switch word {
        case "Round of 32": self = .roundOf32
        case "Round of 16": self = .roundOf16
        case "Quarterfinal": self = .quarterfinals
        case "Semifinal":    self = .semifinals
        default:             return nil
        }
    }

    /// Human-readable round name (used for headings and status).
    var label: String {
        switch self {
        case .roundOf32:     return "Round of 32"
        case .roundOf16:     return "Round of 16"
        case .quarterfinals: return "Quarterfinals"
        case .semifinals:    return "Semifinals"
        case .thirdPlace:    return "Third-Place Match"
        case .final:         return "Final"
        }
    }

    /// Noun used when referring to one specific match of this round, e.g. the
    /// humanized fallback "Round of 16 match 1 winner" / "Quarterfinal 2 winner".
    var matchReferenceNoun: String {
        switch self {
        case .roundOf32:     return "Round of 32 match"
        case .roundOf16:     return "Round of 16 match"
        case .quarterfinals: return "Quarterfinal"
        case .semifinals:    return "Semifinal"
        case .thirdPlace:    return "Third-place match"
        case .final:         return "Final"
        }
    }

    /// The round a *winner* of this round advances to (nil for the final).
    var nextRoundForWinner: KnockoutRound? {
        switch self {
        case .roundOf32:     return .roundOf16
        case .roundOf16:     return .quarterfinals
        case .quarterfinals: return .semifinals
        case .semifinals:    return .final
        case .thirdPlace, .final: return nil
        }
    }

    static func < (lhs: KnockoutRound, rhs: KnockoutRound) -> Bool {
        lhs.rawValue < rhs.rawValue
    }
}

// MARK: - Slot references

/// One side of a match: either a known team or a placeholder pointing at the
/// winner/loser of an earlier match.
enum BracketSide {
    case team(Game.Team)
    case slot(round: KnockoutRound, number: Int, outcome: Outcome)

    enum Outcome { case winner, loser }
}

extension BracketSide {
    /// Parses a competitor's `displayName` into a placeholder slot, if it is one.
    /// Examples: "Round of 32 1 Winner", "Quarterfinal 2 Winner", "Semifinal 1 Loser".
    static func parsePlaceholder(_ name: String) -> BracketSide? {
        let outcome: Outcome
        let body: Substring
        if name.hasSuffix(" Winner") {
            outcome = .winner
            body = name.dropLast(" Winner".count)
        } else if name.hasSuffix(" Loser") {
            outcome = .loser
            body = name.dropLast(" Loser".count)
        } else {
            return nil
        }
        // body is e.g. "Round of 32 1" — split off the trailing match number.
        guard let lastSpace = body.lastIndex(of: " ") else { return nil }
        let numberStr = body[body.index(after: lastSpace)...]
        guard let number = Int(numberStr) else { return nil }
        let word = String(body[..<lastSpace])
        guard let round = KnockoutRound(placeholderWord: word) else { return nil }
        return .slot(round: round, number: number, outcome: outcome)
    }
}

// MARK: - Bracket matches

/// One knockout match, with its round and 1-based number within that round.
struct BracketMatch: Identifiable {
    let round: KnockoutRound
    let number: Int
    let game: Game

    var id: String { game.id }
    var isCompleted: Bool { game.status.isCompleted }

    /// Competitors in display order (away first, then home).
    var competitors: [Game.Team] { [game.awayTeam, game.homeTeam] }

    var winnerTeam: Game.Team? {
        guard isCompleted else { return nil }
        return competitors.first { $0.isWinner == true }
    }

    var loserTeam: Game.Team? {
        guard isCompleted else { return nil }
        return competitors.first { $0.isWinner == false } ?? competitors.first { $0.id != winnerTeam?.id }
    }

    func competitor(withId id: String) -> Game.Team? {
        competitors.first { $0.id == id }
    }
}

// MARK: - Team status

/// How far a team has gone / can still go in the tournament.
enum TeamFate {
    case alive(next: KnockoutRound)   // their next/ongoing match is in this round
    case champion
    case runnerUp                     // lost the Final
    case thirdPlace                   // won the third-place match
    case fourthPlace                  // lost the third-place match
    case eliminated(KnockoutRound)    // lost at this round (Round of 32 … Semifinals)
    case eliminatedInGroup

    var isAlive: Bool { if case .alive = self { return true }; return false }
}

/// A team in the tournament, with enough identity to label it for any name
/// preference plus its current fate.
struct BracketTeam: Identifiable {
    let id: String
    let displayName: String
    let abbreviation: String
    let groupName: String?
    /// The richest `Game.Team` we have for this team (from a knockout match it
    /// played), used so the user's name preference (mascot/city) works.
    let team: Game.Team?
    let fate: TeamFate

    func name(for pref: TeamNamePreference) -> String {
        if let team { return team.voiceOverName(for: pref) }
        // Group-only teams: we only have abbreviation + displayName.
        switch pref {
        case .abbreviation: return abbreviation
        default:            return displayName
        }
    }
}

// MARK: - Bracket

/// The full knockout bracket, built from each round's games plus the group
/// standings (so group-stage-eliminated teams are still listed).
struct WorldCupBracket {

    /// All knockout matches, keyed by round.
    private let matchesByRound: [KnockoutRound: [BracketMatch]]
    /// Fast lookup of a match by (round, number).
    private let matchIndex: [String: BracketMatch]
    /// Every team in the tournament, keyed by id.
    let teamsById: [String: BracketTeam]

    // MARK: Build

    /// - Parameters:
    ///   - roundGames: knockout games grouped by round (each round's games in
    ///     any order — numbering is derived here).
    ///   - matchNumbers: `[eventId: officialMatchNumber]` from the core API. This
    ///     is what ESPN's "Round of 32 N Winner" placeholders actually reference;
    ///     neither kickoff order nor event-id order matches it (FIFA's match
    ///     numbers follow the fixed bracket layout, not the schedule).
    ///   - groups: group standings, used as the master list of all teams.
    init(roundGames: [KnockoutRound: [Game]],
         matchNumbers: [String: Int],
         groups: [WorldCupGroup]) {
        var byRound: [KnockoutRound: [BracketMatch]] = [:]
        var index: [String: BracketMatch] = [:]

        for (round, games) in roundGames {
            // Number matches within a round by their official match number. Within
            // a round these are contiguous (R32 = 73–88, R16 = 89–96, …), so
            // sorting by match number and assigning 1…K reproduces exactly the N
            // that the "Round of 32 N Winner" placeholders point at. Fall back to
            // kickoff time, then event id, if a match number is unavailable.
            let ordered = games.sorted { a, b in
                if let na = matchNumbers[a.id], let nb = matchNumbers[b.id], na != nb {
                    return na < nb
                }
                if a.date != b.date { return a.date < b.date }
                return (Int(a.id) ?? 0) < (Int(b.id) ?? 0)
            }
            var matches: [BracketMatch] = []
            for (i, game) in ordered.enumerated() {
                let m = BracketMatch(round: round, number: i + 1, game: game)
                matches.append(m)
                index["\(round.rawValue)-\(i + 1)"] = m
            }
            byRound[round] = matches
        }

        self.matchesByRound = byRound
        self.matchIndex = index

        // Build the team registry.
        self.teamsById = WorldCupBracket.buildTeams(
            byRound: byRound, index: index, groups: groups
        )
    }

    private func match(round: KnockoutRound, number: Int) -> BracketMatch? {
        matchIndex["\(round.rawValue)-\(number)"]
    }

    private static func match(_ index: [String: BracketMatch],
                              round: KnockoutRound, number: Int) -> BracketMatch? {
        index["\(round.rawValue)-\(number)"]
    }

    /// True once at least one knockout round of games has been loaded.
    var hasKnockoutGames: Bool { !matchIndex.isEmpty }

    /// Matches for a round, ordered by match number.
    func matches(in round: KnockoutRound) -> [BracketMatch] {
        matchesByRound[round]?.sorted { $0.number < $1.number } ?? []
    }

    // MARK: Side classification & resolution

    /// Classify a competitor as a known team or a placeholder slot.
    func side(of team: Game.Team) -> BracketSide {
        BracketSide.parsePlaceholder(team.displayName) ?? .team(team)
    }

    /// The distinct real teams that can still occupy a side, resolving completed
    /// feeders to their actual winner/loser and recursing into undecided ones.
    func possibleTeams(_ side: BracketSide) -> [Game.Team] {
        var seen = Set<String>()
        var result: [Game.Team] = []
        func walk(_ side: BracketSide) {
            switch side {
            case .team(let t):
                if seen.insert(t.id).inserted { result.append(t) }
            case .slot(let round, let number, let outcome):
                guard let m = match(round: round, number: number) else { return }
                if m.isCompleted {
                    let resolved = outcome == .winner ? m.winnerTeam : m.loserTeam
                    if let t = resolved {
                        if seen.insert(t.id).inserted { result.append(t) }
                        return
                    }
                }
                for c in m.competitors { walk(self.side(of: c)) }
            }
        }
        walk(side)
        return result
    }

    // MARK: Display

    private func teamName(_ team: Game.Team, voiceOver: Bool, pref: TeamNamePreference) -> String {
        voiceOver ? team.voiceOverName(for: pref) : team.abbreviation
    }

    private func joinNames(_ names: [String], voiceOver: Bool) -> String {
        guard names.count > 1 else { return names.first ?? "" }
        if names.count == 2 {
            // A two-team slot is a single match — "vs" reads as a matchup, whereas
            // "or" sounds like a choice. (The 3+ case below stays a list with "or".)
            return voiceOver ? "\(names[0]) vs \(names[1])" : "\(names[0])/\(names[1])"
        }
        if voiceOver {
            let head = names.dropLast().joined(separator: ", ")
            return "\(head), or \(names.last!)"
        }
        return names.joined(separator: ", ")
    }

    /// A human description of one side: a team name, "Winner of A/B", or for the
    /// many-team case "one of A, B, C, D". Collapses automatically as results land.
    func description(of side: BracketSide, voiceOver: Bool, pref: TeamNamePreference) -> String {
        switch side {
        case .team(let t):
            return teamName(t, voiceOver: voiceOver, pref: pref)
        case .slot(_, _, let outcome):
            let teams = possibleTeams(side)
            let names = teams.map { teamName($0, voiceOver: voiceOver, pref: pref) }
            if names.count <= 1 { return names.first ?? "TBD" }
            if names.count == 2 {
                let prefix = outcome == .winner ? "Winner of " : "Loser of "
                return prefix + joinNames(names, voiceOver: voiceOver)
            }
            return (voiceOver ? "one of " : "1 of: ") + joinNames(names, voiceOver: voiceOver)
        }
    }

    /// Humanized fallback for a slot we choose not to expand (would exceed the
    /// inline team budget): "Round of 16 match 1 winner".
    private func fallbackLabel(for side: BracketSide, voiceOver: Bool, pref: TeamNamePreference) -> String {
        switch side {
        case .team(let t):
            return teamName(t, voiceOver: voiceOver, pref: pref)
        case .slot(let round, let number, let outcome):
            return "\(round.matchReferenceNoun) \(number) \(outcome == .winner ? "winner" : "loser")"
        }
    }

    /// Labels for both sides of a knockout match, for inline display.
    ///
    /// If resolving the placeholders would force the reader to track more than
    /// four real teams, we fall back to the humanized round reference instead of
    /// expanding — honoring the "never more than four teams" rule.
    struct SideLabels {
        let awayVisual: String
        let homeVisual: String
        let awayVoice: String
        let homeVoice: String
    }

    func inlineLabels(for game: Game, pref: TeamNamePreference, maxTeams: Int = 4) -> SideLabels {
        let awaySide = side(of: game.awayTeam)
        let homeSide = side(of: game.homeTeam)

        // Distinct real teams across both sides.
        var ids = Set<String>()
        let pool = possibleTeams(awaySide) + possibleTeams(homeSide)
        for t in pool { ids.insert(t.id) }
        let expand = ids.count <= maxTeams

        func label(_ s: BracketSide, voiceOver: Bool) -> String {
            expand ? description(of: s, voiceOver: voiceOver, pref: pref)
                   : fallbackLabel(for: s, voiceOver: voiceOver, pref: pref)
        }

        return SideLabels(
            awayVisual: label(awaySide, voiceOver: false),
            homeVisual: label(homeSide, voiceOver: false),
            awayVoice:  label(awaySide, voiceOver: true),
            homeVoice:  label(homeSide, voiceOver: true)
        )
    }

    // MARK: Forward path

    /// A stage on a team's road to the Cup: the round, the scheduled match (for
    /// date/venue), and the opponent they would face there (resolved as far as
    /// results allow).
    struct PathStage {
        let round: KnockoutRound
        let game: Game
        let opponent: BracketSide
    }

    /// Knockout matches the team actually played in, shallowest round first.
    /// (Group-stage history is fetched separately — those games aren't in the bracket.)
    func playedMatches(forTeamId id: String) -> [BracketMatch] {
        KnockoutRound.allCases.compactMap { round in
            matchesByRound[round]?.first { $0.competitor(withId: id) != nil }
        }
    }

    /// The match in the next round that a given (round, number) winner feeds into.
    private func nextMatch(afterRound round: KnockoutRound, number: Int) -> BracketMatch? {
        guard let nextRound = round.nextRoundForWinner else { return nil }
        return matches(in: nextRound).first { m in
            m.competitors.contains { c in
                if case .slot(let r, let n, .winner) = side(of: c) {
                    return r == round && n == number
                }
                return false
            }
        }
    }

    /// The deepest match a team actually appears in as a real competitor.
    private func deepestMatch(forTeamId id: String) -> BracketMatch? {
        var best: BracketMatch?
        for round in KnockoutRound.allCases {
            if let m = matchesByRound[round]?.first(where: { $0.competitor(withId: id) != nil }) {
                if best == nil || m.round > best!.round { best = m }
            }
        }
        return best
    }

    /// The remaining stages a team must win to lift the trophy, opponents resolved
    /// dynamically. Empty if the team is eliminated or already champion.
    func forwardPath(forTeamId id: String) -> [PathStage] {
        guard let anchor = deepestMatch(forTeamId: id) else { return [] }

        var current: BracketMatch
        // Whether we entered `current` via a feeder slot (future match) and which
        // (round, number) that feeder is — so we can pick out the opponent side.
        var enteredVia: (round: KnockoutRound, number: Int)?

        if anchor.isCompleted {
            // If they won and there's a next match, project from there (covers the
            // brief window before ESPN propagates the winner forward).
            guard anchor.competitor(withId: id)?.isWinner == true,
                  let nxt = nextMatch(afterRound: anchor.round, number: anchor.number) else {
                return []   // eliminated, champion, or final/third already played
            }
            current = nxt
            enteredVia = (anchor.round, anchor.number)
        } else {
            current = anchor
            enteredVia = nil
        }

        var stages: [PathStage] = []
        while true {
            let opponent: BracketSide
            if let via = enteredVia {
                let sides = current.competitors.map { side(of: $0) }
                let myIndex = sides.firstIndex { s in
                    if case .slot(let r, let n, .winner) = s { return r == via.round && n == via.number }
                    return false
                } ?? 0
                opponent = sides[1 - myIndex]
            } else {
                let myIndex = current.competitors.firstIndex { $0.id == id } ?? 0
                opponent = side(of: current.competitors[1 - myIndex])
            }
            stages.append(PathStage(round: current.round, game: current.game, opponent: opponent))

            guard let nxt = nextMatch(afterRound: current.round, number: current.number) else { break }
            enteredVia = (current.round, current.number)
            current = nxt
        }
        return stages
    }

    // MARK: Team registry construction

    private static func buildTeams(
        byRound: [KnockoutRound: [BracketMatch]],
        index: [String: BracketMatch],
        groups: [WorldCupGroup]
    ) -> [String: BracketTeam] {

        // Richest Game.Team and deepest match per real team id.
        var bestTeam: [String: Game.Team] = [:]
        var deepest: [String: BracketMatch] = [:]
        for round in KnockoutRound.allCases {
            for m in byRound[round] ?? [] {
                for c in m.competitors {
                    // Skip placeholder competitors (their ids aren't real team ids).
                    guard BracketSide.parsePlaceholder(c.displayName) == nil else { continue }
                    bestTeam[c.id] = c
                    if let d = deepest[c.id] {
                        if m.round > d.round { deepest[c.id] = m }
                    } else {
                        deepest[c.id] = m
                    }
                }
            }
        }

        func fate(forId id: String) -> TeamFate {
            guard let m = deepest[id] else { return .eliminatedInGroup }
            guard m.isCompleted else { return .alive(next: m.round) }
            let won = m.competitor(withId: id)?.isWinner == true
            switch m.round {
            case .final:      return won ? .champion : .runnerUp
            case .thirdPlace: return won ? .thirdPlace : .fourthPlace
            default:
                if won {
                    // Advanced; next round not yet showing them (propagation lag).
                    return .alive(next: m.round.nextRoundForWinner ?? m.round)
                }
                return .eliminated(m.round)
            }
        }

        var result: [String: BracketTeam] = [:]

        // Master list = all group teams (covers group-stage-eliminated teams).
        for group in groups {
            for e in group.entries {
                result[e.id] = BracketTeam(
                    id: e.id,
                    displayName: e.teamDisplayName,
                    abbreviation: e.teamAbbreviation,
                    groupName: group.name,
                    team: bestTeam[e.id],
                    fate: fate(forId: e.id)
                )
            }
        }
        // Safety: include any knockout team missing from group data.
        for (id, t) in bestTeam where result[id] == nil {
            result[id] = BracketTeam(
                id: id,
                displayName: t.displayName,
                abbreviation: t.abbreviation,
                groupName: nil,
                team: t,
                fate: fate(forId: id)
            )
        }
        return result
    }

    // MARK: Team listings & status text

    /// All teams, alive first (then by how far eliminated), each alphabetical.
    var teamsForPicker: [BracketTeam] {
        teamsById.values.sorted { a, b in
            let ra = pickerRank(a.fate), rb = pickerRank(b.fate)
            if ra != rb { return ra < rb }
            return a.displayName.localizedCaseInsensitiveCompare(b.displayName) == .orderedAscending
        }
    }

    private func pickerRank(_ fate: TeamFate) -> Int {
        switch fate {
        case .champion:          return 0
        case .alive:             return 1
        // Eliminated knockout teams in the order they went out: Round of 32 first,
        // then Round of 16, Quarterfinals, Semifinals (rawValue 0…3).
        case .eliminated(let r): return 10 + r.rawValue
        case .runnerUp:          return 20   // lost the Final
        case .thirdPlace:        return 21
        case .fourthPlace:       return 22
        case .eliminatedInGroup: return 30   // never reached the knockouts → last
        }
    }

    /// Short status line for a team (used on the team's own path detail screen).
    func statusText(for fate: TeamFate) -> String {
        switch fate {
        case .alive(let next):      return "Still active — next: \(next.label)"
        case .champion:             return "World Cup champion 🏆"
        case .runnerUp:             return "Runner-up — lost in the Final"
        case .thirdPlace:           return "Third place"
        case .fourthPlace:          return "Fourth place"
        case .eliminated(let r):    return "Eliminated in the \(r.label)"
        case .eliminatedInGroup:    return "Eliminated in the group stage"
        }
    }

    /// Section heading a team belongs under in the picker. Teams are grouped by
    /// status so the heading conveys it once — rows don't repeat the status.
    func sectionTitle(for fate: TeamFate) -> String {
        switch fate {
        case .alive:             return "Still Active"
        case .champion:          return "Champion"
        case .runnerUp:          return "Runner-up (lost in the Final)"
        case .thirdPlace:        return "Third Place"
        case .fourthPlace:       return "Fourth Place"
        case .eliminated(let r): return "Eliminated in the \(r.label)"
        case .eliminatedInGroup: return "Eliminated in the Group Stage"
        }
    }

    /// Teams grouped into ordered sections by status (Still Active first, then
    /// eliminations from the deepest round back to the group stage).
    var teamSections: [(title: String, teams: [BracketTeam])] {
        var order: [String] = []
        var map: [String: [BracketTeam]] = [:]
        for t in teamsForPicker {   // already sorted: alive first, then by depth, alpha within
            let title = sectionTitle(for: t.fate)
            if map[title] == nil { order.append(title) }
            map[title, default: []].append(t)
        }
        return order.map { (title: $0, teams: map[$0] ?? []) }
    }
}
