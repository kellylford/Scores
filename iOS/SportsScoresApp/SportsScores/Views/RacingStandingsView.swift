//
//  RacingStandingsView.swift
//  SportsScores
//
//  Championship points standings for a racing series.
//  F1 shows two sections (Driver + Constructor); IndyCar and NASCAR show one.
//  Supports three view modes (Quick List / Full List / Table).
//

import SwiftUI

struct RacingStandingsView: View {
    let standings: [RacingStandingsGroup]
    let isLoading: Bool
    let viewMode: ViewMode

    // Table column definitions (nationality omitted for Constructor groups)
    private func tableHeaders(for group: RacingStandingsGroup) -> [String] {
        group.isConstructors ? ["Pos", "Constructor", "Pts"] : ["Pos", "Driver", "Nat", "Pts"]
    }
    private func tableRow(_ entry: RacingStandingsEntry, isConstructors: Bool) -> [String] {
        if isConstructors {
            return [String(entry.rank), entry.name, entry.points]
        } else {
            return [String(entry.rank), entry.name, entry.nationality, entry.points]
        }
    }

    var body: some View {
        if isLoading && standings.isEmpty {
            ProgressView("Loading standings…")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if standings.isEmpty {
            emptyState
        } else {
            standingsContent
        }
    }

    // MARK: - Content switch

    private var standingsContent: some View {
        ScrollView {
            VStack(spacing: 16) {
                ForEach(standings) { group in
                    switch viewMode {
                    case .table:     tableSection(group)
                    case .quickList: listSection(group, fullLabels: false)
                    case .fullList:  listSection(group, fullLabels: true)
                    }
                }
            }
            .padding(.vertical, 8)
        }
    }

    // MARK: - Table mode

    private func tableSection(_ group: RacingStandingsGroup) -> some View {
        let isConstructors = group.isConstructors
        let headers = tableHeaders(for: group)

        return VStack(spacing: 0) {
            // Section heading
            Text(group.name)
                .font(.caption.bold())
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 16)
                .padding(.top, 4)
                .padding(.bottom, 4)
                .accessibilityAddTraits(.isHeader)

            // Column header row
            HStack(spacing: 0) {
                Text("Pos")
                    .frame(width: 36, alignment: .trailing)
                Text(isConstructors ? "Constructor" : "Driver")
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.leading, 12)
                if !isConstructors {
                    Text("Nat")
                        .frame(width: 44, alignment: .trailing)
                }
                Text("Pts")
                    .frame(width: 52, alignment: .trailing)
            }
            .font(.caption.bold())
            .foregroundColor(.secondary)
            .padding(.vertical, 6)
            .padding(.horizontal, 16)
            .background(Color.secondary.opacity(0.10))

            Divider()

            VStack(spacing: 0) {
                ForEach(Array(group.entries.enumerated()), id: \.element.id) { idx, entry in
                    tableEntryRow(entry, isConstructors: isConstructors, idx: idx)
                    if idx < group.entries.count - 1 {
                        Divider().padding(.leading, 16)
                    }
                }
            }
            .accessibilityHidden(true)
            .overlay(
                AccessibleDataTable(
                    headers: headers,
                    rows: group.entries.map { tableRow($0, isConstructors: isConstructors) }
                )
                .allowsHitTesting(false)
            )
        }
    }

    private func tableEntryRow(_ entry: RacingStandingsEntry, isConstructors: Bool, idx: Int) -> some View {
        HStack(spacing: 0) {
            Text(String(entry.rank))
                .font(.system(.body, design: .monospaced))
                .foregroundColor(podiumColor(entry.rank))
                .frame(width: 36, alignment: .trailing)

            Text(entry.name)
                .font(.body)
                .lineLimit(1)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.leading, 12)

            if !isConstructors {
                Text(entry.nationality)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .frame(width: 44, alignment: .trailing)
            }

            Text(entry.points)
                .font(.system(.body, design: .monospaced))
                .frame(width: 52, alignment: .trailing)
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 16)
        .background(idx % 2 == 0 ? Color.clear : Color.secondary.opacity(0.04))
    }

    // MARK: - Quick List / Full List (visually identical; only VoiceOver label differs)

    private func listSection(_ group: RacingStandingsGroup, fullLabels: Bool) -> some View {
        VStack(spacing: 0) {
            Text(group.name)
                .font(.caption.bold())
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 16)
                .padding(.top, 4)
                .padding(.bottom, 4)
                .accessibilityAddTraits(.isHeader)

            VStack(spacing: 0) {
                ForEach(group.entries) { entry in
                    listEntryRow(entry, isConstructors: group.isConstructors, fullLabels: fullLabels)
                    Divider().padding(.leading, 16)
                }
            }
        }
    }

    private func listEntryRow(_ entry: RacingStandingsEntry, isConstructors: Bool, fullLabels: Bool) -> some View {
        HStack(spacing: 0) {
            Text(String(entry.rank))
                .font(.system(.subheadline, design: .monospaced))
                .foregroundColor(podiumColor(entry.rank))
                .frame(width: 32, alignment: .trailing)

            VStack(alignment: .leading, spacing: 1) {
                Text(entry.name)
                    .font(.subheadline)
                    .lineLimit(1)
                if !isConstructors && !entry.nationality.isEmpty {
                    Text(entry.nationality)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(.leading, 12)

            Spacer()

            Text(entry.points)
                .font(.system(.subheadline, design: .monospaced))
                .frame(width: 52, alignment: .trailing)
        }
        .padding(.vertical, 9)
        .padding(.horizontal, 16)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(fullLabels
            ? fullListLabel(entry, isConstructors: isConstructors)
            : quickListLabel(entry, isConstructors: isConstructors))
    }

    // MARK: - Accessibility labels

    private func quickListLabel(_ entry: RacingStandingsEntry, isConstructors: Bool) -> String {
        // Terse: "1 Max Verstappen — 350"
        var label = "\(entry.rank) \(entry.name)"
        if !isConstructors && !entry.nationality.isEmpty {
            label += " · \(entry.nationality)"
        }
        label += " — \(entry.points)"
        return label
    }

    private func fullListLabel(_ entry: RacingStandingsEntry, isConstructors: Bool) -> String {
        // Verbose: "Rank: 1, Driver: Max Verstappen, Nationality: Dutch, Points: 350"
        let entityWord = isConstructors ? "Constructor" : "Driver"
        var parts = ["Rank: \(entry.rank)", "\(entityWord): \(entry.name)"]
        if !isConstructors && !entry.nationality.isEmpty {
            parts.append("Nationality: \(entry.nationality)")
        }
        parts.append("Points: \(entry.points)")
        return parts.joined(separator: ", ")
    }

    // MARK: - Empty state

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "list.number")
                .font(.system(size: 48)).foregroundColor(.secondary)
            Text("Standings unavailable")
                .font(.headline).foregroundColor(.secondary)
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
}

private extension RacingStandingsGroup {
    var isConstructors: Bool { name.lowercased().contains("constructor") }
}
