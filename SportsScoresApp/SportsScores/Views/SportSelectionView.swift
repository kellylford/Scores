//
//  SportSelectionView.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI

struct SportSelectionView: View {
    var body: some View {
        NavigationStack {
            List {
                // Live Scores - All Sports
                Section {
                    NavigationLink(destination: LiveScoresView()) {
                        HStack {
                            Image(systemName: "circle.fill")
                                .foregroundColor(.red)
                                .font(.title2)
                            VStack(alignment: .leading, spacing: 2) {
                                Text("Live Scores")
                                    .font(.headline)
                                Text("All sports - Live, completed & upcoming")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.vertical, 4)
                    }
                    .accessibilityLabel("Live Scores - View all games from all sports")
                } header: {
                    Text("Today's Games")
                }
                
                // Individual Sports
                Section {
                    ForEach(Sport.allCases) { sport in
                        NavigationLink(destination: ScoresView(sport: sport)) {
                            HStack {
                                Text(sport.icon)
                                    .font(.title2)
                                Text(sport.displayName)
                                    .font(.headline)
                            }
                            .padding(.vertical, 4)
                        }
                        .accessibilityLabel(sport.displayName)
                    }
                } header: {
                    Text("Browse by Sport")
                }
            }
            .navigationTitle("Sports Scores")
        }
    }
}

#Preview {
    SportSelectionView()
}
