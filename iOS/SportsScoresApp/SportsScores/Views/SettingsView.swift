//
//  SettingsView.swift
//  SportsScores
//
//  Settings tab — accessible from the bottom tab bar.
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var appSettings: AppSettings

    var body: some View {
        Form {
            teamNameSection
            sportsSection
            stadiumExplorationSection
            aboutSection
        }
        .navigationTitle("Settings")
    }

    // MARK: - Team Name Section

    private var teamNameSection: some View {
        Section {
            Picker("Announce teams as", selection: $appSettings.teamNamePreference) {
                ForEach(TeamNamePreference.allCases) { preference in
                    Text(preference.settingsLabel).tag(preference)
                }
            }
            .accessibilityLabel("Announce teams as")
            .accessibilityHint("Selects how team names are spoken by VoiceOver")
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
            Text(pref.settingsDescription)
            Text("Example — Milwaukee Brewers: \"\(pref.exampleText)\"")
                .fontWeight(.semibold)
                .foregroundColor(.accentColor)
        }
        .font(.caption)
        .padding(.top, 4)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(pref.settingsDescription). Example: VoiceOver would say \(pref.exampleText) for the Milwaukee Brewers")
    }

    // MARK: - Sports Section

    private var sportsSection: some View {
        Section {
            // Fixed "Live Scores" row — always first, not movable
            HStack(spacing: 12) {
                Image(systemName: "circle.fill")
                    .foregroundColor(.red)
                    .frame(width: 28)
                VStack(alignment: .leading, spacing: 2) {
                    Text("Live Scores")
                        .font(.headline)
                    Text("All sports — always first")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Spacer()
                Image(systemName: "lock.fill")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Live Scores, always first, locked")

            ForEach(appSettings.sportOrder) { sport in
                SportSettingsRow(sport: sport,
                                 isHidden: appSettings.hiddenSports.contains(sport),
                                 onToggle: { toggle(sport) },
                                 onMoveUp:     { move(sport, by: -1) },
                                 onMoveDown:   { move(sport, by: +1) },
                                 onMoveToTop:  { moveToTop(sport) },
                                 onMoveToBottom: { moveToBottom(sport) })
            }
            .onMove { source, destination in
                appSettings.sportOrder.move(fromOffsets: source, toOffset: destination)
            }
        } header: {
            Text("Home Page Sports")
        } footer: {
            Text("Drag to reorder. Toggle to show or hide a sport. Live Scores is always first.")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - Stadium Exploration Section

    private var stadiumExplorationSection: some View {
        Section {
            Toggle(isOn: $appSettings.useDirectTouchForTours) {
                VStack(alignment: .leading, spacing: 3) {
                    Text("Use Direct Touch")
                    Text("Your finger goes straight to the drag gesture. Turn off to use VoiceOver's standard double-tap-and-hold passthrough instead.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .accessibilityLabel("Use Direct Touch for stadium exploration")
            .accessibilityHint(appSettings.useDirectTouchForTours
                ? "On. Turn off to use VoiceOver double-tap-and-hold passthrough instead."
                : "Off. Turn on for the most responsive drag experience.")
        } header: {
            Text("Stadium Exploration")
        } footer: {
            Text(appSettings.useDirectTouchForTours
                ? "Direct Touch is on. Your finger controls the drag canvas immediately without VoiceOver interception."
                : "Direct Touch is off. Swipe to focus the canvas, then double-tap and hold to drag freely.")
                .font(.caption)
                .foregroundColor(.secondary)
                .accessibilityHidden(true)
        }
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

    // MARK: - Sport ordering helpers

    private func toggle(_ sport: Sport) {
        if appSettings.hiddenSports.contains(sport) {
            appSettings.hiddenSports.remove(sport)
        } else {
            appSettings.hiddenSports.insert(sport)
        }
    }

    private func move(_ sport: Sport, by delta: Int) {
        guard let idx = appSettings.sportOrder.firstIndex(of: sport) else { return }
        let dest = (idx + delta).clamped(to: 0...(appSettings.sportOrder.count - 1))
        guard dest != idx else { return }
        appSettings.sportOrder.move(fromOffsets: IndexSet(integer: idx),
                                    toOffset: dest > idx ? dest + 1 : dest)
    }

    private func moveToTop(_ sport: Sport) {
        guard let idx = appSettings.sportOrder.firstIndex(of: sport), idx != 0 else { return }
        appSettings.sportOrder.move(fromOffsets: IndexSet(integer: idx), toOffset: 0)
    }

    private func moveToBottom(_ sport: Sport) {
        guard let idx = appSettings.sportOrder.firstIndex(of: sport),
              idx != appSettings.sportOrder.count - 1 else { return }
        appSettings.sportOrder.move(fromOffsets: IndexSet(integer: idx),
                                    toOffset: appSettings.sportOrder.count)
    }
}

// MARK: - Sport settings row

private struct SportSettingsRow: View {
    let sport: Sport
    let isHidden: Bool
    let onToggle: () -> Void
    let onMoveUp: () -> Void
    let onMoveDown: () -> Void
    let onMoveToTop: () -> Void
    let onMoveToBottom: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            // Drag handle (visual affordance; actual drag handled by .onMove)
            Image(systemName: "line.3.horizontal")
                .foregroundColor(.secondary)
                .font(.body)
                .frame(width: 24)
                .accessibilityHidden(true)

            Text(sport.icon)
                .font(.title3)
                .frame(width: 28)
                .accessibilityHidden(true)

            Text(sport.displayName)
                .font(.headline)
                .foregroundColor(isHidden ? .secondary : .primary)

            Spacer()

            Button(action: onToggle) {
                Image(systemName: isHidden ? "eye.slash" : "eye")
                    .foregroundColor(isHidden ? .secondary : .accentColor)
            }
            .buttonStyle(.plain)
            .accessibilityLabel(isHidden ? "Show \(sport.displayName)" : "Hide \(sport.displayName)")
            .accessibilityHint(isHidden ? "Adds this sport to the home page" : "Removes this sport from the home page")
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(sport.displayName), \(isHidden ? "hidden" : "visible")")
        .accessibilityHint("Double-tap to toggle visibility. Use actions to reorder.")
        .accessibilityAction(named: "Toggle visibility") { onToggle() }
        .accessibilityAction(named: "Move up") { onMoveUp() }
        .accessibilityAction(named: "Move down") { onMoveDown() }
        .accessibilityAction(named: "Move to top") { onMoveToTop() }
        .accessibilityAction(named: "Move to bottom") { onMoveToBottom() }
    }
}

// MARK: - Comparable clamping helper

private extension Comparable {
    func clamped(to range: ClosedRange<Self>) -> Self {
        min(max(self, range.lowerBound), range.upperBound)
    }
}

#Preview {
    NavigationStack {
        SettingsView()
            .environmentObject(AppSettings())
    }
}
