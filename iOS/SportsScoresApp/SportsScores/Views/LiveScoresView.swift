//
//  LiveScoresView.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI

// MARK: - Golf live state (lightweight, separate from team-sport viewmodel)

@MainActor
private class GolfLiveViewModel: ObservableObject {
    @Published var activeTournaments: [(sport: Sport, tournament: GolfTournament)] = []
    private let api = ESPNAPIService.shared

    func fetch() async {
        var found: [(sport: Sport, tournament: GolfTournament)] = []
        await withTaskGroup(of: (Sport, GolfTournament?).self) { group in
            for tour in Sport.golfTours {
                group.addTask {
                    let result = try? await self.api.fetchGolfTournament(for: tour)
                    return (tour, result?.tournament)
                }
            }
            for await (tour, tournament) in group {
                if let t = tournament, t.isInProgress {
                    found.append((sport: tour, tournament: t))
                }
            }
        }
        activeTournaments = found.sorted { $0.sport.rawValue < $1.sport.rawValue }
    }
}

struct LiveScoresView: View {
    @StateObject private var viewModel = LiveScoresViewModel()
    @StateObject private var golfVM   = GolfLiveViewModel()
    @EnvironmentObject private var appSettings: AppSettings

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading all games...")
            } else if let error = viewModel.errorMessage {
                VStack(spacing: 16) {
                    Image(systemName: "calendar.badge.clock")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text(error)
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)
                    Button("Retry") {
                        Task {
                            await viewModel.fetchAllGames()
                        }
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
            } else {
                scrollContent
            }
        }
        .navigationTitle("Live Scores")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Menu {
                    ForEach(AutoRefreshInterval.allCases) { interval in
                        Button {
                            appSettings.autoRefreshInterval = interval
                        } label: {
                            HStack {
                                Text(interval == .manual ? "Manual" : "Every \(interval.label)")
                                if appSettings.autoRefreshInterval == interval {
                                    Image(systemName: "checkmark")
                                }
                            }
                        }
                    }
                } label: {
                    Label(appSettings.autoRefreshInterval == .manual
                          ? "Manual" : "Auto \(appSettings.autoRefreshInterval.label)",
                          systemImage: "arrow.clockwise")
                    .font(.subheadline)
                }
            }
        }
        .task {
            await viewModel.fetchAllGames()
            if appSettings.golfHubEnabled { await golfVM.fetch() }
        }
        .task(id: appSettings.autoRefreshInterval) {
            while !Task.isCancelled {
                let secs = appSettings.autoRefreshInterval.rawValue
                if secs > 0 {
                    try? await Task.sleep(for: .seconds(secs))
                    guard !Task.isCancelled else { break }
                    await viewModel.refresh()
                    if appSettings.golfHubEnabled { await golfVM.fetch() }
                } else {
                    try? await Task.sleep(for: .seconds(86400))
                }
            }
        }
        .refreshable {
            await viewModel.refresh()
            if appSettings.golfHubEnabled { await golfVM.fetch() }
        }
    }
    
    private var scrollContent: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                // Golf Live Now section (shown first when a tournament is in progress)
                if appSettings.golfHubEnabled && !golfVM.activeTournaments.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        sectionHeader(title: "⛳ GOLF LIVE", count: golfVM.activeTournaments.count)
                        ForEach(golfVM.activeTournaments, id: \.sport.rawValue) { item in
                            NavigationLink(destination: GolfLeagueView(sport: item.sport)) {
                                golfTournamentRow(item.tournament, sport: item.sport)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal)
                }

                // Live Games Section
                if !viewModel.liveGames.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        sectionHeader(title: "LIVE NOW", count: totalCount(viewModel.liveGames))
                        
                        ForEach(viewModel.liveGames) { sportGames in
                            sportSection(sportGames: sportGames, isLive: true)
                        }
                    }
                    .padding(.horizontal)
                }
                
                // Upcoming Games Section
                if !viewModel.upcomingGames.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        sectionHeader(title: "UPCOMING", count: totalCount(viewModel.upcomingGames))
                        
                        ForEach(viewModel.upcomingGames) { sportGames in
                            sportSection(sportGames: sportGames, isLive: false)
                        }
                    }
                    .padding(.horizontal)
                }
                
                // Completed Games Section
                if !viewModel.completedGames.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        sectionHeader(title: "COMPLETED", count: totalCount(viewModel.completedGames))
                        
                        ForEach(viewModel.completedGames) { sportGames in
                            sportSection(sportGames: sportGames, isLive: false)
                        }
                    }
                    .padding(.horizontal)
                }
                
                if viewModel.liveGames.isEmpty && viewModel.completedGames.isEmpty && viewModel.upcomingGames.isEmpty && (!appSettings.golfHubEnabled || golfVM.activeTournaments.isEmpty) {
                    VStack(spacing: 16) {
                        Image(systemName: "calendar.badge.exclamationmark")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("No games today")
                            .font(.headline)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.top, 40)
                }
            }
            .padding(.vertical)
        }
    }
    
    private func sectionHeader(title: String, count: Int) -> some View {
        HStack {
            Text(title)
                .font(.headline)
                .fontWeight(.bold)
            
            Text("\(count)")
                .font(.caption)
                .foregroundColor(.white)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.blue)
                .cornerRadius(12)
        }
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits(.isHeader)
    }
    
    private func sportSection(sportGames: LiveScoresViewModel.SportGames, isLive: Bool) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            // Sport Header
            HStack {
                Text(sportGames.sport.icon)
                    .font(.title3)
                Text(sportGames.sport.displayName)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Spacer()
                Text("\(sportGames.games.count)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color.secondary.opacity(0.1))
            .cornerRadius(8)
            .accessibilityElement(children: .combine)
            .accessibilityAddTraits(.isHeader)
            
            // Games List
            ForEach(sportGames.games) { game in
                NavigationLink(destination: GameDetailView(game: game, sport: sportGames.sport)) {
                    CompactGameRow(game: game, isLive: isLive, sport: sportGames.sport)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.vertical, 4)
    }
    
    private func totalCount(_ sportGames: [LiveScoresViewModel.SportGames]) -> Int {
        sportGames.reduce(0) { $0 + $1.games.count }
    }

    private func golfTournamentRow(_ tournament: GolfTournament, sport: Sport) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: sport.systemImage)
                    .font(.title3)
                Text(sport.displayName)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Spacer()
                Label(tournament.roundStatusText, systemImage: "circle.fill")
                    .font(.caption)
                    .foregroundColor(.red)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color.secondary.opacity(0.1))
            .cornerRadius(8)

            HStack {
                Text(tournament.name)
                    .font(.subheadline)
                Spacer()
                // Top 3 leaders
                if !tournament.competitors.isEmpty {
                    VStack(alignment: .trailing, spacing: 2) {
                        ForEach(tournament.competitors.prefix(3)) { comp in
                            Text("\(comp.positionDisplay). \(comp.shortName)  \(comp.overallScore)")
                                .font(.caption.monospacedDigit())
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
            .padding(.horizontal, 12)
            .padding(.bottom, 4)
        }
        .padding(.vertical, 4)
        .accessibilityElement(children: .combine)
        .accessibilityLabel({
            let leaders = tournament.competitors.prefix(3).map { "\($0.positionDisplay). \($0.playerName), \($0.overallScore)" }.joined(separator: "; ")
            return "\(sport.displayName), \(tournament.name), \(tournament.roundStatusText). Leaders: \(leaders)"
        }())
        .accessibilityHint("Opens \(sport.displayName) leaderboard")
    }
}

struct CompactGameRow: View {
    let game: Game
    let isLive: Bool
    let sport: Sport

    @EnvironmentObject private var appSettings: AppSettings
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Teams and Scores FIRST
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(game.awayTeam.abbreviation)
                        .font(.body)
                        .fontWeight(.medium)
                    
                    Text(game.homeTeam.abbreviation)
                        .font(.body)
                        .fontWeight(.medium)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    if let score = game.awayTeam.score {
                        Text("\(score)")
                            .font(.title3)
                            .fontWeight(.bold)
                            .monospacedDigit()
                    } else {
                        Text("-")
                            .font(.title3)
                            .foregroundColor(.secondary)
                    }
                    
                    if let score = game.homeTeam.score {
                        Text("\(score)")
                            .font(.title3)
                            .fontWeight(.bold)
                            .monospacedDigit()
                    } else {
                        Text("-")
                            .font(.title3)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            // Status Bar SECOND (below teams)
            HStack {
                if isLive {
                    Label(game.status.displayText, systemImage: "circle.fill")
                        .foregroundColor(.red)
                        .font(.caption)
                        .fontWeight(.semibold)
                } else if game.status.isCompleted {
                    Text("Final")
                        .font(.caption)
                        .foregroundColor(.secondary)
                } else {
                    Text(game.displayTime)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                if game.shouldShowBroadcastInfo, !game.broadcasts.isEmpty {
                    Text(game.broadcasts.first ?? "")
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.blue.opacity(0.2))
                        .cornerRadius(4)
                }
            }
            
            // Last play / situation info (no truncation for accessibility)
            if isLive, let situation = game.situation, let displayText = situation.displayText {
                Text(displayText)
                    .font(.caption)
                    .foregroundColor(.primary)
                    .fixedSize(horizontal: false, vertical: true)
                    .lineLimit(nil)
            }
            
            // Team records (less important, shown last)
            if let awayRecord = game.awayTeam.record, let homeRecord = game.homeTeam.record {
                HStack(spacing: 12) {
                    Text("(\(awayRecord))")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text("(\(homeRecord))")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(12)
        .background(Color.secondary.opacity(0.05))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(isLive ? Color.red.opacity(0.3) : Color.clear, lineWidth: 2)
        )
        // Combine all sub-elements so VoiceOver reads a single coherent label (design debt #2)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(compactAccessibilityLabel)
        .onAppear {
            debugLogAccessibilityLabelIfNeeded()
        }
    }

    private var compactAccessibilityLabel: String {
        let pref = appSettings.teamNamePreference
        var parts: [String] = []

        // Section headings in LiveScoresView already communicate status —
        // omit "Live" / "Final" to avoid redundancy (design debt #5).
        // Scores
        parts.append(
            "\(game.awayTeam.voiceOverName(for: pref)) \(game.awayTeam.score.map { "\($0)" } ?? "")"
        )
        parts.append(
            "at \(game.homeTeam.voiceOverName(for: pref)) \(game.homeTeam.score.map { "\($0)" } ?? "")"
        )

        if !game.status.isLive && !game.status.isCompleted {
            parts.append(game.displayTime)
        }

        // For live games: inning first for baseball so listeners get game context immediately,
        // then situation. For all other sports, situation leads and period/clock follows.
        if isLive {
            if sport == .mlb {
                parts.append(game.status.detail)
                if let sit = game.situation, let t = sit.displayText {
                    parts.append(t)
                }
            } else {
                if let sit = game.situation, let t = sit.displayText {
                    parts.append(t)
                }
                parts.append(game.status.displayText)
            }
        }

        // Broadcast last
        if game.shouldShowBroadcastInfo,
           let broadcast = game.broadcasts.first,
           !broadcast.isEmpty {
            parts.append("on \(broadcast)")
        }

        return parts.joined(separator: ", ")
    }

    private func debugLogAccessibilityLabelIfNeeded() {
        #if DEBUG
        guard isLive else { return }
        guard ProcessInfo.processInfo.arguments.contains("-A11YDebugLiveLabels") else { return }
        print("[A11Y][LiveScoresView][\(game.id)] \(compactAccessibilityLabel)")
        #endif
    }
}

#Preview {
    NavigationStack {
        LiveScoresView()
    }
    .environmentObject(AppSettings())
}
