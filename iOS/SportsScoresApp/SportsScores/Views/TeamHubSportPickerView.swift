//
//  TeamHubSportPickerView.swift
//  SportsScores
//
//  First level of Team Hub navigation — pick a sport.
//

import SwiftUI

struct TeamHubSportPickerView: View {
    var body: some View {
        List {
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
        .navigationTitle("Team Hub")
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
}
