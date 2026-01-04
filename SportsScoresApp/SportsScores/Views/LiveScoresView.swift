//
//  LiveScoresView.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI

struct LiveScoresView: View {
    @StateObject private var viewModel = LiveScoresViewModel()
    
    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading all games...")
            } else if let error = viewModel.errorMessage {
                VStack(spacing: 16) {
                    Image(systemName: "calendar.badge.clock")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text(error)
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)
                    Button("Retry") {
                        Task {
                            await viewModel.fetchAllGames()
                        }
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
            } else {
                scrollContent
            }
        }
        .navigationTitle("🔴 Live Scores")
        .task {
            await viewModel.fetchAllGames()
        }
        .refreshable {
            await viewModel.refresh()
        }
    }
    
    private var scrollContent: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                // Live Games Section
                if !viewModel.liveGames.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        sectionHeader(title: "🔴 LIVE NOW", count: totalCount(viewModel.liveGames))
                        
                        ForEach(viewModel.liveGames) { sportGames in
                            sportSection(sportGames: sportGames, isLive: true)
                        }
                    }
                    .padding(.horizontal)
                }
                
                // Completed Games Section
                if !viewModel.completedGames.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        sectionHeader(title: "✅ COMPLETED", count: totalCount(viewModel.completedGames))
                        
                        ForEach(viewModel.completedGames) { sportGames in
                            sportSection(sportGames: sportGames, isLive: false)
                        }
                    }
                    .padding(.horizontal)
                }
                
                // Upcoming Games Section
                if !viewModel.upcomingGames.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        sectionHeader(title: "📅 UPCOMING", count: totalCount(viewModel.upcomingGames))
                        
                        ForEach(viewModel.upcomingGames) { sportGames in
                            sportSection(sportGames: sportGames, isLive: false)
                        }
                    }
                    .padding(.horizontal)
                }
                
                if viewModel.liveGames.isEmpty && viewModel.completedGames.isEmpty && viewModel.upcomingGames.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "calendar.badge.exclamationmark")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("No games today")
                            .font(.headline)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.top, 40)
                }
            }
            .padding(.vertical)
        }
    }
    
    private func sectionHeader(title: String, count: Int) -> some View {
        HStack {
            Text(title)
                .font(.headline)
                .fontWeight(.bold)
            
            Text("\(count)")
                .font(.caption)
                .foregroundColor(.white)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.blue)
                .cornerRadius(12)
        }
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits(.isHeader)
    }
    
    private func sportSection(sportGames: LiveScoresViewModel.SportGames, isLive: Bool) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            // Sport Header
            HStack {
                Text(sportGames.sport.icon)
                    .font(.title3)
                Text(sportGames.sport.displayName)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Spacer()
                Text("\(sportGames.games.count)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color.secondary.opacity(0.1))
            .cornerRadius(8)
            .accessibilityElement(children: .combine)
            .accessibilityAddTraits(.isHeader)
            
            // Games List
            ForEach(sportGames.games) { game in
                NavigationLink(destination: GameDetailView(game: game, sport: sportGames.sport)) {
                    CompactGameRow(game: game, isLive: isLive)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.vertical, 4)
    }
    
    private func totalCount(_ sportGames: [LiveScoresViewModel.SportGames]) -> Int {
        sportGames.reduce(0) { $0 + $1.games.count }
    }
}

struct CompactGameRow: View {
    let game: Game
    let isLive: Bool
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Status Bar
            HStack {
                if isLive {
                    Label(game.status.displayText, systemImage: "circle.fill")
                        .foregroundColor(.red)
                        .font(.caption)
                        .fontWeight(.semibold)
                } else if game.status.isCompleted {
                    Text("Final")
                        .font(.caption)
                        .foregroundColor(.secondary)
                } else {
                    Text(game.displayTime)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                if !game.broadcasts.isEmpty {
                    Text(game.broadcasts.first ?? "")
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.blue.opacity(0.2))
                        .cornerRadius(4)
                }
            }
            
            // Teams and Scores (Score more prominent than records)
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(game.awayTeam.abbreviation)
                        .font(.body)
                        .fontWeight(.medium)
                    
                    Text(game.homeTeam.abbreviation)
                        .font(.body)
                        .fontWeight(.medium)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    if let score = game.awayTeam.score {
                        Text("\(score)")
                            .font(.title3)
                            .fontWeight(.bold)
                            .monospacedDigit()
                    } else {
                        Text("-")
                            .font(.title3)
                            .foregroundColor(.secondary)
                    }
                    
                    if let score = game.homeTeam.score {
                        Text("\(score)")
                            .font(.title3)
                            .fontWeight(.bold)
                            .monospacedDigit()
                    } else {
                        Text("-")
                            .font(.title3)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            // Last play / situation info (no truncation for accessibility)
            if isLive, let situation = game.situation, let displayText = situation.displayText {
                Text(displayText)
                    .font(.caption)
                    .foregroundColor(.primary)
                    .fixedSize(horizontal: false, vertical: true)
                    .lineLimit(nil)
            }
            
            // Team records (less important, shown last)
            if let awayRecord = game.awayTeam.record, let homeRecord = game.homeTeam.record {
                HStack(spacing: 12) {
                    Text("(\(awayRecord))")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text("(\(homeRecord))")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(12)
        .background(Color.secondary.opacity(0.05))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(isLive ? Color.red.opacity(0.3) : Color.clear, lineWidth: 2)
        )
    }
}

#Preview {
    NavigationStack {
        LiveScoresView()
    }
}
