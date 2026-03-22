//
//  TeamScheduleView.swift
//  SportsScores
//
//  Created on 2/26/26.
//

import SwiftUI

struct TeamScheduleView: View {
    let team: Game.Team
    let sport: Sport
    @StateObject private var viewModel: TeamScheduleViewModel

    init(team: Game.Team, sport: Sport) {
        self.team = team
        self.sport = sport
        _viewModel = StateObject(wrappedValue: TeamScheduleViewModel(teamId: team.id, sport: sport))
    }

    private static let monthFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "MMMM yyyy"
        return f
    }()

    private static let dayFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "EEE, MMM d"
        return f
    }()

    private static let timeFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateStyle = .none
        f.timeStyle = .short   // e.g. "3:05 PM"
        return f
    }()

    // Group games by "Month Year" string
    private var groupedGames: [(month: String, games: [ScheduleGame])] {
        var dict: [(String, [ScheduleGame])] = []
        var seen: [String: Int] = [:]
        for game in viewModel.games {
            let key = Self.monthFormatter.string(from: game.date)
            if let idx = seen[key] {
                dict[idx].1.append(game)
            } else {
                seen[key] = dict.count
                dict.append((key, [game]))
            }
        }
        return dict.map { (month: $0.0, games: $0.1) }
    }

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading schedule…")
            } else if viewModel.games.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "calendar.badge.exclamationmark")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text("No schedule available")
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
            } else {
                scheduleList
            }
        }
        .navigationTitle("\(team.abbreviation) Schedule")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                yearPicker
            }
        }
        .task { await viewModel.fetchSchedule() }
    }

    // MARK: - Year Picker

    private var yearPicker: some View {
        Menu {
            ForEach(viewModel.availableYears, id: \.self) { year in
                Button("\(year)") {
                    Task { await viewModel.changeYear(year) }
                }
            }
        } label: {
            HStack(spacing: 2) {
                Text("\(viewModel.selectedYear)")
                    .font(.subheadline.bold())
                Image(systemName: "chevron.down")
                    .font(.caption)
            }
        }
        .accessibilityLabel("Season year, currently \(viewModel.selectedYear)")
    }

    // MARK: - Schedule List

    private var scheduleList: some View {
        List {
            ForEach(groupedGames, id: \.month) { section in
                Section(header: Text(section.month).font(.headline)) {
                    ForEach(section.games) { game in
                        NavigationLink(destination: GameDetailView(game: game.toGame(), sport: sport)) {
                            scheduleRow(game)
                        }
                        .listRowBackground(game.isToday ? Color.accentColor.opacity(0.12) : Color.clear)
                    }
                }
            }
        }
        .listStyle(.insetGrouped)
        .refreshable { await viewModel.fetchSchedule() }
    }

    // MARK: - Schedule Row

    private func scheduleRow(_ game: ScheduleGame) -> some View {
        HStack(spacing: 12) {
            // Date column
            VStack(alignment: .leading, spacing: 2) {
                Text(Self.dayFormatter.string(from: game.date))
                    .font(.caption.bold())
                    .foregroundColor(game.isToday ? .accentColor : .secondary)
                if game.isToday {
                    Text("TODAY")
                        .font(.caption2.bold())
                        .foregroundColor(.accentColor)
                }
            }
            .frame(width: 80, alignment: .leading)

            Divider()

            // Matchup column
            VStack(alignment: .leading, spacing: 3) {
                // Indicate home/away
                let isHome = game.homeTeam.id == team.id
                let opponent = isHome ? game.awayTeam : game.homeTeam
                HStack(spacing: 4) {
                    Text(isHome ? "vs" : "@")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(opponent.abbreviation)
                        .font(.subheadline.bold())
                }
                Text(game.venueName ?? (isHome ? "Home" : "Away"))
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }

            Spacer()

            // Score / Status column
            VStack(alignment: .trailing, spacing: 2) {
                if game.isCompleted {
                    let myTeam  = game.homeTeam.id == team.id ? game.homeTeam : game.awayTeam
                    let oppTeam = game.homeTeam.id == team.id ? game.awayTeam : game.homeTeam
                    if let myScore = myTeam.score, let oppScore = oppTeam.score {
                        let won = myScore > oppScore
                        Text(won ? "W" : (myScore == oppScore ? "T" : "L"))
                            .font(.caption.bold())
                            .foregroundColor(won ? .green : (myScore == oppScore ? .secondary : .red))
                        Text("\(myScore)-\(oppScore)")
                            .font(.caption.monospacedDigit())
                            .foregroundColor(.secondary)
                    } else {
                        Text("Final")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                } else if game.isInProgress {
                    Text(game.statusText)
                        .font(.caption)
                        .foregroundColor(.green)
                        .multilineTextAlignment(.trailing)
                } else {
                    // Scheduled: show local game time derived from the parsed date
                    Text(Self.timeFormatter.string(from: game.date))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.vertical, 4)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(scheduleAccessibilityLabel(game))
    }

    private func scheduleAccessibilityLabel(_ game: ScheduleGame) -> String {
        let isHome = game.homeTeam.id == team.id
        let opponent = isHome ? game.awayTeam : game.homeTeam
        let homeAway = isHome ? "vs" : "at"
        let dateStr = Self.dayFormatter.string(from: game.date)
        let statusPart: String
        if game.isCompleted {
            let myTeam  = game.homeTeam.id == team.id ? game.homeTeam : game.awayTeam
            let oppTeam = game.homeTeam.id == team.id ? game.awayTeam : game.homeTeam
            if let myScore = myTeam.score, let oppScore = oppTeam.score {
                let result = myScore > oppScore ? "Win" : (myScore == oppScore ? "Tie" : "Loss")
                statusPart = "\(result), \(myScore) to \(oppScore)"
            } else {
                statusPart = "Final"
            }
        } else if game.isInProgress {
            statusPart = game.statusText
        } else {
            statusPart = Self.timeFormatter.string(from: game.date)
        }
        return "\(dateStr), \(homeAway) \(opponent.displayName), \(statusPart)"
    }
}

#Preview {
    NavigationStack {
        TeamScheduleView(
            team: Game.Team(id: "10", name: "Yankees", abbreviation: "NYY",
                            displayName: "New York Yankees", score: nil, record: nil, logo: nil),
            sport: .mlb
        )
    }
}
