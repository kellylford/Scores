//
//  RacingResultsView.swift
//  SportsScores
//
//  Displays the current or most recent race for a series.
//
//  States:
//   - Scheduled: race name, date, broadcast network
//   - In Progress / Final: driver finishing order list
//   - No event: off-season placeholder
//

import SwiftUI

struct RacingResultsView: View {
    let series: Sport
    let raceEvent: RaceEvent?
    let isLoading: Bool

    var body: some View {
        if isLoading && raceEvent == nil {
            ProgressView("Loading…")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if let event = raceEvent {
            raceContent(event)
        } else {
            emptyState
        }
    }

    // MARK: - Main content

    @ViewBuilder
    private func raceContent(_ event: RaceEvent) -> some View {
        List {
            raceHeaderSection(event)

            if !event.competitors.isEmpty {
                resultsSection(event)
            }
        }
        .listStyle(.insetGrouped)
    }

    // Race name / date / status header
    private func raceHeaderSection(_ event: RaceEvent) -> some View {
        Section {
            VStack(alignment: .leading, spacing: 8) {
                HStack(alignment: .top) {
                    Text(event.name)
                        .font(.headline)
                        .fixedSize(horizontal: false, vertical: true)

                    Spacer()

                    if event.isInProgress {
                        Text("LIVE")
                            .font(.caption.bold())
                            .foregroundColor(.white)
                            .padding(.horizontal, 7)
                            .padding(.vertical, 3)
                            .background(Color.red, in: Capsule())
                    } else if event.isCompleted {
                        Text("FINAL")
                            .font(.caption.bold())
                            .foregroundColor(.secondary)
                    }
                }

                HStack(spacing: 16) {
                    Label(
                        event.date.formatted(date: .abbreviated, time: event.isScheduled ? .shortened : .omitted),
                        systemImage: "calendar"
                    )
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                    if !event.broadcastText.isEmpty {
                        Label(event.broadcastText, systemImage: "tv")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding(.vertical, 4)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(headerAccessibilityLabel(event))
    }

    // Finishing order or current running order
    private func resultsSection(_ event: RaceEvent) -> some View {
        Section {
            ForEach(event.competitors) { competitor in
                competitorRow(competitor, isWinner: event.isCompleted && competitor.position == 1)
            }
        } header: {
            Text(event.isInProgress ? "Current Running Order" : "Results")
        }
    }

    private func competitorRow(_ competitor: RaceCompetitor, isWinner: Bool) -> some View {
        HStack(spacing: 12) {
            // Position number
            Text(String(competitor.position))
                .font(.system(.body, design: .monospaced).bold())
                .foregroundColor(competitor.position <= 3 ? podiumColor(competitor.position) : .secondary)
                .frame(width: 28, alignment: .trailing)

            // Trophy for winner when completed
            if isWinner {
                Image(systemName: "trophy.fill")
                    .font(.caption)
                    .foregroundColor(.yellow)
                    .frame(width: 18)
            } else {
                Spacer().frame(width: 18)
            }

            VStack(alignment: .leading, spacing: 1) {
                Text(competitor.driverName)
                    .font(.body)
                if !competitor.nationality.isEmpty {
                    Text(competitor.nationality)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()
        }
        .padding(.vertical, 2)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(competitorAccessibilityLabel(competitor))
    }

    // MARK: - Empty state

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "flag.checkered")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("No Race Scheduled")
                .font(.headline)
                .foregroundColor(.secondary)
            Text("Check back during the racing season.")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // MARK: - Helpers

    private func podiumColor(_ position: Int) -> Color {
        switch position {
        case 1: return .yellow
        case 2: return Color(white: 0.6)
        case 3: return Color(red: 0.72, green: 0.45, blue: 0.20)
        default: return .secondary
        }
    }

    private func headerAccessibilityLabel(_ event: RaceEvent) -> String {
        var parts = [event.name]
        if event.isInProgress {
            parts.append("Live")
        } else if event.isCompleted {
            parts.append("Final")
        } else {
            parts.append(event.date.formatted(date: .long, time: .shortened))
        }
        if !event.broadcastText.isEmpty {
            parts.append("on \(event.broadcastText)")
        }
        return parts.joined(separator: ". ")
    }

    private func competitorAccessibilityLabel(_ competitor: RaceCompetitor) -> String {
        var label = "Position \(competitor.position), \(competitor.driverName)"
        if !competitor.nationality.isEmpty {
            label += ", \(competitor.nationality)"
        }
        return label
    }
}
