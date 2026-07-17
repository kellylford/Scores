//
//  ScoringSettingsView.swift
//  SportsScores
//
//  Editable league scoring rules. Changing any value re-ranks the cheatsheet
//  instantly via the viewModel's published scoringSettings. Presets offer
//  quick standard / Half-PPR / PPR setup.
//

import SwiftUI

struct ScoringSettingsView: View {
    @ObservedObject var viewModel: FantasyCheatsheetViewModel
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        Form {
            presetsSection
            passingSection
            rushingSection
            receivingSection
            kickingSection
            defenseSection
            pointsAgainstSection
            draftActionsSection
        }
        .navigationTitle("Scoring Settings")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Done") { dismiss() }
            }
        }
    }

    // MARK: - Presets

    private var presetsSection: some View {
        Section {
            HStack(spacing: 8) {
                ForEach(ScoringPreset.allCases) { preset in
                    Button {
                        viewModel.applyPreset(preset)
                    } label: {
                        Text(preset.rawValue)
                            .font(.subheadline.bold())
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 8)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(presetMatches(preset) ? Color.accentColor.opacity(0.18) : Color.secondary.opacity(0.10))
                            )
                            .foregroundColor(presetMatches(preset) ? .accentColor : .primary)
                    }
                    .accessibilityLabel("\(preset.rawValue) preset")
                    .accessibilityValue(presetMatches(preset) ? "active" : "inactive")
                }
            }
        } header: {
            Text("Presets")
        }
    }

    private func presetMatches(_ preset: ScoringPreset) -> Bool {
        switch preset {
        case .standard: return viewModel.scoringSettings == .standard
        case .ppr:      return viewModel.scoringSettings == .ppr
        case .halfPPR:  return viewModel.scoringSettings == .halfPPR
        }
    }

    // MARK: - Passing

    private var passingSection: some View {
        Section {
            settingRow("Passing yards per point", value: $viewModel.scoringSettings.passingYardsPerPoint, step: 1.0, hint: "Default 25 = 1 pt per 25 yards")
            settingRow("Passing TD", value: $viewModel.scoringSettings.passingTD, step: 0.5)
            settingRow("Interception", value: $viewModel.scoringSettings.passingInterception, step: 0.5)
        } header: {
            Text("Passing")
        }
    }

    // MARK: - Rushing

    private var rushingSection: some View {
        Section {
            settingRow("Rushing yards per point", value: $viewModel.scoringSettings.rushingYardsPerPoint, step: 1.0)
            settingRow("Rushing TD", value: $viewModel.scoringSettings.rushingTD, step: 0.5)
            settingRow("Fumble lost", value: $viewModel.scoringSettings.rushingFumble, step: 0.5)
        } header: {
            Text("Rushing")
        }
    }

    // MARK: - Receiving

    private var receivingSection: some View {
        Section {
            settingRow("Receiving yards per point", value: $viewModel.scoringSettings.receivingYardsPerPoint, step: 1.0)
            settingRow("Receiving TD", value: $viewModel.scoringSettings.receivingTD, step: 0.5)
            settingRow("Reception (PPR)", value: $viewModel.scoringSettings.receptions, step: 0.5, hint: "1.0 = PPR, 0.5 = Half-PPR, 0 = Standard")
        } header: {
            Text("Receiving")
        }
    }

    // MARK: - Kicking

    private var kickingSection: some View {
        Section {
            settingRow("Field goal made", value: $viewModel.scoringSettings.fieldGoalMade, step: 0.5)
            settingRow("Extra point made", value: $viewModel.scoringSettings.extraPointMade, step: 0.5)
        } header: {
            Text("Kicking")
        }
    }

    // MARK: - Defense

    private var defenseSection: some View {
        Section {
            settingRow("Sack", value: $viewModel.scoringSettings.defenseSack, step: 0.5)
            settingRow("Interception", value: $viewModel.scoringSettings.defenseInterception, step: 0.5)
            settingRow("Fumble recovered", value: $viewModel.scoringSettings.defenseFumbleRecovered, step: 0.5)
            settingRow("Safety", value: $viewModel.scoringSettings.defenseSafety, step: 0.5)
            settingRow("Defensive TD", value: $viewModel.scoringSettings.defenseTD, step: 0.5)
        } header: {
            Text("Defense / Special Teams")
        }
    }

    // MARK: - Points against (defense)

    private var pointsAgainstSection: some View {
        Section {
            settingRow("0 points allowed", value: $viewModel.scoringSettings.pointsAllowed0, step: 1.0)
            settingRow("1–6 points allowed", value: $viewModel.scoringSettings.pointsAllowed1_6, step: 1.0)
            settingRow("7–13 points allowed", value: $viewModel.scoringSettings.pointsAllowed7_13, step: 1.0)
            settingRow("14–20 points allowed", value: $viewModel.scoringSettings.pointsAllowed14_20, step: 1.0)
            settingRow("21–27 points allowed", value: $viewModel.scoringSettings.pointsAllowed21_27, step: 1.0)
            settingRow("28–34 points allowed", value: $viewModel.scoringSettings.pointsAllowed28_34, step: 1.0)
            settingRow("35+ points allowed", value: $viewModel.scoringSettings.pointsAllowed35Plus, step: 1.0)
        } header: {
            Text("Defense — Points Allowed Bonus")
        } footer: {
            Text("Bonus/penalty added to each team defense based on points allowed. Applies to D/ST only.")
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

    // MARK: - Setting row helper

    @ViewBuilder
    private func settingRow(_ title: String, value: Binding<Double>, step: Double, hint: String? = nil) -> some View {
        HStack {
            VStack(alignment: .leading) {
                Text(title)
                if let hint {
                    Text(hint).font(.caption).foregroundColor(.secondary)
                }
            }
            Spacer()
            Stepper(value: value, step: step) {
                Text(formatted(value: value.wrappedValue))
                    .font(.system(.body, design: .monospaced))
                    .foregroundColor(.accentColor)
            }
            .labelsHidden()
            .accessibilityLabel(title)
            .accessibilityValue(formatted(value: value.wrappedValue))
        }
    }

    private func formatted(value: Double) -> String {
        if value == floor(value) {
            return String(format: "%.0f", value)
        }
        return String(format: "%.1f", value)
    }
}