//
//  ErrorStateView.swift
//  SportsScores
//

import SwiftUI

/// Reusable error + retry state used across all loading views.
struct ErrorStateView: View {
    let message: String
    let retryAction: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 48))
                .foregroundColor(.orange)
            Text(message)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
            Button("Retry", action: retryAction)
                .buttonStyle(.bordered)
        }
        .padding()
    }
}
