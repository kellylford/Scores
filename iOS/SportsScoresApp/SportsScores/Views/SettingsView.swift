//
//  SettingsView.swift
//  SportsScores
//
//  User-facing settings sheet. Opened from the gear button in
//  SportSelectionView's navigation bar.
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var appSettings: AppSettings
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Form {
                teamNameSection
                aboutSection
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }

    // MARK: - Team Name Section

    private var teamNameSection: some View {
        Section {
            ForEach(TeamNamePreference.allCases) { preference in
                Button {
                    appSettings.teamNamePreference = preference
                } label: {
                    HStack {
                        VStack(alignment: .leading, spacing: 3) {
                            Text(preference.settingsLabel)
                                .foregroundColor(.primary)
                            Text(preference.settingsDescription)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        Spacer()
                        if appSettings.teamNamePreference == preference {
                            Image(systemName: "checkmark")
                                .foregroundColor(.accentColor)
                                .fontWeight(.semibold)
                        }
                    }
                }
                .accessibilityLabel("\(preference.settingsLabel): \(preference.settingsDescription)")
                .accessibilityAddTraits(appSettings.teamNamePreference == preference ? [.isSelected] : [])
            }
        } header: {
            Text("VoiceOver Team Names")
        } footer: {
            exampleFooter
        }
    }

    @ViewBuilder
    private var exampleFooter: some View {
        let pref = appSettings.teamNamePreference
        VStack(alignment: .leading, spacing: 4) {
            Text("Example — Milwaukee Brewers:")
            Text("\"\(pref.exampleText)\"")
                .fontWeight(.semibold)
                .foregroundColor(.accentColor)
        }
        .font(.caption)
        .padding(.top, 4)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Example: VoiceOver would say \(pref.exampleText) for the Milwaukee Brewers")
    }

    // MARK: - About Section

    private var aboutSection: some View {
        Section("About") {
            HStack {
                Text("Version")
                Spacer()
                Text(appVersion)
                    .foregroundColor(.secondary)
            }
        }
    }

    private var appVersion: String {
        let info = Bundle.main.infoDictionary
        let version = info?["CFBundleShortVersionString"] as? String ?? "—"
        let build   = info?["CFBundleVersion"] as? String ?? "—"
        return "\(version) (\(build))"
    }
}

#Preview {
    SettingsView()
        .environmentObject(AppSettings())
}
