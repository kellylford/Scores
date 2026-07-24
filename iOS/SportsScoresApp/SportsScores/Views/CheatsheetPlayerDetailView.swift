//
//  CheatsheetPlayerDetailView.swift
//  SportsScores
//
//  Detail screen for a single cheatsheet row (player or D/ST). Surfaces the
//  draft data ESPN's fantasy feed provides — consensus ranks, ADP, auction
//  value, and season projections for each scoring format — plus a taken/available
//  toggle for live drafts.
//
//  Value tables are presented as an AccessibleDataTable (two-column key/value
//  grid) so VoiceOver users get proper row navigation rather than a flat label.
//

import SwiftUI

struct CheatsheetPlayerDetailView: View {
    let player: CheatsheetPlayer
    @ObservedObject var viewModel: FantasyCheatsheetViewModel
    @Environment(\.dismiss) private var dismiss

    private var preset: ScoringPreset { viewModel.preset }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                headerCard
                projectedPointsCard
                draftValuesSection
                projectionsSection
            }
            .padding(.vertical, 16)
        }
        .navigationTitle(player.displayName)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(viewModel.isTaken(player) ? "Mark Available" : "Mark Taken") {
                    viewModel.toggleTaken(player)
                }
            }
        }
    }

    // MARK: - Header card

    private var headerCard: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline) {
                Text(player.displayName)
                    .font(.title2.bold())
                Spacer()
                takenBadge
            }
            Text("\(player.position.displayName) · \(player.teamAbbreviation)")
                .font(.subheadline)
                .foregroundColor(.secondary)
            if player.isDST {
                Text("Team defense / special teams")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            if let injury = player.injuryStatus {
                Label(injury, systemImage: "cross.case")
                    .font(.caption.bold())
                    .foregroundColor(.orange)
            }
        }
        .padding(16)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
        .padding(.horizontal, 16)
    }

    private var takenBadge: some View {
        Group {
            if viewModel.isTaken(player) {
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

    // MARK: - Projected points card (current format)

    private var projectedPointsCard: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("Projected Points · \(preset.rawValue)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text(player.projectedPointsString(for: preset))
                    .font(.system(.title, design: .monospaced).bold())
                    .foregroundColor(.accentColor)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 2) {
                if let rank = player.rank(for: preset) {
                    Text("#\(rank)")
                        .font(.title3.bold())
                    Text("\(preset.rawValue) rank")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(16)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
        .padding(.horizontal, 16)
        .accessibilityElement(children: .combine)
    }

    // MARK: - Draft values

    private var draftValuesSection: some View {
        valueTable(
            title: "Draft Values",
            rows: [
                ("PPR Rank", player.pprRank.map { "#\($0)" } ?? "—"),
                ("Standard Rank", player.standardRank.map { "#\($0)" } ?? "—"),
                ("ADP", player.adpString),
                ("Auction Value", player.auctionString),
            ]
        )
    }

    // MARK: - Projections per format

    private var projectionsSection: some View {
        valueTable(
            title: "Projected Points by Format",
            rows: ScoringPreset.allCases.map { fmt in
                (fmt.rawValue, player.projectedPointsString(for: fmt))
            }
        )
    }

    // MARK: - Reusable value table

    private func valueTable(title: String, rows: [(String, String)]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
                .padding(.horizontal, 16)
                .accessibilityAddTraits(.isHeader)

            VStack(spacing: 0) {
                ForEach(Array(rows.enumerated()), id: \.offset) { idx, row in
                    HStack {
                        Text(row.0)
                            .font(.subheadline)
                            .foregroundColor(.primary)
                        Spacer()
                        Text(row.1)
                            .font(.system(.subheadline, design: .monospaced))
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 8)
                    .padding(.horizontal, 12)
                    .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
                }
            }
            .accessibilityHidden(true)
            .overlay(
                AccessibleDataTable(
                    headers: ["Field", "Value"],
                    rows: rows.map { [$0.0, $0.1] }
                )
                .allowsHitTesting(false)
            )
            .padding(.horizontal, 16)
        }
    }
}
