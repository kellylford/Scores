//
//  WorldCupBracketView.swift
//  SportsScores
//
//  Tournament bracket tab for the World Cup hub.
//
//  Phase picker across the top selects the tournament round.
//  - Group Stage → delegates to WorldCupGroupsView (re-uses groups data)
//  - Knockout rounds → fetches and shows a list of matches in 3 view modes
//
//  List-based design keeps it fully accessible to VoiceOver without requiring
//  a visual bracket tree.
//

import SwiftUI

struct WorldCupBracketView: View {

    @ObservedObject var viewModel: WorldCupViewModel
    let sport: Sport

    @State private var viewMode: ViewMode = .quickList
    @State private var viewModeInitialized = false
    @EnvironmentObject private var appSettings: AppSettings

    var body: some View {
        VStack(spacing: 0) {
            phasePicker
                .padding(.horizontal)
                .padding(.vertical, 8)
                .background(Color.secondary.opacity(0.05))
                .overlay(alignment: .bottom) { Divider() }

            phaseContent
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .toolbar {
            // Only show view-mode button on knockout phases (Group Stage uses its own toolbar button)
            if viewModel.selectedPhaseId != "1" {
                ToolbarItem(placement: .navigationBarTrailing) {
                    ViewModeMenuButton(currentMode: $viewMode)
                }
            }
        }
        .task {
            // Load the initial phase on first appear.
            if let phase = viewModel.selectedPhase, phase.id != "1" {
                await viewModel.loadBracket(for: phase)
            }
        }
        .onAppear {
            guard !viewModeInitialized else { return }
            viewMode = appSettings.defaultTableViewMode
            viewModeInitialized = true
        }
    }

    // MARK: - Phase picker

    private var phasePicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(viewModel.phases) { phase in
                    Button {
                        Task { await viewModel.loadBracket(for: phase) }
                    } label: {
                        Text(phase.label)
                            .font(.subheadline.bold())
                            .padding(.horizontal, 14)
                            .padding(.vertical, 7)
                            .background(
                                viewModel.selectedPhaseId == phase.id
                                    ? Color.accentColor
                                    : Color.secondary.opacity(0.15),
                                in: Capsule()
                            )
                            .foregroundColor(
                                viewModel.selectedPhaseId == phase.id ? .white : .primary
                            )
                    }
                    .accessibilityLabel(phase.label)
                    .accessibilityAddTraits(viewModel.selectedPhaseId == phase.id ? .isSelected : [])
                }
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Tournament phases")
    }

    // MARK: - Content for selected phase

    @ViewBuilder
    private var phaseContent: some View {
        if viewModel.selectedPhaseId == "1" {
            // Group Stage — show the group standings view
            WorldCupGroupsView(
                groups: viewModel.groups,
                sport: sport,
                phases: viewModel.phases,
                isLoading: viewModel.isLoadingGroups,
                error: viewModel.groupsError,
                onRetry: { Task { await viewModel.loadGroups() } }
            )
        } else if viewModel.isLoadingBracket {
            ProgressView("Loading matches…")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .accessibilityLabel("Loading \(viewModel.selectedPhase?.label ?? "bracket") matches")
        } else if let err = viewModel.bracketError {
            ErrorStateView(message: err) {
                Task {
                    if let phase = viewModel.selectedPhase {
                        await viewModel.loadBracket(for: phase)
                    }
                }
            }
        } else if viewModel.bracketGames.isEmpty {
            emptyBracket
        } else {
            matchList(games: viewModel.bracketGames)
        }
    }

    // MARK: - Match list (3 view modes)

    private func matchList(games: [Game]) -> some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 16) {
                let live      = games.filter { $0.status.isLive }
                let upcoming  = games.filter { !$0.status.isLive && !$0.status.isCompleted
                                                && !$0.status.isPostponed && !$0.status.isCancelled }
                let completed = games.filter { $0.status.isCompleted }
                let other     = games.filter { $0.status.isPostponed || $0.status.isCancelled }

                matchSection(title: "In Progress", games: live)
                matchSection(title: "Upcoming",    games: upcoming)
                matchSection(title: "Completed",   games: completed)
                matchSection(title: "Other",       games: other)
            }
            .padding(.vertical)
        }
    }

    @ViewBuilder
    private func matchSection(title: String, games: [Game]) -> some View {
        if !games.isEmpty {
            switch viewMode {
            case .table:    tableSection(title: title, games: games)
            case .quickList: quickSection(title: title, games: games)
            case .fullList:  fullSection(title: title, games: games)
            }
        }
    }

    // -- Table mode --

    private func tableSection(title: String, games: [Game]) -> some View {
        let headers = ["Away", "Home", "Status"]
        let rows = games.map { tableRow($0) }
        return VStack(alignment: .leading, spacing: 0) {
            sectionHeader(title)
            VStack(spacing: 0) {
                HStack(spacing: 0) {
                    ForEach(headers, id: \.self) { h in
                        Text(h)
                            .font(.caption.bold())
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 6)
                            .background(Color.secondary.opacity(0.12))
                    }
                }
                .accessibilityHidden(true)
                ForEach(Array(games.enumerated()), id: \.element.id) { idx, game in
                    NavigationLink(destination: GameDetailView(game: game, sport: sport)) {
                        HStack(spacing: 0) {
                            ForEach(Array(tableRow(game).enumerated()), id: \.offset) { _, val in
                                Text(val)
                                    .font(.subheadline)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 8)
                            }
                        }
                        .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
                    }
                    .buttonStyle(.plain)
                    .accessibilityHidden(true)
                    if idx < games.count - 1 { Divider() }
                }
            }
            .background(Color.secondary.opacity(0.04))
            .cornerRadius(8)
            .accessibilityHidden(true)
            .overlay(
                AccessibleDataTable(headers: headers, rows: rows)
                    .allowsHitTesting(false)
            )
            .padding(.horizontal)
        }
    }

    // -- Quick List mode --

    private func quickSection(title: String, games: [Game]) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            sectionHeader(title)
            ForEach(games) { game in
                NavigationLink(destination: GameDetailView(game: game, sport: sport)) {
                    Text(quickText(game))
                        .font(.subheadline)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 6)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.plain)
                .accessibilityLabel(quickAccessibilityText(game))
                .accessibilityHint("Opens match details")
            }
        }
    }

    // -- Full List mode --

    private func fullSection(title: String, games: [Game]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionHeader(title)
            ForEach(games) { game in
                NavigationLink(destination: GameDetailView(game: game, sport: sport)) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("\(game.awayTeam.displayName) vs \(game.homeTeam.displayName)")
                            .font(.headline)
                        Text(fullDetailText(game))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.secondary.opacity(0.05))
                    .cornerRadius(8)
                    .padding(.horizontal, 12)
                }
                .buttonStyle(.plain)
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(quickAccessibilityText(game))
                .accessibilityHint("Opens match details")
            }
        }
    }

    // MARK: - Row formatters

    private func tableRow(_ game: Game) -> [String] {
        let away = game.awayTeam.abbreviation + (game.awayTeam.score.map { " \($0)" } ?? "")
        let home = game.homeTeam.abbreviation + (game.homeTeam.score.map { " \($0)" } ?? "")
        let status: String
        if game.status.isLive            { status = game.status.displayText }
        else if game.status.isPostponed  { status = "PPD" }
        else if game.status.isCancelled  { status = "Cxl" }
        else if game.status.isCompleted  { status = "Final" }
        else                             { status = game.displayTime }
        return [away, home, status]
    }

    private func quickText(_ game: Game) -> String {
        let away = game.awayTeam.abbreviation + (game.awayTeam.score.map { " \($0)" } ?? "")
        let home = game.homeTeam.abbreviation + (game.homeTeam.score.map { " \($0)" } ?? "")
        let status = statusText(game, abbreviated: true)
        return "\(away) @ \(home) — \(status)"
    }

    private func quickAccessibilityText(_ game: Game) -> String {
        let pref = appSettings.teamNamePreference
        let away = game.awayTeam.voiceOverName(for: pref) + (game.awayTeam.score.map { " \($0)" } ?? "")
        let home = game.homeTeam.voiceOverName(for: pref) + (game.homeTeam.score.map { " \($0)" } ?? "")
        return "\(away) at \(home), \(statusText(game, abbreviated: false))"
    }

    private func fullDetailText(_ game: Game) -> String {
        var parts: [String] = [statusText(game, abbreviated: false)]
        if let venue = game.venue?.fullName, !venue.isEmpty { parts.append(venue) }
        if game.shouldShowBroadcastInfo, let b = game.broadcasts.first, !b.isEmpty {
            parts.append("TV: \(b)")
        }
        return parts.joined(separator: " · ")
    }

    private func statusText(_ game: Game, abbreviated: Bool) -> String {
        if game.status.isLive           { return game.status.displayText }
        if game.status.isPostponed      { return abbreviated ? "PPD" : "Postponed" }
        if game.status.isCancelled      { return abbreviated ? "Cxl" : "Cancelled" }
        if game.status.isCompleted      { return "Final" }
        return game.displayTime
    }

    // MARK: - Helpers

    private func sectionHeader(_ title: String) -> some View {
        Text(title)
            .font(.subheadline.bold())
            .foregroundColor(.secondary)
            .padding(.horizontal, 16)
            .padding(.bottom, 4)
            .accessibilityAddTraits(.isHeader)
    }

    private var emptyBracket: some View {
        VStack(spacing: 16) {
            Image(systemName: "bracket")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
                .accessibilityHidden(true)
            Text("Matches will appear here as the tournament progresses.")
                .font(.headline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
