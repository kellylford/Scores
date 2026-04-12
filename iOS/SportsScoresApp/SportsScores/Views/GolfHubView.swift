//
//  GolfHubView.swift
//  SportsScores
//
//  Golf entry point — shows PGA Tour and LPGA Tour rows,
//  each navigating into GolfLeagueView.
//  Mirrors the SoccerHubView pattern.
//

import SwiftUI

struct GolfHubView: View {

    var body: some View {
        List {
            Section {
                ForEach(Sport.golfTours) { tour in
                    NavigationLink(destination: GolfLeagueView(sport: tour)) {
                        HStack(spacing: 12) {
                            Image(systemName: tour.systemImage)
                                .font(.title2)
                                .foregroundColor(.accentColor)
                                .frame(width: 36)
                            VStack(alignment: .leading, spacing: 2) {
                                Text(tour.displayName)
                                    .font(.headline)
                                Text(tourSubtitle(tour))
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.vertical, 4)
                    }
                    .accessibilityLabel(accessibilityLabel(for: tour))
                }
            } header: {
                Text("Select a Tour")
            }
        }
        .navigationTitle("Golf")
        .listStyle(.insetGrouped)
    }

    private func tourSubtitle(_ tour: Sport) -> String {
        switch tour {
        case .pga:  return "PGA Tour · FedEx Cup"
        case .lpga: return "LPGA Tour · CME Globe"
        default:    return ""
        }
    }

    private func accessibilityLabel(for tour: Sport) -> String {
        "\(tour.displayName). \(tourSubtitle(tour))"
    }
}

#Preview {
    NavigationStack {
        GolfHubView()
    }
}
