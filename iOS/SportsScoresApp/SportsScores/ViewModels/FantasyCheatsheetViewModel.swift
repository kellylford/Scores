//
//  FantasyCheatsheetViewModel.swift
//  SportsScores
//
//  Owns the cheatsheet state: player pool (offense), team defenses (D/ST),
//  draft-taken set, scoring settings, sort/filter, and the load pipeline.
//
//  Load pipeline (optimized for the ~32-call roster limit):
//    1. Fetch all 32 NFL teams (1 call)
//    2. Fetch each team's roster (32 parallel calls) → player pool (identity+position)
//    3. Fetch league leaders (1 call) → resolve athlete ids with real stats
//    4. For leaders found, fetch per-athlete stat splits in parallel (top-N only)
//    5. Build D/ST rows from team list (stats enriched lazily on demand)
//
//  Only the top-N (leaders) players get full stat splits up front; the rest of
//  the pool is still browsable/searchable by name+position+team and shows
//  "—" for points until enriched. This keeps the initial load to ~35 calls
//  instead of ~1,700 per-athlete calls.
//

import Foundation
import Combine

@MainActor
final class FantasyCheatsheetViewModel: ObservableObject {

    // MARK: - Published state

    @Published var offensivePlayers: [CheatsheetPlayer] = []
    @Published var teamDefenses: [CheatsheetTeamDefense] = []
    @Published var isLoading = false
    @Published var isEnriching = false
    @Published var errorMessage: String?

    @Published var scoringSettings: FantasyScoringSettings {
        didSet { persistScoringSettings(); recomputeAllPoints() }
    }
    @Published var draftState: DraftState {
        didSet { persistDraftState() }
    }
    @Published var selectedSort: CheatsheetSort = .fantasyPoints
    @Published var selectedPositions: Set<FantasyPosition> = Set(FantasyPosition.allCases)
    @Published var searchQuery: String = ""
    @Published var hideTaken: Bool = false
    @Published var statsSeason: Int

    // MARK: - Private

    private let service = FantasyCheatsheetService.shared
    private let scoringKey = "fantasyScoringSettings"
    private let draftStateKey = "fantasyDraftTaken"

    // MARK: - Init

    init() {
        // Restore persisted scoring settings
        if let data = UserDefaults.standard.data(forKey: "fantasyScoringSettings"),
           let saved = try? JSONDecoder().decode(FantasyScoringSettings.self, from: data) {
            self.scoringSettings = saved
        } else {
            self.scoringSettings = .standard
        }

        // Restore persisted draft state
        if let data = UserDefaults.standard.data(forKey: "fantasyDraftTaken"),
           let saved = try? JSONDecoder().decode(DraftState.self, from: data) {
            self.draftState = saved
        } else {
            self.draftState = DraftState()
        }

        self.statsSeason = service.statsSeason()
    }

    // MARK: - Computed filtered + sorted output

    /// The combined, filtered, sorted list the view renders.
    var displayedRows: [CheatsheetRow] {
        var rows: [CheatsheetRow] = []

        // Offensive players
        for var p in offensivePlayers {
            p.computedPoints = points(for: p)
            if matchesFilters(player: p) {
                rows.append(.player(p))
            }
        }

        // Team defenses
        if selectedPositions.contains(.dst) {
            for var d in teamDefenses {
                d.computedPoints = points(for: d)
                if matchesFilters(defense: d) {
                    rows.append(.defense(d))
                }
            }
        }

        return rows.sorted(by: sortComparator)
    }

    /// Total player count (offense + defense), pre-filter.
    var totalPlayerCount: Int { offensivePlayers.count + teamDefenses.count }

    /// Count of players currently displayed after filtering.
    var displayedCount: Int { displayedRows.count }

    // MARK: - Points computation

    func points(for player: CheatsheetPlayer) -> Double {
        FantasyPointsEngine.points(for: player, settings: scoringSettings)
    }

    func points(for defense: CheatsheetTeamDefense) -> Double {
        FantasyPointsEngine.points(for: defense, settings: scoringSettings)
    }

    /// Recomputes cached points for all rows. Called when settings change.
    private func recomputeAllPoints() {
        // Points are computed on-demand in `displayedRows`; this just forces
        // a published refresh by mutating the arrays in place.
        offensivePlayers = offensivePlayers.map { var p = $0; p.computedPoints = nil; return p }
        teamDefenses = teamDefenses.map { var d = $0; d.computedPoints = nil; return d }
    }

    // MARK: - Filtering helpers

    private func matchesFilters(player: CheatsheetPlayer) -> Bool {
        if !selectedPositions.contains(player.position) { return false }
        if hideTaken && draftState.isTaken(player.id) { return false }
        if !searchQuery.isEmpty {
            let q = searchQuery.lowercased()
            if !player.fullName.lowercased().contains(q)
                && !player.teamAbbreviation.lowercased().contains(q) {
                return false
            }
        }
        return true
    }

    private func matchesFilters(defense: CheatsheetTeamDefense) -> Bool {
        if hideTaken && draftState.isTaken(defense.id) { return false }
        if !searchQuery.isEmpty {
            let q = searchQuery.lowercased()
            if !defense.teamDisplayName.lowercased().contains(q)
                && !defense.teamAbbreviation.lowercased().contains(q) {
                return false
            }
        }
        return true
    }

    // MARK: - Sorting

    private func sortComparator(lhs: CheatsheetRow, rhs: CheatsheetRow) -> Bool {
        let lhsValue = rowStatValue(lhs)
        let rhsValue = rowStatValue(rhs)
        return lhsValue > rhsValue  // descending
    }

    private func rowStatValue(_ row: CheatsheetRow) -> Double {
        switch row {
        case .player(let p):
            if selectedSort == .fantasyPoints { return points(for: p) }
            return p.stats[selectedSort.statKey ?? ""] ?? 0
        case .defense(let d):
            if selectedSort == .fantasyPoints { return points(for: d) }
            // D/ST has no passing/receiving stats; only totalTDs is meaningful.
            if selectedSort == .totalTDs { return d.stats["totalTouchdowns"] ?? 0 }
            return 0
        }
    }

    // MARK: - Draft actions

    func toggleTaken(_ row: CheatsheetRow) {
        let id: String
        switch row {
        case .player(let p): id = p.id
        case .defense(let d): id = d.id
        }
        draftState.toggleTaken(id)
    }

    func isTaken(_ row: CheatsheetRow) -> Bool {
        switch row {
        case .player(let p): return draftState.isTaken(p.id)
        case .defense(let d): return draftState.isTaken(d.id)
        }
    }

    func clearDraft() {
        draftState = DraftState()
    }

    // MARK: - Position filter

    func togglePosition(_ pos: FantasyPosition) {
        if selectedPositions.contains(pos) {
            selectedPositions.remove(pos)
        } else {
            selectedPositions.insert(pos)
        }
    }

    func selectAllPositions() { selectedPositions = Set(FantasyPosition.allCases) }

    // MARK: - Load pipeline

    func loadAll() async {
        guard !isLoading else { return }
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            // 1. Fetch all 32 teams
            let teams = try await service.fetchAllNFLTeams()

            // 2. Build D/ST rows (one per team) — stats enriched later
            teamDefenses = teams.map { team in
                CheatsheetTeamDefense(
                    teamId: team.id,
                    abbreviation: team.abbreviation,
                    displayName: team.displayName
                )
            }

            // 3. Fetch rosters in parallel (32 calls)
            var pool: [CheatsheetPlayer] = []
            await withTaskGroup(of: [CheatsheetPlayer].self) { group in
                for team in teams {
                    group.addTask { [service] in
                        (try? await service.fetchRoster(teamId: team.id)) ?? []
                    }
                }
                for await result in group {
                    pool.append(contentsOf: result)
                }
            }
            offensivePlayers = pool

            // 4. Fetch leaders → resolve ids with real stats (top-N)
            await enrichTopPlayersFromLeaders()
        } catch {
            errorMessage = "Could not load fantasy data: \(error.localizedDescription)"
        }
    }

    /// Enriches the top players (those appearing on the leaders board) with
    /// full stat splits so they have real fantasy points. Other players keep
    /// empty stats until individually enriched.
    private func enrichTopPlayersFromLeaders() async {
        isEnriching = true
        defer { isEnriching = false }

        do {
            let leaders = try await service.fetchLeaders(season: statsSeason, limit: 40)
            // Unique athlete ids from leaders
            let leaderIds = Set(leaders.map { $0.athleteId })
            guard !leaderIds.isEmpty else { return }

            // Fetch stat splits for each leader id in parallel
            let statsById = await withTaskGroup(of: (String, [String: Double]).self) { group -> [String: [String: Double]] in
                for id in leaderIds {
                    group.addTask { [service, statsSeason] in
                        let stats = await service.fetchAthleteStats(athleteId: id, season: statsSeason)
                        return (id, stats)
                    }
                }
                var dict = [String: [String: Double]]()
                for await (id, stats) in group { dict[id] = stats }
                return dict
            }

            // Merge stats into the pool
            for i in offensivePlayers.indices {
                if let stats = statsById[offensivePlayers[i].id], !stats.isEmpty {
                    offensivePlayers[i].stats = stats
                    offensivePlayers[i].computedPoints = points(for: offensivePlayers[i])
                }
            }
        } catch {
            // Leaders fetch is best-effort; the pool is still browsable.
        }

        // Enrich D/ST rows with team defensive stats (32 parallel calls).
        await enrichTeamDefenses()
    }

    /// Fetches team defensive/special-teams stats for every NFL team in
    /// parallel so each D/ST row gets a real fantasy-points value.
    private func enrichTeamDefenses() async {
        let season = statsSeason
        let defenseStatsByTeamId = await withTaskGroup(
            of: (String, [String: Double]).self
        ) { group -> [String: [String: Double]] in
            for defense in teamDefenses {
                let teamId = defense.teamId
                group.addTask { [service] in
                    let stats = await service.fetchTeamDefenseStats(teamId: teamId, season: season)
                    return (teamId, stats)
                }
            }
            var dict = [String: [String: Double]]()
            for await (id, stats) in group { dict[id] = stats }
            return dict
        }

        for i in teamDefenses.indices {
            if let stats = defenseStatsByTeamId[teamDefenses[i].teamId], !stats.isEmpty {
                teamDefenses[i].stats = stats
                teamDefenses[i].computedPoints = points(for: teamDefenses[i])
            }
        }
    }

    /// Lazily enrich a single player's stats when the user taps into detail.
    func enrichPlayer(_ player: CheatsheetPlayer) async {
        guard offensivePlayers.first(where: { $0.id == player.id })?.stats.isEmpty ?? true else { return }
        let stats = await service.fetchAthleteStats(athleteId: player.id, season: statsSeason)
        guard !stats.isEmpty else { return }
        if let idx = offensivePlayers.firstIndex(where: { $0.id == player.id }) {
            offensivePlayers[idx].stats = stats
            offensivePlayers[idx].computedPoints = points(for: offensivePlayers[idx])
        }
    }

    /// Lazily enrich a single team defense's stats when the user taps into detail.
    func enrichTeamDefense(_ defense: CheatsheetTeamDefense) async {
        guard teamDefenses.first(where: { $0.id == defense.id })?.stats.isEmpty ?? true else { return }
        let stats = await service.fetchTeamDefenseStats(teamId: defense.teamId, season: statsSeason)
        guard !stats.isEmpty else { return }
        if let idx = teamDefenses.firstIndex(where: { $0.id == defense.id }) {
            teamDefenses[idx].stats = stats
            teamDefenses[idx].computedPoints = points(for: teamDefenses[idx])
        }
    }

    // MARK: - Persistence

    private func persistScoringSettings() {
        if let data = try? JSONEncoder().encode(scoringSettings) {
            UserDefaults.standard.set(data, forKey: scoringKey)
        }
    }

    private func persistDraftState() {
        if let data = try? JSONEncoder().encode(draftState) {
            UserDefaults.standard.set(data, forKey: draftStateKey)
        }
    }

    // MARK: - Scoring presets

    func applyPreset(_ preset: ScoringPreset) {
        switch preset {
        case .standard: scoringSettings = .standard
        case .ppr:      scoringSettings = .ppr
        case .halfPPR:  scoringSettings = .halfPPR
        }
    }
}

// MARK: - Row enum (player vs defense)

enum CheatsheetRow: Identifiable, Hashable {
    case player(CheatsheetPlayer)
    case defense(CheatsheetTeamDefense)

    var id: String {
        switch self {
        case .player(let p): return p.id
        case .defense(let d): return d.id
        }
    }

    /// Position label for the row (D/ST for defenses).
    var positionLabel: String {
        switch self {
        case .player(let p): return p.position.displayName
        case .defense:      return "D/ST"
        }
    }

    /// Primary display name.
    var displayName: String {
        switch self {
        case .player(let p): return p.fullName
        case .defense(let d): return d.teamDisplayName + " D/ST"
        }
    }

    /// Team abbreviation.
    var teamAbbreviation: String {
        switch self {
        case .player(let p): return p.teamAbbreviation
        case .defense(let d): return d.teamAbbreviation
        }
    }

    /// Fantasy points string (1-decimal) or "—" if uncomputed.
    /// Takes settings directly to avoid a MainActor-isolated `vm` hop from a
    /// non-isolated enum context.
    func pointsString(settings: FantasyScoringSettings) -> String {
        let pts: Double
        switch self {
        case .player(let p): pts = FantasyPointsEngine.points(for: p, settings: settings)
        case .defense(let d): pts = FantasyPointsEngine.points(for: d, settings: settings)
        }
        if pts == 0 {
            // Distinguish "0 points" from "no stats loaded yet" — if stats are
            // empty, show "—" instead of "0.0".
            switch self {
            case .player(let p) where p.stats.isEmpty: return "—"
            case .defense(let d) where d.stats.isEmpty: return "—"
            default: break
            }
        }
        return String(format: "%.1f", pts)
    }
}

// MARK: - Scoring preset

enum ScoringPreset: String, CaseIterable, Identifiable {
    case standard = "Standard"
    case halfPPR = "Half-PPR"
    case ppr = "PPR"

    var id: String { rawValue }
}