//
//  CheatsheetPlayerDetailView.swift
//  SportsScores
//
//  Detail sheet for a single cheatsheet row (player or D/ST). Shows the full
//  stat line used to compute fantasy points. For players whose stats haven't
//  been enriched yet, fetches them on demand. Supports marking taken/available.
//
//  Stats are presented as an AccessibleDataTable (two-column key/value grid)
//  so VoiceOver users get proper row navigation rather than a flat label dump.
//

import SwiftUI

struct CheatsheetPlayerDetailView: View {
    let row: CheatsheetRow
    @ObservedObject var viewModel: FantasyCheatsheetViewModel
    @Environment(\.dismiss) private var dismiss

    @State private var isEnriching = false
    @State private var enrichError: String?

    private var settings: FantasyScoringSettings { viewModel.scoringSettings }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    headerCard
                    fantasyPointsCard
                    statsSection
                    if let err = enrichError {
                        Text(err)
                            .font(.caption)
                            .foregroundColor(.red)
                            .padding(.horizontal)
                    }
                }
                .padding(.vertical, 16)
            }
            .navigationTitle(row.displayName)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(viewModel.isTaken(row) ? "Mark Available" : "Mark Taken") {
                        viewModel.toggleTaken(row)
                    }
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                }
            }
            .task { await enrichIfNeeded() }
        }
    }

    // MARK: - Header card

    private var headerCard: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline) {
                Text(row.displayName)
                    .font(.title2.bold())
                Spacer()
                takenBadge
            }
            Text("\(row.positionLabel) · \(row.teamAbbreviation)")
                .font(.subheadline)
                .foregroundColor(.secondary)
            switch row {
            case .player(let p):
                if let exp = p.experienceYears {
                    Text(exp == 0 ? "Rookie" : "Year \(exp)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            case .defense:
                Text("Team defense / special teams")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(16)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
        .padding(.horizontal, 16)
    }

    private var takenBadge: some View {
        Group {
            if viewModel.isTaken(row) {
                Label("Taken", systemImage: "checkmark.circle.fill")
                    .labelStyle(.titleAndIcon)
                    .font(.caption.bold())
                    .foregroundColor(.green)
            } else {
                Label("Available", systemImage: "circle")
                    .labelStyle(.titleAndIcon)
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
            }
        }
        .accessibilityHidden(true)
    }

    // MARK: - Fantasy points card

    private var fantasyPointsCard: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("Fantasy Points")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text(row.pointsString(settings: settings))
                    .font(.system(.title, design: .monospaced).bold())
                    .foregroundColor(.accentColor)
            }
            Spacer()
            if isEnriching {
                ProgressView()
                    .accessibilityLabel("Loading stats")
            }
        }
        .padding(16)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
        .padding(.horizontal, 16)
    }

    // MARK: - Stats section (AccessibleDataTable)

    private var statsSection: some View {
        let statRows = sortedStatRows

        return VStack(alignment: .leading, spacing: 8) {
            Text("Stat Line")
                .font(.headline)
                .padding(.horizontal, 16)
                .accessibilityAddTraits(.isHeader)

            if statRows.isEmpty {
                Text(isEnriching ? "Loading stats…" : "No stats available")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .padding(.horizontal, 16)
            } else {
                // Visual two-column grid
                VStack(spacing: 0) {
                    HStack {
                        Text("Stat").font(.caption.bold()).foregroundColor(.secondary)
                        Spacer()
                        Text("Value").font(.caption.bold()).foregroundColor(.secondary)
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 6)

                    ForEach(Array(statRows.enumerated()), id: \.offset) { idx, row in
                        statVisualRow(idx, row)
                    }
                }
                .accessibilityHidden(true)
                .overlay(
                    AccessibleDataTable(
                        headers: ["Stat", "Value"],
                        rows: statRows.map { [$0.0, $0.1] }
                    )
                    .allowsHitTesting(false)
                )
                .padding(.horizontal, 16)
            }
        }
    }

    private func statVisualRow(_ idx: Int, _ row: (String, String)) -> some View {
        HStack {
            Text(row.0)
                .font(.subheadline)
                .foregroundColor(.primary)
            Spacer()
            Text(row.1)
                .font(.system(.subheadline, design: .monospaced))
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 6)
        .padding(.horizontal, 12)
        .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
        .accessibilityHidden(true)
    }

    // MARK: - Stat rows (filtered to fantasy-relevant keys)

    /// Returns (label, value) tuples for the fantasy-relevant stats this row has.
    private var sortedStatRows: [(String, String)] {
        switch row {
        case .player(let p): return playerStatRows(p)
        case .defense(let d): return defenseStatRows(d)
        }
    }

    private func playerStatRows(_ player: CheatsheetPlayer) -> [(String, String)] {
        let s = player.stats
        let keys: [(String, String)] = [
            ("passingYards", "Passing Yards"),
            ("passingTouchdowns", "Passing TDs"),
            ("interceptions", "Interceptions"),
            ("rushingYards", "Rushing Yards"),
            ("rushingTouchdowns", "Rushing TDs"),
            ("receptions", "Receptions"),
            ("receivingYards", "Receiving Yards"),
            ("receivingTouchdowns", "Receiving TDs"),
            ("fieldGoalsMade", "Field Goals Made"),
            ("extraPointsMade", "Extra Points Made"),
            ("totalTouchdowns", "Total TDs"),
            ("gamesPlayed", "Games Played"),
        ]
        return keys.compactMap { key, label in
            guard let v = s[key] else { return nil }
            return (label, formatStat(v))
        }
    }

    private func defenseStatRows(_ defense: CheatsheetTeamDefense) -> [(String, String)] {
        let s = defense.stats
        let keys: [(String, String)] = [
            ("sacks", "Sacks"),
            ("interceptions", "Interceptions"),
            ("fumblesRecovered", "Fumbles Recovered"),
            ("safeties", "Safeties"),
            ("defensiveTouchdowns", "Defensive TDs"),
            ("interceptionTouchdowns", "INT TDs"),
            ("kickReturnTouchdowns", "Kick Return TDs"),
            ("pointsAllowed", "Points Allowed"),
            ("totalTackles", "Total Tackles"),
        ]
        return keys.compactMap { key, label in
            guard let v = s[key] else { return nil }
            return (label, formatStat(v))
        }
    }

    private func formatStat(_ v: Double) -> String {
        if v == floor(v) { return "\(Int(v))" }
        return String(format: "%.1f", v)
    }

    // MARK: - Lazy enrichment

    /// If the row has no stats yet (a non-leaders player), fetch them on demand.
    private func enrichIfNeeded() async {
        switch row {
        case .player(let p):
            guard p.stats.isEmpty else { return }
            isEnriching = true
            defer { isEnriching = false }
            await viewModel.enrichPlayer(p)
            if let idx = viewModel.offensivePlayers.firstIndex(where: { $0.id == p.id }),
               viewModel.offensivePlayers[idx].stats.isEmpty {
                enrichError = "No stats found for this player this season."
            }
        case .defense(let d):
            guard d.stats.isEmpty else { return }
            isEnriching = true
            defer { isEnriching = false }
            await viewModel.enrichTeamDefense(d)
            if let idx = viewModel.teamDefenses.firstIndex(where: { $0.id == d.id }),
               viewModel.teamDefenses[idx].stats.isEmpty {
                enrichError = "No defensive stats found for this team this season."
            }
        }
    }
}