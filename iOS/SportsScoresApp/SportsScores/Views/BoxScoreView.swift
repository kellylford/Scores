//
//  BoxScoreView.swift
//  SportsScores
//
//  Renders the box score one table at a time.
//  Every table is its own tab-bar button.  Examples:
//    MLB:        "NYY Batting"  "BOS Batting"  "NYY Pitching"  "BOS Pitching"
//                "Team Batting"  "Team Pitching"
//    NFL/NBA:    "Chiefs Passing"  "Eagles Passing"  …  "Team Stats"
//    NHL:        "EDM Skaters"  "CGY Skaters"  "EDM Goalies"  "CGY Goalies"  "Team Stats"
//

import SwiftUI

// MARK: - Page Model

/// One page = exactly one table.  Hashable so it works as a SwiftUI `.id` and
/// can be stored as `@State`.
private enum BoxScorePage: Hashable {
    /// A single team's player-level stat table for one stat group.
    case playerGroup(teamDisplayName: String, teamAbbr: String, groupTitle: String)
    /// Side-by-side team-stat comparison for one MLB category (Batting / Pitching / …).
    case mlbTeamStats(groupTitle: String)
    /// The single flat team-stats table used by NFL / NBA / NHL / Soccer.
    case flatTeamStats

    var tabLabel: String {
        switch self {
        case let .playerGroup(_, abbr, group): return "\(abbr) \(group)"
        case let .mlbTeamStats(group):         return "Team \(group)"
        case .flatTeamStats:                   return "Team Stats"
        }
    }
}

// MARK: - View

struct BoxScoreView: View {
    let boxscore: GameDetails.Boxscore
    let sport: Sport
    @State private var showingAllStats = false
    @State private var selectedPage: BoxScorePage?

    // MARK: - Page List

    /// Ordered list of all navigable pages (one page = one table).
    ///
    /// Order:
    ///   • Player tables — for each stat group, one entry per team in API order
    ///     (e.g. "NYY Batting", "BOS Batting", "NYY Pitching", "BOS Pitching")
    ///   • Team-stat tables — one per MLB category, or a single flat table for others
    private var pages: [BoxScorePage] {
        var result: [BoxScorePage] = []

        // ── Player pages ───────────────────────────────────────────────────────
        if let players = boxscore.players {
            // Collect group titles in the order they first appear across all teams.
            var seenGroups = Set<String>()
            var groupOrder: [String] = []
            for teamPlayers in players {
                for group in teamPlayers.statistics {
                    if seenGroups.insert(group.groupTitle).inserted {
                        groupOrder.append(group.groupTitle)
                    }
                }
            }
            // For each group, emit one page per team (keeps groups together).
            for groupTitle in groupOrder {
                for teamPlayers in players {
                    if teamPlayers.statistics.contains(where: { $0.groupTitle == groupTitle }) {
                        result.append(.playerGroup(
                            teamDisplayName: teamPlayers.team.displayName,
                            teamAbbr: teamPlayers.team.abbreviation,
                            groupTitle: groupTitle
                        ))
                    }
                }
            }
        }

        // ── Team-stat pages ────────────────────────────────────────────────────
        if boxscore.teams.first?.statistics.first?.isNested == true {
            // MLB: one side-by-side comparison table per category.
            for cat in boxscore.teams.first?.statistics ?? [] {
                result.append(.mlbTeamStats(groupTitle: cat.groupTitle))
            }
        } else if !boxscore.teams.isEmpty {
            result.append(.flatTeamStats)
        }

        return result
    }

    private var currentPage: BoxScorePage {
        if let sel = selectedPage, pages.contains(sel) { return sel }
        return pages.first ?? .flatTeamStats
    }

    // MARK: - Body

    var body: some View {
        VStack(spacing: 0) {
            if pages.count > 1 {
                pageTabBar
            }

            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    if boxscore.teams.isEmpty {
                        Text("Box score not available")
                            .foregroundColor(.secondary)
                            .padding()
                    } else {
                        toggleButton
                        pageContent
                    }
                }
                // Reset scroll offset whenever the page changes.
                .id(currentPage)
                .padding()
            }
        }
        .onAppear {
            if selectedPage == nil { selectedPage = pages.first }
        }
    }

    // MARK: - Tab Bar

    private var pageTabBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 0) {
                ForEach(pages, id: \.self) { page in
                    let isSelected = currentPage == page
                    Button(action: { selectedPage = page }) {
                        Text(page.tabLabel)
                            .font(.subheadline.bold())
                            .padding(.horizontal, 16)
                            .padding(.vertical, 10)
                            .foregroundColor(isSelected ? .white : .primary)
                    }
                    .background(isSelected ? Color.blue : Color.clear)
                    .accessibilityAddTraits(isSelected ? .isSelected : [])
                }
            }
        }
        .background(Color.secondary.opacity(0.1))
    }

    // MARK: - Essential / All Stats Toggle

    private var toggleButton: some View {
        HStack {
            Spacer()
            Button(action: { showingAllStats.toggle() }) {
                HStack(spacing: 6) {
                    Image(systemName: showingAllStats ? "checkmark.circle.fill" : "circle")
                        .font(.caption)
                    Text(showingAllStats ? "All Stats" : "Essential Stats")
                        .font(.caption)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(Color.blue.opacity(0.1))
                .cornerRadius(6)
            }
            .buttonStyle(.plain)
            .accessibilityHint("Toggle between essential and all statistics")
        }
        .padding(.horizontal, 8)
    }

    // MARK: - Page Content Router

    @ViewBuilder
    private var pageContent: some View {
        switch currentPage {
        case let .playerGroup(teamDisplayName, _, groupTitle):
            singleTeamPlayerView(teamDisplayName: teamDisplayName, groupTitle: groupTitle)
        case let .mlbTeamStats(groupTitle):
            mlbTeamStatsPage(groupTitle: groupTitle)
        case .flatTeamStats:
            flatTeamStats
        }
    }

    // MARK: - Single Team Player Table

    private func singleTeamPlayerView(teamDisplayName: String, groupTitle: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            if let players = boxscore.players,
               let teamPlayers = players.first(where: { $0.team.displayName == teamDisplayName }),
               let group = teamPlayers.statistics.first(where: { $0.groupTitle == groupTitle }) {
                playerStatGroupView(teamName: teamDisplayName, statGroup: group)
            } else {
                Text("No statistics available.")
                    .foregroundColor(.secondary)
            }
        }
    }

    // MARK: - MLB Team Stats Page (one category, both teams side-by-side)

    private func mlbTeamStatsPage(groupTitle: String) -> some View {
        let teams = boxscore.teams
        let profile = BoxScoreProfiles.profile(for: sport)
        let catEntry = teams.first?.statistics.first(where: { $0.groupTitle == groupTitle })
        let filteredItems = catEntry?.stats?.filter { stat in
            showingAllStats || profile.essentialTeamStats.contains(stat.name)
        } ?? []

        let tableHeaders: [String] = filteredItems.isEmpty
            ? [] : (["Stat"] + teams.map { $0.team.abbreviation })
        let tableRows: [[String]] = filteredItems.map { stat in
            [stat.displayName] + teams.map { team in
                team.statistics
                    .first(where: { $0.name == catEntry?.name })?
                    .stats?
                    .first(where: { $0.name == stat.name })?
                    .displayValue ?? "-"
            }
        }

        return VStack(alignment: .leading, spacing: 8) {
            if filteredItems.isEmpty {
                Text("No team statistics available.")
                    .foregroundColor(.secondary)
            } else {
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
                    ForEach(Array(filteredItems.enumerated()), id: \.element.name) { rowIdx, stat in
                        HStack(spacing: 0) {
                            Text(stat.displayName)
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                            ForEach(teams, id: \.team.displayName) { team in
                                let matchedStat = team.statistics
                                    .first(where: { $0.name == catEntry?.name })?
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
        }
    }

    // MARK: - Flat Team Stats (NFL / NBA / NHL)

    private var flatTeamStats: some View {
        let teams = boxscore.teams
        let allRows = teams.first?.statistics ?? []
        let profile = BoxScoreProfiles.profile(for: sport)

        // Filter rows based on showingAllStats
        let rows = allRows.filter { stat in
            showingAllStats || profile.essentialTeamStats.contains(stat.name)
        }

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

    // MARK: - Player Stat Group View

    private func playerStatGroupView(teamName: String, statGroup: GameDetails.Boxscore.TeamPlayers.PlayerStatGroup) -> some View {
        let allStatNames = statGroup.columnHeaders
        let profile = BoxScoreProfiles.profile(for: sport)
        
        // Filter stat columns based on profile if not showing all
        let filteredStatNames = showingAllStats 
            ? allStatNames
            : filterPlayerStatNames(allStatNames, for: statGroup.type ?? statGroup.name ?? "", profile: profile)
        
        // Show all athletes regardless of active state.
        // For baseball, pitchers are marked active:false once done pitching, but
        // we still want to display their stats. For basketball, inactive = DNP,
        // which are also useful to show (zero minutes, etc.).
        let athletes = statGroup.athletes
        
        // Create filtered stats array (only include columns that are in filteredStatNames)
        let filteredAthletes: [(athlete: GameDetails.Boxscore.TeamPlayers.PlayerStatGroup.AthleteStats, filteredStats: [String])] = athletes.map { athlete in
            let filtered = athlete.stats.enumerated().compactMap { idx, stat in
                idx < allStatNames.count && filteredStatNames.contains(allStatNames[idx]) ? stat : nil
            }
            return (athlete: athlete, filteredStats: filtered)
        }
        
        let tableHeaders = ["Player", "Pos"] + filteredStatNames
        let tableRows = filteredAthletes.map { entry in
            [entry.athlete.athlete.displayName, entry.athlete.athlete.position?.abbreviation ?? ""] + entry.filteredStats
        }
        
        guard !athletes.isEmpty, !filteredStatNames.isEmpty else {
            return AnyView(EmptyView())
        }
        
        return AnyView(
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
                            
                            ForEach(filteredStatNames.indices, id: \.self) { idx in
                                Text(filteredStatNames[idx])
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
                        ForEach(filteredAthletes.indices, id: \.self) { athleteIdx in
                            let entry = filteredAthletes[athleteIdx]
                            
                            HStack(spacing: 0) {
                                Text(entry.athlete.athlete.displayName)
                                    .font(.caption)
                                    .frame(width: 140, alignment: .leading)
                                    .lineLimit(1)
                                
                                Text(entry.athlete.athlete.position?.abbreviation ?? "")
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                                    .frame(width: 45, alignment: .center)
                                
                                ForEach(entry.filteredStats.indices, id: \.self) { statIdx in
                                    Text(entry.filteredStats[statIdx])
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
        )
    }
    
    /// Filter stat column names based on the sport profile
    private func filterPlayerStatNames(_ names: [String], for groupType: String, profile: BoxScoreProfile) -> [String] {
        let lowerType = groupType.lowercased()
        let essentialStats = profile.essentialPlayerStats[lowerType] 
            ?? profile.essentialPlayerStats.values.first 
            ?? Set<String>()
        
        return names.filter { essentialStats.contains($0.lowercased()) }
    }
}

// MARK: - Box Score Profiles

struct BoxScoreProfile {
    /// Essential stat names (map to ESPN's internal `name` field) to show by default
    let essentialTeamStats: Set<String>
    
    /// Essential player stat column names (map to ESPN's `names` array in player statistics)
    let essentialPlayerStats: [String: Set<String>]
}

enum BoxScoreProfiles {
    
    // MARK: - MLB
    
    static let mlb = BoxScoreProfile(
        essentialTeamStats: [
            // Batting — names match ESPN's boxscore.teams[].statistics[].stats[].name
            "hits", "runs", "runnersLeftOnBase", "homeRuns", "RBIs", "walks", "strikeouts",
            // Pitching
            "earnedRuns", "strikeouts", "walks", "homeRuns"
        ],
        essentialPlayerStats: [
            // Column names match ESPN's boxscore.players[].statistics[].names[] display values
            "batting":  ["h-ab", "ab", "r", "h", "rbi", "bb", "k", "avg"],
            "pitching": ["ip", "h", "r", "er", "bb", "k", "era"]
        ]
    )
    
    // MARK: - NFL / NCAAF
    
    static let football = BoxScoreProfile(
        essentialTeamStats: [
            "firstDowns", "passYards", "rushYards", "totalYards", "turnovers", "penalties", "timeOfPossession"
        ],
        essentialPlayerStats: [
            "passing": ["cmp", "att", "yds", "td", "int"],
            "rushing": ["car", "yds", "avg", "td"],
            "receiving": ["rec", "yds", "avg", "td"],
            "defense": ["tackles", "sacks", "int", "pd"]
        ]
    )
    
    // MARK: - NBA / NCAAM / NCAAWB / WNBA
    
    static let basketball = BoxScoreProfile(
        essentialTeamStats: [
            "fieldGoalsMade", "fieldGoalsAttempted", "threePointsMade", "threePointsAttempted",
            "freeThrowsMade", "freeThrowsAttempted", "rebounds", "assists", "turnovers", "steals", "blocks"
        ],
        essentialPlayerStats: [
            "player": ["min", "fgm", "fga", "3pm", "3pa", "ftm", "fta", "pts", "reb", "ast", "stl", "blk", "to"]
        ]
    )
    
    // MARK: - NHL / NCAAH / NCAAWH
    
    static let hockey = BoxScoreProfile(
        essentialTeamStats: [
            "shots", "hits", "blocks", "giveaways", "takeaways", "faceoffWinPercentage",
            "powerPlayGoals", "powerPlayAttempts", "penaltyKillPercentage"
        ],
        essentialPlayerStats: [
            "skater": ["g", "a", "plusMinus", "shots", "hits", "blocks"],
            "goalie": ["saves", "shotsAgainst", "gaa", "sv%", "so"]
        ]
    )
    
    // MARK: - Profile Lookup by Sport
    
    static func profile(for sport: Sport) -> BoxScoreProfile {
        switch sport {
        case .mlb:
            return mlb
        case .nfl, .ncaaf:
            return football
        case .nba, .ncaam, .ncaawb, .wnba:
            return basketball
        case .nhl, .ncaah, .ncaawh:
            return hockey
        default:
            // Soccer and any future sports — no sport-specific profile; show raw stats as-is.
            return BoxScoreProfile(
                essentialTeamStats: [],
                essentialPlayerStats: [:]
            )
        }
    }
}


