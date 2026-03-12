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
    static let useDirectTouchForTours = "useDirectTouchForTours"
    static let sportOrder = "sportOrder"
    static let hiddenSports = "hiddenSports"
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

    // MARK: - Home Page Sport Customization

    /// Ordered list of main sports shown on the home page.
    /// Always contains every Sport.allCases entry; users change the order but cannot remove entries.
    /// Soccer is a separate hardcoded row and is not included here.
    @Published var sportOrder: [Sport] {
        didSet {
            UserDefaults.standard.set(sportOrder.map(\.rawValue), forKey: StorageKeys.sportOrder)
        }
    }

    /// Raw values of sports the user has hidden from the home page.
    @Published var hiddenSports: Set<Sport> {
        didSet {
            UserDefaults.standard.set(Array(hiddenSports.map(\.rawValue)), forKey: StorageKeys.hiddenSports)
        }
    }

    /// Sports in user-defined order, filtering out hidden ones — ready for the home page ForEach.
    var visibleSports: [Sport] {
        sportOrder.filter { !hiddenSports.contains($0) }
    }

    // MARK: - Stadium Tour Accessibility

    /// When true the drag canvases in stadium tours use .accessibilityDirectTouch(options: .silentOnTouch)
    /// so VoiceOver silences itself and passes touches straight to the drag gesture.
    /// When false VoiceOver behaves normally; users can still drag via the double-tap-and-hold passthrough.
    @Published var useDirectTouchForTours: Bool {
        didSet {
            UserDefaults.standard.set(useDirectTouchForTours, forKey: StorageKeys.useDirectTouchForTours)
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

        // Default to true (direct touch on) — only false if user has explicitly disabled it
        if UserDefaults.standard.object(forKey: StorageKeys.useDirectTouchForTours) == nil {
            useDirectTouchForTours = true
        } else {
            useDirectTouchForTours = UserDefaults.standard.bool(forKey: StorageKeys.useDirectTouchForTours)
        }

        // Sport order: restore from defaults, filling in any missing sports at the end
        let defaultOrder = Sport.allCases
        if let saved = UserDefaults.standard.stringArray(forKey: StorageKeys.sportOrder) {
            let savedSports = saved.compactMap { Sport(rawValue: $0) }
            let knownSet = Set(savedSports)
            let extras = defaultOrder.filter { !knownSet.contains($0) }
            sportOrder = savedSports + extras
        } else {
            sportOrder = defaultOrder
        }

        // Hidden sports
        if let savedHidden = UserDefaults.standard.stringArray(forKey: StorageKeys.hiddenSports) {
            hiddenSports = Set(savedHidden.compactMap { Sport(rawValue: $0) })
        } else {
            hiddenSports = []
        }
    }
}
