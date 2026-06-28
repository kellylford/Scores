//
//  WorldCupPathView.swift
//  SportsScores
//
//  "Path to the Cup" — a picker of every team in the tournament. Each row shows
//  the team and its current status (still alive, or where it was eliminated).
//  Selecting a team opens its road to the title (WorldCupPathDetailView).
//
//  Reachable from a button at the top of the bracket page.
//

import SwiftUI

struct WorldCupPathView: View {

    @ObservedObject var viewModel: WorldCupViewModel
    let sport: Sport
    @EnvironmentObject private var appSettings: AppSettings

    var body: some View {
        Group {
            if let bracket = viewModel.bracket, bracket.hasKnockoutGames {
                teamList(bracket)
            } else if viewModel.isLoadingFullBracket {
                ProgressView("Loading bracket…")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .accessibilityLabel("Loading bracket")
            } else {
                ContentUnavailableView(
                    "Bracket Not Available Yet",
                    systemImage: "trophy",
                    description: Text("Team paths will appear once the knockout stage is set.")
                )
            }
        }
        .navigationTitle("Path to the Cup")
        .navigationBarTitleDisplayMode(.inline)
        // Refresh on open and on pull so the section counts and next-match details
        // reflect results as games finish.
        .task { await viewModel.loadFullBracket(force: true) }
        .refreshable { await viewModel.loadFullBracket(force: true) }
    }

    private func teamList(_ bracket: WorldCupBracket) -> some View {
        // Teams are grouped by status; the section heading carries the status, so
        // rows don't repeat it — but active rows show their next match.
        List {
            ForEach(bracket.teamSections, id: \.title) { section in
                Section("\(section.title) (\(section.teams.count))") {
                    ForEach(section.teams) { row(for: $0, bracket: bracket) }
                }
            }
        }
        .listStyle(.insetGrouped)
    }

    private func row(for team: BracketTeam, bracket: WorldCupBracket) -> some View {
        let name = team.name(for: appSettings.teamNamePreference)
        let nextMatch = nextMatchSummary(for: team, bracket: bracket)
        return NavigationLink {
            WorldCupPathDetailView(team: team, bracket: bracket, sport: sport, phases: viewModel.phases)
        } label: {
            VStack(alignment: .leading, spacing: 2) {
                Text(name)
                    .font(.body.weight(.semibold))
                if let nextMatch {
                    Text(nextMatch)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(nextMatch.map { "\(name). Next match: \($0)" } ?? name)
        .accessibilityHint("Opens this team's tournament path")
    }

    /// For an active team, a one-line summary of their next match: round, opponent
    /// (resolved as far as results allow), date/time and venue. nil for teams that
    /// are out (their section heading already says where their run ended).
    private func nextMatchSummary(for team: BracketTeam, bracket: WorldCupBracket) -> String? {
        guard team.fate.isAlive,
              let stage = bracket.forwardPath(forTeamId: team.id).first else { return nil }
        let opponent = bracket.description(of: stage.opponent, voiceOver: true,
                                           pref: appSettings.teamNamePreference)
        var parts = ["\(stage.round.label) vs \(opponent)", stage.game.displayTime]
        if let venue = stage.game.venue, !venue.name.isEmpty {
            parts.append(venue.fullName)
        }
        return parts.joined(separator: " · ")
    }
}
