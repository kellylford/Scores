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
        // The season travels through userInfo because each player's `stats` array
        // holds a projected set for the prior season as well as this one, and
        // the decoder has to know which it is looking for.
        let decoder = JSONDecoder()
        decoder.userInfo[.fantasySeason] = season
        let raw = try decoder.decode([RawFantasyPlayer].self, from: data)
        var mapped = raw.compactMap { Self.map($0) }
        Self.blankPlaceholderADP(&mapped)
        Self.assignBoardRanks(&mapped)
        return mapped.sorted { ($0.pprRank ?? Int.max) < ($1.pprRank ?? Int.max) }
    }

    // MARK: - Post-processing over the whole pool

    /// Clear the placeholder ADP ESPN gives players nobody is actually drafting.
    ///
    /// ESPN does not omit `averageDraftPosition` for undrafted players — it hands
    /// out a value just past the end of a real draft, jittered by a fraction. In
    /// the 2026 pool that is ~170, shared by 826 of 1,026 players, while genuine
    /// ADPs stop around 168. Left alone it reads as a real draft position, and
    /// because the jitter is in the third decimal it also defeats sorting: rows
    /// that all display "170.0" order by noise the user cannot see.
    ///
    /// The placeholder is found rather than hard-coded, since it tracks the size
    /// of the draft ESPN samples and would drift between seasons.
    static func blankPlaceholderADP(_ players: inout [CheatsheetPlayer]) {
        var counts: [Int: Int] = [:]
        for player in players {
            if let adp = player.adp, adp > 0 {
                counts[Int(adp.rounded()), default: 0] += 1
            }
        }
        var placeholder = 0
        var hits = 0
        for (value, count) in counts where count > hits {
            placeholder = value
            hits = count
        }
        // A real ADP is never shared by a large slice of the pool; a placeholder is.
        guard hits >= max(20, players.count / 20) else { return }
        let threshold = Double(placeholder - 1)
        for index in players.indices {
            if let adp = players[index].adp, adp >= threshold {
                players[index].adp = nil
            }
        }
    }

    /// Number the board densely from 1, keeping ESPN's ordering.
    ///
    /// ESPN's published rank orders a much larger pool than a fantasy board: it
    /// interleaves ~1,750 IDP players, 51 punters and the 32 "Team QB" slots that
    /// only a few league formats use. Shown raw it reads as a broken sequence —
    /// the 2026 board covers ranks 1 to 2565 with 1,539 holes, running 36 -> 69
    /// near the top and 519 -> 978 further down.
    static func assignBoardRanks(_ players: inout [CheatsheetPlayer]) {
        var pprOrder: [(index: Int, rank: Int)] = []
        var standardOrder: [(index: Int, rank: Int)] = []
        for index in players.indices {
            if let rank = players[index].pprRank { pprOrder.append((index, rank)) }
            if let rank = players[index].standardRank { standardOrder.append((index, rank)) }
        }
        pprOrder.sort { $0.rank < $1.rank }
        standardOrder.sort { $0.rank < $1.rank }
        for (position, entry) in pprOrder.enumerated() {
            players[entry.index].pprBoardRank = position + 1
        }
        for (position, entry) in standardOrder.enumerated() {
            players[entry.index].standardBoardRank = position + 1
        }
    }

    // MARK: - Mapping

    private static func map(_ raw: RawFantasyPlayer) -> CheatsheetPlayer? {
        guard let posId = raw.defaultPositionId,
              let position = FantasyPosition.from(positionId: posId) else { return nil }
        // ESPN keeps ranking players it has flagged inactive — retirees like
        // Matthew Slater. All of them are owned in 0.0% of leagues.
        if raw.active == false { return nil }

        let pprRank = raw.rank(for: "PPR")
        let stdRank = raw.rank(for: "STANDARD")
        // Whether ESPN publishes a rank at all is ESPN's own answer to "is this
        // player fantasy-relevant". There is deliberately no rank cutoff: ESPN's
        // overall rank does not order draft relevance — Ricky Pearsall sits at
        // 1507 and Tyreek Hill at 1899, both rostered in real leagues — so any
        // cap silently hides players people are drafting. The unranked remainder
        // of the feed is owned in 0.0% of leagues.
        guard [pprRank, stdRank].contains(where: { $0 != nil }) else { return nil }

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
            // Kickers and D/ST have no usable ESPN projection, so we don't score them.
            projectedPointsBase: (position == .k || position == .dst) ? nil : raw.projectedPointsBase,
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
    let active: Bool?
    let ownership: Ownership?
    let draftRanksByRankType: [String: DraftRank]?

    /// Non-reception projected points, scored from ESPN's raw projected stat
    /// line. (ESPN's own `appliedTotal` is corrupted for many players — kickers
    /// read ~23,000, some QBs/WRs 2–30× too high — so we never use it.)
    let projectedPointsBase: Double?
    /// Projected receptions (stat id "53"), valued per format by the caller.
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
        let scoringPeriodId: Int?
        let seasonId: Int?
        let stats: [String: Double]?
    }

    func rank(for type: String) -> Int? {
        guard let r = draftRanksByRankType?[type]?.rank, r > 0 else { return nil }
        return r
    }

    private enum CodingKeys: String, CodingKey {
        case id, fullName, defaultPositionId, proTeamId, injuryStatus, active, ownership, draftRanksByRankType, stats
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(Int.self, forKey: .id)
        fullName = try c.decodeIfPresent(String.self, forKey: .fullName)
        defaultPositionId = try c.decodeIfPresent(Int.self, forKey: .defaultPositionId)
        proTeamId = try c.decodeIfPresent(Int.self, forKey: .proTeamId)
        injuryStatus = try c.decodeIfPresent(String.self, forKey: .injuryStatus)
        active = try c.decodeIfPresent(Bool.self, forKey: .active)
        ownership = try c.decodeIfPresent(Ownership.self, forKey: .ownership)
        draftRanksByRankType = try c.decodeIfPresent([String: DraftRank].self, forKey: .draftRanksByRankType)

        // Score the projected SEASON stat line ourselves — the source-1 /
        // season-split / period-0 set with a non-empty stat dict. ESPN's own
        // `appliedTotal` is unreliable, so we compute from the raw stats.
        // The decoded array is local and released when init returns.
        //
        // The seasonId match is not optional. A player's `stats` array carries a
        // projected full-season set for BOTH the upcoming and the prior season,
        // in no stable order, so taking the first match reads last year's
        // projections for a slice of the pool.
        let season = decoder.userInfo[.fantasySeason] as? Int
        var base: Double?
        var rec: Double = 0
        if let sets = try? c.decodeIfPresent([StatSet].self, forKey: .stats) {
            for set in sets where set.statSourceId == 1
                && set.statSplitTypeId == 0
                && set.scoringPeriodId == 0
                && (season == nil || set.seasonId == season) {
                guard let st = set.stats, !st.isEmpty else { continue }
                func v(_ k: String) -> Double { st[k] ?? 0 }
                rec = v("53")                       // receptions
                base = v("3") * 0.04                // passing yards (1 pt / 25)
                     + v("4") * 4                   // passing TD
                     + v("19") * 2                  // two-point conversion passed
                     - v("20") * 2                  // interception thrown
                     + v("24") * 0.1                // rushing yards (1 pt / 10)
                     + v("25") * 6                  // rushing TD
                     + v("26") * 2                  // two-point conversion rushed
                     + v("42") * 0.1                // receiving yards (1 pt / 10)
                     + v("43") * 6                  // receiving TD
                     + v("44") * 2                  // two-point conversion caught
                     - v("72") * 2                  // fumbles lost
                break
            }
        }
        projectedPointsBase = base
        projectedReceptions = rec
    }
}

extension CodingUserInfoKey {
    /// The season the caller wants projections for. Carried through the decoder
    /// because each player's stat array holds more than one season's worth.
    static let fantasySeason = CodingUserInfoKey(rawValue: "fantasySeason")!
}
