//
//  ScoresView.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI

struct ScoresView: View {
    let sport: Sport
    @StateObject private var viewModel = ScoresViewModel()
    @State private var selectedTab = 0
    @State private var showDatePicker = false

    var body: some View {
        VStack(spacing: 0) {

            // ── Tab selector (Scores / Standings / News / Stats [/ Polls]) ─
            Picker("View", selection: $selectedTab) {
                Text("Scores").tag(0)
                Text("Standings").tag(1)
                Text("News").tag(2)
                Text("Stats").tag(3)
                if sport.hasPolls {
                    Text("Polls").tag(4)
                }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)
            .padding(.top, 8)
            .padding(.bottom, 4)

            // ── Date / Week navigation bar (only on Scores tab) ──────────
            if selectedTab == 0 {
                dateNavigationBar
                    .padding(.horizontal)
                    .padding(.bottom, 6)
            }

            // ── Content ───────────────────────────────────────────────────
            tabContent
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .navigationTitle(sport.displayName)
        .task { await viewModel.fetchGames(for: sport) }
        .refreshable {
            // Refresh the active tab
            switch selectedTab {
            case 0: await viewModel.refresh(for: sport)
            default: break  // Standings and News have their own refresh
            }
        }
        .sheet(isPresented: $showDatePicker) {
            DatePickerView(selectedDate: viewModel.currentDate) { pickedDate in
                Task { await viewModel.goToDate(pickedDate, for: sport) }
            }
        }
    }

    // MARK: - Date / Week Navigation Bar

    @ViewBuilder
    private var dateNavigationBar: some View {
        HStack(spacing: 0) {
            Button {
                Task { await viewModel.goBack(for: sport) }
            } label: {
                Image(systemName: "chevron.left")
                    .font(.body.bold())
                    .frame(width: 44, height: 36)
                    .contentShape(Rectangle())
            }
            .disabled(viewModel.isLoading)
            .accessibilityLabel(sport.isFootball ? "Previous Week" : "Previous Day")

            Spacer()

            if sport.isFootball {
                Text(viewModel.weekLabel.isEmpty
                     ? (viewModel.currentWeek.map { "Week \($0)" } ?? "Current Week")
                     : viewModel.weekLabel)
                    .font(.subheadline.bold())
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
            } else {
                Button {
                    showDatePicker = true
                } label: {
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
                .accessibilityLabel("Choose date, currently \(viewModel.dateLabelText)")
            }

            Spacer()

            Button {
                Task { await viewModel.goForward(for: sport) }
            } label: {
                Image(systemName: "chevron.right")
                    .font(.body.bold())
                    .frame(width: 44, height: 36)
                    .contentShape(Rectangle())
            }
            .disabled(viewModel.isLoading)
            .accessibilityLabel(sport.isFootball ? "Next Week" : "Next Day")
        }
        .animation(.none, value: viewModel.weekLabel)
    }

    // MARK: - Tab content (conditional — no TabView to avoid height/task issues)

    @ViewBuilder
    private var tabContent: some View {
        switch selectedTab {
        case 1:
            StandingsView(sport: sport)
        case 2:
            NewsView(sport: sport)
        case 3:
            StatisticsView(sport: sport)
        case 4 where sport.hasPolls:
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
                VStack(spacing: 16) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 48))
                        .foregroundColor(.orange)
                    Text(error)
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)
                    Button("Retry") {
                        Task { await viewModel.fetchGames(for: sport) }
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
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
            ForEach(viewModel.games) { game in
                NavigationLink(destination: GameDetailView(game: game, sport: sport)) {
                    GameRow(game: game, sport: sport)
                }
            }
        }
        .listStyle(.plain)
    }
}

// MARK: - Game Row

struct GameRow: View {
    let game: Game
    let sport: Sport

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {

            // Status / time + broadcast chip
            HStack {
                statusChip
                Spacer()
                if let broadcast = game.broadcasts.first, !broadcast.isEmpty {
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

            // Live situation line (Football: down/distance; MLB: handled in detail)
            if game.status.isLive, let sit = game.situation {
                if let text = sit.displayText, !text.isEmpty {
                    Text(text)
                        .font(.caption)
                        .foregroundColor(.orange)
                        .lineLimit(1)
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
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityLabel)
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
        var parts: [String] = []
        if game.status.isLive        { parts.append("Live") }
        else if game.status.isCompleted { parts.append("Final") }

        parts.append("\(game.awayTeam.displayName) \(game.awayTeam.score.map { "\($0)" } ?? "")")
        parts.append("at \(game.homeTeam.displayName) \(game.homeTeam.score.map { "\($0)" } ?? "")")

        if !game.status.isLive && !game.status.isCompleted {
            parts.append(game.displayTime)
        }

        if game.status.isLive, let sit = game.situation, let t = sit.displayText {
            parts.append(t)
        }

        return parts.joined(separator: ", ")
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
}

