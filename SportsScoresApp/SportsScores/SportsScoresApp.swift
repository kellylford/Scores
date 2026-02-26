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
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onAppear {
                    UNUserNotificationCenter.current().requestAuthorization(
                        options: [.alert, .sound, .badge]
                    ) { _, _ in }
                }
        }
    }
}
