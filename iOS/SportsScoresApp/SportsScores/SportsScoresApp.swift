//
//  SportsScoresApp.swift
//  SportsScores
//
//  Created on 1/4/26.
//

import SwiftUI

@main
struct SportsScoresApp: App {
    @StateObject private var appSettings = AppSettings()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appSettings)
        }
        .onChange(of: scenePhase) { _, newPhase in
            AppLifecycle.handlePhaseChange(newPhase)
        }
    }
}
