//
//  TeamHubTeamPickerView.swift
//  SportsScores
//
//  Second level of Team Hub navigation — pick a team within a sport.
//

import SwiftUI

struct TeamHubTeamPickerView: View {
    let sport: Sport
    @State private var teams: [TransactionTeam] = []
    @State private var isLoading = false
    @State private var errorMessage: String?

    private let apiService = ESPNAPIService.shared

    var body: some View {
        Group {
            if isLoading {
                ProgressView("Loading teams…")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = errorMessage {
                VStack(spacing: 16) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 40))
                        .foregroundColor(.secondary)
                    Text(error)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                    Button("Retry") { Task { await loadTeams() } }
                        .buttonStyle(.borderedProminent)
                }
                .padding()
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                List(teams) { team in
                    NavigationLink(destination: TeamHubDetailView(team: team, sport: sport)) {
                        HStack(spacing: 12) {
                            if let logoURL = team.primaryLogoURL {
                                AsyncImage(url: logoURL) { phase in
                                    switch phase {
                                    case .success(let img):
                                        img.resizable()
                                            .scaledToFit()
                                            .frame(width: 36, height: 36)
                                    default:
                                        Image(systemName: "shield.fill")
                                            .font(.title2)
                                            .foregroundColor(.secondary)
                                            .frame(width: 36, height: 36)
                                    }
                                }
                            } else {
                                Image(systemName: "shield.fill")
                                    .font(.title2)
                                    .foregroundColor(.secondary)
                                    .frame(width: 36, height: 36)
                            }
                            Text(team.displayName)
                                .font(.body)
                        }
                        .padding(.vertical, 2)
                    }
                    .accessibilityLabel(team.displayName)
                }
            }
        }
        .navigationTitle(sport.displayName)
        .task { await loadTeams() }
    }

    private func loadTeams() async {
        isLoading = true
        errorMessage = nil
        do {
            let fetched = try await apiService.fetchTeamsForSport(sport: sport)
            teams = fetched.sorted { $0.displayName < $1.displayName }
        } catch {
            errorMessage = "Could not load teams for \(sport.displayName)."
        }
        isLoading = false
    }
}

#Preview {
    NavigationStack { TeamHubTeamPickerView(sport: .mlb) }
}
