//
//  VenueToursView.swift
//  SportsScores
//
//  Hub for all venue audio tours. Accessible from the home screen.
//  Each sport plays continuous terrain-based audio as you drag.
//

import SwiftUI

struct VenueToursView: View {
    var body: some View {
        List {
            Section {
                rowLink(
                    title: "MLB Stadiums",
                    subtitle: "All 30 parks — real wall distances",
                    icon: "figure.baseball",
                    destination: BaseballFieldTourView()
                )
            } header: {
                Text("Baseball")
            }

            Section {
                rowLink(
                    title: "NFL Football Field",
                    subtitle: "120 yds · yard lines · hash marks · goal posts",
                    icon: "figure.american.football",
                    destination: FootballFieldTourView()
                )
            } header: {
                Text("Football")
            }

            Section {
                rowLink(
                    title: "NHL Hockey Rink",
                    subtitle: "200 ft · zones · blue lines · creases",
                    icon: "figure.ice.hockey",
                    destination: HockeyRinkTourView()
                )
            } header: {
                Text("Hockey")
            }

            Section {
                rowLink(
                    title: "NBA Basketball Court",
                    subtitle: "94 ft · paint · 3-point arc · free throw line",
                    icon: "figure.basketball",
                    destination: BasketballCourtTourView()
                )
            } header: {
                Text("Basketball")
            }
        }
        .navigationTitle("Field Tours")
    }

    @ViewBuilder
    private func rowLink<Dest: View>(title: String, subtitle: String, icon: String, destination: Dest) -> some View {
        NavigationLink(destination: destination) {
            HStack(spacing: 14) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.accentColor)
                    .frame(width: 34)
                VStack(alignment: .leading, spacing: 2) {
                    Text(title).font(.headline)
                    Text(subtitle).font(.caption).foregroundColor(.secondary)
                }
            }
            .padding(.vertical, 4)
        }
        .accessibilityLabel("\(title). \(subtitle)")
    }
}

#Preview {
    NavigationStack { VenueToursView() }
}
