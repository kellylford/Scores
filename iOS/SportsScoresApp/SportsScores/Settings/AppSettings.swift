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

    // MARK: - Init

    init() {
        let raw = UserDefaults.standard.string(forKey: StorageKeys.teamNamePreference) ?? ""
        teamNamePreference = TeamNamePreference(rawValue: raw) ?? .full
    }
}
