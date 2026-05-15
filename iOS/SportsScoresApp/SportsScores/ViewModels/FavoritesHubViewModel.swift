//
//  FavoritesHubViewModel.swift
//  SportsScores
//
//  Loads live/next game info and two news headlines for each favorite team.
//  Owned by TeamHubSportPickerView so data persists while the hub is in the nav stack.
//

import Foundation

@MainActor
final class FavoritesHubViewModel: ObservableObject {

    @Published var teamInfoMap: [String: TeamHubTeamInfo] = [:]  // keyed by teamId
    @Published var newsMap: [String: [NewsItem]] = [:]           // keyed by teamId, up to 2 items
    @Published var scheduleMap: [String: [ScheduleGame]] = [:]   // keyed by teamId
    @Published var isLoading = false

    private let apiService = ESPNAPIService.shared

    func loadFavorites(_ favorites: [FavoriteTeam]) async {
        guard !favorites.isEmpty else {
            teamInfoMap = [:]
            newsMap = [:]
            scheduleMap = [:]
            return
        }
        isLoading = true
        await withTaskGroup(of: Void.self) { group in
            for fav in favorites {
                group.addTask { await self.loadSingleFavorite(fav) }
            }
        }
        isLoading = false
    }

    private func loadSingleFavorite(_ fav: FavoriteTeam) async {
        async let infoFetch = fetchInfo(fav)
        async let newsFetch = fetchNews(fav)
        async let scheduleFetch = fetchSchedule(fav)
        let (info, news, sched) = await (infoFetch, newsFetch, scheduleFetch)
        if let info { teamInfoMap[fav.id] = info }
        if let news { newsMap[fav.id] = news }
        if let sched { scheduleMap[fav.id] = sched }
    }

    private func fetchInfo(_ fav: FavoriteTeam) async -> TeamHubTeamInfo? {
        try? await apiService.fetchTeamHubInfo(teamId: fav.id, sport: fav.sport)
    }

    private func fetchNews(_ fav: FavoriteTeam) async -> [NewsItem]? {
        try? await apiService.fetchTeamNews(teamId: fav.id, sport: fav.sport, limit: 2)
    }

    private func fetchSchedule(_ fav: FavoriteTeam) async -> [ScheduleGame]? {
        try? await apiService.fetchTeamHubSchedule(teamId: fav.id, sport: fav.sport)
    }
}
