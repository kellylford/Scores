//
//  RacingStandingsView.swift
//  SportsScores
//
//  Championship points standings for a racing series.
//  F1 shows two sections (Driver + Constructor); IndyCar and NASCAR show one.
//

import SwiftUI

struct RacingStandingsView: View {
    let standings: [RacingStandingsGroup]
    let isLoading: Bool

    var body: some View {
        if isLoading && standings.isEmpty {
            ProgressView("Loading standings…")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if standings.isEmpty {
            emptyState
        } else {
            standingsList
        }
    }

    // MARK: - List

    private var standingsList: some View {
        List {
            ForEach(standings) { group in
                Section {
                    ForEach(group.entries) { entry in
                        standingsRow(entry)
                    }
                } header: {
                    standingsHeader(group.name)
                }
            }
        }
        .listStyle(.insetGrouped)
    }

    private func standingsHeader(_ groupName: String) -> some View {
        HStack {
            Text("Pos")
                .frame(width: 32, alignment: .trailing)
            Text("Name")
            Spacer()
            Text("Pts")
                .frame(width: 44, alignment: .trailing)
        }
        .font(.caption)
        .foregroundColor(.secondary)
        .accessibilityHidden(true)
    }

    private func standingsRow(_ entry: RacingStandingsEntry) -> some View {
        HStack(spacing: 0) {
            // Position
            Text(String(entry.rank))
                .font(.system(.body, design: .monospaced))
                .foregroundColor(entry.rank <= 3 ? podiumColor(entry.rank) : .primary)
                .frame(width: 32, alignment: .trailing)
                .padding(.trailing, 12)

            // Name + nationality
            VStack(alignment: .leading, spacing: 1) {
                Text(entry.name)
                    .font(.body)
                    .lineLimit(1)
                if !entry.nationality.isEmpty {
                    Text(entry.nationality)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()

            // Points
            Text(entry.points)
                .font(.system(.body, design: .monospaced))
                .frame(width: 44, alignment: .trailing)
        }
        .padding(.vertical, 2)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(rowAccessibilityLabel(entry))
    }

    // MARK: - Empty

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "list.number")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("Standings unavailable")
                .font(.headline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // MARK: - Helpers

    private func podiumColor(_ rank: Int) -> Color {
        switch rank {
        case 1: return .yellow
        case 2: return Color(white: 0.55)
        case 3: return Color(red: 0.72, green: 0.45, blue: 0.20)
        default: return .primary
        }
    }

    private func rowAccessibilityLabel(_ entry: RacingStandingsEntry) -> String {
        var parts = ["Rank \(entry.rank)", entry.name]
        if !entry.nationality.isEmpty { parts.append(entry.nationality) }
        parts.append("\(entry.points) points")
        return parts.joined(separator: ", ")
    }
}
