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
    @State private var hasLoadedInitialData = false
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
            // Only show auto-refresh on the Scores tab and only when viewing current data.
            // Historical dates/weeks can't meaningfully auto-refresh, and other tabs
            // (Standings, News, Stats, Polls) are not wired to this refresh loop.
            let isViewingCurrent = sport.isFootball ? viewModel.isOnCurrentWeek : viewModel.isOnToday
            if selectedTab == .scores && isViewingCurrent {
                ToolbarItem(placement: .navigationBarTrailing) {
                    autoRefreshMenu
                }
            }
        }
        .task {
            guard !hasLoadedInitialData else { return }
            hasLoadedInitialData = true
            if let initialDate = initialDate {
                await viewModel.goToDate(initialDate, for: sport)
            } else {
                await viewModel.fetchGames(for: sport)
            }
        }
        // Auto-refresh loop — cancels and restarts whenever the interval changes.
        // Only actually refreshes when on the Scores tab viewing current data.
        .task(id: appSettings.autoRefreshInterval) {
            while !Task.isCancelled {
                let secs = appSettings.autoRefreshInterval.rawValue
                if secs > 0 {
                    try? await Task.sleep(for: .seconds(secs))
                    guard !Task.isCancelled else { break }
                    let isViewingCurrent = sport.isFootball ? viewModel.isOnCurrentWeek : viewModel.isOnToday
                    if selectedTab == .scores && isViewingCurrent {
                        await viewModel.refresh(for: sport)
                    }
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
            .disabled(viewModel.isLoading || (sport.isFootball && viewModel.isAtWeekStart))
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
                        // Static text — VoiceOver reads it as part of the row; no interactive trait.
                        .accessibilityLabel(weekText)

                    HStack(spacing: 6) {
                        // Season year picker
                        Menu {
                            ForEach(sport.availableSeasonYears, id: \.self) { year in
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
                        .accessibilityLabel("\(viewModel.resolvedSeason) season")
                        .accessibilityHint("Select to change season")

                        // Season type picker (only when calendar is loaded with >1 type)
                        if viewModel.availableSeasonTypes.count > 1 {
                            let currentTypeName = viewModel.availableSeasonTypes
                                .first { $0.type == viewModel.currentSeasonType }?.label ?? "Regular"
                            Menu {
                                ForEach(viewModel.availableSeasonTypes) { typeInfo in
                                    Button(typeInfo.label) {
                                        Task { await viewModel.goToSeasonType(typeInfo.type, for: sport); announceNavigation() }
                                    }
                                }
                            } label: {
                                let shortLabel = viewModel.availableSeasonTypes
                                    .first { $0.type == viewModel.currentSeasonType }?.shortLabel ?? "Reg"
                                HStack(spacing: 2) {
                                    Text(shortLabel)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Image(systemName: "chevron.up.chevron.down")
                                        .font(.system(size: 9))
                                        .foregroundColor(.secondary)
                                }
                            }
                            .accessibilityLabel("\(currentTypeName)")
                            .accessibilityHint("Select to change between preseason, regular, and postseason")
                        }
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("\(weekText), \(viewModel.resolvedSeason)")
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
                VStack(spacing: 2) {
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
                    .accessibilityLabel(viewModel.dateAccessibilityString)
                    .accessibilityHint("Opens date picker. Swipe up for next day, swipe down for previous day")
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

                    // Season picker for non-football, non-soccer sports
                    if !sport.isSoccer {
                        let displayYear = viewModel.displaySeasonYear(for: sport)
                        let seasonName  = sport.seasonDisplayName(year: displayYear)
                        Menu {
                            ForEach(sport.availableSeasonYears, id: \.self) { year in
                                Button(sport.seasonDisplayName(year: year)) {
                                    Task { await viewModel.goToSeason(year, for: sport); announceNavigation() }
                                }
                            }
                        } label: {
                            HStack(spacing: 3) {
                                Text(seasonName)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Image(systemName: "chevron.up.chevron.down")
                                    .font(.system(size: 9))
                                    .foregroundColor(.secondary)
                            }
                        }
                        .accessibilityLabel("\(seasonName) season")
                        .accessibilityHint("Select to change season")
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
            .disabled(viewModel.isLoading || (sport.isFootball && viewModel.isAtWeekEnd))
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
            description = "\(weekText), \(viewModel.resolvedSeason)"
        } else {
            description = viewModel.dateAccessibilityString
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
            if game.status.isLive, let sit = game.situation, let text = sit.displayText, !text.isEmpty {
                HStack(spacing: 6) {
                    Text(text)
                        .font(.caption)
                        .foregroundColor(.orange)
                        .lineLimit(2)
                        .fixedSize(horizontal: false, vertical: true)
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

        // For live games: inning first for baseball so listeners get game context immediately,
        // then situation. For all other sports, situation leads and period/clock follows.
        if game.status.isLive {
            if sport == .mlb {
                parts.append(game.status.detail)
                if let sit = game.situation, let t = sit.displayText, !t.isEmpty {
                    parts.append(t)
                }
            } else {
                if let sit = game.situation {
                    if let t = sit.displayText, !t.isEmpty {
                        parts.append(t)
                    }
                    if sit.isRedZone == true { parts.append("Red Zone") }
                }
            }
        }

        // Period / clock — the key time-reference for live games (e.g. "3rd Quarter - 8:42")
        // Baseball: omit clock (ESPN sends "0:00" but baseball has no game clock)
        if game.status.isLive {
            if sport == .mlb {
                // Already appended detail above
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

#Preview {
    NavigationStack {
        ScoresView(sport: .mlb)
    }
    .environmentObject(AppSettings())
}

