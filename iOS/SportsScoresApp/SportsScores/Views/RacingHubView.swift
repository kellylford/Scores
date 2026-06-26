//
//  RacingHubView.swift
//  SportsScores
//
//  Entry point for auto racing — lists F1, IndyCar, and NASCAR Cup as rows
//  navigating into RacingLeagueView. Mirrors the GolfHubView pattern.
//

import SwiftUI

struct RacingHubView: View {

    var body: some View {
        List {
            Section {
                ForEach(Sport.racingSeries) { series in
                    NavigationLink(destination: RacingLeagueView(series: series)) {
                        HStack(spacing: 12) {
                            Image(systemName: "flag.checkered")
                                .font(.title2)
                                .foregroundColor(.accentColor)
                                .frame(width: 36)
                            VStack(alignment: .leading, spacing: 2) {
                                Text(series.displayName)
                                    .font(.headline)
                                Text(seriesSubtitle(series))
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.vertical, 4)
                    }
                    .accessibilityLabel(accessibilityLabel(for: series))
                }
            } header: {
                Text("Select a Series")
            }
        }
        .navigationTitle("Auto Racing")
        .listStyle(.insetGrouped)
    }

    private func seriesSubtitle(_ series: Sport) -> String {
        switch series {
        case .formulaOne: return "FIA Formula One World Championship"
        case .indyCar:    return "NTT IndyCar Series"
        case .nascarCup:  return "NASCAR Cup Series"
        default:          return ""
        }
    }

    private func accessibilityLabel(for series: Sport) -> String {
        "\(series.displayName). \(seriesSubtitle(series))"
    }
}

#Preview {
    NavigationStack {
        RacingHubView()
    }
}
