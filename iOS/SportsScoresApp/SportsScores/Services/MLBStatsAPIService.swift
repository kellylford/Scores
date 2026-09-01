//
//  MLBStatsAPIService.swift
//  SportsScores
//
//  MLB's official Stats API, used for the one thing ESPN's standings feed cannot
//  answer: the wild card race.
//

import Foundation

/// Fetches the wild card standings from MLB's own API.
///
/// ESPN's standings feed carries no wild card grouping at all — it returns the
/// two leagues, which the app then sub-divides into divisions itself. Deriving a
/// wild card race from win percentage would get MLB's published tiebreakers
/// wrong, so this goes to the source: statsapi returns the official
/// `wildCardRank` and `wildCardGamesBack` directly.
///
/// Mirrors `CFLAPIService` — a non-ESPN source that produces the same app-level
/// model types, so the views do not care where the data came from.
final class MLBStatsAPIService {
    static let shared = MLBStatsAPIService()

    private let baseURL = "https://statsapi.mlb.com/api/v1"
    private let session: URLSession

    /// Number of wild card berths per league.
    private static let wildCardSpots = 3

    /// statsapi league ids, in the order the groups should appear.
    private static let leagues: [(id: Int, label: String)] = [
        (103, "AL Wild Card"),
        (104, "NL Wild Card"),
    ]

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)
    }

    // MARK: - Fetch

    /// The current wild card picture as two groups, "AL Wild Card" and
    /// "NL Wild Card".
    ///
    /// Each group is in display order: the three division leaders first (already
    /// holding a playoff spot), then the 12-team race in MLB's official rank
    /// order, the top three of which hold the wild card berths.
    func fetchWildCardStandings() async throws -> [StandingsGroup] {
        // `hydrate=team` is what upgrades the bare {id, name} team stub into full
        // names, abbreviations and division names — without it the rows read
        // "Orioles" rather than "Baltimore Orioles".
        let urlString = "\(baseURL)/standings"
            + "?leagueId=103,104&standingsTypes=wildCardWithLeaders&hydrate=team"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }

        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }

        let decoded = try JSONDecoder().decode(WildCardResponse.self, from: data)
        return Self.buildGroups(from: decoded)
    }

    // MARK: - Mapping

    private static func buildGroups(from response: WildCardResponse) -> [StandingsGroup] {
        var leaders: [Int: [StandingsEntry]] = [:]
        var race: [Int: [(rank: Int, entry: StandingsEntry)]] = [:]

        for record in response.records {
            guard let leagueID = record.league?.id else { continue }
            for teamRecord in record.teamRecords {
                switch record.standingsType {
                case "divisionLeaders":
                    let division = shortDivisionName(teamRecord.team.division?.name)
                    leaders[leagueID, default: []].append(entry(
                        from: teamRecord,
                        position: "-",
                        status: division.isEmpty ? "Division leader" : "\(division) leader",
                        gamesBack: "-"
                    ))
                case "wildCard":
                    let rank = Int(teamRecord.wildCardRank ?? "") ?? 0
                    let status = (rank > 0 && rank <= wildCardSpots) ? "Wild card \(rank)" : ""
                    race[leagueID, default: []].append((rank, entry(
                        from: teamRecord,
                        position: rank > 0 ? "\(rank)" : "-",
                        status: status,
                        gamesBack: teamRecord.wildCardGamesBack ?? "-"
                    )))
                default:
                    continue
                }
            }
        }

        return leagues.compactMap { league in
            // Division leaders sort by record; the race keeps MLB's official rank.
            let orderedLeaders = (leaders[league.id] ?? [])
                .sorted { $0.stats.winPercent > $1.stats.winPercent }
            let orderedRace = (race[league.id] ?? [])
                .sorted { $0.rank < $1.rank }
                .map(\.entry)
            let entries = orderedLeaders + orderedRace
            guard !entries.isEmpty else { return nil }
            return StandingsGroup(name: league.label, entries: entries)
        }
    }

    private static func entry(from record: WildCardResponse.Record.TeamRecord,
                              position: String,
                              status: String,
                              gamesBack: String) -> StandingsEntry {
        let wins = record.leagueRecord.wins
        let losses = record.leagueRecord.losses
        let team = record.team

        return StandingsEntry(
            rank: Int(position) ?? 0,
            team: StandingsEntry.TeamInfo(
                id: "\(team.id)",
                name: team.teamName ?? team.name,
                abbreviation: team.abbreviation ?? "",
                displayName: team.name,
                logo: nil
            ),
            stats: StandingsEntry.StandingsStats(
                wins: wins,
                losses: losses,
                winPercent: Double(record.leagueRecord.pct) ?? 0,
                gamesBack: gamesBack,
                streak: record.streak?.streakCode ?? "-",
                record: "\(wins)-\(losses)",
                pointsFor: nil, pointsAgainst: nil,
                ties: nil, otLosses: nil, nhlPoints: nil,
                avgPointsFor: nil, avgPointsAgainst: nil,
                homeRecord: nil, roadRecord: nil, lastTenRecord: nil,
                divisionRecord: nil, playoffSeed: nil, differential: nil
            ),
            wildCard: WildCardStanding(position: position, status: status, gamesBack: gamesBack)
        )
    }

    /// "American League East" -> "AL East", matching the division group names.
    private static func shortDivisionName(_ fullName: String?) -> String {
        (fullName ?? "")
            .replacingOccurrences(of: "American League", with: "AL")
            .replacingOccurrences(of: "National League", with: "NL")
    }

    // MARK: - API response

    private struct WildCardResponse: Decodable {
        let records: [Record]

        struct Record: Decodable {
            let standingsType: String?
            let league: LeagueRef?
            let teamRecords: [TeamRecord]

            struct LeagueRef: Decodable { let id: Int }

            struct TeamRecord: Decodable {
                let team: Team
                let leagueRecord: LeagueRecord
                let streak: Streak?
                let wildCardRank: String?
                let wildCardGamesBack: String?

                struct Team: Decodable {
                    let id: Int
                    /// Full name once `hydrate=team` is applied, e.g. "New York Yankees".
                    let name: String
                    /// Club name only, e.g. "Yankees".
                    let teamName: String?
                    let abbreviation: String?
                    let division: Division?

                    struct Division: Decodable { let name: String? }
                }

                struct LeagueRecord: Decodable {
                    let wins: Int
                    let losses: Int
                    let pct: String
                }

                struct Streak: Decodable { let streakCode: String? }
            }
        }
    }
}
