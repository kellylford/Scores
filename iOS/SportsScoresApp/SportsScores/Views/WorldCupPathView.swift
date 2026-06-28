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
        .task { await viewModel.loadFullBracket() }
    }

    private func teamList(_ bracket: WorldCupBracket) -> some View {
        // Teams are grouped by status; the section heading carries the status, so
        // rows don't repeat it.
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
        return NavigationLink {
            WorldCupPathDetailView(team: team, bracket: bracket, sport: sport, phases: viewModel.phases)
        } label: {
            Text(name)
                .font(.body.weight(.semibold))
        }
        .accessibilityLabel(name)
        .accessibilityHint("Opens this team's tournament path")
    }
}
