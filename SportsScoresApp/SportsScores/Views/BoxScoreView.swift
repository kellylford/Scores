//
//  BoxScoreView.swift
//  SportsScores
//
//  Renders a game box score as an HStack-based table.
//
//  IMPORTANT: Grid/GridRow are layout-only constructs — modifiers placed on a
//  GridRow do NOT create a real accessibility node, so children remain flat
//  children of the Grid and VoiceOver reads every cell independently.
//  This file uses plain HStack rows instead, which ARE real view containers
//  and correctly honour .accessibilityElement(children: .ignore).
//
//  Two ESPN stat shapes are handled:
//    MLB:        statistics = [{name, displayName, stats:[{name, displayName, displayValue}]}]
//                Rendered as: category subheading + rows of stat | value per team
//    NFL/NBA/NHL: statistics = [{name, label, displayValue}]  (flat rows per team)
//                Rendered as: stat name | team1 | team2 header + value rows
//

import SwiftUI

struct BoxScoreView: View {
    let boxscore: GameDetails.Boxscore

    var body: some View {
        ScrollView {
            if boxscore.teams.isEmpty {
                Text("Box score not available")
                    .foregroundColor(.secondary)
                    .padding()
            } else if boxscore.teams.first?.statistics.first?.isNested == true {
                mlbTable
            } else {
                flatTable
            }
        }
    }

    // MARK: - MLB nested-category table
    // Layout: Each category (Batting, Pitching…) is a section; each stat is a
    // row with Stat | Team A | Team B values side by side.

    private var mlbTable: some View {
        let teams = boxscore.teams
        return VStack(alignment: .leading, spacing: 0) {

            // Column header row — hidden from VoiceOver; team names appear in every row label
            HStack(spacing: 0) {
                Text("Stat")
                    .font(.caption.bold())
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                ForEach(teams, id: \.team.displayName) { team in
                    Text(team.team.abbreviation)
                        .font(.caption.bold())
                        .foregroundColor(.secondary)
                        .frame(minWidth: 60, alignment: .trailing)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 6)
            .background(Color.secondary.opacity(0.12))
            .accessibilityHidden(true)

            Divider()

            // Iterate through categories from first team; align values by category.name
            let categories = teams.first?.statistics ?? []
            let catCount = categories.count
            ForEach(Array(categories.enumerated()), id: \.element.name) { catIdx, cat in
                if let items = cat.stats, !items.isEmpty {

                    // Category sub-header
                    Text(cat.groupTitle.uppercased())
                        .font(.caption2.bold())
                        .foregroundColor(.secondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal, 16)
                        .padding(.top, 8)
                        .padding(.bottom, 2)
                        .accessibilityAddTraits(.isHeader)
                        .accessibilityLabel(cat.groupTitle)

                    // Stat rows — each HStack is a single accessibility element
                    ForEach(Array(items.enumerated()), id: \.element.name) { rowIdx, stat in
                        let rowLabel: String = {
                            let parts = teams.map { team -> String in
                                let v = team.statistics
                                    .first(where: { $0.name == cat.name })?
                                    .stats?
                                    .first(where: { $0.name == stat.name })?
                                    .displayValue ?? "–"
                                return "\(team.team.abbreviation) \(v)"
                            }
                            return "\(stat.displayName): \(parts.joined(separator: ", "))"
                        }()

                        HStack(spacing: 0) {
                            Text(stat.displayName)
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                            ForEach(teams, id: \.team.displayName) { team in
                                let matchedStat = team.statistics
                                    .first(where: { $0.name == cat.name })?
                                    .stats?
                                    .first(where: { $0.name == stat.name })
                                Text(matchedStat?.displayValue ?? "–")
                                    .font(.caption.monospacedDigit())
                                    .frame(minWidth: 60, alignment: .trailing)
                            }
                        }
                        .padding(.horizontal, 16)
                        .padding(.vertical, 4)
                        .background((rowIdx % 2 == 0) ? Color.clear : Color.secondary.opacity(0.04))
                        .accessibilityElement(children: .ignore)
                        .accessibilityLabel(rowLabel)
                    }

                    if catIdx < catCount - 1 {
                        Divider().padding(.horizontal, 16).padding(.top, 4)
                    }
                }
            }
        }
        .background(Color.secondary.opacity(0.04))
        .cornerRadius(12)
        .padding()
    }

    // MARK: - Flat table (NFL / NBA / NHL)
    // Layout: Stat label | Team A value | Team B value

    private var flatTable: some View {
        let teams = boxscore.teams
        return VStack(spacing: 0) {

            // Header row — hidden from VoiceOver; team names appear in every row label
            HStack(spacing: 0) {
                Text("")
                    .frame(maxWidth: .infinity, alignment: .leading)
                ForEach(teams, id: \.team.displayName) { team in
                    Text(team.team.abbreviation)
                        .font(.subheadline.bold())
                        .frame(minWidth: 60, alignment: .trailing)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(Color.secondary.opacity(0.12))
            .accessibilityHidden(true)

            Divider()

            // Stat rows — each HStack is a single accessibility element
            let rows = teams.first?.statistics ?? []
            ForEach(Array(rows.enumerated()), id: \.element.name) { rowIdx, stat in
                let statName = stat.label ?? stat.displayName ?? stat.name
                let rowLabel: String = {
                    let parts = teams.map { team -> String in
                        let v = team.statistics
                            .first(where: { $0.name == stat.name })?
                            .displayValue ?? "–"
                        return "\(team.team.abbreviation) \(v)"
                    }
                    return "\(statName): \(parts.joined(separator: ", "))"
                }()

                HStack(spacing: 0) {
                    Text(statName)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    ForEach(teams, id: \.team.displayName) { team in
                        let matchedStat = team.statistics
                            .first(where: { $0.name == stat.name })
                        Text(matchedStat?.displayValue ?? "–")
                            .font(.caption.monospacedDigit())
                            .frame(minWidth: 60, alignment: .trailing)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 4)
                .background((rowIdx % 2 == 0) ? Color.clear : Color.secondary.opacity(0.04))
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(rowLabel)
            }
        }
        .background(Color.secondary.opacity(0.04))
        .cornerRadius(12)
        .padding()
    }
}
