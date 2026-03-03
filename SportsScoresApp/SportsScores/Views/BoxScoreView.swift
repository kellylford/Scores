//
//  BoxScoreView.swift
//  SportsScores
//
//  Renders a game box score as a proper table using SwiftUI Grid (iOS 16+).
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
            // Column header row
            Grid(alignment: .leading, horizontalSpacing: 8, verticalSpacing: 0) {
                GridRow {
                    Text("Stat")
                        .font(.caption.bold())
                        .foregroundColor(.secondary)
                        .gridCellColumns(1)
                    ForEach(teams, id: \.team.displayName) { team in
                        Text(team.team.abbreviation)
                            .font(.caption.bold())
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .trailing)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 6)
                .background(Color.secondary.opacity(0.12))
                .accessibilityHidden(true) // team names are in every row label

                Divider()

                // Iterate through categories from first team; align values by category.name
                let categories = teams.first?.statistics ?? []
                let catCount = categories.count
                ForEach(Array(categories.enumerated()), id: \.element.name) { catIdx, cat in
                    if let items = cat.stats, !items.isEmpty {
                        // Category sub-header
                        GridRow {
                            Text(cat.groupTitle.uppercased())
                                .font(.caption2.bold())
                                .foregroundColor(.secondary)
                                .gridCellColumns(1 + teams.count)
                        }
                        .padding(.horizontal, 16)
                        .padding(.top, 8)
                        .padding(.bottom, 2)
                        .accessibilityElement(children: .ignore)
                        .accessibilityLabel(cat.groupTitle)
                        .accessibilityAddTraits(.isHeader)

                        // Stat rows
                        ForEach(Array(items.enumerated()), id: \.element.name) { rowIdx, stat in
                            GridRow {
                                Text(stat.displayName)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                    .accessibilityHidden(true)
                                ForEach(teams, id: \.team.displayName) { team in
                                    let matchedStat = team.statistics
                                        .first(where: { $0.name == cat.name })?
                                        .stats?
                                        .first(where: { $0.name == stat.name })
                                    Text(matchedStat?.displayValue ?? "–")
                                        .font(.caption.monospacedDigit())
                                        .frame(maxWidth: .infinity, alignment: .trailing)
                                        .accessibilityHidden(true)
                                }
                            }
                            .padding(.horizontal, 16)
                            .padding(.vertical, 4)
                            .background((rowIdx % 2 == 0) ? Color.clear : Color.secondary.opacity(0.04))
                            .accessibilityElement(children: .ignore)
                            .accessibilityLabel({
                                let parts = teams.map { team -> String in
                                    let v = team.statistics
                                        .first(where: { $0.name == cat.name })?
                                        .stats?
                                        .first(where: { $0.name == stat.name })?
                                        .displayValue ?? "–"
                                    return "\(team.team.abbreviation) \(v)"
                                }
                                return "\(stat.displayName): \(parts.joined(separator: ", "))"
                            }())
                        }

                        if catIdx < catCount - 1 {
                            Divider().padding(.horizontal, 16).padding(.top, 4)
                        }
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
            // Header row with team names
            Grid(alignment: .leading, horizontalSpacing: 8, verticalSpacing: 0) {
                GridRow {
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
                .accessibilityHidden(true) // team names are in every row label

                Divider()

                // Stat rows
                let rows = teams.first?.statistics ?? []
                ForEach(Array(rows.enumerated()), id: \.element.name) { rowIdx, stat in
                    GridRow {
                        Text(stat.label ?? stat.displayName ?? stat.name)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .accessibilityHidden(true)
                        ForEach(teams, id: \.team.displayName) { team in
                            let matchedStat = team.statistics
                                .first(where: { $0.name == stat.name })
                            Text(matchedStat?.displayValue ?? "–")
                                .font(.caption.monospacedDigit())
                                .frame(minWidth: 60, alignment: .trailing)
                                .accessibilityHidden(true)
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 4)
                    .background((rowIdx % 2 == 0) ? Color.clear : Color.secondary.opacity(0.04))
                    .accessibilityElement(children: .ignore)
                    .accessibilityLabel({
                        let statName = stat.label ?? stat.displayName ?? stat.name
                        let parts = teams.map { team -> String in
                            let v = team.statistics
                                .first(where: { $0.name == stat.name })?
                                .displayValue ?? "–"
                            return "\(team.team.abbreviation) \(v)"
                        }
                        return "\(statName): \(parts.joined(separator: ", "))"
                    }())
                }
            }
        }
        .background(Color.secondary.opacity(0.04))
        .cornerRadius(12)
        .padding()
    }
}
