//
//  TeamStatsStore.swift
//  SportsScores
//
//  Caches ESPN's league team-statistics payload and the stat glossary derived
//  from it.
//
//  This is an actor rather than a plain dictionary on ESPNAPIService because
//  every visible stat heading asks for its definition as it appears — a
//  screenful of sections hits this from many tasks at once, and unsynchronised
//  dictionary writes corrupt memory rather than merely losing a cache entry.
//  Concurrent callers for the same sport also share one download instead of
//  starting a request each.
//

import Foundation

actor TeamStatsStore {
    private let session: URLSession
    /// ESPN web API root, e.g. "https://site.web.api.espn.com/apis/common/v3/sports"
    private let baseURL: String
    private let ttl: TimeInterval = 15 * 60

    private struct CachedPayload {
        let response: TeamStatsByTeamResponse
        let fetchedAt: Date
    }

    private var payloads: [Sport: CachedPayload] = [:]
    private var payloadTasks: [Sport: Task<TeamStatsByTeamResponse, Error>] = [:]
    private var glossaries: [Sport: [String: String]] = [:]
    private var glossaryTasks: [Sport: Task<[String: String], Never>] = [:]

    init(session: URLSession, baseURL: String) {
        self.session = session
        self.baseURL = baseURL
    }

    // MARK: - Full payload

    /// Every team's full stat line for the sport's current season.
    ///
    /// No season parameters are sent — ESPN resolves the most recent season that
    /// has data, which is what we want in the offseason (asking for a season
    /// that hasn't started returns an empty document).
    func payload(for sport: Sport) async throws -> TeamStatsByTeamResponse {
        if let cached = payloads[sport], Date().timeIntervalSince(cached.fetchedAt) < ttl {
            return cached.response
        }
        if let inFlight = payloadTasks[sport] {
            return try await inFlight.value
        }

        // College leagues need a high limit: ESPN's list runs to several hundred
        // teams (including non-Division-I opponents), and it is not ordered by
        // rank, so a small limit would silently drop the actual leaders.
        let limit = sport.isCollegeSport ? 500 : 50
        let task = Task<TeamStatsByTeamResponse, Error> { [session, baseURL] in
            try await Self.fetch(sport: sport, limit: limit, session: session, baseURL: baseURL)
        }
        payloadTasks[sport] = task
        defer { payloadTasks[sport] = nil }

        let decoded = try await task.value
        payloads[sport] = CachedPayload(response: decoded, fetchedAt: Date())
        return decoded
    }

    // MARK: - Stat glossary

    /// Stat key → ESPN's plain-English definition. Kept for the session;
    /// glossary text does not change mid-season.
    func glossary(for sport: Sport) async -> [String: String] {
        if let cached = glossaries[sport] { return cached }
        if let inFlight = glossaryTasks[sport] { return await inFlight.value }

        // Reuse the full payload when it is already in hand; otherwise ask for a
        // single team. The glossary lives in the payload's top-level category
        // metadata, so one team's worth of data (~3 KB) carries every definition
        // instead of the whole league (350 KB for college basketball).
        let cachedResponse = payloads[sport].map(\.response)
        let task = Task<[String: String], Never> { [session, baseURL] in
            let categories: [TeamStatsByTeamResponse.CategoryMetadata]
            if let cachedResponse {
                categories = cachedResponse.categories ?? []
            } else {
                let light = try? await Self.fetch(sport: sport, limit: 1, session: session, baseURL: baseURL)
                categories = light?.categories ?? []
            }

            var definitions: [String: String] = [:]
            for category in categories {
                guard let names = category.names, let descriptions = category.descriptions else { continue }
                for (index, name) in names.enumerated() {
                    guard let text = descriptions[safe: index], !text.isEmpty,
                          definitions[name] == nil else { continue }
                    definitions[name] = text
                }
            }
            return definitions
        }
        glossaryTasks[sport] = task

        let definitions = await task.value
        glossaryTasks[sport] = nil
        // Don't cache a failed lookup — a definition missed while offline should
        // be retried, not remembered as "this sport has none".
        if !definitions.isEmpty { glossaries[sport] = definitions }
        return definitions
    }

    // MARK: - Networking

    private static func fetch(
        sport: Sport,
        limit: Int,
        session: URLSession,
        baseURL: String
    ) async throws -> TeamStatsByTeamResponse {
        let urlString = "\(baseURL)/\(sport.apiPath)/statistics/byteam?region=us&lang=en&limit=\(limit)"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }

        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        return try JSONDecoder().decode(TeamStatsByTeamResponse.self, from: data)
    }
}
