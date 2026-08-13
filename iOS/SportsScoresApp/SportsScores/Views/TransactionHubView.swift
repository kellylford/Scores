//
//  TransactionHubView.swift
//  SportsScores
//
//  Entry point for Transaction Hub — lets the user pick a sport to browse.
//

import SwiftUI

struct TransactionHubView: View {
    var body: some View {
        List {
            Section {
                ForEach(Sport.allCases) { sport in
                    sportRow(sport)
                }
            } header: {
                Text("Main Sports")
            }

            Section {
                ForEach(Sport.soccerLeagues) { sport in
                    sportRow(sport)
                }
            } header: {
                Text("Soccer")
            }

            Section {
                ForEach(Sport.golfTours) { sport in
                    sportRow(sport)
                }
            } header: {
                Text("Golf")
            }
        }
        .navigationTitle("Transaction Hub")
    }

    @ViewBuilder
    private func sportRow(_ sport: Sport) -> some View {
        NavigationLink(destination: TransactionTeamPickerView(sport: sport)) {
            HStack(spacing: 14) {
                Image(systemName: sport.systemImage)
                    .font(.title2)
                    .foregroundColor(.accentColor)
                    .frame(width: 34)
                VStack(alignment: .leading, spacing: 2) {
                    Text(sport.displayName).font(.headline)
                    Text("Browse transactions").font(.caption).foregroundColor(.secondary)
                }
            }
            .padding(.vertical, 4)
        }
        .accessibilityLabel("\(sport.displayName). Browse transactions.")
    }
}

#Preview {
    NavigationStack { TransactionHubView() }
}
