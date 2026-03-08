//
//  AppSettings.swift
//  SportsScores
//
//  Root-level ObservableObject injected into the SwiftUI environment via
//  `.environmentObject()` at the app entry point. All views read
//  preferences through `@EnvironmentObject var appSettings: AppSettings`.
//
//  Preferences are persisted in UserDefaults so they survive restarts.
//

import Foundation
import Combine

private enum StorageKeys {
    static let teamNamePreference = "teamNamePreference"
    static let autoRefreshInterval = "autoRefreshInterval"
}

@MainActor
final class AppSettings: ObservableObject {

    // MARK: - Team Name Announcement

    /// Controls how team names are spoken by VoiceOver in accessible labels.
    /// Visual abbreviations are unaffected by this setting.
    @Published var teamNamePreference: TeamNamePreference {
        didSet {
            UserDefaults.standard.set(
                teamNamePreference.rawValue,
                forKey: StorageKeys.teamNamePreference
            )
        }
    }

    // MARK: - Auto-Refresh Interval

    /// Shared refresh cadence used by both ScoresView and LiveScoresView.
    /// Persisted in UserDefaults so it survives app restarts.
    @Published var autoRefreshInterval: AutoRefreshInterval {
        didSet {
            UserDefaults.standard.set(
                autoRefreshInterval.rawValue,
                forKey: StorageKeys.autoRefreshInterval
            )
        }
    }

    // MARK: - Init

    init() {
        let raw = UserDefaults.standard.string(forKey: StorageKeys.teamNamePreference) ?? ""
        teamNamePreference = TeamNamePreference(rawValue: raw) ?? .full

        let storedInterval = UserDefaults.standard.object(forKey: StorageKeys.autoRefreshInterval) as? Int
        autoRefreshInterval = storedInterval.flatMap { AutoRefreshInterval(rawValue: $0) } ?? .manual
    }
}
