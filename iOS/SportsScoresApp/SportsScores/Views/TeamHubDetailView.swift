//
//  TeamHubDetailView.swift
//  SportsScores
//
//  Team Hub detail screen — five-tab experience for a single team.
//

import SwiftUI

enum TeamHubTab: String, CaseIterable {
    case info         = "Info"
    case roster       = "Roster"
    case news         = "News"
    case schedule     = "Schedule"
    case transactions = "Transactions"

    var systemImage: String {
        switch self {
        case .info:         return "info.circle"
        case .roster:       return "person.3"
        case .news:         return "newspaper"
        case .schedule:     return "calendar"
        case .transactions: return "arrow.left.arrow.right"
        }
    }
}

struct TeamHubDetailView: View {
    let team: TransactionTeam
    let sport: Sport

    @StateObject private var viewModel: TeamHubViewModel
    @State private var selectedTab: TeamHubTab = .info

    init(team: TransactionTeam, sport: Sport) {
        self.team = team
        self.sport = sport
        _viewModel = StateObject(wrappedValue: TeamHubViewModel(teamId: team.id, sport: sport))
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationStack {
                TeamInfoTabView(viewModel: viewModel, team: team, sport: sport)
            }
            .tabItem {
                Label(TeamHubTab.info.rawValue, systemImage: TeamHubTab.info.systemImage)
            }
            .tag(TeamHubTab.info)

            NavigationStack {
                TeamRosterTabView(viewModel: viewModel)
            }
            .tabItem {
                Label(TeamHubTab.roster.rawValue, systemImage: TeamHubTab.roster.systemImage)
            }
            .tag(TeamHubTab.roster)

            NavigationStack {
                TeamNewsTabView(viewModel: viewModel)
            }
            .tabItem {
                Label(TeamHubTab.news.rawValue, systemImage: TeamHubTab.news.systemImage)
            }
            .tag(TeamHubTab.news)

            NavigationStack {
                TeamScheduleTabView(viewModel: viewModel, sport: sport)
            }
            .tabItem {
                Label(TeamHubTab.schedule.rawValue, systemImage: TeamHubTab.schedule.systemImage)
            }
            .tag(TeamHubTab.schedule)

            NavigationStack {
                TeamTransactionsTabView(team: team, sport: sport)
            }
            .tabItem {
                Label(TeamHubTab.transactions.rawValue, systemImage: TeamHubTab.transactions.systemImage)
            }
            .tag(TeamHubTab.transactions)
        }
        .navigationTitle(team.displayName)
        .navigationBarTitleDisplayMode(.inline)
        .onChange(of: selectedTab) { tab in
            Task { await loadTabIfNeeded(tab) }
        }
        .task { await viewModel.loadInfo() }
    }

    private func loadTabIfNeeded(_ tab: TeamHubTab) async {
        switch tab {
        case .info:         await viewModel.loadInfo()
        case .roster:       await viewModel.loadRoster()
        case .news:         await viewModel.loadNews()
        case .schedule:     await viewModel.loadSchedule()
        case .transactions: break  // TransactionListView manages its own loading
        }
    }
}

#Preview {
    let mockTeam = TransactionTeam(
        id: "10", location: "New York", name: "Yankees",
        abbreviation: "NYY", displayName: "New York Yankees",
        color: "132448", logos: nil
    )
    return NavigationStack {
        TeamHubDetailView(team: mockTeam, sport: .mlb)
    }
}
