//
//  FantasyCheatsheetService.swift
//  SportsScores
//
//  Loads the fantasy draft board from ESPN's fantasy player universe:
//    lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/players
//      ?view=kona_player_info
//
//  Unlike the public site/core ESPN APIs (raw stats only), this feed carries the
//  draft data the cheatsheet needs: ADP, auction values, PPR/Standard consensus
//  ranks, and season projections — all in ONE response.
//
//  Quirks handled here:
//   • The `X-Fantasy-Filter` header must be PRESENT to get the full pool, but
//     ESPN ignores its `limit`/`sort` fields — so we always receive every player
//     (~11.5k) and filter + sort client-side.
//   • The payload is large (~38 MB decompressed). We decode with a custom
//     initializer that pulls only the projected-points scalars out of each
//     player's `stats` array and immediately discards the heavy stat dictionaries,
//     keeping peak memory low. Decoding runs off the main actor.
//

import Foundation

final class FantasyCheatsheetService {
    static let shared = FantasyCheatsheetService()

    private let base = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons"
    /// Only players ranked at or above this position are kept — a generous
    /// draftable pool (covers deep leagues) while discarding ~10k irrelevant ids.
    private let maxRank = 500

    private let session: URLSession

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 60
        config.timeoutIntervalForResource = 180
        self.session = URLSession(configuration: config)
    }

    // MARK: - Season resolution

    /// The season whose draft data to load. ESPN publishes the upcoming season's
    /// ADP/auction/ranks in late winter/spring; once a season completes those
    /// pre-draft values are scrubbed. We target the current calendar year and
    /// rely on the empty-feed fallback in `fetchCheatsheet` for the deep offseason.
    func upcomingSeason() -> Int {
        Calendar.current.component(.year, from: Date())
    }

    // MARK: - Public load

    /// Loads and returns the draft board (players + D/ST) sorted by ESPN's PPR
    /// rank. If the requested season carries almost no draft data (deep offseason
    /// before ESPN publishes), retries the prior season.
    func fetchCheatsheet(season: Int) async throws -> [CheatsheetPlayer] {
        let rows = try await load(season: season)
        if rows.count < 50 {
            // Feed not populated for this season yet — fall back a year.
            let fallback = try await load(season: season - 1)
            if fallback.count > rows.count { return fallback }
        }
        return rows
    }

    private func load(season: Int) async throws -> [CheatsheetPlayer] {
        let urlString = "\(base)/\(season)/players?view=kona_player_info&scoringPeriodId=0"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }

        var request = URLRequest(url: url)
        // Header must be present to receive the full player pool. The filter body
        // itself is ignored by ESPN, so a minimal value is fine.
        request.setValue(#"{"players":{"limit":12000}}"#, forHTTPHeaderField: "X-Fantasy-Filter")

        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }

        // Decode + map off the main actor (this call is already non-isolated).
        let raw = try JSONDecoder().decode([RawFantasyPlayer].self, from: data)
        let mapped = raw.compactMap { Self.map($0, maxRank: maxRank) }
        return mapped.sorted { ($0.pprRank ?? Int.max) < ($1.pprRank ?? Int.max) }
    }

    // MARK: - Mapping

    private static func map(_ raw: RawFantasyPlayer, maxRank: Int) -> CheatsheetPlayer? {
        guard let posId = raw.defaultPositionId,
              let position = FantasyPosition.from(positionId: posId) else { return nil }

        let pprRank = raw.rank(for: "PPR")
        let stdRank = raw.rank(for: "STANDARD")
        // Keep only players inside the draftable pool.
        guard let best = [pprRank, stdRank].compactMap({ $0 }).min(), best <= maxRank else {
            return nil
        }

        let proTeamId = raw.proTeamId ?? 0
        let isDST = position == .dst
        let id = isDST ? "dst-\(proTeamId)" : String(raw.id)
        let headshot = isDST ? nil
            : URL(string: "https://a.espncdn.com/i/headshots/nfl/players/full/\(raw.id).png")

        return CheatsheetPlayer(
            id: id,
            fullName: raw.fullName ?? "Unknown",
            position: position,
            proTeamId: proTeamId,
            teamAbbreviation: NFLProTeams.abbreviation(for: proTeamId),
            injuryStatus: normalizedInjury(raw.injuryStatus),
            adp: raw.ownership?.averageDraftPosition,
            auctionValue: raw.ownership?.auctionValueAverage,
            pprRank: pprRank,
            standardRank: stdRank,
            pprProjectedPoints: raw.pprProjectedPoints,
            projectedReceptions: raw.projectedReceptions,
            headshotURL: headshot
        )
    }

    /// ESPN reports healthy players as "ACTIVE"; surface only real designations.
    private static func normalizedInjury(_ raw: String?) -> String? {
        guard let raw, !raw.isEmpty, raw.uppercased() != "ACTIVE" else { return nil }
        // Convert "INJURY_RESERVE" → "Injury Reserve", "DAY_TO_DAY" → "Day To Day".
        return raw.split(separator: "_")
            .map { $0.prefix(1).uppercased() + $0.dropFirst().lowercased() }
            .joined(separator: " ")
    }
}

// MARK: - Raw decode DTOs

/// Minimal decodable mirror of a fantasy-feed player. The custom initializer
/// extracts the projected-points scalars from `stats` and discards the heavy
/// per-player stat dictionaries so they are never retained in bulk.
private struct RawFantasyPlayer: Decodable {
    let id: Int
    let fullName: String?
    let defaultPositionId: Int?
    let proTeamId: Int?
    let injuryStatus: String?
    let ownership: Ownership?
    let draftRanksByRankType: [String: DraftRank]?

    /// ESPN's projected season points under PPR scoring (its `appliedTotal`).
    let pprProjectedPoints: Double?
    /// Projected receptions (stat id "53"), used to derive Half/Standard points.
    let projectedReceptions: Double

    struct Ownership: Decodable {
        let averageDraftPosition: Double?
        let auctionValueAverage: Double?
    }
    struct DraftRank: Decodable {
        let rank: Int?
    }
    private struct StatSet: Decodable {
        let statSourceId: Int?
        let statSplitTypeId: Int?
        let appliedTotal: Double?
        let stats: [String: Double]?
    }

    func rank(for type: String) -> Int? {
        guard let r = draftRanksByRankType?[type]?.rank, r > 0 else { return nil }
        return r
    }

    private enum CodingKeys: String, CodingKey {
        case id, fullName, defaultPositionId, proTeamId, injuryStatus, ownership, draftRanksByRankType, stats
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(Int.self, forKey: .id)
        fullName = try c.decodeIfPresent(String.self, forKey: .fullName)
        defaultPositionId = try c.decodeIfPresent(Int.self, forKey: .defaultPositionId)
        proTeamId = try c.decodeIfPresent(Int.self, forKey: .proTeamId)
        injuryStatus = try c.decodeIfPresent(String.self, forKey: .injuryStatus)
        ownership = try c.decodeIfPresent(Ownership.self, forKey: .ownership)
        draftRanksByRankType = try c.decodeIfPresent([String: DraftRank].self, forKey: .draftRanksByRankType)

        // Pull projected points + receptions from the projected season stat set
        // (statSourceId 1, statSplitTypeId 0). The decoded array is a local and
        // is released as soon as this initializer returns.
        var proj: Double?
        var rec: Double = 0
        if let sets = try? c.decodeIfPresent([StatSet].self, forKey: .stats) {
            for set in sets where set.statSourceId == 1 && set.statSplitTypeId == 0 {
                if proj == nil, let total = set.appliedTotal { proj = total }
                if let r = set.stats?["53"], r > 0 { rec = r }
            }
        }
        pprProjectedPoints = proj
        projectedReceptions = rec
    }
}
