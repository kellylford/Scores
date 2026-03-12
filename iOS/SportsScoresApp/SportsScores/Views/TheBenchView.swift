//
//  TheBenchView.swift
//  SportsScores
//
//  Hub for all venue audio touch tours. Accessible from the The Bench tab.
//  Each sport plays continuous terrain-based audio as you drag across the field.
//

import SwiftUI

struct TheBenchView: View {
    var body: some View {
        List {
            Section {
                rowLink(
                    title: "MLB Stadiums",
                    subtitle: "All 30 parks — real wall distances",
                    icon: "figure.baseball",
                    destination: BaseballTourInfoView()
                )
            } header: {
                Text("Baseball")
            }

            Section {
                rowLink(
                    title: "NFL Football Field",
                    subtitle: "120 yds · yard lines · hash marks · goal posts",
                    icon: "figure.american.football",
                    destination: FootballTourInfoView()
                )
            } header: {
                Text("Football")
            }

            Section {
                rowLink(
                    title: "NHL Hockey Rink",
                    subtitle: "200 ft · zones · blue lines · creases",
                    icon: "figure.ice.hockey",
                    destination: HockeyTourInfoView()
                )
            } header: {
                Text("Hockey")
            }

            Section {
                rowLink(
                    title: "NBA Basketball Court",
                    subtitle: "94 ft · paint · 3-point arc · free throw line",
                    icon: "figure.basketball",
                    destination: BasketballTourInfoView()
                )
            } header: {
                Text("Basketball")
            }

            Section {
                rowLink(
                    title: "Soccer Pitch",
                    subtitle: "105m × 68m · center circle · penalty areas · goals",
                    icon: "figure.soccer",
                    destination: SoccerTourInfoView()
                )
            } header: {
                Text("Soccer")
            }
        }
        .navigationTitle("The Bench")
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
    NavigationStack { TheBenchView() }
}
