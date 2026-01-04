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
                    Text("Select a Sport")
                }
            }
            .navigationTitle("Sports Scores")
        }
    }
}

#Preview {
    SportSelectionView()
}
