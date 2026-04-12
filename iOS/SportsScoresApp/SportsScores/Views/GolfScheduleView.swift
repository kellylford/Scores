//
//  GolfScheduleView.swift
//  SportsScores
//
//  Full-season tournament schedule list for a golf tour.
//  Grouped by month, shows past/current/upcoming tournaments.
//  Tapping a row navigates to that tournament in GolfLeagueView.
//

import SwiftUI

struct GolfScheduleView: View {

    let calendar: [GolfCalendarEntry]
    let selectedIndex: Int?
    let onSelect: (Int) -> Void

    private var groupedByMonth: [(String, [(Int, GolfCalendarEntry)])] {
        let fmt = DateFormatter()
        fmt.dateFormat = "MMMM yyyy"
        var groups: [(String, [(Int, GolfCalendarEntry)])] = []
        var currentMonth = ""
        var currentGroup: [(Int, GolfCalendarEntry)] = []

        for (idx, entry) in calendar.enumerated() {
            let month = fmt.string(from: entry.startDate)
            if month != currentMonth {
                if !currentGroup.isEmpty {
                    groups.append((currentMonth, currentGroup))
                }
                currentMonth = month
                currentGroup = []
            }
            currentGroup.append((idx, entry))
        }
        if !currentGroup.isEmpty {
            groups.append((currentMonth, currentGroup))
        }
        return groups
    }

    var body: some View {
        if calendar.isEmpty {
            VStack(spacing: 16) {
                Image(systemName: "calendar")
                    .font(.system(size: 48))
                    .foregroundColor(.secondary)
                Text("Schedule Not Available")
                    .font(.headline)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else {
            List {
                ForEach(groupedByMonth, id: \.0) { month, entries in
                    Section(header: Text(month).accessibilityAddTraits(.isHeader)) {
                        ForEach(entries, id: \.0) { idx, entry in
                            tournamentRow(entry: entry, index: idx)
                        }
                    }
                }
            }
            .listStyle(.insetGrouped)
        }
    }

    private func tournamentRow(entry: GolfCalendarEntry, index: Int) -> some View {
        let isSelected = selectedIndex == index
        let isPast     = entry.endDate < Date()
        let isActive   = entry.startDate <= Date() && entry.endDate >= Date()

        return Button {
            onSelect(index)
        } label: {
            HStack(spacing: 12) {
                // Status indicator dot
                Circle()
                    .fill(dotColor(isPast: isPast, isActive: isActive))
                    .frame(width: 8, height: 8)

                VStack(alignment: .leading, spacing: 2) {
                    Text(entry.name)
                        .font(.subheadline)
                        .foregroundColor(isPast ? .secondary : .primary)
                        .lineLimit(2)
                    Text(entry.dateRangeText)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                if isSelected {
                    Image(systemName: "checkmark")
                        .font(.caption.bold())
                        .foregroundColor(.accentColor)
                }
            }
            .padding(.vertical, 2)
        }
        .buttonStyle(.plain)
        .listRowBackground(isSelected ? Color.accentColor.opacity(0.08) : Color.clear)
        .accessibilityLabel(accessibilityLabel(entry: entry, isPast: isPast, isActive: isActive, isSelected: isSelected))
        .accessibilityHint("Double tap to view leaderboard")
    }

    private func dotColor(isPast: Bool, isActive: Bool) -> Color {
        if isActive { return .red }
        if isPast   { return Color.secondary.opacity(0.4) }
        return Color.secondary.opacity(0.2)
    }

    private func accessibilityLabel(entry: GolfCalendarEntry, isPast: Bool, isActive: Bool, isSelected: Bool) -> String {
        let status = isActive ? "In progress" : (isPast ? "Completed" : "Upcoming")
        let selected = isSelected ? ", currently selected" : ""
        return "\(entry.name), \(entry.dateRangeText), \(status)\(selected)"
    }
}
