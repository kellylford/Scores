//
//  ScoresView.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI
import UIKit

private enum ScoresTab: Int {
    case scores = 0, standings, news, stats, polls
}

struct ScoresView: View {
    let sport: Sport
    let initialDate: Date?
    @StateObject private var viewModel = ScoresViewModel()
    @State private var selectedTab = ScoresTab.scores
    @State private var showDatePicker = false
    @EnvironmentObject private var appSettings: AppSettings

    init(sport: Sport, initialDate: Date? = nil) {
        self.sport = sport
        self.initialDate = initialDate
        _viewModel = StateObject(wrappedValue: ScoresViewModel())
        _selectedTab = State(initialValue: .scores)
        _showDatePicker = State(initialValue: false)
    }

    var body: some View {
        VStack(spacing: 0) {

            // ── Date / Week navigation bar (only on Scores tab) ──────────
            if selectedTab == .scores {
                dateNavigationBar
                    .padding(.horizontal)
                    .padding(.top, 8)
                    .padding(.bottom, 6)
            }

            // ── Content ───────────────────────────────────────────────────
            tabContent
                .frame(maxWidth: .infinity, maxHeight: .infinity)

            // ── Tab selector (Scores / Standings / News / Stats [/ Polls]) ─
            Divider()
            Picker("View", selection: $selectedTab) {
                Text("Scores").tag(ScoresTab.scores)
                Text("Standings").tag(ScoresTab.standings)
                Text("News").tag(ScoresTab.news)
                Text("Stats").tag(ScoresTab.stats)
                if sport.hasPolls {
                    Text("Polls").tag(ScoresTab.polls)
                }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)
            .padding(.top, 4)
            .padding(.bottom, 8)
        }
        .navigationTitle(sport.displayName)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                autoRefreshMenu
            }
        }
        .task {
            if let initialDate = initialDate {
                await viewModel.goToDate(initialDate, for: sport)
            } else {
                await viewModel.fetchGames(for: sport)
            }
        }
        // Auto-refresh loop — cancels and restarts whenever the interval changes
        .task(id: appSettings.autoRefreshInterval) {
            while !Task.isCancelled {
                let secs = appSettings.autoRefreshInterval.rawValue
                if secs > 0 {
                    try? await Task.sleep(for: .seconds(secs))
                    guard !Task.isCancelled else { break }
                    await viewModel.refresh(for: sport)
                } else {
                    // Manual — park until cancelled
                    try? await Task.sleep(for: .seconds(86400))
                }
            }
        }
        .refreshable {
            // Refresh the active tab
            switch selectedTab {
            case .scores: await viewModel.refresh(for: sport)
            default: break  // Standings and News have their own refresh
            }
        }
        .sheet(isPresented: $showDatePicker) {
            DatePickerView(selectedDate: viewModel.currentDate) { pickedDate in
                Task { await viewModel.goToDate(pickedDate, for: sport) }
            }
        }
    }

    // MARK: - Auto-refresh menu

    private var autoRefreshMenu: some View {
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
                  ? "Manual"
                  : "Auto \(appSettings.autoRefreshInterval.label)",
                  systemImage: "arrow.clockwise")
            .font(.subheadline)
        }
        .accessibilityLabel("Auto-refresh interval, currently \(appSettings.autoRefreshInterval == .manual ? "manual" : "every \(appSettings.autoRefreshInterval.label)")")
    }

    // MARK: - Date / Week Navigation Bar

    @ViewBuilder
    private var dateNavigationBar: some View {
        HStack(spacing: 8) {

            // ── Previous button ──────────────────────────────────────────
            Button {
                Task { await viewModel.goBack(for: sport); announceNavigation() }
            } label: {
                Image(systemName: "chevron.left")
                    .font(.body.bold())
                    .frame(width: 44, height: 36)
                    .contentShape(Rectangle())
            }
            .disabled(viewModel.isLoading)
            .accessibilityLabel(sport.isFootball ? "Previous Week" : "Previous Day")

            Spacer()

            // ── Centre label ─────────────────────────────────────────────
            if sport.isFootball {
                let weekText = viewModel.weekLabel.isEmpty
                    ? (viewModel.currentWeek.map { "Week \($0)" } ?? "Current Week")
                    : viewModel.weekLabel
                VStack(spacing: 2) {
                    Text(weekText)
                        .font(.subheadline.bold())
                        .lineLimit(1)
                        .minimumScaleFactor(0.7)

                    // Season year picker — lets users jump to historical seasons
                    let currentYear = Calendar.current.component(.year, from: Date())
                    let availableSeasons = Array((viewModel.earliestFootballSeason...currentYear).reversed())
                    Menu {
                        ForEach(availableSeasons, id: \.self) { year in
                            Button(String(year)) {
                                Task { await viewModel.goToSeason(year, for: sport); announceNavigation() }
                            }
                        }
                    } label: {
                        HStack(spacing: 3) {
                            Text(String(viewModel.resolvedSeason))
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Image(systemName: "chevron.up.chevron.down")
                                .font(.system(size: 9))
                                .foregroundColor(.secondary)
                        }
                    }
                    .accessibilityLabel("Season \(viewModel.resolvedSeason). Tap to pick a different season year.")
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Currently viewing \(weekText), \(viewModel.resolvedSeason) season")
                .accessibilityAddTraits(.isButton)
                .accessibilityHint("Swipe up for next week, swipe down for previous week")
                .accessibilityAdjustableAction { direction in
                    Task {
                        switch direction {
                        case .increment: await viewModel.goForward(for: sport)
                        case .decrement: await viewModel.goBack(for: sport)
                        @unknown default: break
                        }
                        announceNavigation()
                    }
                }
            } else {
                Button { showDatePicker = true } label: {
                    HStack(spacing: 4) {
                        Text(viewModel.dateLabelText)
                            .font(.subheadline.bold())
                        Image(systemName: "calendar")
                            .font(.caption)
                    }
                    .foregroundColor(.primary)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 6)
                    .background(Color.secondary.opacity(0.12))
                    .cornerRadius(8)
                }
                .accessibilityLabel("Currently viewing \(viewModel.dateAccessibilityString). Tap to open date picker.")
                .accessibilityHint("Swipe up for next day, swipe down for previous day")
                .accessibilityAdjustableAction { direction in
                    Task {
                        switch direction {
                        case .increment: await viewModel.goForward(for: sport)
                        case .decrement: await viewModel.goBack(for: sport)
                        @unknown default: break
                        }
                        announceNavigation()
                    }
                }
            }

            Spacer()

            // ── Next button ───────────────────────────────────────────────
            Button {
                Task { await viewModel.goForward(for: sport); announceNavigation() }
            } label: {
                Image(systemName: "chevron.right")
                    .font(.body.bold())
                    .frame(width: 44, height: 36)
                    .contentShape(Rectangle())
            }
            .disabled(viewModel.isLoading)
            .accessibilityLabel(sport.isFootball ? "Next Week" : "Next Day")

            // ── Today button (only when not on today / current week) ──────
            let showToday = sport.isFootball ? !viewModel.isOnCurrentWeek : !viewModel.isOnToday
            if showToday {
                Button("Today") {
                    Task { await viewModel.goToToday(for: sport); announceNavigation() }
                }
                .font(.subheadline)
                .buttonStyle(.bordered)
                .controlSize(.small)
                .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.15), value: viewModel.isOnToday)
        .animation(.easeInOut(duration: 0.15), value: viewModel.isOnCurrentWeek)
        .animation(.none, value: viewModel.weekLabel)
        // Belt-and-suspenders named actions for VoiceOver custom actions rotor
        .accessibilityAction(named: sport.isFootball ? "Previous Week" : "Previous Day") {
            Task { await viewModel.goBack(for: sport); announceNavigation() }
        }
        .accessibilityAction(named: sport.isFootball ? "Next Week" : "Next Day") {
            Task { await viewModel.goForward(for: sport); announceNavigation() }
        }
    }

    /// Posts a haptic and VoiceOver announcement after any date/week navigation.
    private func announceNavigation() {
        UINotificationFeedbackGenerator().notificationOccurred(.success)
        let description: String
        if sport.isFootball {
            let weekText = viewModel.weekLabel.isEmpty
                ? (viewModel.currentWeek.map { "Week \($0)" } ?? "Current Week")
                : viewModel.weekLabel
            description = "\(sport.displayName), \(weekText), \(viewModel.resolvedSeason)"
        } else {
            description = "\(sport.displayName), \(viewModel.dateAccessibilityString)"
        }
        UIAccessibility.post(notification: .announcement, argument: description)
    }

    // MARK: - Tab content (conditional — no TabView to avoid height/task issues)

    @ViewBuilder
    private var tabContent: some View {
        switch selectedTab {
        case .standings:
            StandingsView(sport: sport)
        case .news:
            NewsView(sport: sport)
        case .stats:
            StatisticsView(sport: sport)
        case .polls where sport.hasPolls:
            PollsView(sport: sport)
        default:
            scoresTab
        }
    }

    private var scoresTab: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading games...")
            } else if let error = viewModel.errorMessage {
                ErrorStateView(message: error) {
                    Task { await viewModel.fetchGames(for: sport) }
                }
            } else if viewModel.games.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "calendar.badge.exclamationmark")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text("No games scheduled")
                        .font(.headline)
                        .foregroundColor(.secondary)
                    if !sport.isFootball {
                        Button("Go to Today") {
                            Task { await viewModel.goToToday(for: sport) }
                        }
                        .buttonStyle(.bordered)
                    }
                }
            } else {
                gamesList
            }
        }
    }

    private var gamesList: some View {
        List {
            // ── In Progress ───────────────────────────────────────────────
            if !viewModel.inProgressGames.isEmpty {
                Section {
                    ForEach(viewModel.inProgressGames) { game in
                        gameRow(game, context: .inProgress)
                    }
                } header: {
                    Text("In Progress")
                        .accessibilityAddTraits(.isHeader)
                }
            }

            // ── Upcoming ──────────────────────────────────────────────────
            if !viewModel.upcomingGames.isEmpty {
                Section {
                    ForEach(viewModel.upcomingGames) { game in
                        gameRow(game, context: .upcoming)
                    }
                } header: {
                    Text("Upcoming")
                        .accessibilityAddTraits(.isHeader)
                }
            }

            // ── Completed ─────────────────────────────────────────────────
            if !viewModel.completedGames.isEmpty {
                Section {
                    ForEach(viewModel.completedGames) { game in
                        gameRow(game, context: .completed)
                    }
                } header: {
                    Text("Completed")
                        .accessibilityAddTraits(.isHeader)
                }
            }
        }
        .listStyle(.plain)
    }

    @ViewBuilder
    private func gameRow(_ game: Game, context: GameSectionContext) -> some View {
        NavigationLink(destination: GameDetailView(game: game, sport: sport)) {
            GameRow(game: game, sport: sport, sectionContext: context)
        }
        .swipeActions(edge: .trailing, allowsFullSwipe: false) {
            MonitorToggleButton(game: game)
        }
        .contextMenu {
            MonitorContextMenuItem(game: game)
        }
    }
}

// MARK: - Section Context

/// Indicates which status section a game row is displayed in.
/// Used to suppress redundant VoiceOver status words (design debt #5).
enum GameSectionContext {
    case inProgress, upcoming, completed
}

// MARK: - Game Row

struct GameRow: View {
    let game: Game
    let sport: Sport
    /// The list section this row is in. `nil` = unknown / no sectioning.
    var sectionContext: GameSectionContext? = nil

    @EnvironmentObject private var appSettings: AppSettings

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {

            // Status / time + broadcast chip
            HStack {
                statusChip
                Spacer()
                if game.shouldShowBroadcastInfo,
                   let broadcast = game.broadcasts.first,
                   !broadcast.isEmpty {
                    Text(broadcast)
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.blue.opacity(0.2))
                        .cornerRadius(4)
                }
            }

            // Away / Home score rows
            VStack(alignment: .leading, spacing: 4) {
                TeamScoreRow(team: game.awayTeam, isHome: false)
                TeamScoreRow(team: game.homeTeam, isHome: true)
            }

            // Live situation line
            if game.status.isLive, let sit = game.situation {
                // MLB: show base runners + count, then pitcher/batter on second line
                if sport == .mlb, let baseInfo = sit.baseballSituationText {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(baseInfo)
                            .font(.caption)
                            .foregroundColor(.orange)
                            .lineLimit(2)
                        if let p = sit.pitcherName, let b = sit.batterName {
                            Text("P: \(p)  ·  AB: \(b)")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                                .lineLimit(1)
                        }
                    }
                } else if let text = sit.displayText, !text.isEmpty {
                    // Football: down/distance + optional red zone badge; other: last play
                    HStack(spacing: 6) {
                        Text(text)
                            .font(.caption)
                            .foregroundColor(.orange)
                            .lineLimit(1)
                        if sit.isRedZone == true {
                            Text("🔴 Red Zone")
                                .font(.caption2)
                                .padding(.horizontal, 5)
                                .padding(.vertical, 2)
                                .background(Color.red.opacity(0.18))
                                .foregroundColor(.red)
                                .cornerRadius(4)
                        }
                    }
                }
            }

            // Venue (compact)
            if let venue = game.venue, let city = venue.city {
                Text("\(city)\(venue.state.map { ", \($0)" } ?? "")")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(accessibilityLabel)
        .onAppear {
            debugLogAccessibilityLabelIfNeeded()
        }
    }

    @ViewBuilder
    private var statusChip: some View {
        if game.status.isLive {
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
    }

    private var accessibilityLabel: String {
        let pref = appSettings.teamNamePreference
        var parts: [String] = []

        // Suppress status word when section heading already communicates it (design debt #5)
        let suppressFinal = sectionContext == .completed

        if game.status.isCompleted && !suppressFinal { parts.append("Final") }

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

        // Last action / situation
        if game.status.isLive, let sit = game.situation {
            if sport == .mlb, let baseInfo = sit.baseballSituationText {
                parts.append(baseInfo)
                if let p = sit.pitcherName { parts.append("Pitching: \(p)") }
                if let b = sit.batterName  { parts.append("At bat: \(b)") }
            } else if let t = sit.displayText {
                parts.append(t)
                if sit.isRedZone == true { parts.append("Red Zone") }
            }
        }

        // Period / clock — the key time-reference for live games (e.g. "3rd Quarter - 8:42")
        // Baseball: omit clock (ESPN sends "0:00" but baseball has no game clock)
        if game.status.isLive {
            if sport == .mlb {
                parts.append(game.status.detail)
            } else {
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
        guard game.status.isLive else { return }
        guard ProcessInfo.processInfo.arguments.contains("-A11YDebugLiveLabels") else { return }
        print("[A11Y][ScoresView][\(sport.rawValue)][\(game.id)] \(accessibilityLabel)")
        #endif
    }
}

// MARK: - Team Score Row

struct TeamScoreRow: View {
    let team: Game.Team
    let isHome: Bool

    var body: some View {
        HStack {
            Text(isHome ? "vs" : "@")
                .font(.caption)
                .foregroundColor(.secondary)
                .frame(width: 20)

            Text(team.abbreviation)
                .font(.body)
                .fontWeight(.medium)

            if let record = team.record {
                Text("(\(record))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()

            if let score = team.score {
                Text("\(score)")
                    .font(.title3)
                    .fontWeight(.bold)
                    .monospacedDigit()
            }
        }
    }
}

// MARK: - Swipe action button

private struct MonitorToggleButton: View {
    let game: Game
    @ObservedObject private var monitor = ScoreMonitorService.shared

    var body: some View {
        let watched = monitor.isMonitored(gameId: game.id)
        Button {
            monitor.toggle(game: game)
        } label: {
            Label(watched ? "Unwatch" : "Watch",
                  systemImage: watched ? "bell.slash.fill" : "bell.fill")
        }
        .tint(watched ? .gray : .orange)
    }
}

// MARK: - Context menu item

private struct MonitorContextMenuItem: View {
    let game: Game
    @ObservedObject private var monitor = ScoreMonitorService.shared

    var body: some View {
        let watched = monitor.isMonitored(gameId: game.id)
        Button {
            monitor.toggle(game: game)
        } label: {
            Label(watched ? "Stop Monitoring Score" : "Monitor Score",
                  systemImage: watched ? "bell.slash" : "bell")
        }
    }
}

#Preview {
    NavigationStack {
        ScoresView(sport: .mlb)
    }
    .environmentObject(AppSettings())
}

