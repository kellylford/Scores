//
//  FavoriteTeamCardView.swift
//  SportsScores
//
//  A card in the Favorites section of Team Hub. Each piece of information is a
//  separate VoiceOver element so users can navigate between them individually:
//    1. Team name — heading + button (pushes to TeamHubDetailView)
//    2. Live or next game — navigates to GameDetailView
//    3. First news headline — opens article in Safari sheet
//    4. Second news headline — opens article in Safari sheet
//

import SwiftUI

struct FavoriteTeamCardView: View {

    let favorite: FavoriteTeam
    let schedule: [ScheduleGame]
    let news: [NewsItem]          // up to 2 items
    /// Header data from the ESPN summary endpoint for any live game.
    /// Scores here are always current; schedule-based scores can be nil/stale.
    let liveGameHeader: GameDetails.GameHeader?
    /// Called when the user activates the "Remove from Favorites" VoiceOver action.
    var onRemove: (() -> Void)? = nil

    @State private var showArticle1 = false
    @State private var showArticle2 = false

    // MARK: - Date formatter

    private static let gameDateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateStyle = .short
        f.timeStyle = .short
        return f
    }()

    // MARK: - Derived game data

    private var liveGame: ScheduleGame? {
        schedule.first { $0.isInProgress }
    }

    private var lastGame: ScheduleGame? {
        schedule.filter { $0.isCompleted }.last
    }

    private var nextGame: ScheduleGame? {
        let now = Date()
        return schedule.first { !$0.isCompleted && !$0.isInProgress && $0.date > now }
    }

    private func gameLabel(for game: ScheduleGame, prefix: String) -> String {
        let isHome = game.homeTeam.id == favorite.id
        let opp = isHome ? game.awayTeam : game.homeTeam
        let loc = isHome ? "vs" : "@"
        if game.isInProgress {
            // Prefer live scores from the summary header (always current).
            // Fall back to schedule scores only if the header isn't loaded yet.
            let myScore: Int?
            let oppScore: Int?
            if let header = liveGameHeader,
               let comp = header.competitions.first {
                let mySide = comp.competitors.first(where: { ($0.homeAway == "home") == isHome })
                let oppSide = comp.competitors.first(where: { ($0.homeAway == "home") != isHome })
                myScore = mySide?.score
                oppScore = oppSide?.score
            } else {
                myScore = isHome ? game.homeTeam.score : game.awayTeam.score
                oppScore = isHome ? game.awayTeam.score : game.homeTeam.score
            }
            if let my = myScore, let op = oppScore {
                return "\(prefix): \(loc) \(opp.abbreviation) \(my)-\(op)"
            }
            return "\(prefix): \(loc) \(opp.abbreviation)"
        }
        let myScore = isHome ? game.homeTeam.score : game.awayTeam.score
        let oppScore = isHome ? game.awayTeam.score : game.homeTeam.score
        if game.isCompleted {
            let my = myScore ?? 0
            let op = oppScore ?? 0
            let result = my > op ? "W" : my < op ? "L" : "T"
            return "\(prefix): \(result) \(loc) \(opp.abbreviation) \(my)-\(op)"
        }
        return "\(prefix): \(loc) \(opp.abbreviation), \(Self.gameDateFormatter.string(from: game.date))"
    }

    // MARK: - Body

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {

            // 1. Team name — heading + button
            NavigationLink(destination: TeamHubDetailView(team: favorite.asTransactionTeam, sport: favorite.sport)) {
                HStack(spacing: 12) {
                    logoView
                    Text(favorite.displayName)
                        .font(.headline)
                        .foregroundColor(.primary)
                    Spacer()
                    Text(favorite.sport.displayName)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .accessibilityLabel("\(favorite.displayName), \(favorite.sport.displayName)")
            .accessibilityAddTraits(.isButton)
            .accessibilityAction(named: "Remove from Favorites") { onRemove?() }

            // 2. Live or last game — navigates to GameDetailView
            if let live = liveGame {
                NavigationLink(destination: GameDetailView(game: live.toGame(), sport: favorite.sport)) {
                    gameStatusView(label: gameLabel(for: live, prefix: "Live"), isLive: true)
                }
                .accessibilityLabel(gameLabel(for: live, prefix: "Live"))
                .accessibilityHint("Open game details.")
            } else if let last = lastGame {
                NavigationLink(destination: GameDetailView(game: last.toGame(), sport: favorite.sport)) {
                    gameStatusView(label: gameLabel(for: last, prefix: "Last"), isLive: false)
                }
                .accessibilityLabel(gameLabel(for: last, prefix: "Last"))
                .accessibilityHint("Open game details.")
            }

            // 3. Next game — navigates to GameDetailView
            if let next = nextGame {
                NavigationLink(destination: GameDetailView(game: next.toGame(), sport: favorite.sport)) {
                    gameStatusView(label: gameLabel(for: next, prefix: "Next"), isLive: false)
                }
                .accessibilityLabel(gameLabel(for: next, prefix: "Next"))
                .accessibilityHint("Open game details.")
            }

            // 4. First news headline — opens article in Safari
            if !news.isEmpty {
                if let url = news[0].articleURL {
                    Button { showArticle1 = true } label: {
                        Text(news[0].headline)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .lineLimit(2)
                            .padding(.leading, 48)
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel(news[0].headline)
                    .accessibilityHint("Double tap to open article.")
                    .sheet(isPresented: $showArticle1) {
                        SafariView(url: url).ignoresSafeArea()
                    }
                } else {
                    Text(news[0].headline)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                        .padding(.leading, 48)
                }
            }

            // 5. Second news headline — opens article in Safari
            if news.count > 1 {
                if let url = news[1].articleURL {
                    Button { showArticle2 = true } label: {
                        Text(news[1].headline)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .lineLimit(2)
                            .padding(.leading, 48)
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel(news[1].headline)
                    .accessibilityHint("Double tap to open article.")
                    .sheet(isPresented: $showArticle2) {
                        SafariView(url: url).ignoresSafeArea()
                    }
                } else {
                    Text(news[1].headline)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                        .padding(.leading, 48)
                }
            }
        }
        .padding(.vertical, 4)
    }

    // MARK: - Sub-views

    private var logoView: some View {
        Group {
            if let url = favorite.logoURL {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .success(let img):
                        img.resizable().scaledToFit()
                    default:
                        Image(systemName: "shield.fill")
                            .font(.title2)
                            .foregroundColor(.secondary)
                    }
                }
            } else {
                Image(systemName: "shield.fill")
                    .font(.title2)
                    .foregroundColor(.secondary)
            }
        }
        .frame(width: 36, height: 36)
        .accessibilityHidden(true)
    }

    private func gameStatusView(label: String, isLive: Bool) -> some View {
        HStack(spacing: 4) {
            if isLive {
                Circle()
                    .fill(Color.red)
                    .frame(width: 6, height: 6)
                    .accessibilityHidden(true)
            }
            Text(label)
                .font(.caption)
                .foregroundColor(isLive ? .red : .secondary)
        }
        .padding(.leading, 48)
    }
}

