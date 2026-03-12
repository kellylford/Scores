//
//  ViewMode.swift
//  SportsScores
//
//  Created on 1/4/26.
//
//  This implements the revolutionary three-view-mode system from the desktop app

import Foundation
import SwiftUI

enum ViewMode: String, CaseIterable {
    case table = "Table View"
    case quickList = "Quick List"
    case fullList = "Full List"
    
    var icon: String {
        switch self {
        case .table: return "tablecells"
        case .quickList: return "list.bullet"
        case .fullList: return "list.bullet.rectangle"
        }
    }
    
    var description: String {
        switch self {
        case .table:
            return "Traditional grid format with columns and rows"
        case .quickList:
            return "Comma-separated values for rapid scanning"
        case .fullList:
            return "Header-value pairs for complete context"
        }
    }
    
    var accessibilityLabel: String {
        switch self {
        case .table:
            return "Table View: Grid format with arrow key navigation"
        case .quickList:
            return "Quick List: Comma-separated values"
        case .fullList:
            return "Full List: Complete header-value pairs"
        }
    }
    
    func next() -> ViewMode {
        let all = ViewMode.allCases
        let currentIndex = all.firstIndex(of: self) ?? 0
        let nextIndex = (currentIndex + 1) % all.count
        return all[nextIndex]
    }
}

// MARK: - View Mode Picker Component
struct ViewModePicker: View {
    @Binding var selectedMode: ViewMode
    
    var body: some View {
        Picker("View Mode", selection: $selectedMode) {
            ForEach(ViewMode.allCases, id: \.self) { mode in
                Label(mode.rawValue, systemImage: mode.icon)
                    .tag(mode)
            }
        }
        .pickerStyle(.segmented)
        .padding(.horizontal)
    }
}

// MARK: - View Mode Toggle Button
struct ViewModeToggleButton: View {
    @Binding var currentMode: ViewMode
    
    var body: some View {
        Button(action: {
            withAnimation(.easeInOut(duration: 0.2)) {
                currentMode = currentMode.next()
            }
        }) {
            Label("Cycle View", systemImage: "arrow.triangle.2.circlepath")
        }
        .accessibilityLabel("Cycle through view modes")
        .accessibilityHint("Currently in \(currentMode.rawValue)")
    }
}

// MARK: - Conditional Direct Touch

extension View {
    /// Applies `.accessibilityDirectTouch(options: .silentOnTouch)` only when `enabled` is true.
    /// When disabled, VoiceOver treats the view as a standard element; users can still pass
    /// touches through via the VoiceOver double-tap-and-hold gesture.
    @ViewBuilder
    func conditionalDirectTouch(_ enabled: Bool) -> some View {
        if enabled {
            self.accessibilityDirectTouch(options: .silentOnTouch)
        } else {
            self
        }
    }
}
