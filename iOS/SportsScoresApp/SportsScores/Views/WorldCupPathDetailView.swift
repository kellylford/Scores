//
//  WorldCupPathDetailView.swift
//  SportsScores
//
//  One team's "Path to the Cup":
//    • Remaining stages they must win to lift the trophy — each line is the round
//      plus the real match details (vs opponent, date, venue). Opponents resolve
//      as far as results allow and the list shrinks as teams are eliminated.
//    • Tournament history — every game they've already played, with the result.
//
//  Eliminated teams show where their run ended (no remaining path) plus history.
//

import SwiftUI

struct WorldCupPathDetailView: View {

    let team: BracketTeam
    let bracket: WorldCupBracket
    let sport: Sport
    let phases: [WorldCupPhase]

    @StateObject private var viewModel: WorldCupPathDetailViewModel
    @EnvironmentObject private var appSettings: AppSettings

    init(team: BracketTeam, bracket: WorldCupBracket, sport: Sport, phases: [WorldCupPhase]) {
        self.team = team
        self.bracket = bracket
        self.sport = sport
        self.phases = phases
        _viewModel = StateObject(wrappedValue: WorldCupPathDetailViewModel(
            teamId: team.id, sport: sport, phases: phases))
    }

    private var pref: TeamNamePreference { appSettings.teamNamePreference }
    private var teamName: String { team.name(for: pref) }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header

                let stages = bracket.forwardPath(forTeamId: team.id)
                if stages.isEmpty {
                    outcomeNote
                } else {
                    sectionHeading("Path to the Cup")
                    pathIntro(count: stages.count)
                    ForEach(Array(stages.enumerated()), id: \.offset) { index, stage in
                        stageCard(stage, index: index, total: stages.count)
                    }
                }

                historySection
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .navigationTitle(teamName)
        .navigationBarTitleDisplayMode(.inline)
        .task { await viewModel.load() }
    }

    // MARK: - Header

    private var header: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(teamName)
                .font(.title2.bold())
            if let group = team.groupName {
                Text(group)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color.accentColor.opacity(0.10), in: RoundedRectangle(cornerRadius: 12))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(team.groupName.map { "\(teamName), \($0)" } ?? teamName)
        .accessibilityAddTraits(.isHeader)
    }

    // MARK: - Path stages

    private func pathIntro(count: Int) -> some View {
        let matchWord = count == 1 ? "match" : "matches"
        return Text("\(teamName) must win \(count) more \(matchWord) to lift the trophy.")
            .font(.subheadline)
            .foregroundColor(.secondary)
            .frame(maxWidth: .infinity, alignment: .leading)
            .fixedSize(horizontal: false, vertical: true)
    }

    private func stageCard(_ stage: WorldCupBracket.PathStage, index: Int, total: Int) -> some View {
        let opponent = bracket.description(of: stage.opponent, voiceOver: true, pref: pref)
        let roundLabel = stage.round.label
        let when = stage.game.displayTime
        let venue = stage.game.venue.flatMap { $0.name.isEmpty ? nil : $0.fullName }

        // Visual detail line(s).
        let detail = "vs \(opponent)"
        var meta = when
        if let venue { meta += " · \(venue)" }

        // One coherent VoiceOver line: round, opponent, when, venue.
        var a11y = "\(roundLabel), versus \(opponent), \(when)"
        if let venue { a11y += ", \(venue)" }

        return HStack(alignment: .top, spacing: 12) {
            Text("\(index + 1)")
                .font(.headline.monospacedDigit())
                .foregroundColor(.white)
                .frame(width: 28, height: 28)
                .background(Circle().fill(Color.accentColor))
                .accessibilityHidden(true)

            VStack(alignment: .leading, spacing: 3) {
                Text(roundLabel)
                    .font(.subheadline.bold())
                Text(detail)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                Text(meta)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(Color.secondary.opacity(0.06), in: RoundedRectangle(cornerRadius: 10))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Stage \(index + 1) of \(total). \(a11y)")
    }

    // MARK: - Outcome (eliminated / final standing)

    @ViewBuilder
    private var outcomeNote: some View {
        let message: String = {
            switch team.fate {
            case .champion:          return "\(teamName) won the tournament. There are no more matches to play."
            case .runnerUp:          return "\(teamName) reached the Final but finished as runner-up."
            case .thirdPlace:        return "\(teamName) finished third."
            case .fourthPlace:       return "\(teamName) finished fourth."
            case .eliminatedInGroup: return "\(teamName) did not advance from the group stage."
            case .eliminated(let r): return "\(teamName) was eliminated in the \(r.label)."
            case .alive:             return ""
            }
        }()
        if !message.isEmpty {
            Text(message)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityLabel(message)
        }
    }

    // MARK: - Tournament history

    private var historyItems: [(label: String, game: Game)] {
        var items: [(label: String, date: Date, game: Game)] = []
        // Group-stage games (completed) from the fetch.
        for g in viewModel.groupGames where g.status.isCompleted {
            items.append(("Group Stage", g.date, g))
        }
        // Knockout games (completed) from the bracket.
        for m in bracket.playedMatches(forTeamId: team.id) where m.isCompleted {
            items.append((m.round.label, m.game.date, m.game))
        }
        return items.sorted { $0.date < $1.date }.map { (label: $0.label, game: $0.game) }
    }

    @ViewBuilder
    private var historySection: some View {
        let items = historyItems
        sectionHeading("Tournament History")
        if viewModel.isLoading && items.isEmpty {
            Text("Loading history…")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .accessibilityLabel("Loading history")
        } else if items.isEmpty {
            Text("No completed matches yet.")
                .font(.subheadline)
                .foregroundColor(.secondary)
        } else {
            ForEach(Array(items.enumerated()), id: \.offset) { _, item in
                historyRow(label: item.label, game: item.game)
            }
        }
    }

    private func historyRow(label: String, game: Game) -> some View {
        let line = historyLine(label: label, game: game)
        return HStack(alignment: .top, spacing: 8) {
            Text(label)
                .font(.caption.bold())
                .foregroundColor(.secondary)
                .frame(width: 96, alignment: .leading)
                .fixedSize(horizontal: false, vertical: true)
            Text(line.visual)
                .font(.subheadline)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, 6)
        .padding(.horizontal, 10)
        .background(Color.secondary.opacity(0.05), in: RoundedRectangle(cornerRadius: 8))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(label). \(line.voice)")
    }

    /// Result of a completed game from this team's perspective.
    private func historyLine(label: String, game: Game) -> (visual: String, voice: String) {
        let teamIsHome = game.homeTeam.id == team.id
        let me  = teamIsHome ? game.homeTeam : game.awayTeam
        let opp = teamIsHome ? game.awayTeam : game.homeTeam
        let oppName = opp.voiceOverName(for: pref)

        guard let ms = me.score, let os = opp.score else {
            return ("vs \(oppName)", "versus \(oppName)")
        }

        let result: String
        if ms > os { result = "Won" }
        else if ms < os { result = "Lost" }
        else if me.isWinner == true { result = "Won on penalties" }
        else if opp.isWinner == true { result = "Lost on penalties" }
        else { result = "Drew" }

        let visual = "\(result) \(ms)–\(os) vs \(oppName)"
        let voice  = "\(result), \(ms) to \(os), versus \(oppName)"
        return (visual, voice)
    }

    // MARK: - Helpers

    private func sectionHeading(_ text: String) -> some View {
        Text(text)
            .font(.headline)
            .frame(maxWidth: .infinity, alignment: .leading)
            .accessibilityAddTraits(.isHeader)
    }
}
