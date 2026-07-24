//
//  ScoringSettingsView.swift
//  SportsScores
//
//  Lightweight cheatsheet settings: pick the scoring format (which ESPN rank +
//  projection the board shows) and clear the draft-taken marks. ESPN publishes
//  PPR and Standard rank boards directly; Half-PPR is derived from the PPR board.
//

import SwiftUI

struct ScoringSettingsView: View {
    @ObservedObject var viewModel: FantasyCheatsheetViewModel
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        Form {
            formatSection
            draftActionsSection
        }
        .navigationTitle("Cheatsheet Settings")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Done") { dismiss() }
            }
        }
    }

    // MARK: - Scoring format

    private var formatSection: some View {
        Section {
            Picker("Scoring format", selection: $viewModel.preset) {
                ForEach(ScoringPreset.allCases) { preset in
                    Text(preset.rawValue).tag(preset)
                }
            }
            .pickerStyle(.inline)
            .labelsHidden()
        } header: {
            Text("Scoring Format")
        } footer: {
            Text("Ranks and projected points come straight from ESPN. PPR and Standard use ESPN's published boards; Half-PPR is derived from the PPR board with receptions worth half a point.")
        }
    }

    // MARK: - Draft actions

    private var draftActionsSection: some View {
        Section {
            Button(role: .destructive) {
                viewModel.clearDraft()
            } label: {
                Label("Clear all taken marks", systemImage: "arrow.counterclockwise")
            }
        } header: {
            Text("Draft")
        } footer: {
            Text("Taken/available marks are stored on this device and survive app restarts.")
        }
    }
}
