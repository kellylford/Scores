//
//  StatLeaderDetailView.swift
//  SportsScores
//
//  Full leader list for a single stat category, opened via "View All".
//

import SwiftUI

struct StatLeaderDetailView: View {
    let category: LeagueLeaderCategory
    let sport: Sport
    let initialViewMode: ViewMode

    @State private var viewMode: ViewMode

    init(category: LeagueLeaderCategory, sport: Sport, initialViewMode: ViewMode) {
        self.category = category
        self.sport = sport
        self.initialViewMode = initialViewMode
        self._viewMode = State(initialValue: initialViewMode)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                LeaderCategorySection(category: category, viewMode: viewMode)
                    .padding()
            }
        }
        .navigationTitle(category.displayName)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                ViewModeMenuButton(currentMode: $viewMode)
            }
        }
    }
}
