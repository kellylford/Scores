//
//  SportsScoresApp.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI
import UserNotifications

@main
struct SportsScoresApp: App {
    @StateObject private var appSettings = AppSettings()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appSettings)
                .onAppear {
                    UNUserNotificationCenter.current().requestAuthorization(
                        options: [.alert, .sound, .badge]
                    ) { _, _ in }
                }
        }
    }
}
