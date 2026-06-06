//
//  WorldCup.swift
//  SportsScores
//
//  Domain models and API response models for the FIFA World Cup hub.
//  Covers both the men's (2026) and women's (2027) tournaments.
//

import Foundation

// MARK: - Domain Models

struct WorldCupGroup: Identifiable {
    let id: String
    let name: String
    let entries: [WorldCupGroupEntry]
}

struct WorldCupGroupEntry: Identifiable {
    let id: String
    let teamAbbreviation: String
    let teamDisplayName: String
    let rank: Int
    let gamesPlayed: Int
    let wins: Int
    let draws: Int
    let losses: Int
    let goalsFor: Int
    let goalsAgainst: Int
    let goalDifference: Int
    let points: Int
    let advancementNote: String?

    var goalDifferenceFormatted: String {
        goalDifference > 0 ? "+\(goalDifference)" : "\(goalDifference)"
    }

    var record: String { "\(wins)-\(draws)-\(losses)" }

    // MARK: Three view mode text

    var tableRow: [String] {
        [teamAbbreviation, "\(gamesPlayed)", "\(wins)", "\(draws)", "\(losses)",
         goalDifferenceFormatted, "\(points)"]
    }

    var quickListText: String {
        "\(teamAbbreviation), \(record), \(points) pts"
    }

    var fullListText: String {
        "GP: \(gamesPlayed), W: \(wins), D: \(draws), L: \(losses), GF: \(goalsFor), GA: \(goalsAgainst), GD: \(goalDifferenceFormatted), Pts: \(points)"
    }

    func accessibilityLabel() -> String {
        var parts: [String] = [
            teamDisplayName,
            "\(ordinal(rank)) in group",
            "\(points) \(points == 1 ? "point" : "points")",
            "\(wins) \(wins == 1 ? "win" : "wins")",
            "\(draws) \(draws == 1 ? "draw" : "draws")",
            "\(losses) \(losses == 1 ? "loss" : "losses")",
            "goal difference \(goalDifferenceFormatted)",
        ]
        if let note = advancementNote { parts.append(note) }
        return parts.joined(separator: ", ")
    }

    private func ordinal(_ n: Int) -> String {
        switch n % 10 {
        case 1 where n % 100 != 11: return "\(n)st"
        case 2 where n % 100 != 12: return "\(n)nd"
        case 3 where n % 100 != 13: return "\(n)rd"
        default:                     return "\(n)th"
        }
    }
}

// MARK: - Tournament Phases

struct WorldCupPhase: Identifiable {
    let id: String
    let label: String
    let startDate: Date
    let endDate: Date

    var isActive: Bool {
        let now = Date()
        return now >= startDate && now <= endDate
    }
    var isPast: Bool { Date() > endDate }
}

extension WorldCupPhase {
    static let wc2026: [WorldCupPhase] = build(year: 2026, entries: [
        ("1", "Group Stage",     6, 11, 6, 27),
        ("2", "Round of 32",     6, 28, 7,  3),
        ("3", "Round of 16",     7,  4, 7,  7),
        ("4", "Quarterfinals",   7,  9, 7, 11),
        ("5", "Semifinals",      7, 14, 7, 15),
        ("6", "3rd-Place Match", 7, 18, 7, 18),
        ("7", "Final",           7, 19, 7, 19),
    ])

    // 2027 Women's World Cup in Brazil — dates TBC; placeholders only.
    static let wwc2027: [WorldCupPhase] = build(year: 2027, entries: [
        ("1", "Group Stage",     7,  1, 7, 20),
        ("2", "Round of 16",     7, 21, 7, 24),
        ("3", "Quarterfinals",   7, 26, 7, 29),
        ("4", "Semifinals",      8,  1, 8,  2),
        ("5", "3rd-Place Match", 8,  5, 8,  5),
        ("6", "Final",           8,  6, 8,  6),
    ])

    private static func build(
        year: Int,
        entries: [(String, String, Int, Int, Int, Int)]
    ) -> [WorldCupPhase] {
        entries.map { id, label, sm, sd, em, ed in
            WorldCupPhase(
                id: id, label: label,
                startDate: utcDate(year: year, month: sm, day: sd),
                endDate:   utcDate(year: year, month: em, day: ed)
            )
        }
    }

    private static func utcDate(year: Int, month: Int, day: Int) -> Date {
        var c = DateComponents()
        c.year = year; c.month = month; c.day = day; c.hour = 4; c.minute = 0
        return Calendar(identifier: .gregorian).date(from: c) ?? Date()
    }
}

// MARK: - API Response Models

struct WorldCupStandingsResponse: Codable {
    let children: [APIGroup]

    struct APIGroup: Codable {
        let id: String
        let name: String
        let standings: APIStandings

        struct APIStandings: Codable {
            let entries: [APIEntry]

            struct APIEntry: Codable {
                let team: APITeam
                let note: APINote?
                let stats: [APIStat]

                struct APITeam: Codable {
                    let id: String
                    let abbreviation: String
                    let displayName: String
                }

                struct APINote: Codable {
                    let color: String?
                    let description: String?
                    let rank: Int?
                }

                struct APIStat: Codable {
                    let name: String
                    let value: Double
                    let displayValue: String

                    init(from decoder: Decoder) throws {
                        let c = try decoder.container(keyedBy: CodingKeys.self)
                        name         = try  c.decode(String.self, forKey: .name)
                        value        = (try? c.decodeIfPresent(Double.self, forKey: .value)) ?? 0
                        displayValue = try  c.decode(String.self, forKey: .displayValue)
                    }

                    enum CodingKeys: String, CodingKey { case name, value, displayValue }
                }
            }
        }
    }
}

// MARK: - API → Domain conversion

extension WorldCupGroup {
    init(from apiGroup: WorldCupStandingsResponse.APIGroup) {
        id   = apiGroup.id
        name = apiGroup.name
        entries = apiGroup.standings.entries.enumerated()
            .map { idx, entry in WorldCupGroupEntry(from: entry, rank: idx + 1) }
            .sorted { $0.rank < $1.rank }
    }
}

extension WorldCupGroupEntry {
    init(from e: WorldCupStandingsResponse.APIGroup.APIStandings.APIEntry, rank: Int) {
        func v(_ name: String) -> Int {
            Int(e.stats.first(where: { $0.name == name })?.value ?? 0)
        }
        let gd = v("pointDifferential")
        id                   = e.team.id
        teamAbbreviation     = e.team.abbreviation
        teamDisplayName      = e.team.displayName
        self.rank            = Int(e.stats.first(where: { $0.name == "rank" })?.value ?? Double(rank))
        gamesPlayed          = v("gamesPlayed")
        wins                 = v("wins")
        draws                = v("ties")
        losses               = v("losses")
        goalsFor             = v("pointsFor")
        goalsAgainst         = v("pointsAgainst")
        goalDifference       = gd
        points               = v("points")
        advancementNote      = e.note?.description
    }
}
