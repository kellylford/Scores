//
//  TeamHubSportPickerView.swift
//  SportsScores
//
//  First level of Team Hub navigation — pick a sport.
//  A Favorites section appears above the sport list when the user has bookmarked teams.
//

import SwiftUI

struct TeamHubSportPickerView: View {

    @EnvironmentObject private var appSettings: AppSettings
    @StateObject private var favoritesVM = FavoritesHubViewModel()

    var body: some View {
        List {
            Section {
                if appSettings.favoriteTeams.isEmpty {
                    Text("Browse a sport below and use Add to Favorites on a team page to add it here.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .accessibilityLabel("No favorites yet. Browse a sport below and use Add to Favorites on a team page to add it here.")
                } else {
                    ForEach(appSettings.favoriteTeams) { fav in
                        FavoriteTeamCardView(
                            favorite: fav,
                            schedule: favoritesVM.scheduleMap[fav.id] ?? [],
                            news: favoritesVM.newsMap[fav.id] ?? [],
                            liveGameHeader: favoritesVM.liveDetailsMap[fav.id]?.header
                        )
                    }
                }
            } header: {
                Text("Favorites")
                    .accessibilityAddTraits(.isHeader)
            }
            Section {
                ForEach(Sport.teamHubSports) { sport in
                    if sport.isCollegeSport {
                        NavigationLink(destination: TeamHubConferencePickerView(sport: sport)) {
                            sportRow(sport: sport, subtitle: "Browse by conference")
                        }
                        .accessibilityLabel("\(sport.displayName). Browse by conference.")
                    } else {
                        NavigationLink(destination: TeamHubTeamPickerView(sport: sport)) {
                            sportRow(sport: sport, subtitle: "Browse teams")
                        }
                        .accessibilityLabel("\(sport.displayName). Browse teams.")
                    }
                }
            }
        }
        .navigationTitle("Team Hub")
        .task(id: appSettings.favoriteTeams.map(\.id).joined()) {
            await favoritesVM.loadFavorites(appSettings.favoriteTeams)
        }
    }

    private func sportRow(sport: Sport, subtitle: String) -> some View {
        HStack(spacing: 14) {
            Image(systemName: sport.systemImage)
                .font(.title2)
                .foregroundColor(.accentColor)
                .frame(width: 34)
            VStack(alignment: .leading, spacing: 2) {
                Text(sport.displayName).font(.headline)
                Text(subtitle).font(.caption).foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    NavigationStack { TeamHubSportPickerView() }
        .environmentObject(AppSettings())
}

