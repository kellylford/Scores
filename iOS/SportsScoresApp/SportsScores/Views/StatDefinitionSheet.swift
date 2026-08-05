//
//  StatDefinitionSheet.swift
//  SportsScores
//
//  Definition of a single stat, opened by activating a stat category heading
//  on the Stats screen. Text comes from ESPN's own glossary — see
//  `ESPNAPIService.statDefinition(for:sport:)`.
//

import SwiftUI

struct StatDefinitionSheet: View {
    let title: String
    let definition: String
    /// Set for categories that rank teams by what opponents did against them,
    /// where ESPN's definition describes the raw stat and needs that context.
    let opponentNote: String?

    @Environment(\.dismiss) private var dismiss
    /// Moves VoiceOver to the heading when the sheet opens, so the definition is
    /// read instead of leaving focus behind on the list underneath.
    @AccessibilityFocusState private var titleFocused: Bool

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text(title)
                        .font(.title2.bold())
                        .accessibilityAddTraits(.isHeader)
                        .accessibilityFocused($titleFocused)

                    // For an opponent category ESPN's text defines the raw stat
                    // ("the number of points scored per game"), which reads
                    // backwards under a heading like "Fewest Points Allowed Per
                    // Game". Lead with the context so the definition lands
                    // right way round.
                    if let opponentNote {
                        Text(opponentNote)
                            .font(.body)
                            .fixedSize(horizontal: false, vertical: true)

                        Text("ESPN defines the underlying statistic as: \(definition)")
                            .font(.body)
                            .foregroundColor(.secondary)
                            .fixedSize(horizontal: false, vertical: true)
                    } else {
                        Text(definition)
                            .font(.body)
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    Text("Definition from ESPN.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    // .cancelAction binds Escape on any hardware keyboard, which
                    // covers iPad and Mac; the button itself is the only way out
                    // on iPhone.
                    Button("Close") { dismiss() }
                        .keyboardShortcut(.cancelAction)
                }
            }
        }
        .presentationDetents([.medium])
        .onAppear { titleFocused = true }
    }
}

#Preview {
    Text("Stats")
        .sheet(isPresented: .constant(true)) {
            StatDefinitionSheet(
                title: "WHIP",
                definition: "The number representing walks plus hits divided by innings pitched.",
                opponentNote: nil
            )
        }
}
