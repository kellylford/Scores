//
//  Standings.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

struct StandingsGroup: Identifiable {
    let id = UUID()
    let name: String
    let entries: [StandingsEntry]
}

/// A team's place in the wild card picture.
///
/// `nil` on ordinary division standings. The playoff cut line lives in `status`
/// rather than being drawn, so VoiceOver speaks who is in.
struct WildCardStanding {
    /// "-" for a division leader, otherwise MLB's official wild card rank.
    let position: String
    /// "AL East leader", "Wild card 1", or "" for teams outside the spots.
    let status: String
    /// Games back of the last wild card spot ("+8.5", "-", "0.5").
    let gamesBack: String

    /// Status as words. A bare "-" is not spoken at all at the default
    /// punctuation level in either VoiceOver or NVDA, so a team outside the
    /// spots would read as silence — indistinguishable from a cell that failed
    /// to populate. Every surface uses this rather than a dash.
    var spokenStatus: String {
        status.isEmpty ? "Not in a playoff spot" : status
    }

    /// Position as words, for the same reason: leaders carry "-", not a number.
    var positionText: String {
        position == "-" ? "Division leader" : position
    }
}

struct StandingsEntry: Identifiable {
    let id = UUID()
    let rank: Int
    let team: TeamInfo
    var stats: StandingsStats
    /// Set only on wild card standings; nil for division/conference groups.
    var wildCard: WildCardStanding? = nil
    
    struct TeamInfo {
        let id: String
        let name: String
        let abbreviation: String
        let displayName: String
        let logo: String?

        var cityName: String {
            guard displayName.hasSuffix(name) else { return displayName }
            let city = String(displayName.dropLast(name.count)).trimmingCharacters(in: .whitespaces)
            return city.isEmpty ? displayName : city
        }

        func voiceOverName(for preference: TeamNamePreference) -> String {
            switch preference {
            case .full:         return displayName
            case .mascot:       return name
            case .city:         return cityName
            case .abbreviation: return abbreviation
            }
        }
    }
    
    struct StandingsStats {
        let wins: Int
        let losses: Int
        let winPercent: Double
        let gamesBack: String
        let streak: String
        let record: String
        // Raw scoring totals (MLB=runs, NFL/NBA/NHL=points/goals)
        let pointsFor: Int?
        let pointsAgainst: Int?
        // Extended: present for some sports only
        let ties: Int?          // NFL
        let otLosses: Int?      // NHL
        let nhlPoints: Int?     // NHL standings points
        let avgPointsFor: Double?    // NBA PPG
        let avgPointsAgainst: Double? // NBA opp PPG
        let homeRecord: String?
        let roadRecord: String?
        let lastTenRecord: String?
        let divisionRecord: String?
        let playoffSeed: Int?
        let differential: String?   // formatted e.g. "+61", "-7"

        var displayWinPercent: String {
            let formatted = String(format: "%.3f", winPercent)
            return formatted.hasPrefix("0") ? String(formatted.dropFirst()) : formatted
        }
    }
    
    // For table view display
    var tableRow: [String] {
        [
            "\(rank)",
            team.abbreviation,
            "\(stats.wins)",
            "\(stats.losses)",
            stats.displayWinPercent,
            stats.gamesBack,
            stats.streak,
            stats.record
        ]
    }
    
    // For quick list display
    var quickListText: String {
        if let wc = wildCard {
            // Leaders have no rank, so lead with the team rather than a bare "-".
            let lead = wc.position == "-" ? "" : "\(wc.position). "
            return "\(lead)\(team.abbreviation), \(stats.wins)-\(stats.losses), "
                + "\(stats.displayWinPercent), WCGB: \(wc.gamesBack), \(stats.streak), "
                + "\(wc.spokenStatus)"
        }
        var text = "\(team.abbreviation), \(stats.wins)-\(stats.losses), \(stats.displayWinPercent), GB: \(stats.gamesBack)"
        if let l10 = stats.lastTenRecord { text += ", L10: \(l10)" }
        return text
    }

    // For full list display
    var fullListText: String {
        if let wc = wildCard {
            return "Position: \(wc.positionText); Team: \(team.displayName); Wins: \(stats.wins); "
                + "Losses: \(stats.losses); Win%: \(stats.displayWinPercent); "
                + "Wild card games back: \(wc.gamesBack); Streak: \(stats.streak); "
                + "Record: \(stats.record); Status: \(wc.spokenStatus)"
        }
        var text = "Rank: \(rank); Team: \(team.displayName); Wins: \(stats.wins); Losses: \(stats.losses); Win%: \(stats.displayWinPercent); Games Back: \(stats.gamesBack); Streak: \(stats.streak); Record: \(stats.record)"
        if let l10 = stats.lastTenRecord { text += "; Last 10: \(l10)" }
        return text
    }
}

// MARK: - Shared entry-building helper
extension StandingsEntry {
    /// Build a StandingsEntry from a raw API entry, populating all extended fields.
    init(fromAPIEntry apiEntry: APIStandingsGroup.APIStandings.APIStandingsEntry) {
        typealias AS = APIStandingsGroup.APIStandings.APIStandingsEntry.APIStat
        func stat(_ name: String) -> AS? {
            apiEntry.stats.first(where: { $0.name == name })
        }
        let t = apiEntry.team
        self.wildCard = nil
        self.rank = Int(stat("rank")?.value ?? 0)
        self.team = TeamInfo(
            id: t.id, name: t.name, abbreviation: t.abbreviation,
            displayName: t.displayName, logo: t.logos?.first?.href
        )
        self.stats = StandingsStats(
            wins:          Int(stat("wins")?.value ?? 0),
            losses:        Int(stat("losses")?.value ?? 0),
            winPercent:    stat("winPercent")?.value ?? 0,
            gamesBack:     stat("divisionGamesBehind")?.displayValue ?? stat("gamesBehind")?.displayValue ?? "-",
            streak:        stat("streak")?.displayValue ?? "-",
            record:        stat("overall")?.displayValue ?? "-",
            pointsFor:     stat("pointsFor").map { Int($0.value) },
            pointsAgainst: stat("pointsAgainst").map { Int($0.value) },
            ties:          stat("ties").map { Int($0.value) },
            otLosses:      stat("otLosses").map { Int($0.value) }
                            ?? stat("OTLosses").map { Int($0.value) },
            nhlPoints:     stat("points").map { Int($0.value) },
            avgPointsFor:  stat("avgPointsFor")?.value,
            avgPointsAgainst: stat("avgPointsAgainst")?.value,
            homeRecord:    stat("Home")?.displayValue,
            roadRecord:    stat("Road")?.displayValue,
            lastTenRecord: stat("Last Ten Games")?.displayValue,
            divisionRecord: stat("vs. Div.")?.displayValue ?? stat("divisionRecord")?.displayValue,
            playoffSeed:   stat("playoffSeed").map { Int($0.value) },
            differential:  stat("differential")?.displayValue
        )
    }
}

// MARK: - API Response Models
extension StandingsGroup {
    init(from apiResponse: APIStandingsGroup) throws {
        self.name = apiResponse.name
        self.entries = apiResponse.standings.entries.map { StandingsEntry(fromAPIEntry: $0) }
    }
}

struct APIStandingsGroup: Codable {
    let name: String
    let standings: APIStandings
    
    struct APIStandings: Codable {
        let entries: [APIStandingsEntry]
        
        struct APIStandingsEntry: Codable {
            let team: APITeam
            let stats: [APIStat]
            
            struct APITeam: Codable {
                let id: String
                let name: String
                let abbreviation: String
                let displayName: String
                let logos: [APILogo]?
                
                struct APILogo: Codable {
                    let href: String
                }
            }
            
            struct APIStat: Codable {
                let name: String
                let displayName: String?   // absent on some ESPN stats (e.g. "overall")
                let value: Double          // defaulted to 0 when ESPN omits the field
                let displayValue: String

                // Custom decoder: ESPN omits `value` on record-string stats like
                // "overall" (W-L), "Home", "Road", "vs. Div.", etc.  Without
                // this, a single missing `value` causes the *entire* standings
                // response to fail with a DecodingError.
                init(from decoder: Decoder) throws {
                    let c = try decoder.container(keyedBy: CodingKeys.self)
                    self.name         = try  c.decode(String.self,         forKey: .name)
                    self.displayName  = try  c.decodeIfPresent(String.self, forKey: .displayName)
                    self.value        = (try? c.decodeIfPresent(Double.self, forKey: .value)) ?? 0
                    self.displayValue = try  c.decode(String.self,         forKey: .displayValue)
                }

                enum CodingKeys: String, CodingKey {
                    case name, displayName, value, displayValue
                }
            }
        }
    }
}

struct APIStandingsResponse: Codable {
    let children: [APIStandingsGroup]
}
