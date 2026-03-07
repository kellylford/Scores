//
//  BoxScoreView.swift
//  SportsScores
//
//  Renders game box score with player statistics followed by team statistics.
//  Organized in a clear, hierarchical structure for better accessibility.
//

import SwiftUI

struct BoxScoreView: View {
    let boxscore: GameDetails.Boxscore

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                if boxscore.teams.isEmpty {
                    Text("Box score not available")
                        .foregroundColor(.secondary)
                        .padding()
                } else {
                    // Player Statistics Section
                    if let players = boxscore.players, !players.isEmpty {
                        playerStatsSection(players: players)
                    }
                    
                    // Team Statistics Section
                    teamStatsSection
                }
            }
            .padding()
        }
    }

    // MARK: - Team Statistics Section
    
    private var teamStatsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Team Statistics")
                .font(.title2.bold())
                .accessibilityAddTraits(.isHeader)
            
            if boxscore.teams.first?.statistics.first?.isNested == true {
                // MLB nested format
                mlbTeamStats
            } else {
                // Flat format (NFL/NBA/NHL)
                flatTeamStats
            }
        }
    }
    
    // MARK: - MLB Team Stats (nested categories)
    
    private var mlbTeamStats: some View {
        let teams = boxscore.teams
        let categories = teams.first?.statistics ?? []
        
        return VStack(alignment: .leading, spacing: 16) {
            ForEach(Array(categories.enumerated()), id: \.element.name) { catIdx, cat in
                if let items = cat.stats, !items.isEmpty {
                    let tableHeaders = ["Stat"] + teams.map { $0.team.abbreviation }
                    let tableRows = items.map { stat in
                        [stat.displayName] + teams.map { team in
                            team.statistics
                                .first(where: { $0.name == cat.name })?
                                .stats?
                                .first(where: { $0.name == stat.name })?
                                .displayValue ?? "-"
                        }
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        // Category header
                        Text(cat.groupTitle)
                            .font(.headline)
                            .foregroundColor(.primary)
                            .accessibilityAddTraits(.isHeader)
                        
                        // Stats table
                        VStack(spacing: 0) {
                            // Header row
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
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(Color.secondary.opacity(0.12))
                            .accessibilityHidden(true)
                            
                            // Data rows
                            ForEach(Array(items.enumerated()), id: \.element.name) { rowIdx, stat in
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
                                .padding(.horizontal, 12)
                                .padding(.vertical, 4)
                                .background((rowIdx % 2 == 0) ? Color.clear : Color.secondary.opacity(0.04))
                                .accessibilityHidden(true)
                            }
                        }
                        .background(Color.secondary.opacity(0.04))
                        .cornerRadius(8)
                        .accessibilityHidden(true)
                        .overlay(
                            AccessibleDataTable(headers: tableHeaders, rows: tableRows)
                                .allowsHitTesting(false)
                        )
                    }
                    
                    if catIdx < categories.count - 1 {
                        Divider().padding(.vertical, 4)
                    }
                }
            }
        }
    }
    
    // MARK: - Flat Team Stats (NFL/NBA/NHL)
    
    private var flatTeamStats: some View {
        let teams = boxscore.teams
        let rows = teams.first?.statistics ?? []
        let tableHeaders = [""] + teams.map { $0.team.abbreviation }
        let tableRows = rows.map { stat in
            let statName = stat.label ?? stat.displayName ?? stat.name
            return [statName] + teams.map { team in
                team.statistics
                    .first(where: { $0.name == stat.name })?
                    .displayValue ?? "-"
            }
        }
        
        return VStack(spacing: 0) {
            // Header row
            HStack(spacing: 0) {
                Text("")
                    .frame(maxWidth: .infinity, alignment: .leading)
                ForEach(teams, id: \.team.displayName) { team in
                    Text(team.team.abbreviation)
                        .font(.subheadline.bold())
                        .frame(minWidth: 70, alignment: .trailing)
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color.secondary.opacity(0.12))
            .accessibilityHidden(true)
            
            // Data rows
            ForEach(Array(rows.enumerated()), id: \.element.name) { rowIdx, stat in
                let statName = stat.label ?? stat.displayName ?? stat.name
                
                HStack(spacing: 0) {
                    Text(statName)
                        .font(.caption)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    ForEach(teams, id: \.team.displayName) { team in
                        let matchedStat = team.statistics
                            .first(where: { $0.name == stat.name })
                        Text(matchedStat?.displayValue ?? "–")
                            .font(.caption.monospacedDigit())
                            .frame(minWidth: 70, alignment: .trailing)
                    }
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 4)
                .background((rowIdx % 2 == 0) ? Color.clear : Color.secondary.opacity(0.04))
                .accessibilityHidden(true)
            }
        }
        .background(Color.secondary.opacity(0.04))
        .cornerRadius(8)
        .accessibilityHidden(true)
        .overlay(
            AccessibleDataTable(headers: tableHeaders, rows: tableRows)
                .allowsHitTesting(false)
        )
    }
    
    // MARK: - Player Statistics Section
    
    private func playerStatsSection(players: [GameDetails.Boxscore.TeamPlayers]) -> some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Player Statistics")
                .font(.title2.bold())
                .accessibilityAddTraits(.isHeader)
            
            ForEach(players.indices, id: \.self) { teamIdx in
                let teamPlayers = players[teamIdx]
                playerStatsForTeam(teamPlayers: teamPlayers)
            }
        }
    }
    
    private func playerStatsForTeam(teamPlayers: GameDetails.Boxscore.TeamPlayers) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            // Team name header
            Text(teamPlayers.team.displayName)
                .font(.title3.bold())
                .foregroundColor(.primary)
                .accessibilityAddTraits(.isHeader)
            
            // Each stat group (Batting, Pitching, etc.)
            ForEach(teamPlayers.statistics.indices, id: \.self) { groupIdx in
                let statGroup = teamPlayers.statistics[groupIdx]
                playerStatGroupView(
                    teamName: teamPlayers.team.displayName,
                    statGroup: statGroup
                )
            }
        }
    }
    
    private func playerStatGroupView(teamName: String, statGroup: GameDetails.Boxscore.TeamPlayers.PlayerStatGroup) -> some View {
        let statNames = statGroup.names ?? []
        let athletes = statGroup.athletes.filter { $0.isActive }
        let tableHeaders = ["Player", "Pos"] + statNames
        let tableRows = athletes.map { athlete in
            [athlete.athlete.displayName, athlete.athlete.position?.abbreviation ?? ""] + athlete.stats
        }
        
        guard !athletes.isEmpty, !statNames.isEmpty else {
            return AnyView(EmptyView())
        }
        
        return AnyView(
            VStack(alignment: .leading, spacing: 8) {
                // Stat group header (e.g., "Batting", "Pitching")
                Text(statGroup.groupTitle)
                    .font(.headline)
                    .foregroundColor(.secondary)
                    .accessibilityAddTraits(.isHeader)
                
                ScrollView(.horizontal, showsIndicators: true) {
                    VStack(spacing: 0) {
                        // Header row
                        HStack(spacing: 0) {
                            Text("Player")
                                .font(.caption.bold())
                                .foregroundColor(.secondary)
                                .frame(width: 140, alignment: .leading)
                            
                            Text("Pos")
                                .font(.caption.bold())
                                .foregroundColor(.secondary)
                                .frame(width: 45, alignment: .center)
                            
                            ForEach(statNames.indices, id: \.self) { idx in
                                Text(statNames[idx])
                                    .font(.caption.bold())
                                    .foregroundColor(.secondary)
                                    .frame(width: 50, alignment: .trailing)
                            }
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.secondary.opacity(0.12))
                        .accessibilityHidden(true)
                        
                        // Player rows
                        ForEach(athletes.indices, id: \.self) { athleteIdx in
                            let athlete = athletes[athleteIdx]
                            
                            HStack(spacing: 0) {
                                Text(athlete.athlete.displayName)
                                    .font(.caption)
                                    .frame(width: 140, alignment: .leading)
                                    .lineLimit(1)
                                
                                Text(athlete.athlete.position?.abbreviation ?? "")
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                                    .frame(width: 45, alignment: .center)
                                
                                ForEach(athlete.stats.indices, id: \.self) { statIdx in
                                    Text(athlete.stats[statIdx])
                                        .font(.caption.monospacedDigit())
                                        .frame(width: 50, alignment: .trailing)
                                }
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 4)
                            .background((athleteIdx % 2 == 0) ? Color.clear : Color.secondary.opacity(0.04))
                            .accessibilityHidden(true)
                        }
                    }
                    .accessibilityHidden(true)
                    .overlay(
                        AccessibleDataTable(headers: tableHeaders, rows: tableRows)
                            .allowsHitTesting(false)
                    )
                }
                .background(Color.secondary.opacity(0.04))
                .cornerRadius(8)
            }
        )
    }
}

