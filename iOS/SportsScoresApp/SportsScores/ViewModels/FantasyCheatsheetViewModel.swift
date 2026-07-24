//
//  FantasyCheatsheetViewModel.swift
//  SportsScores
//
//  Owns the cheatsheet state: the draft board (players + D/ST), the taken set,
//  the scoring preset, and sort/filter/search. Everything the board needs —
//  ranks, ADP, auction values, projections — arrives in a single service call,
//  so changing the preset or sort just re-derives locally (no refetch).
//

import Foundation
import Combine

@MainActor
final class FantasyCheatsheetViewModel: ObservableObject {

    // MARK: - Published state

    @Published private(set) var players: [CheatsheetPlayer] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    @Published var preset: ScoringPreset { didSet { persistPreset() } }
    @Published var draftState: DraftState { didSet { persistDraftState() } }
    @Published var selectedSort: CheatsheetSort = .rank
    @Published var selectedPositions: Set<FantasyPosition> = Set(FantasyPosition.allCases)
    @Published var searchQuery: String = ""
    @Published var hideTaken: Bool = false
    @Published private(set) var season: Int

    // MARK: - Private

    private let service = FantasyCheatsheetService.shared
    private let presetKey = "fantasyScoringPreset"
    private let draftStateKey = "fantasyDraftTaken"

    // MARK: - Init

    init() {
        if let raw = UserDefaults.standard.string(forKey: "fantasyScoringPreset"),
           let saved = ScoringPreset(rawValue: raw) {
            self.preset = saved
        } else {
            self.preset = .ppr   // PPR is the most common league format.
        }

        if let data = UserDefaults.standard.data(forKey: "fantasyDraftTaken"),
           let saved = try? JSONDecoder().decode(DraftState.self, from: data) {
            self.draftState = saved
        } else {
            self.draftState = DraftState()
        }

        self.season = service.upcomingSeason()
    }

    // MARK: - Derived output

    /// Filtered + sorted rows the view renders.
    var displayedPlayers: [CheatsheetPlayer] {
        players.filter(matches).sorted(by: sortComparator)
    }

    var totalPlayerCount: Int { players.count }
    var displayedCount: Int { displayedPlayers.count }

    // MARK: - Filtering

    private func matches(_ p: CheatsheetPlayer) -> Bool {
        if !selectedPositions.contains(p.position) { return false }
        if hideTaken && draftState.isTaken(p.id) { return false }
        if !searchQuery.isEmpty {
            let q = searchQuery.lowercased()
            if !p.fullName.lowercased().contains(q)
                && !p.teamAbbreviation.lowercased().contains(q) {
                return false
            }
        }
        return true
    }

    // MARK: - Sorting

    private func sortComparator(_ a: CheatsheetPlayer, _ b: CheatsheetPlayer) -> Bool {
        switch selectedSort {
        case .rank:
            return (a.rank(for: preset) ?? .max) < (b.rank(for: preset) ?? .max)
        case .adp:
            return sortableADP(a) < sortableADP(b)
        case .auctionValue:
            return (a.auctionValue ?? 0) > (b.auctionValue ?? 0)          // higher $ first
        case .projectedPoints:
            return (a.projectedPoints(for: preset) ?? 0) > (b.projectedPoints(for: preset) ?? 0)
        }
    }

    /// ADP for sorting: undrafted players sort to the bottom.
    private func sortableADP(_ p: CheatsheetPlayer) -> Double {
        if let a = p.adp, a > 0, a < 300 { return a }
        return .greatestFiniteMagnitude
    }

    // MARK: - Draft actions

    func toggleTaken(_ player: CheatsheetPlayer) { draftState.toggleTaken(player.id) }
    func isTaken(_ player: CheatsheetPlayer) -> Bool { draftState.isTaken(player.id) }
    func clearDraft() { draftState = DraftState() }

    // MARK: - Filters

    func togglePosition(_ pos: FantasyPosition) {
        if selectedPositions.contains(pos) { selectedPositions.remove(pos) }
        else { selectedPositions.insert(pos) }
    }

    func selectAllPositions() { selectedPositions = Set(FantasyPosition.allCases) }

    func setPreset(_ preset: ScoringPreset) { self.preset = preset }

    // MARK: - Load

    func loadAll() async {
        guard !isLoading else { return }
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let rows = try await service.fetchCheatsheet(season: season)
            players = rows
            if rows.isEmpty {
                errorMessage = "No fantasy draft data is available yet for the \(season) season."
            }
        } catch {
            errorMessage = "Could not load fantasy data: \(error.localizedDescription)"
        }
    }

    // MARK: - Persistence

    private func persistPreset() {
        UserDefaults.standard.set(preset.rawValue, forKey: presetKey)
    }

    private func persistDraftState() {
        if let data = try? JSONEncoder().encode(draftState) {
            UserDefaults.standard.set(data, forKey: draftStateKey)
        }
    }
}
