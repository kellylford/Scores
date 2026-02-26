//
//  ScoreMonitorService.swift
//  SportsScores
//
//  Phase 7.2 — Score change monitoring.
//
//  Usage:
//    • Toggle monitoring:  ScoreMonitorService.shared.toggle(game:)
//    • Check if watched:   ScoreMonitorService.shared.isMonitored(gameId:)
//    • After each scores refresh pass the fresh Game array to checkForChanges(games:)
//      – foreground: accessibility announcement
//      – background: local UNUserNotification
//
//  Watched game IDs are persisted across launches in UserDefaults.
//  Last-known scores are in-memory only (reset on launch is intentional).
//

import Foundation
import UserNotifications
import UIKit

@MainActor
final class ScoreMonitorService: ObservableObject {

    static let shared = ScoreMonitorService()

    // MARK: - Published / Observed state

    /// Set of game IDs currently being monitored.
    @Published private(set) var monitoredIds: Set<String> = []

    // MARK: - Private storage

    /// Last-known scores keyed by game ID.  Format: (away, home)
    private var lastKnownScores: [String: (away: Int, home: Int)] = [:]

    private let defaults = UserDefaults.standard
    private let defaultsKey = "monitoredGameIds"

    // MARK: - Init

    private init() {
        // Restore persisted watched IDs
        let saved = defaults.stringArray(forKey: defaultsKey) ?? []
        monitoredIds = Set(saved)
    }

    // MARK: - Toggle monitoring

    func toggle(game: Game) {
        if monitoredIds.contains(game.id) {
            monitoredIds.remove(game.id)
            lastKnownScores.removeValue(forKey: game.id)
        } else {
            monitoredIds.insert(game.id)
            // Seed the current score so the first check doesn't immediately fire.
            if let away = game.awayTeam.score, let home = game.homeTeam.score {
                lastKnownScores[game.id] = (away, home)
            }
        }
        persist()
    }

    func isMonitored(gameId: String) -> Bool {
        monitoredIds.contains(gameId)
    }

    // MARK: - Score-change detection

    /// Call this every time a fresh batch of games arrives (from ScoresViewModel.fetchGames).
    /// Compares incoming scores against last-known values for watched games and fires
    /// notifications / accessibility announcements for any changes.
    func checkForChanges(games: [Game]) {
        for game in games {
            guard monitoredIds.contains(game.id) else { continue }
            guard let awayScore = game.awayTeam.score,
                  let homeScore = game.homeTeam.score else { continue }

            let last = lastKnownScores[game.id]
            if let last = last {
                if awayScore != last.away || homeScore != last.home {
                    // Score changed — announce
                    let message = "\(game.awayTeam.abbreviation) \(awayScore) – \(homeScore) \(game.homeTeam.abbreviation)"
                    fire(update: message, game: game)
                }
            }
            // Update cache regardless (seeds on first call if not yet present)
            lastKnownScores[game.id] = (awayScore, homeScore)
        }
    }

    // MARK: - Fire notification / announcement

    private func fire(update message: String, game: Game) {
        let appState = UIApplication.shared.applicationState

        if appState == .active {
            // Foreground: VoiceOver accessibility announcement
            UIAccessibility.post(notification: .announcement, argument: message)
        } else {
            // Background / inactive: local push notification
            let content = UNMutableNotificationContent()
            content.title = "Score Update"
            content.body = message
            content.sound = .default
            let request = UNNotificationRequest(
                identifier: "score-\(game.id)-\(Int(Date().timeIntervalSince1970))",
                content: content,
                trigger: nil  // deliver immediately
            )
            UNUserNotificationCenter.current().add(request) { error in
                if let error = error {
                    print("[ScoreMonitor] Notification error: \(error)")
                }
            }
        }
    }

    // MARK: - Persistence

    private func persist() {
        defaults.set(Array(monitoredIds), forKey: defaultsKey)
    }
}
