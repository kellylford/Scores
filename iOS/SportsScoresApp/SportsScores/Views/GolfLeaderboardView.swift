//
//  GolfLeaderboardView.swift
//  SportsScores
//
//  Three-view accessible leaderboard for golf tournaments.
//  Mirrors the StandingsTableView pattern: visual grid hidden from VoiceOver,
//  AccessibleDataTable UIKit overlay provides proper row/column navigation.
//
//  View modes:
//    • Table   — grid: Pos | Player | Score | R1 | R2 | R3 | R4
//    • Quick List — compact: "1. Cameron Young (USA)  -12  67 / 69 / 68 / 71"
//    • Full List  — player cards with all round detail
//

import SwiftUI

struct GolfLeaderboardView: View {

    let tournament: GolfTournament
    @State private var viewMode: ViewMode = .table

    // MARK: - Column definitions

    private let headers = ["Pos", "Player", "Ctry", "Score", "R1", "R2", "R3", "R4"]

    private func rowData(for competitor: GolfCompetitor) -> [String] {
        [
            competitor.positionDisplay,
            competitor.shortName,
            competitor.country,
            competitor.overallScore,
            competitor.roundScore(for: 1),
            competitor.roundScore(for: 2),
            competitor.roundScore(for: 3),
            competitor.roundScore(for: 4)
        ]
    }

    /// Full names + thru-hole annotation for the AccessibleDataTable overlay.
    private func accessibleRowData(for competitor: GolfCompetitor) -> [String] {
        var cols = rowData(for: competitor)
        if cols.count > 1 { cols[1] = competitor.playerName }
        // Annotate the Score cell with "thru N holes" when in progress
        if let progress = competitor.currentRoundProgress, tournament.isInProgress,
           let scoreIdx = headers.firstIndex(of: "Score") {
            cols[scoreIdx] = "\(competitor.overallScore), through \(progress.holesPlayed) holes"
        }
        return cols
    }

    var body: some View {
        VStack(spacing: 0) {
            ViewModePicker(selectedMode: $viewMode)
                .padding(.vertical, 8)

            Divider()

            // Status banner
            if !tournament.isScheduled {
                tournamentStatusBanner
            }

            ScrollView {
                switch viewMode {
                case .table:
                    leaderboardTable
                case .quickList:
                    quickListContent
                case .fullList:
                    fullListContent
                }
            }
        }
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                ViewModeToggleButton(currentMode: $viewMode)
            }
        }
    }

    // MARK: - Status Banner

    private var tournamentStatusBanner: some View {
        VStack(spacing: 2) {
            HStack {
                if tournament.isInProgress {
                    Circle()
                        .fill(Color.red)
                        .frame(width: 8, height: 8)
                }
                Text(tournament.roundStatusText)
                    .font(.caption.bold())
                    .foregroundColor(tournament.isInProgress ? .red : .secondary)
                Spacer()
                if !tournament.broadcastText.isEmpty {
                    Text(tournament.broadcastText)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 6)
        .background(Color.secondary.opacity(0.07))
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(tournament.roundStatusText)\(tournament.broadcastText.isEmpty ? "" : ". Broadcast: \(tournament.broadcastText)")")
    }

    // MARK: - Empty / Scheduled state

    private var scheduledPlaceholder: some View {
        VStack(spacing: 16) {
            Image(systemName: "calendar.badge.clock")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("Leaderboard Not Yet Available")
                .font(.headline)
                .foregroundColor(.secondary)
            Text("The field has not been announced yet.\nCheck back closer to the tournament start date.")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding(.top, 48)
        .padding(.horizontal, 24)
    }

    // MARK: - Table mode

    private var leaderboardTable: some View {
        Group {
            if tournament.competitors.isEmpty {
                scheduledPlaceholder
            } else {
                tableGrid
            }
        }
    }

    private var tableGrid: some View {
        VStack(spacing: 0) {
            // Header row
            HStack(spacing: 0) {
                Text("Pos").font(.caption.bold()).frame(width: 36)
                Text("Player").font(.caption.bold()).frame(maxWidth: .infinity, alignment: .leading).padding(.leading, 8)
                Text("Ctry").font(.caption.bold()).frame(width: 38)
                Text("Score").font(.caption.bold()).frame(width: 48)
                ForEach(1...4, id: \.self) { round in
                    Text("R\(round)").font(.caption.bold()).frame(width: 38)
                }
            }
            .padding(.vertical, 6)
            .padding(.horizontal, 8)
            .background(Color.secondary.opacity(0.15))

            Divider()

            let activeCompetitors = tournament.competitors.filter(\.isActive)
            let cutCompetitors    = tournament.competitors.filter { $0.isCut || $0.isWithdrawn }

            VStack(spacing: 0) {
                ForEach(Array(activeCompetitors.enumerated()), id: \.element.id) { idx, comp in
                    competitorRow(comp, at: idx)
                    if idx < activeCompetitors.count - 1 {
                        Divider().padding(.leading, 8)
                    }
                }

                if !cutCompetitors.isEmpty {
                    // Cut / WD divider
                    HStack {
                        Divider()
                        Text("– CUT / WD –")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                            .padding(.horizontal, 8)
                        Divider()
                    }
                    .padding(.vertical, 4)
                    .accessibilityLabel("Cut line")

                    ForEach(Array(cutCompetitors.enumerated()), id: \.element.id) { idx, comp in
                        competitorRow(comp, at: activeCompetitors.count + idx)
                        if idx < cutCompetitors.count - 1 {
                            Divider().padding(.leading, 8)
                        }
                    }
                }
            }
            .accessibilityHidden(true) // UIKit overlay handles VoiceOver
        }
        .accessibilityHidden(true)
        .overlay(
            AccessibleDataTable(
                headers: headers,
                rows: tournament.competitors.map { accessibleRowData(for: $0) }
            )
            .allowsHitTesting(false)
        )
        .padding(.bottom, 16)
    }

    private func competitorRow(_ comp: GolfCompetitor, at idx: Int) -> some View {
        HStack(spacing: 0) {
            // Position
            Text(comp.positionDisplay)
                .font(.caption.monospacedDigit())
                .frame(width: 36)
                .foregroundColor(positionColor(comp.position))

            // Player name
            Text(comp.shortName)
                .font(.subheadline)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.leading, 8)
                .lineLimit(1)
                .foregroundColor(comp.isActive ? .primary : .secondary)

            // Country
            Text(comp.country.prefix(3).uppercased())
                .font(.caption2)
                .foregroundColor(.secondary)
                .frame(width: 38)

            // Overall score
            VStack(spacing: 1) {
                Text(comp.overallScore)
                    .font(.subheadline.monospacedDigit().bold())
                    .foregroundColor(scoreColor(comp.overallScore))
                if let progress = comp.currentRoundProgress, tournament.isInProgress {
                    Text("T\(progress.holesPlayed)")
                        .font(.caption2.monospacedDigit())
                        .foregroundColor(.secondary)
                }
            }
            .frame(width: 48)

            // Round scores
            ForEach(1...4, id: \.self) { round in
                Text(comp.roundScore(for: round))
                    .font(.caption.monospacedDigit())
                    .frame(width: 38)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 7)
        .padding(.horizontal, 8)
        .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
    }

    // MARK: - Quick List mode

    private var quickListContent: some View {
        Group {
            if tournament.competitors.isEmpty {
                scheduledPlaceholder
            } else {
                VStack(alignment: .leading, spacing: 4) {
                    ForEach(tournament.competitors) { comp in
                        Text(comp.quickListText)
                            .font(.subheadline.monospacedDigit())
                            .padding(.horizontal, 16)
                            .padding(.vertical, 6)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .accessibilityLabel(comp.quickListText)
                    }
                }
                .padding(.vertical, 8)
            }
        }
    }

    // MARK: - Full List mode

    private var fullListContent: some View {
        Group {
            if tournament.competitors.isEmpty {
                scheduledPlaceholder
            } else {
                VStack(alignment: .leading, spacing: 8) {
                    ForEach(tournament.competitors) { comp in
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text(comp.positionDisplay)
                                    .font(.headline.monospacedDigit())
                                    .foregroundColor(positionColor(comp.position))
                                Text(comp.playerName)
                                    .font(.headline)
                                Spacer()
                                Text(comp.overallScore)
                                    .font(.title3.bold().monospacedDigit())
                                    .foregroundColor(scoreColor(comp.overallScore))
                            }

                            if !comp.country.isEmpty {
                                Text(comp.country)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }

                            if !comp.rounds.isEmpty {
                                HStack(spacing: 16) {
                                    ForEach(comp.rounds) { round in
                                        VStack(spacing: 2) {
                                            Text(round.label)
                                                .font(.caption2)
                                                .foregroundColor(.secondary)
                                            Text(round.isComplete ? round.displayScore : "--")
                                                .font(.subheadline.monospacedDigit())
                                                .foregroundColor(scoreColor(round.displayScore))
                                            if round.isComplete {
                                                Text("(\(round.strokes))")
                                                    .font(.caption2)
                                                    .foregroundColor(.secondary)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.secondary.opacity(0.05))
                        .cornerRadius(8)
                        .padding(.horizontal, 12)
                        .accessibilityElement(children: .ignore)
                        .accessibilityLabel("\(comp.positionDisplay). \(comp.playerName). \(comp.country). \(comp.fullListText)")
                    }
                }
                .padding(.vertical, 8)
            }
        }
    }

    // MARK: - Color helpers

    private func positionColor(_ position: Int) -> Color {
        switch position {
        case 1:  return .yellow
        case 2, 3: return Color(red: 0.75, green: 0.75, blue: 0.75)
        default: return .secondary
        }
    }

    private func scoreColor(_ score: String) -> Color {
        if score.hasPrefix("-") { return .red }
        if score.hasPrefix("+") { return .blue }
        if score == "E"         { return .primary }
        return .secondary
    }
}
