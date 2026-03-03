//
//  SportSelectionView.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI

// MARK: - Home game-count view model

@MainActor
private class HomeViewModel: ObservableObject {
    @Published var gameCounts: [Sport: Int] = [:]
    @Published var isLoading = true

    private let api = ESPNAPIService.shared

    func load() async {
        isLoading = true
        let calendar = Calendar.current
        let start = calendar.startOfDay(for: Date())
        let end   = calendar.date(byAdding: .day, value: 1, to: start)!

        await withTaskGroup(of: (Sport, Int).self) { group in
            for sport in Sport.allCases {
                group.addTask {
                    let count = (try? await self.api.fetchGames(for: sport))
                        .map { $0.filter { $0.date >= start && $0.date < end }.count } ?? 0
                    return (sport, count)
                }
            }
            for await (sport, count) in group {
                gameCounts[sport] = count
            }
        }
        isLoading = false
    }
}

// MARK: - View

struct SportSelectionView: View {
    @State private var showSettings = false
    @StateObject private var homeVM = HomeViewModel()

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
                            SportRowView(sport: sport,
                                         count: homeVM.gameCounts[sport],
                                         isLoading: homeVM.isLoading)
                        }
                        .accessibilityLabel(accessibilityLabel(for: sport))
                    }
                } header: {
                    Text("Browse by Sport")
                }

                // Field Tours
                Section {
                    NavigationLink(destination: VenueToursView()) {
                        HStack(spacing: 14) {
                            Image(systemName: "waveform.and.mic")
                                .font(.title2)
                                .foregroundColor(.accentColor)
                                .frame(width: 34)
                            VStack(alignment: .leading, spacing: 2) {
                                Text("Audio Field Tours")
                                    .font(.headline)
                                Text("Baseball · Football · Hockey · Basketball")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.vertical, 4)
                    }
                    .accessibilityLabel("Audio Field Tours — explore venue layouts through sound and touch")
                } header: {
                    Text("Explore")
                }
            }
            .navigationTitle("Sports Scores")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        showSettings = true
                    } label: {
                        Image(systemName: "gearshape")
                    }
                    .accessibilityLabel("Settings")
                }
            }
            .sheet(isPresented: $showSettings) {
                SettingsView()
            }
            .task { await homeVM.load() }
        }
    }

    private func accessibilityLabel(for sport: Sport) -> String {
        guard !homeVM.isLoading else { return sport.displayName }
        let count = homeVM.gameCounts[sport] ?? 0
        if count == 0 { return "\(sport.displayName), no games today" }
        return "\(sport.displayName), \(count) \(count == 1 ? "game" : "games") today"
    }
}

// MARK: - Sport row with game count badge

private struct SportRowView: View {
    let sport: Sport
    let count: Int?       // nil while loading
    let isLoading: Bool

    var body: some View {
        HStack(spacing: 12) {
            Text(sport.icon)
                .font(.title2)
                .frame(width: 36)

            Text(sport.displayName)
                .font(.headline)

            Spacer()

            gameBadge
        }
        .padding(.vertical, 4)
    }

    @ViewBuilder
    private var gameBadge: some View {
        if isLoading {
            ProgressView()
                .scaleEffect(0.75)
                .frame(width: 36, height: 20)
        } else if let n = count, n > 0 {
            Text("\(n)")
                .font(.system(.caption, design: .rounded).bold())
                .foregroundColor(.white)
                .padding(.horizontal, 8)
                .padding(.vertical, 3)
                .background(badgeColor(n), in: Capsule())
                .accessibilityHidden(true)   // spoken via accessibilityLabel on the row
        } else {
            Text("—")
                .font(.caption)
                .foregroundColor(.secondary)
                .accessibilityHidden(true)
        }
    }

    private func badgeColor(_ n: Int) -> Color {
        switch n {
        case 1...5:  return .blue
        case 6...10: return .orange
        default:     return .red
        }
    }
}

#Preview {
    SportSelectionView()
        .environmentObject(AppSettings())
}
