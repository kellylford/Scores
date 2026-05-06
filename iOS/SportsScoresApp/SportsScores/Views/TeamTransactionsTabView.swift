//
//  TeamTransactionsTabView.swift
//  SportsScores
//
//  Transactions tab for Team Hub — reuses TransactionListView with team filter.
//

import SwiftUI

struct TeamTransactionsTabView: View {
    let team: TransactionTeam
    let sport: Sport

    var body: some View {
        TransactionListView(sport: sport, team: team)
            .navigationTitle("Transactions")
            .navigationBarTitleDisplayMode(.inline)
    }
}
