//
//  StandingsViewModel.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import Foundation

/// Which grouping the standings screen is showing. MLB is the only sport with a
/// wild card race, so the picker only appears there.
enum StandingsMode: String, CaseIterable, Identifiable {
    case divisions
    case wildCard

    var id: String { rawValue }

    var label: String {
        switch self {
        case .divisions: return "Divisions"
        case .wildCard:  return "Wild Card"
        }
    }
}

@MainActor
class StandingsViewModel: ObservableObject {
    @Published var standingsGroups: [StandingsGroup] = []
    @Published var wildCardGroups: [StandingsGroup] = []
    @Published var mode: StandingsMode = .divisions
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiService = ESPNAPIService.shared

    /// The groups the view should render for the current mode.
    var visibleGroups: [StandingsGroup] {
        mode == .wildCard ? wildCardGroups : standingsGroups
    }

    func fetchStandings(for sport: Sport) async {
        isLoading = standingsGroups.isEmpty
        errorMessage = nil
        
        do {
            if sport.usesCFLSource {
                standingsGroups = try await CFLAPIService.shared.fetchStandings()
            } else {
                standingsGroups = try await apiService.fetchStandings(for: sport)
            }
        } catch {
            errorMessage = "Failed to load standings: \(error.localizedDescription)"
        }
        
        isLoading = false
    }

    /// Loads the wild card race the first time the user switches to it. Kept
    /// separate from `fetchStandings` so the divisions view, which is what most
    /// people want, is never held up by a second network call.
    func loadWildCardIfNeeded(for sport: Sport) async {
        guard sport.hasWildCardStandings, wildCardGroups.isEmpty else { return }
        isLoading = true
        errorMessage = nil
        do {
            wildCardGroups = try await MLBStatsAPIService.shared.fetchWildCardStandings()
        } catch {
            errorMessage = "Failed to load wild card standings: \(error.localizedDescription)"
        }
        isLoading = false
    }

    func refresh(for sport: Sport) async {
        if mode == .wildCard && sport.hasWildCardStandings {
            wildCardGroups = []
            await loadWildCardIfNeeded(for: sport)
        } else {
            await fetchStandings(for: sport)
        }
    }
}
