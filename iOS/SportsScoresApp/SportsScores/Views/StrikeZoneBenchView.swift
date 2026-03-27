//
//  StrikeZoneBenchView.swift
//  SportsScores
//
//  Educational strike zone touch explorer for The Bench tab.
//  No real pitch data — users freely drag the zone to learn its dimensions and
//  position relative to home plate, guided by spatial audio tones and haptics.
//
//  Audio model (matches stadium tour pattern):
//    • PitchAudioEngine tones — pitch rises as you move higher in the zone;
//      stereo pan tracks left–right position across the plate.
//    • Landmark chime (FieldAudioEngine) + haptic fire when entering the
//      home-plate region — the same mechanic used in the stadium tours.
//

import SwiftUI
import UIKit

// MARK: - Batter hand

private enum BatterHand: String, CaseIterable, Identifiable {
    case right = "R"
    case left  = "L"
    var id: String { rawValue }
    var label: String { self == .right ? "Right-Handed" : "Left-Handed" }
}

// MARK: - Info / landing view

struct StrikeZoneInfoView: View {
    @State private var showHandPicker  = false
    @State private var navigateToZone  = false
    @State private var selectedHand: BatterHand = .right

    var body: some View {
        List {
            Section {
                Text(
                    "The strike zone is the three-dimensional space above home plate " +
                    "through which a pitch must pass to be called a strike. Its " +
                    "boundaries are set relative to each individual batter's natural " +
                    "stance — so a taller batter's zone is taller."
                )
                .font(.body)
                .padding(.vertical, 4)
            } header: { Text("About the Strike Zone") }

            Section {
                dimensionRow(label: "Width",                    value: "17 inches — same as home plate")
                dimensionRow(label: "Bottom of zone",           value: "~18 in — top of the knees")
                dimensionRow(label: "Top of zone",              value: "~42 in — midpoint of shoulder tops and belt")
                dimensionRow(label: "Height (6-foot batter)",   value: "~24 inches")
            } header: { Text("Standard Dimensions") }

            Section {
                Text(
                    "Home plate is a five-sided rubber slab. The front edge facing " +
                    "the pitcher is 17 inches wide — exactly as wide as the strike " +
                    "zone. The sides are 8½ inches, then angle back to a point " +
                    "facing the catcher. The zone sits directly above it."
                )
                .font(.body)
                .padding(.vertical, 4)
            } header: { Text("Home Plate") }

            Section {
                Text(
                    "Audio tones rise in pitch as you move higher in the zone and " +
                    "pan left or right as you cross the plate. A chime fires when " +
                    "you reach home plate. Inside and outside labels swap depending " +
                    "on which side the batter stands."
                )
                .font(.body)
                .padding(.vertical, 4)
            } header: { Text("How to Explore") }
        }
        .navigationTitle("Strike Zone")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button { showHandPicker = true } label: {
                    Label("Touch the Zone", systemImage: "hand.tap.fill")
                }
                .accessibilityHint("Choose batter handedness then explore the strike zone with audio feedback")
            }
        }
        .confirmationDialog(
            "Choose Batter Stance",
            isPresented: $showHandPicker,
            titleVisibility: .visible
        ) {
            Button("Right-Handed Batter") { selectedHand = .right; navigateToZone = true }
            Button("Left-Handed Batter")  { selectedHand = .left;  navigateToZone = true }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Which side of the plate does the batter stand on?")
        }
        .navigationDestination(isPresented: $navigateToZone) {
            StrikeZoneTouchView(initialHand: selectedHand)
        }
    }

    private func dimensionRow(label: String, value: String) -> some View {
        HStack(alignment: .firstTextBaseline) {
            Text(label).font(.subheadline.bold())
            Spacer()
            Text(value)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.trailing)
        }
        .accessibilityElement(children: .combine)
    }
}

// MARK: - Touch canvas

struct StrikeZoneTouchView: View {

    // MARK: Init

    let initialHand: BatterHand

    init(initialHand: BatterHand) {
        self.initialHand = initialHand
        _currentHand = State(initialValue: initialHand)
    }

    // MARK: Audio

    @StateObject private var pitchAudio = PitchAudioEngine()
    @StateObject private var fieldAudio = FieldAudioEngine()

    // MARK: State

    @State private var currentHand: BatterHand
    @State private var fingerNorm: CGPoint? = nil   // 0–1 normalized canvas; nil = not touching
    @State private var inZone     = false
    @State private var nearPlate  = false
    @State private var lastIn     = false
    @State private var lastNear   = false
    @State private var lastAudioFire: Date = .distantPast

    // MARK: Layout constants (normalized: x=0 left, x=1 right, y=0 top, y=1 bottom)
    //
    // Sized for a 6-foot batter viewed from the catcher's perspective.
    // The zone is centred horizontally; home plate sits below it.
    //   zoneTop    ≈ 42" off the ground (high in zone, near top of canvas)
    //   zoneBottom ≈ 18" off the ground (low in zone, above the plate)
    //   plateCenterY — home plate pentagon centroid

    private let zoneLeft:      CGFloat = 0.28
    private let zoneRight:     CGFloat = 0.72
    private let zoneTop:       CGFloat = 0.18
    private let zoneBottom:    CGFloat = 0.60
    private let plateCenterY:  CGFloat = 0.80

    // MARK: Body

    var body: some View {
        VStack(spacing: 0) {
            // Batter hand toggle — user can switch without leaving the view
            Picker("Batter", selection: $currentHand) {
                ForEach(BatterHand.allCases) { h in Text(h.label).tag(h) }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(Color(uiColor: .systemBackground))

            // Interactive canvas
            GeometryReader { geo in
                let sz = geo.size
                Canvas { ctx, csz in
                    drawScene(&ctx, sz: csz)
                }
                .gesture(
                    DragGesture(minimumDistance: 0, coordinateSpace: .local)
                        .onChanged { v in
                            let n = CGPoint(
                                x: v.location.x / sz.width,
                                y: v.location.y / sz.height
                            )
                            fingerNorm = n
                            handleDrag(norm: n)
                        }
                        .onEnded { _ in handleDragEnd() }
                )
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(canvasA11yLabel)
                .accessibilityHint(
                    "Drag to explore. Pitch rises as you move higher. " +
                    "Left-right pan shows inside and outside of the plate. " +
                    "A chime plays when you reach home plate."
                )
                .accessibilityDirectTouch(options: .silentOnTouch)
            }
        }
        .navigationTitle("Strike Zone")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear  { fieldAudio.start() }
        .onDisappear {
            pitchAudio.stop()
            fieldAudio.stop()
        }
    }

    // MARK: - Interaction

    private func handleDrag(norm: CGPoint) {
        let nowIn   = isInZone(norm)
        let nowNear = isNearPlate(norm)

        if nowIn != lastIn {
            UIImpactFeedbackGenerator(style: .medium).impactOccurred()
            lastIn = nowIn
        }

        if nowNear && !lastNear {
            fieldAudio.playLandmark()
            UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
            TouchTourAnnouncementService.shared.announce("Home plate")
        }
        lastNear  = nowNear
        inZone    = nowIn
        nearPlate = nowNear

        let now = Date()
        if now.timeIntervalSince(lastAudioFire) > 0.30 {
            lastAudioFire = now
            let (ex, ey) = toESPN(norm)
            pitchAudio.playCoordinate(espnX: ex, espnY: ey)
        }
    }

    private func handleDragEnd() {
        pitchAudio.stop()
        if let fn = fingerNorm {
            TouchTourAnnouncementService.shared.announce(positionLabel(fn))
        }
        fingerNorm = nil
        inZone     = false
        nearPlate  = false
        lastIn     = false
        lastNear   = false
    }

    // MARK: - Geometry helpers

    private func isInZone(_ n: CGPoint) -> Bool {
        n.x >= zoneLeft && n.x <= zoneRight && n.y >= zoneTop && n.y <= zoneBottom
    }

    private func isNearPlate(_ n: CGPoint) -> Bool {
        abs(n.x - 0.5) < 0.25 && abs(n.y - plateCenterY) < 0.09
    }

    /// Canvas (0–1) → ESPN coordinate space (0–255).
    /// PitchAudioEngine inverts y internally so y=0 (canvas top) → highest note.
    private func toESPN(_ n: CGPoint) -> (Int, Int) {
        let ex = Int(max(0, min(n.x * 255, 255)))
        let ey = Int(max(0, min(n.y * 255, 255)))
        return (ex, ey)
    }

    // MARK: - Position label (announced on lift)

    private func positionLabel(_ n: CGPoint) -> String {
        if isNearPlate(n) { return "Home plate" }
        var parts: [String] = []

        // Vertical
        if n.y < zoneTop {
            parts.append("Above the zone")
        } else if n.y > zoneBottom {
            parts.append("Below the zone")
        } else {
            let frac = (n.y - zoneTop) / (zoneBottom - zoneTop)
            if frac < 0.34      { parts.append("High in the zone") }
            else if frac < 0.67 { parts.append("Middle of the zone") }
            else                { parts.append("Low in the zone") }
        }

        // Horizontal — inside/outside depend on batter side (catcher's view)
        let isRight = currentHand == .right
        if n.x < zoneLeft {
            parts.append(isRight ? "inside" : "outside")
        } else if n.x > zoneRight {
            parts.append(isRight ? "outside" : "inside")
        } else {
            let frac = (n.x - zoneLeft) / (zoneRight - zoneLeft)
            if frac < 0.34      { parts.append(isRight ? "inner third" : "outer third") }
            else if frac < 0.67 { parts.append("middle of the plate") }
            else                { parts.append(isRight ? "outer third" : "inner third") }
        }

        return parts.joined(separator: ", ")
    }

    private var canvasA11yLabel: String {
        let side = currentHand == .right ? "inside" : "outside"
        return
            "Strike zone for \(currentHand.label) batter. " +
            "Width 17 inches, height 24 inches. " +
            "Home plate is at the bottom center. " +
            "Drag to hear tones: pitch rises higher in the zone, " +
            "left pan is \(side) the plate."
    }

    // MARK: - Drawing

    private func drawScene(_ ctx: inout GraphicsContext, sz: CGSize) {
        // Dark background
        ctx.fill(Path(CGRect(origin: .zero, size: sz)), with: .color(.black.opacity(0.88)))
        drawHomePlate(&ctx, sz: sz)
        drawConnectors(&ctx, sz: sz)
        drawStrikeZone(&ctx, sz: sz)
        drawBatterIndicator(&ctx, sz: sz)
        if let fn = fingerNorm { drawCursor(&ctx, sz: sz, norm: fn) }
    }

    // Home plate — five-sided pentagon (front edge at top, point toward catcher)
    private func drawHomePlate(_ ctx: inout GraphicsContext, sz: CGSize) {
        let zoneW  = (zoneRight - zoneLeft) * sz.width   // plate width = zone width (both 17″)
        let plateH = zoneW * 0.56
        let cx     = sz.width / 2
        let cy     = plateCenterY * sz.height
        let l      = cx - zoneW / 2
        let r      = cx + zoneW / 2
        let top      = cy - plateH * 0.42
        let shoulder = cy + plateH * 0.14
        let tip      = cy + plateH * 0.58

        var p = Path()
        p.move(to: CGPoint(x: l,  y: top))
        p.addLine(to: CGPoint(x: r,  y: top))
        p.addLine(to: CGPoint(x: r,  y: shoulder))
        p.addLine(to: CGPoint(x: cx, y: tip))
        p.addLine(to: CGPoint(x: l,  y: shoulder))
        p.closeSubpath()

        ctx.fill(p,   with: .color(.white.opacity(nearPlate ? 0.95 : 0.80)))
        ctx.stroke(p, with: .color(.white), lineWidth: nearPlate ? 2.5 : 1.5)

        let fontSize = min(zoneW * 0.13, 10.5)
        ctx.draw(
            Text("HOME PLATE")
                .font(.system(size: fontSize, weight: .bold))
                .foregroundColor(.black.opacity(0.65)),
            at: CGPoint(x: cx, y: cy - plateH * 0.12),
            anchor: .center
        )
    }

    // Dashed guide lines connecting zone bottom-corners to plate top-corners
    private func drawConnectors(_ ctx: inout GraphicsContext, sz: CGSize) {
        let zoneW  = (zoneRight - zoneLeft) * sz.width
        let plateH = zoneW * 0.56
        let cx     = sz.width / 2
        let cy     = plateCenterY * sz.height
        let plateTopY = cy - plateH * 0.42
        let plateL    = cx - zoneW / 2
        let plateR    = cx + zoneW / 2

        var path = Path()
        path.move(to:    CGPoint(x: zoneLeft  * sz.width, y: zoneBottom * sz.height))
        path.addLine(to: CGPoint(x: plateL,               y: plateTopY))
        path.move(to:    CGPoint(x: zoneRight * sz.width, y: zoneBottom * sz.height))
        path.addLine(to: CGPoint(x: plateR,               y: plateTopY))
        ctx.stroke(path, with: .color(.white.opacity(0.25)), lineWidth: 1,
                   style: StrokeStyle(dash: [5, 4]))
    }

    // Strike zone rectangle with a 3×3 inner grid
    private func drawStrikeZone(_ ctx: inout GraphicsContext, sz: CGSize) {
        let zr = CGRect(
            x:      zoneLeft   * sz.width,
            y:      zoneTop    * sz.height,
            width:  (zoneRight  - zoneLeft)   * sz.width,
            height: (zoneBottom - zoneTop)    * sz.height
        )

        // Background tint — brightens when inside
        ctx.fill(Path(zr), with: .color(inZone ? .blue.opacity(0.18) : .white.opacity(0.06)))
        ctx.stroke(Path(zr), with: .color(.white.opacity(0.90)), lineWidth: 2)

        // 3×3 inner grid
        let cw = zr.width / 3
        let rh = zr.height / 3
        var grid = Path()
        for i in 1...2 {
            let x = zr.minX + cw * CGFloat(i)
            grid.move(to:    CGPoint(x: x, y: zr.minY))
            grid.addLine(to: CGPoint(x: x, y: zr.maxY))
            let y = zr.minY + rh * CGFloat(i)
            grid.move(to:    CGPoint(x: zr.minX, y: y))
            grid.addLine(to: CGPoint(x: zr.maxX, y: y))
        }
        ctx.stroke(grid, with: .color(.white.opacity(0.22)), lineWidth: 1)

        // Label above the zone
        ctx.draw(
            Text("STRIKE ZONE")
                .font(.system(size: 10, weight: .semibold))
                .foregroundColor(.white.opacity(0.55)),
            at: CGPoint(x: zr.midX, y: zr.minY - 13),
            anchor: .center
        )

        // Height dimension labels on left edge
        ctx.draw(
            Text("42\"").font(.system(size: 9)).foregroundColor(.white.opacity(0.50)),
            at: CGPoint(x: zr.minX - 5, y: zr.minY + 4), anchor: .trailing
        )
        ctx.draw(
            Text("18\"").font(.system(size: 9)).foregroundColor(.white.opacity(0.50)),
            at: CGPoint(x: zr.minX - 5, y: zr.maxY - 4), anchor: .trailing
        )

        // Inside / outside labels below the zone corners — swap by batter hand
        let isRight = currentHand == .right
        ctx.draw(
            Text(isRight ? "INSIDE" : "OUTSIDE")
                .font(.system(size: 9, weight: .medium))
                .foregroundColor(.white.opacity(0.45)),
            at: CGPoint(x: zr.minX + 4, y: zr.maxY + 14), anchor: .leading
        )
        ctx.draw(
            Text(isRight ? "OUTSIDE" : "INSIDE")
                .font(.system(size: 9, weight: .medium))
                .foregroundColor(.white.opacity(0.45)),
            at: CGPoint(x: zr.maxX - 4, y: zr.maxY + 14), anchor: .trailing
        )
    }

    // Simple stick-figure batter on the batting side of the plate
    private func drawBatterIndicator(_ ctx: inout GraphicsContext, sz: CGSize) {
        let isRight = currentHand == .right
        let plateEdgeX: CGFloat = isRight
            ? zoneLeft  * sz.width - 10
            : zoneRight * sz.width + 10
        let anchor: CGFloat = isRight ? -1 : 1   // -1 = draw leftward, +1 = rightward
        let color = Color.white.opacity(0.30)

        let headR: CGFloat  = 7
        let headY: CGFloat  = zoneTop * sz.height + 12 + headR
        let bodyBot: CGFloat = plateCenterY * sz.height - 6

        // Head
        ctx.stroke(
            Path(ellipseIn: CGRect(x: plateEdgeX - headR * (isRight ? 1 : 0),
                                   y: headY - headR,
                                   width: headR * 2, height: headR * 2)),
            with: .color(color), lineWidth: 1.5
        )

        // Body
        let bodyX = plateEdgeX + anchor * headR * 0
        var body  = Path()
        body.move(to:    CGPoint(x: bodyX, y: headY + headR + 2))
        body.addLine(to: CGPoint(x: bodyX, y: bodyBot))
        ctx.stroke(body, with: .color(color), lineWidth: 1.5)

        // Bat — angled toward the zone
        let batStartX = bodyX
        let batStartY = headY + headR + 2 + (bodyBot - headY - headR - 2) * 0.38
        let batTipX   = batStartX + anchor * -30   // toward plate
        var bat = Path()
        bat.move(to:    CGPoint(x: batStartX, y: batStartY))
        bat.addLine(to: CGPoint(x: batTipX,   y: batStartY - 10))
        ctx.stroke(bat, with: .color(color), lineWidth: 2)
    }

    // Crosshair cursor at the touch point
    private func drawCursor(_ ctx: inout GraphicsContext, sz: CGSize, norm: CGPoint) {
        let cx = norm.x * sz.width
        let cy = norm.y * sz.height
        let r: CGFloat = 14
        let color: Color = inZone ? .green : .orange

        var cross = Path()
        cross.move(to: CGPoint(x: cx - r, y: cy)); cross.addLine(to: CGPoint(x: cx + r, y: cy))
        cross.move(to: CGPoint(x: cx, y: cy - r)); cross.addLine(to: CGPoint(x: cx, y: cy + r))
        ctx.stroke(cross, with: .color(color.opacity(0.85)), lineWidth: 2)
        ctx.stroke(
            Path(ellipseIn: CGRect(x: cx - 8, y: cy - 8, width: 16, height: 16)),
            with: .color(color), lineWidth: 2
        )
    }
}
