//
//  PitchZoneExplorerView.swift
//  SportsScores
//
//  Tactile / audio exploration of pitch locations for a single MLB game.
//
//  Layout (top → bottom)
//  ─────────────────────
//  1. Batter info bar — inning, result, hand badge
//  2. Zone canvas — full-width direct-touch area; drag to hear pitch locations
//  3. Status bar — current zone label + nearest pitch details
//  4. Explored pitches — expanding list of pitches "found" by touch
//  5. At-bat navigation — ◀ prev | "At-bat N of M" | next ▶
//
//  Accessibility
//  ─────────────
//  • Canvas is marked .accessibilityDirectTouch(options: .silentOnTouch) so VoiceOver
//    silences itself the moment the finger lands — audio plays without interruption.
//  • An accessible status element sits outside the canvas and receives VoiceOver focus;
//    it is updated after each navigation action and heard without disrupting exploration.
//  • .accessibilityAdjustableAction on the nav bar steps through at-bats without
//    requiring the user to find the ◀ ▶ buttons.
//

import SwiftUI
import UIKit

// MARK: - At-bat grouping

private struct ExplorerAtBat: Identifiable {
    let id: String          // atBatId
    let inning: String      // e.g. "Top 3rd"
    let batterName: String  // from at-bat header play text; "At-bat N" if unavailable
    let pitches: [GameDetails.Play]

    var result: String? { pitches.last?.text }
    var batterHand: String? { pitches.first?.bats?.abbreviation }
    var pitchCount: Int { pitches.count }
}

// MARK: - View

struct PitchZoneExplorerView: View {

    let plays: [GameDetails.Play]

    // MARK: - State

    @StateObject private var audio = PitchAudioEngine()

    @State private var currentAtBatIndex = 0
    @State private var showAllAtBats = false

    // Current finger position in ESPN coordinate space (0–255)
    @State private var fingerX: Double? = nil
    @State private var fingerY: Double? = nil

    // Pitch within ~threshold ESPN units of the finger
    @State private var nearestPitch: GameDetails.Play? = nil

    // Set of pitch IDs touched during this session
    @State private var exploredIds: Set<String> = []
    // Ordered list of first-touch for display
    @State private var exploredOrder: [GameDetails.Play] = []

    // Zone crossing state for haptic
    @State private var wasInStrikeZone = false

    // Rate-limit audio: only retrigger every 120 ms
    @State private var lastAudioFire: Date = .distantPast

    // Expand/collapse explored list
    @State private var showExplored = false

    // MARK: - Derived data

    private var pitchPlays: [GameDetails.Play] { plays.filter { $0.isPitch } }

    private var atBats: [ExplorerAtBat] {
        // Collect batter names from at-bat header plays (summaryType == "A")
        var batterNames: [String: String] = [:]
        for play in plays where play.summaryType == "A" {
            if let abId = play.atBatId, let name = play.text, !name.isEmpty {
                batterNames[abId] = name
            }
        }

        var groups: [String: [GameDetails.Play]] = [:]
        var order: [String] = []
        for play in pitchPlays {
            let key = play.atBatId ?? play.id
            if groups[key] == nil { order.append(key) }
            groups[key, default: []].append(play)
        }

        return order.enumerated().compactMap { (idx, key) in
            guard let pitches = groups[key], !pitches.isEmpty else { return nil }
            let inning = pitches.first?.period?.displayValue ?? ""
            let name = batterNames[key] ?? "At-bat \(idx + 1)"
            return ExplorerAtBat(id: key, inning: inning, batterName: name, pitches: pitches)
        }
    }

    private var currentAtBat: ExplorerAtBat? {
        guard !atBats.isEmpty, currentAtBatIndex < atBats.count else { return nil }
        return atBats[currentAtBatIndex]
    }

    /// Pitches visible on canvas (current at-bat, or all when showAllAtBats is true)
    private var visiblePitches: [GameDetails.Play] {
        if showAllAtBats { return pitchPlays }
        return currentAtBat?.pitches ?? []
    }

    // MARK: - Body

    var body: some View {
        VStack(spacing: 0) {
            if pitchPlays.isEmpty {
                noPitchDataMessage
            } else {
                batterInfoBar
                canvasSection
                statusBar
                exploredSection
                    .frame(maxHeight: showExplored ? 200 : 44)
                    .animation(.easeInOut(duration: 0.2), value: showExplored)
                atBatNavBar
            }
        }
        .background(Color.black)
        .foregroundColor(.white)
    }

    // MARK: - Batter info bar

    private var batterInfoBar: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 2) {
                if let ab = currentAtBat {
                    Text(showAllAtBats ? "All at-bats — \(pitchPlays.count) pitches" : ab.batterName)
                        .font(.subheadline.bold())
                        .lineLimit(1)
                    if !showAllAtBats {
                        Text(ab.inning)
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }
            }

            Spacer()

            // Show batter hand badge
            if let hand = currentAtBat?.batterHand, !showAllAtBats {
                Text(hand == "L" ? "Left-handed" : "Right-handed")
                    .font(.caption2)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.blue.opacity(0.3))
                    .cornerRadius(8)
            }

            // "Show all" toggle
            Button {
                showAllAtBats.toggle()
                if showAllAtBats { exploredIds.removeAll(); exploredOrder.removeAll() }
            } label: {
                Label(showAllAtBats ? "One at-bat" : "All at-bats",
                      systemImage: showAllAtBats ? "person.fill" : "person.3.fill")
                    .font(.caption)
            }
            .buttonStyle(.bordered)
            .tint(showAllAtBats ? .orange : .secondary)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .background(Color.gray.opacity(0.15))
    }

    // MARK: - Canvas section

    private var canvasSection: some View {
        GeometryReader { geo in
            Canvas { ctx, sz in
                drawCanvas(ctx: ctx, size: sz)
            }
            .background(Color(white: 0.08))
            .contentShape(Rectangle())
            .gesture(
                DragGesture(minimumDistance: 0, coordinateSpace: .local)
                    .onChanged { value in handleDrag(location: value.location, in: geo.size) }
                    .onEnded { _ in handleDragEnd() }
            )
            // Gesture and accessibility must be on the same node for direct touch to work.
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(canvasAccessibilityLabel)
            .accessibilityHint("Use the rotor to toggle Direct Touch on or off for this canvas. Two modes available: drag freely to explore pitch locations with spatial audio, or flick up and down to step through pitches one by one.")
            .accessibilityDirectTouch(options: .silentOnTouch)
            .accessibilityValue(currentPitchVoiceOverValue)
            .accessibilityAdjustableAction { direction in
                guard let ab = currentAtBat else { return }
                let pitches = ab.pitches
                guard !pitches.isEmpty else { return }
                let cur = pitches.firstIndex(where: { $0.id == nearestPitch?.id }) ?? -1
                let next: Int
                switch direction {
                case .increment: next = min(cur + 1, pitches.count - 1)
                case .decrement: next = max(cur - 1, 0)
                @unknown default: return
                }
                let pitch = pitches[next]
                nearestPitch = pitch
                audio.play(pitch)
                UIAccessibility.post(notification: .announcement,
                                     argument: buildPitchAnnouncement(pitch, number: next + 1, ab: ab))
            }
        }
        .frame(maxWidth: .infinity)
        .frame(height: 300)
        .clipped()
    }

    private func drawCanvas(ctx: GraphicsContext, size: CGSize) {
        let w = size.width
        let h = size.height

        // ── Strike zone sub-grid (3×3) ──────────────────────────────────
        // Raw ESPN zone: x 90–165, y 80–175
        // On-screen: screenX = espnX/255*w, screenY = espnY/255*h (y NOT inverted here —
        // raw y 80 = top of zone appears near top of canvas; raw y 175 = bottom of zone)
        let zx1 = 90.0 / 255.0 * w
        let zx2 = 165.0 / 255.0 * w
        let zy1 = 80.0 / 255.0 * h    // top of zone (screen top)
        let zy2 = 175.0 / 255.0 * h   // bottom of zone (screen bottom)
        let zw = zx2 - zx1
        let zh = zy2 - zy1

        // Sub-grid lines (lighter)
        let subGridStyle = GraphicsContext.Shading.color(Color.gray.opacity(0.25))
        for col in 1...2 {
            let x = zx1 + (Double(col) / 3.0) * zw
            ctx.stroke(Path { p in p.move(to: CGPoint(x: x, y: zy1)); p.addLine(to: CGPoint(x: x, y: zy2)) },
                       with: subGridStyle, lineWidth: 1)
        }
        for row in 1...2 {
            let y = zy1 + (Double(row) / 3.0) * zh
            ctx.stroke(Path { p in p.move(to: CGPoint(x: zx1, y: y)); p.addLine(to: CGPoint(x: zx2, y: y)) },
                       with: subGridStyle, lineWidth: 1)
        }

        // Tinted zone fill
        let inZone = isInZone(espnX: fingerX ?? -1, espnY: fingerY ?? -1)
        let zoneFill = inZone ? Color.green.opacity(0.12) : Color.white.opacity(0.04)
        ctx.fill(Path(CGRect(x: zx1, y: zy1, width: zw, height: zh)), with: .color(zoneFill))

        // Zone border
        ctx.stroke(Path(CGRect(x: zx1, y: zy1, width: zw, height: zh)),
                   with: .color(Color.white.opacity(0.7)), lineWidth: 1.8)

        // "Ball" label outside left edge
        ctx.draw(Text("BALL").font(.system(size: 9, weight: .semibold)).foregroundColor(.gray),
                 at: CGPoint(x: zx1 * 0.45, y: h * 0.5))

        // ── Pitch dots ──────────────────────────────────────────────────
        for pitch in visiblePitches {
            guard let coord = pitch.pitchCoordinate else { continue }
            let px = Double(coord.x) / 255.0 * w
            let py = Double(coord.y) / 255.0 * h
            let isNearest = pitch.id == nearestPitch?.id
            let isExplored = exploredIds.contains(pitch.id)
            let radius: Double = isNearest ? 11 : (isExplored ? 7 : 5.5)
            let color = pitchColor(pitch)

            if isNearest {
                // Glow ring
                ctx.stroke(Path(ellipseIn: CGRect(x: px - 14, y: py - 14, width: 28, height: 28)),
                           with: .color(color.opacity(0.5)), lineWidth: 2)
            }
            ctx.fill(Path(ellipseIn: CGRect(x: px - radius, y: py - radius, width: radius * 2, height: radius * 2)),
                     with: .color(isExplored ? color : color.opacity(0.5)))

            // Result label on explored pitches
            if isExplored, let num = visiblePitches.firstIndex(where: { $0.id == pitch.id }) {
                ctx.draw(Text("\(num + 1)").font(.system(size: 8, weight: .bold)).foregroundColor(.black),
                         at: CGPoint(x: px, y: py))
            }
        }

        // ── Finger crosshair ────────────────────────────────────────────
        if let ex = fingerX, let ey = fingerY {
            let fx = ex / 255.0 * w
            let fy = ey / 255.0 * h
            let lineColor = GraphicsContext.Shading.color(Color.white.opacity(0.75))
            ctx.stroke(Path { p in p.move(to: CGPoint(x: fx - 16, y: fy)); p.addLine(to: CGPoint(x: fx + 16, y: fy)) },
                       with: lineColor, lineWidth: 1.5)
            ctx.stroke(Path { p in p.move(to: CGPoint(x: fx, y: fy - 16)); p.addLine(to: CGPoint(x: fx, y: fy + 16)) },
                       with: lineColor, lineWidth: 1.5)
            ctx.fill(Path(ellipseIn: CGRect(x: fx - 3.5, y: fy - 3.5, width: 7, height: 7)),
                     with: .color(Color.white))
        }
    }

    // MARK: - Drag handling

    private func handleDrag(location: CGPoint, in size: CGSize) {
        let ex = (location.x / size.width * 255.0).clamped(to: 0...255)
        let ey = (location.y / size.height * 255.0).clamped(to: 0...255)
        fingerX = ex
        fingerY = ey

        // Nearest pitch within threshold — track explored set, one haptic per new discovery
        let threshold = 28.0
        var bestDist = Double.infinity
        var best: GameDetails.Play? = nil
        for pitch in visiblePitches {
            guard let c = pitch.pitchCoordinate else { continue }
            let d = hypot(Double(c.x) - ex, Double(c.y) - ey)
            if d < bestDist { bestDist = d; best = pitch }
        }
        let newNearest = bestDist < threshold ? best : nil
        if newNearest?.id != nearestPitch?.id {
            nearestPitch = newNearest
            if let p = newNearest, !exploredIds.contains(p.id) {
                exploredIds.insert(p.id)
                if !exploredOrder.contains(where: { $0.id == p.id }) {
                    exploredOrder.append(p)
                }
                // Single subtle haptic when landing on a new pitch — no announcement
                UIImpactFeedbackGenerator(style: .light).impactOccurred()
            }
        }

        // Strike zone boundary: haptic only, no VoiceOver announcement during drag
        let nowInZone = isInZone(espnX: ex, espnY: ey)
        if nowInZone != wasInStrikeZone {
            wasInStrikeZone = nowInZone
            UIImpactFeedbackGenerator(style: .medium).impactOccurred()
            // No UIAccessibility.post here — announcements mid-drag override audio
        }

        // Rate-limited audio — slow enough that tones don't overlap (tone is 0.35 s)
        let now = Date()
        if now.timeIntervalSince(lastAudioFire) > 0.45 {
            lastAudioFire = now
            audio.playCoordinate(espnX: Int(ex), espnY: Int(ey))
        }
    }

    private func handleDragEnd() {
        // Single announcement when finger lifts summarising where they are
        let zoneText = zoneLocationText
        let pitchText: String
        if let p = nearestPitch, let ab = currentAtBat {
            let num = (visiblePitches.firstIndex(where: { $0.id == p.id }) ?? 0) + 1
            pitchText = "Pitch \(num): " + buildPitchAnnouncement(p, number: num, ab: ab)
        } else {
            pitchText = zoneText
        }
        UIAccessibility.post(notification: .announcement, argument: pitchText)
        fingerX = nil
        fingerY = nil
        nearestPitch = nil
    }

    // MARK: - Status bar

    private var statusBar: some View {
        VStack(spacing: 4) {
            // Zone location
            Text(zoneLocationText)
                .font(.subheadline.bold())
                .frame(maxWidth: .infinity, alignment: .leading)

            // Nearest pitch details
            if let p = nearestPitch {
                let num = (visiblePitches.firstIndex(where: { $0.id == p.id }) ?? 0) + 1
                HStack(spacing: 8) {
                    Text("Pitch \(num)")
                        .font(.caption.monospacedDigit())
                        .foregroundColor(.gray)
                    Text(p.pitchType?.text ?? p.type.text)
                        .font(.caption.bold())
                    if let v = p.pitchVelocity { Text("\(v) mph").font(.caption).foregroundColor(.gray) }
                    Spacer()
                    Text(p.type.text)
                        .font(.caption)
                        .padding(.horizontal, 6).padding(.vertical, 2)
                        .background(pitchColor(p).opacity(0.3))
                        .cornerRadius(4)
                }
            } else if fingerX == nil {
                Text("Touch the canvas to explore")
                    .font(.caption)
                    .foregroundColor(.gray)
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color.gray.opacity(0.12))
    }

    // MARK: - Explored pitches section

    private var exploredSection: some View {
        VStack(spacing: 0) {
            // Header toggle
            Button {
                withAnimation { showExplored.toggle() }
            } label: {
                HStack {
                    Label("Explored: \(exploredOrder.count) pitch\(exploredOrder.count == 1 ? "" : "es")",
                          systemImage: "hand.tap.fill")
                        .font(.caption.bold())
                    Spacer()
                    Image(systemName: showExplored ? "chevron.up" : "chevron.down")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                .padding(.horizontal, 14)
                .padding(.vertical, 9)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .background(Color.gray.opacity(0.15))
            .accessibilityLabel("Explored pitches: \(exploredOrder.count). Tap to \(showExplored ? "collapse" : "expand").")

            if showExplored {
                ScrollView {
                    VStack(alignment: .leading, spacing: 2) {
                        ForEach(Array(exploredOrder.enumerated()), id: \.element.id) { idx, pitch in
                            exploredRow(pitch, index: idx)
                        }
                    }
                    .padding(.vertical, 4)
                }
                .background(Color.gray.opacity(0.08))
            }
        }
    }

    private func exploredRow(_ pitch: GameDetails.Play, index: Int) -> some View {
        let hand = currentAtBat?.batterHand
        let loc = pitch.locationDescription(batterHand: hand)
        return Button {
            audio.play(pitch)
        } label: {
            HStack(spacing: 10) {
                Text("\(index + 1)")
                    .font(.caption2.monospacedDigit())
                    .foregroundColor(.gray)
                    .frame(width: 18, alignment: .trailing)

                Text(pitch.pitchResultLabel)
                    .font(.system(size: 11, weight: .bold))
                    .foregroundColor(.black)
                    .frame(width: 20, height: 20)
                    .background(pitchColor(pitch))
                    .cornerRadius(3)

                Text(pitch.pitchType?.text ?? pitch.type.text)
                    .font(.caption.bold())
                    .lineLimit(1)

                if let v = pitch.pitchVelocity {
                    Text("\(v) mph")
                        .font(.caption2)
                        .foregroundColor(.gray)
                }

                Text(loc)
                    .font(.caption2)
                    .foregroundColor(.gray)
                    .lineLimit(1)

                Spacer()

                Text(pitch.type.text)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 5)
        }
        .buttonStyle(.plain)
        .accessibilityLabel(buildPitchAnnouncement(
            pitch,
            number: index + 1,
            ab: currentAtBat
        ))
    }

    // MARK: - At-bat navigation bar

    private var atBatNavBar: some View {
        HStack(spacing: 0) {
            Button {
                navigateAtBat(by: -1)
            } label: {
                Image(systemName: "chevron.left")
                    .font(.body.bold())
                    .frame(width: 48, height: 44)
                    .contentShape(Rectangle())
            }
            .disabled(currentAtBatIndex <= 0 || showAllAtBats)
            .accessibilityLabel("Previous at-bat")

            Spacer()

            VStack(spacing: 1) {
                Text("At-bat \(currentAtBatIndex + 1) of \(atBats.count)")
                    .font(.subheadline.bold())
                if let ab = currentAtBat {
                    Text("\(ab.pitchCount) pitch\(ab.pitchCount == 1 ? "" : "es")")
                        .font(.caption2)
                        .foregroundColor(.gray)
                }
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel(atBatNavAccessibilityLabel)
            .accessibilityHint("Swipe up or down to move between at-bats")
            .accessibilityAddTraits(.isButton)
            .accessibilityAdjustableAction { direction in
                switch direction {
                case .increment: navigateAtBat(by: 1)
                case .decrement: navigateAtBat(by: -1)
                @unknown default: break
                }
            }

            Spacer()

            Button {
                navigateAtBat(by: 1)
            } label: {
                Image(systemName: "chevron.right")
                    .font(.body.bold())
                    .frame(width: 48, height: 44)
                    .contentShape(Rectangle())
            }
            .disabled(currentAtBatIndex >= atBats.count - 1 || showAllAtBats)
            .accessibilityLabel("Next at-bat")
        }
        .padding(.horizontal, 8)
        .background(Color.gray.opacity(0.15))
        .frame(height: 52)
    }

    // MARK: - Empty state

    private var noPitchDataMessage: some View {
        VStack(spacing: 16) {
            Image(systemName: "baseball")
                .font(.system(size: 48))
                .foregroundColor(.gray)
            Text("Pitch coordinate data not available for this game.")
                .multilineTextAlignment(.center)
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding()
    }

    // MARK: - Navigation helper

    private func navigateAtBat(by delta: Int) {
        withAnimation(.none) {
            currentAtBatIndex = (currentAtBatIndex + delta)
                .clamped(to: 0..<atBats.count)
        }
        exploredIds.removeAll()
        exploredOrder.removeAll()
        nearestPitch = nil
        fingerX = nil
        fingerY = nil
        UINotificationFeedbackGenerator().notificationOccurred(.success)
        let ab = currentAtBat
        let label = ab.map { "\($0.inning), \($0.batterName), \($0.pitchCount) pitches" } ?? ""
        UIAccessibility.post(notification: .announcement, argument: label)
    }

    // MARK: - Helpers

    private func isInZone(espnX: Double, espnY: Double) -> Bool {
        espnX >= 90 && espnX <= 165 && espnY >= 80 && espnY <= 175
    }

    private func pitchColor(_ pitch: GameDetails.Play) -> Color {
        switch pitch.pitchResultColorName {
        case "blue":    return .blue
        case "red":     return .red
        case "orange":  return .orange
        case "gray":    return .gray
        case "green":   return Color(red: 0.2, green: 0.8, blue: 0.2)
        default:        return Color.secondary
        }
    }

    private var zoneLocationText: String {
        guard let ex = fingerX, let ey = fingerY else {
            return fingerX == nil ? "Lift finger — paused" : "..."
        }
        let hand = currentAtBat?.batterHand
        let isLeft = hand == "L"
        let xNorm = ex / 255.0

        let horizontal: String
        if isLeft {
            horizontal = xNorm < 0.22 ? "Way outside" : xNorm < 0.42 ? "Outside" :
                         xNorm < 0.58 ? "Over the plate" : xNorm < 0.78 ? "Inside" : "Way inside"
        } else {
            horizontal = xNorm < 0.22 ? "Way inside" : xNorm < 0.42 ? "Inside" :
                         xNorm < 0.58 ? "Over the plate" : xNorm < 0.78 ? "Outside" : "Way outside"
        }

        let yNorm = ey / 255.0
        let vertical = yNorm < 0.33 ? "High" : yNorm < 0.67 ? "Middle height" : "Low"
        let inZone = isInZone(espnX: ex, espnY: ey)
        return "\(vertical) — \(horizontal) — \(inZone ? "Strike zone" : "Ball")"
    }

    private var canvasAccessibilityLabel: String {
        if let ab = currentAtBat {
            return "Strike zone canvas. \(ab.pitches.count) pitches from \(ab.batterName), \(ab.inning). " +
                   "Drag to explore pitch locations and hear audio."
        }
        return "Strike zone canvas. Drag to explore pitch locations."
    }

    private var atBatNavAccessibilityLabel: String {
        guard let ab = currentAtBat else { return "At-bat \(currentAtBatIndex + 1)" }
        return "At-bat \(currentAtBatIndex + 1) of \(atBats.count). " +
               "\(ab.inning). \(ab.batterName). \(ab.pitchCount) pitches."
    }

    /// Short accessible value: shows which pitch is selected while navigating via swipe.
    private var currentPitchVoiceOverValue: String {
        guard let ab = currentAtBat, !ab.pitches.isEmpty else { return "" }
        let pitches = ab.pitches
        if let p = nearestPitch, let idx = pitches.firstIndex(where: { $0.id == p.id }) {
            let type = p.pitchType?.text ?? "Pitch"
            return "Pitch \(idx + 1) of \(pitches.count): \(type)"
        }
        return "\(pitches.count) pitches. Swipe up or down to step through them."
    }

    private func buildPitchAnnouncement(_ pitch: GameDetails.Play,
                                        number: Int,
                                        ab: ExplorerAtBat?) -> String {
        var parts = ["Pitch \(number)"]
        if let t = pitch.pitchType?.text { parts.append(t) }
        if let v = pitch.pitchVelocity { parts.append("\(v) miles per hour") }
        parts.append(pitch.locationDescription(batterHand: ab?.batterHand))
        parts.append(pitch.type.text)
        if let c = pitch.resultCount { parts.append("Count: \(c.balls) and \(c.strikes)") }
        return parts.joined(separator: ". ")
    }
}

// MARK: - Preview

#Preview {
    let coord1 = GameDetails.Play.PitchCoordinate(x: 127, y: 100)
    let coord2 = GameDetails.Play.PitchCoordinate(x: 90, y: 160)
    let coord3 = GameDetails.Play.PitchCoordinate(x: 170, y: 80)
    let ptype  = GameDetails.Play.PitchTypeInfo(text: "Four-seam FB", abbreviation: "FF")
    let hand   = GameDetails.Play.BatterHand(abbreviation: "R")
    let count1 = GameDetails.Play.PitchCount(balls: 0, strikes: 0)
    let count2 = GameDetails.Play.PitchCount(balls: 1, strikes: 1)
    let count3 = GameDetails.Play.PitchCount(balls: 1, strikes: 2)
    let period = GameDetails.Play.Period(displayValue: "Top 3rd", type: "Top", number: 3)

    func makePlay(_ id: String, coord: GameDetails.Play.PitchCoordinate,
                  typeText: String, typeSlug: String, count: GameDetails.Play.PitchCount) -> GameDetails.Play {
        GameDetails.Play(id: id, text: typeText,
                         type: GameDetails.Play.PlayType(text: typeText, type: typeSlug),
                         scoreValue: 0, period: period,
                         pitchCoordinate: coord, pitchType: ptype, pitchVelocity: 95,
                         bats: hand, atBatId: "ab1", atBatPitchNumber: 1, resultCount: count, outs: 1)
    }

    let pitches = [
        makePlay("p1", coord: coord1, typeText: "Called Strike", typeSlug: "called-strike", count: count1),
        makePlay("p2", coord: coord2, typeText: "Ball", typeSlug: "ball", count: count1),
        makePlay("p3", coord: coord3, typeText: "Swinging Strike", typeSlug: "swinging-strike", count: count2),
    ]

    return NavigationStack {
        PitchZoneExplorerView(plays: pitches)
            .navigationTitle("Zone Explorer")
            .navigationBarTitleDisplayMode(.inline)
    }
    .preferredColorScheme(.dark)
}
