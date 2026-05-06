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
                NavigationLink(destination: TeamHubTeamPickerView(sport: sport)) {
                    HStack(spacing: 14) {
                        Image(systemName: sport.systemImage)
                            .font(.title2)
                            .foregroundColor(.accentColor)
                            .frame(width: 34)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(sport.displayName).font(.headline)
                            Text("Browse teams").font(.caption).foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 4)
                }
                .accessibilityLabel("\(sport.displayName). Browse teams.")
            }
        }
        .navigationTitle("Team Hub")
    }
}

#Preview {
    NavigationStack { TeamHubSportPickerView() }
}
