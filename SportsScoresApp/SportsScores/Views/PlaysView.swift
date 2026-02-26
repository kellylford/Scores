//
//  PlaysView.swift
//  SportsScores
//
//  Four-level collapsible plays hierarchy for MLB:
//    Inning  →  Half (Top/Bottom)  →  At-bat  →  Pitches
//
//  VoiceOver model on at-bat rows:
//    • accessibilityValue reflects the "current" pitch as you step through
//    • swipe up   (increment) → next pitch, plays audio + announces details
//    • swipe down (decrement) → previous pitch, plays audio + announces details
//    • custom action "Play full at-bat" → plays entire pitch sequence
//
//  For non-MLB sports: two-level grouping (Period → Plays flat list).
//

import SwiftUI

// MARK: - Data model helpers

private struct HalfInningGroup: Identifiable {
    let id: String              // e.g. "Top-3"
    let halfType: String        // "Top" / "Bottom"
    let inningNumber: Int
    let inningLabel: String     // "3rd Inning"
    let atBats: [AtBatGroup]
    let runsScored: Int         // sum of scoreValue in this half
}

private struct AtBatGroup: Identifiable {
    let id: String              // atBatId
    let headerText: String      // "Lopez pitches to Meadows"
    let resultText: String?     // "Meadows grounded out…"
    let pitches: [GameDetails.Play]
    let notePlay: GameDetails.Play?   // the N-type notes play (for outs display)
}

private struct InningGroup: Identifiable {
    let id: String
    let label: String
    let halves: [HalfInningGroup]
    let scoreSummary: String?   // e.g. "Away scored 2" or nil
}

private struct PeriodGroup: Identifiable {
    let id: String
    let label: String
    let plays: [GameDetails.Play]
}

// MARK: - MLB Plays View

struct MLBPlaysView: View {
    let plays: [GameDetails.Play]
    let awayAbbr: String
    let homeAbbr: String
    @ObservedObject var audio: PitchAudioEngine

    @State private var expandedInnings: Set<String> = []
    @State private var expandedHalves: Set<String> = []
    @State private var expandedAtBats: Set<String> = []
    /// Per-at-bat pitch navigation index.
    /// -1 = showing at-bat result (initial). 0..N-1 = pitch at that index.
    @State private var voicePitchIndex: [String: Int] = [:]

    private var innings: [InningGroup] { buildInnings() }

    var body: some View {
        ScrollView {
            if innings.isEmpty {
                Text("Play-by-play not available")
                    .foregroundColor(.secondary)
                    .padding()
            } else {
                // Audio status banner
                audioBanner
                    .padding(.horizontal)
                    .padding(.top, 8)

                LazyVStack(spacing: 6, pinnedViews: []) {
                    ForEach(innings) { inning in
                        inningSection(inning)
                    }
                }
                .padding(.horizontal)
                .padding(.bottom, 16)
            }
        }
    }

    // MARK: - Audio Banner

    private var audioBanner: some View {
        HStack(spacing: 10) {
            Image(systemName: audio.isPlaying ? "speaker.wave.2.fill" : "music.note")
                .foregroundColor(audio.isPlaying ? .blue : .secondary)
                .frame(width: 20)
            Text(audio.statusMessage.isEmpty
                 ? "Focus a batter · swipe ↑↓ to step through pitches"
                 : audio.statusMessage)
                .font(.caption)
                .foregroundColor(audio.isPlaying ? .primary : .secondary)
            Spacer()
            if audio.isPlaying {
                Button("Stop") { audio.stop() }
                    .font(.caption.bold())
                    .buttonStyle(.borderedProminent)
                    .tint(.red)
            }
        }
        .padding(10)
        .background(Color.secondary.opacity(0.08))
        .cornerRadius(10)
    }

    // MARK: - Inning level

    @ViewBuilder
    private func inningSection(_ inning: InningGroup) -> some View {
        let isOpen = expandedInnings.contains(inning.id)

        VStack(spacing: 0) {
            // Inning header button
            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    if isOpen { expandedInnings.remove(inning.id) }
                    else { expandedInnings.insert(inning.id) }
                }
            } label: {
                HStack {
                    Image(systemName: isOpen ? "chevron.down" : "chevron.right")
                        .foregroundColor(.secondary)
                        .frame(width: 16)
                    Text(inning.label)
                        .font(.headline)
                    Spacer()
                    if let summary = inning.scoreSummary {
                        Text(summary)
                            .font(.caption.bold())
                            .foregroundColor(.green)
                    }
                }
                .padding(12)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .accessibilityLabel(inning.label + (inning.scoreSummary.map { ", \($0)" } ?? ""))
            .accessibilityHint(isOpen ? "Double tap to collapse." : "Double tap to expand.")

            if isOpen {
                Divider().padding(.horizontal)
                VStack(spacing: 4) {
                    ForEach(inning.halves) { half in
                        halfSection(half)
                    }
                }
                .padding(.bottom, 4)
            }
        }
        .background(Color.secondary.opacity(0.07))
        .cornerRadius(10)
    }

    // MARK: - Half-inning level

    @ViewBuilder
    private func halfSection(_ half: HalfInningGroup) -> some View {
        let isOpen = expandedHalves.contains(half.id)
        let teamName = half.halfType == "Top" ? awayAbbr : homeAbbr
        let runsText = half.runsScored > 0 ? ", \(half.runsScored) run\(half.runsScored == 1 ? "" : "s")" : ""
        let halfLabel = "\(half.halfType) — \(teamName) Batting"
        let halfLabelFull = halfLabel + runsText

        VStack(spacing: 0) {
            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    if isOpen { expandedHalves.remove(half.id) }
                    else { expandedHalves.insert(half.id) }
                }
            } label: {
                HStack {
                    Image(systemName: isOpen ? "chevron.down" : "chevron.right")
                        .foregroundColor(.secondary)
                        .frame(width: 16)
                    Text(halfLabel)
                        .font(.subheadline.bold())
                    Spacer()
                    if half.runsScored > 0 {
                        Text("\(half.runsScored)R")
                            .font(.caption.bold())
                            .foregroundColor(.green)
                    } else {
                        Text("\(half.atBats.count) AB")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .padding(.leading, 12)
            .accessibilityLabel(halfLabelFull)
            .accessibilityHint(isOpen ? "Double tap to collapse." : "Double tap to expand.")

            if isOpen {
                VStack(spacing: 3) {
                    ForEach(half.atBats) { ab in
                        atBatRow(ab)
                    }
                }
                .padding(.horizontal, 8)
                .padding(.bottom, 4)
            }
        }
        .background(Color.secondary.opacity(0.04))
        .cornerRadius(8)
        .padding(.horizontal, 4)
    }

    // MARK: - At-bat level (with VoiceOver adjustable pitches)

    @ViewBuilder
    private func atBatRow(_ ab: AtBatGroup) -> some View {
        let isOpen = expandedAtBats.contains(ab.id)
        let pitchCount = ab.pitches.count
        let currentIdx = voicePitchIndex[ab.id] ?? -1   // -1 = result (initial)

        VStack(spacing: 0) {
            // At-bat header
            Button {
                withAnimation(.easeInOut(duration: 0.15)) {
                    if isOpen { expandedAtBats.remove(ab.id) }
                    else { expandedAtBats.insert(ab.id) }
                }
            } label: {
                HStack(spacing: 8) {
                    Image(systemName: isOpen ? "chevron.down" : "chevron.right")
                        .foregroundColor(.secondary)
                        .frame(width: 14)

                    VStack(alignment: .leading, spacing: 2) {
                        Text(ab.headerText)
                            .font(.subheadline)
                            .lineLimit(1)
                        if let result = ab.resultText {
                            Text(result)
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .lineLimit(1)
                        }
                    }

                    Spacer()

                    // Pitch count + result dots
                    if pitchCount > 0 {
                        HStack(spacing: 2) {
                            ForEach(ab.pitches, id: \.id) { p in
                                pitchDot(p)
                            }
                        }
                        Text("\(pitchCount)p")
                            .font(.caption2.monospacedDigit())
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 7)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            // VoiceOver: swipe up/down to step through pitches
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(ab.headerText)
            .accessibilityValue(pitchAccessibilityValue(ab: ab, index: currentIdx))
            .accessibilityAdjustableAction { direction in
                guard pitchCount > 0 else { return }
                var idx = voicePitchIndex[ab.id] ?? -1  // -1 = result state
                switch direction {
                case .increment:
                    // Swipe up: step forward through pitches
                    if idx < pitchCount - 1 { idx += 1 }
                    voicePitchIndex[ab.id] = idx
                    if idx >= 0 { audio.play(ab.pitches[idx]) }
                case .decrement:
                    if idx > 0 {
                        // Step back through pitches
                        idx -= 1
                        voicePitchIndex[ab.id] = idx
                        audio.play(ab.pitches[idx])
                    } else if idx == 0 {
                        // Back to result
                        voicePitchIndex[ab.id] = -1
                    } else {
                        // Already at result (idx == -1): play full sequence
                        audio.playSequence(ab.pitches)
                    }
                @unknown default: break
                }
            }
            .accessibilityHint(pitchCount > 0
                ? "Swipe up to step through pitches. Swipe down from result to play full sequence."
                : "")

            // Expanded: pitch rows
            if isOpen && pitchCount > 0 {
                Divider().padding(.horizontal, 10)
                ForEach(Array(ab.pitches.enumerated()), id: \.element.id) { i, pitch in
                    pitchRow(pitch, number: i + 1, batterHand: ab.pitches.first?.bats?.abbreviation)
                }
            }
        }
        .background(Color(uiColor: .systemBackground))
        .cornerRadius(8)
        .shadow(color: .black.opacity(0.04), radius: 1, x: 0, y: 1)
    }

    private func pitchAccessibilityValue(ab: AtBatGroup, index: Int) -> String {
        // index == -1 (or no pitches): show at-bat result
        if index < 0 || ab.pitches.isEmpty {
            return ab.resultText ?? ""
        }
        guard index < ab.pitches.count else { return ab.resultText ?? "" }
        let p = ab.pitches[index]
        let num = "Pitch \(index + 1) of \(ab.pitches.count)"
        let type_ = p.pitchType?.text ?? p.type.text
        let vel = p.pitchVelocity.map { "\($0) mph" } ?? ""
        let loc = p.locationDescription(batterHand: p.bats?.abbreviation)
        let result = p.type.text
        return [num, type_, vel, loc, result].filter { !$0.isEmpty }.joined(separator: ", ")
    }

    // MARK: - Pitch row (sighted expanded view)

    private func pitchRow(_ pitch: GameDetails.Play, number: Int, batterHand: String?) -> some View {
        Button {
            audio.play(pitch)
        } label: {
            HStack(spacing: 8) {
                Text("\(number)")
                    .font(.caption2.monospacedDigit())
                    .foregroundColor(.secondary)
                    .frame(width: 18, alignment: .trailing)

                pitchDot(pitch)

                VStack(alignment: .leading, spacing: 1) {
                    Text(pitch.pitchType?.text ?? pitch.type.text)
                        .font(.caption.bold())
                    if let vel = pitch.pitchVelocity {
                        Text("\(vel) mph")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
                .frame(width: 110, alignment: .leading)

                Text(pitch.locationDescription(batterHand: batterHand))
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)

                if let count = pitch.resultCount {
                    Text("\(count.balls)-\(count.strikes)")
                        .font(.caption2.monospacedDigit())
                        .foregroundColor(.secondary)
                        .frame(width: 26, alignment: .trailing)
                }

                Image(systemName: "speaker.wave.1")
                    .font(.caption2)
                    .foregroundColor(.blue.opacity(0.7))
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 5)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityLabel("\(pitch.pitchType?.text ?? "Pitch") \(pitch.pitchVelocity.map { "\($0) mph" } ?? ""), \(pitch.locationDescription(batterHand: batterHand)), \(pitch.type.text)")
    }

    @ViewBuilder
    private func pitchDot(_ pitch: GameDetails.Play) -> some View {
        let label = pitch.pitchResultLabel
        let color  = pitchResultColor(pitch)
        Text(label)
            .font(.system(size: 9, weight: .bold, design: .monospaced))
            .foregroundColor(.white)
            .frame(width: 16, height: 16)
            .background(color)
            .cornerRadius(3)
    }

    private func pitchResultColor(_ pitch: GameDetails.Play) -> Color {
        switch pitch.type.type {
        case "ball":                              return .blue
        case "called-strike", "swinging-strike": return .red
        case "foul":                              return .orange
        case "in-play-out":                       return .gray
        case "in-play-score", "in-play-no-out":  return .green
        default:                                  return Color.secondary
        }
    }

    // MARK: - Build data

    private func buildInnings() -> [InningGroup] {
        // Only process non-empty plays
        let relevant = plays.filter { $0.summaryType != nil }
        guard !relevant.isEmpty else { return [] }

        // Build ordered list of unique (halfType, inningNumber) keys
        var halfOrder: [String] = []
        var halfPlays: [String: [GameDetails.Play]] = [:]
        var halfMeta: [String: (type: String, number: Int, label: String)] = [:]

        for play in relevant {
            guard let halfType = play.period?.type,
                  let num = play.period?.number else { continue }
            let key = "\(halfType)-\(num)"
            if halfPlays[key] == nil {
                halfOrder.append(key)
                halfMeta[key] = (halfType, num, play.period?.displayValue ?? "Inning \(num)")
            }
            halfPlays[key, default: []].append(play)
        }

        // Group half-innings into innings
        var inningOrder: [Int] = []
        var inningHalves: [Int: [String]] = [:]
        for key in halfOrder {
            guard let meta = halfMeta[key] else { continue }
            if inningHalves[meta.number] == nil { inningOrder.append(meta.number) }
            inningHalves[meta.number, default: []].append(key)
        }

        return inningOrder.map { num in
            let keys = inningHalves[num] ?? []
            let halves: [HalfInningGroup] = keys.compactMap { key in
                guard let meta = halfMeta[key],
                      let plays = halfPlays[key] else { return nil }
                return buildHalf(key: key, meta: meta, plays: plays)
            }
            let label = halves.first?.inningLabel ?? "Inning \(num)"
            // Build score summary: mention halves where runs scored
            let scoreParts: [String] = halves.compactMap { half in
                guard half.runsScored > 0 else { return nil }
                let team = half.halfType == "Top" ? awayAbbr : homeAbbr
                let runs = half.runsScored
                return "\(team) \(runs)\(runs == 1 ? " run" : " runs")"
            }
            let scoreSummary = scoreParts.isEmpty ? nil : scoreParts.joined(separator: ", ")
            return InningGroup(id: "I-\(num)", label: label, halves: halves, scoreSummary: scoreSummary)
        }
    }

    private func buildHalf(
        key: String,
        meta: (type: String, number: Int, label: String),
        plays: [GameDetails.Play]
    ) -> HalfInningGroup {
        // Group by atBatId, preserving order
        var abOrder: [String] = []
        var abPlays: [String: [GameDetails.Play]] = [:]
        for play in plays {
            let abKey = play.atBatId ?? play.id
            if abPlays[abKey] == nil { abOrder.append(abKey) }
            abPlays[abKey, default: []].append(play)
        }

        let atBats: [AtBatGroup] = abOrder.compactMap { abKey -> AtBatGroup? in
            guard let group = abPlays[abKey] else { return nil }
            let header = group.first(where: { $0.summaryType == "A" })?.text
                      ?? group.first?.text
                      ?? "At-bat"
            // "S" = scoring play (HR, RBI hit, etc.), "N" = ordinary result
            let resultPlay = group.first(where: { $0.summaryType == "S" })
                          ?? group.first(where: { $0.summaryType == "N" })
            let result = resultPlay?.text
            let pitches = group.filter { $0.summaryType == "P" && $0.isPitch }
            let notePlay = resultPlay
            // Skip pure inning-header groups (only "I" plays, no batter info)
            guard group.contains(where: { $0.summaryType != "I" }) else { return nil }
            return AtBatGroup(
                id: abKey,
                headerText: header,
                resultText: result,
                pitches: pitches,
                notePlay: notePlay
            )
        }

        let runsScored = plays.reduce(0) { $0 + max(0, $1.scoreValue ?? 0) }
        return HalfInningGroup(
            id: key,
            halfType: meta.type,
            inningNumber: meta.number,
            inningLabel: meta.label,
            atBats: atBats,
            runsScored: runsScored
        )
    }
}

// MARK: - Generic (non-MLB) Plays View

struct GenericPlaysView: View {
    let plays: [GameDetails.Play]
    let awayAbbr: String
    let homeAbbr: String

    @State private var expandedPeriods: Set<String> = []

    private var periods: [PeriodGroup] {
        var order: [String] = []
        var groups: [String: [GameDetails.Play]] = [:]
        for play in plays {
            let key = play.period?.displayValue ?? "Game"
            if groups[key] == nil { order.append(key) }
            groups[key, default: []].append(play)
        }
        return order.map { PeriodGroup(id: $0, label: $0, plays: groups[$0] ?? []) }
    }

    var body: some View {
        ScrollView {
            if periods.isEmpty {
                Text("Play-by-play not available")
                    .foregroundColor(.secondary)
                    .padding()
            } else {
                LazyVStack(spacing: 6) {
                    ForEach(periods) { period in
                        periodSection(period)
                    }
                }
                .padding()
            }
        }
    }

    @ViewBuilder
    private func periodSection(_ period: PeriodGroup) -> some View {
        let isOpen = expandedPeriods.contains(period.id)

        VStack(spacing: 0) {
            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    if isOpen { expandedPeriods.remove(period.id) }
                    else { expandedPeriods.insert(period.id) }
                }
            } label: {
                HStack {
                    Image(systemName: isOpen ? "chevron.down" : "chevron.right")
                        .foregroundColor(.secondary)
                        .frame(width: 16)
                    Text(period.label)
                        .font(.headline)
                    Spacer()
                    Text("\(period.plays.count) plays")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(12)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .accessibilityLabel("\(period.label), \(period.plays.count) plays")
            .accessibilityHint(isOpen ? "Double tap to collapse." : "Double tap to expand.")

            if isOpen {
                Divider().padding(.horizontal)
                ForEach(period.plays, id: \.id) { play in
                    genericPlayRow(play)
                    if play.id != period.plays.last?.id {
                        Divider().padding(.leading, 12)
                    }
                }
            }
        }
        .background(Color.secondary.opacity(0.07))
        .cornerRadius(10)
    }

    private func genericPlayRow(_ play: GameDetails.Play) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            HStack(spacing: 6) {
                if let clock = play.clock {
                    Text(clock.displayValue)
                        .font(.caption.bold())
                        .foregroundColor(.blue)
                }
                Spacer()
                if let away = play.awayScore, let home = play.homeScore {
                    Text("\(awayAbbr) \(away)–\(home) \(homeAbbr)")
                        .font(.caption.monospacedDigit())
                        .foregroundColor(.secondary)
                }
            }
            if let text = play.text, !text.isEmpty {
                Text(text)
                    .font(.body)
            } else {
                Text(play.type.text)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 7)
    }
}
