//
//  AppLifecycle.swift
//  SportsScores
//
//  Detects when the app returns to the foreground on a new calendar day and
//  broadcasts a notification so date-bound ViewModels can reset to today.
//
//  Reset fires when ALL of the following are true:
//    • The app was previously backgrounded
//    • The current calendar day is later than the day it was backgrounded
//    • The local clock is at or past 6:00 AM (avoids resetting for a brief
//      overnight background while the user is still awake)
//

import SwiftUI

extension Notification.Name {
    static let appReturnedToNewDay = Notification.Name("appReturnedToNewDay")
}

enum AppLifecycle {
    private static let lastBackgroundKey = "appLastBackgroundDate"
    private static let resetHour = 6   // 6 AM local time

    static func handlePhaseChange(_ phase: ScenePhase) {
        switch phase {
        case .background:
            UserDefaults.standard.set(Date(), forKey: lastBackgroundKey)
        case .active:
            checkForNewDay()
        default:
            break
        }
    }

    private static func checkForNewDay() {
        guard let lastBg = UserDefaults.standard.object(forKey: lastBackgroundKey) as? Date else { return }
        let cal = Calendar.current
        let today  = cal.startOfDay(for: Date())
        let bgDay  = cal.startOfDay(for: lastBg)
        guard today > bgDay else { return }          // same day — no reset needed
        guard cal.component(.hour, from: Date()) >= resetHour else { return }
        NotificationCenter.default.post(name: .appReturnedToNewDay, object: nil)
    }
}
