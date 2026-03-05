//
//  BaseballFieldTourView.swift
//  SportsScores
//
//  A tactile / audio tour of a real MLB stadium drawn to scale.
//
//  Field coordinate system
//  ───────────────────────
//  Origin = home plate.  +x = toward right field, -x = toward left field.
//  +y = away from batter (toward the outfield). All distances in feet.
//
//  Layout (top → bottom)
//  ─────────────────────
//  1. Stadium picker
//  2. Field canvas — drag to explore; audio pitch maps distance, stereo maps x
//  3. Zone status bar — location description + distance from home
//  4. Notable features — expandable list of unique park characteristics
//

import SwiftUI
import UIKit

// MARK: - Field coordinate helper

private struct FieldLayout {
    let homeScreen: CGPoint  // screen position of home plate
    let scale: Double        // screen points per foot

    func screenPoint(fx: Double, fy: Double) -> CGPoint {
        CGPoint(x: homeScreen.x + fx * scale,
                y: homeScreen.y - fy * scale)
    }

    /// Returns (fieldX, fieldY) in feet.
    func fieldPoint(sx: Double, sy: Double) -> (Double, Double) {
        ((sx - homeScreen.x) / scale,
         (homeScreen.y - sy) / scale)
    }
}

// MARK: - Main View

struct BaseballFieldTourView: View {

    // Optional preselection from game venue lookup
    var preselectedStadium: StadiumGeometry?

    // MARK: - State

    @StateObject private var fieldAudio = FieldAudioEngine()

    @State private var selectedStadium: StadiumGeometry = StadiumGeometry.all.first!

    // Finger position in field feet
    @State private var fingerField: CGPoint? = nil

    // Last announced zone name (to detect zone-crossing haptics)
    @State private var lastZoneName: String = ""

    // Notable features expansion
    @State private var showFeatures = false

    // MARK: - Body

    var body: some View {
        VStack(spacing: 0) {
            stadiumPicker
            canvasSection
            statusBar
            featuresSection
        }
        .background(Color.black)
        .foregroundColor(.white)
        .onAppear {
            if let pre = preselectedStadium { selectedStadium = pre }
        }
    }

    // MARK: - Stadium picker

    private var stadiumPicker: some View {
        HStack {
            Label("Stadium", systemImage: "building.2.fill")
                .font(.caption)
                .foregroundColor(.gray)
            Spacer()
            Picker("Stadium", selection: $selectedStadium) {
                ForEach(StadiumGeometry.all, id: \.id) { stadium in
                    Text("\(stadium.parkName) (\(stadium.teamAbbreviation))")
                        .tag(stadium)
                }
            }
            .pickerStyle(.menu)
            .onChange(of: selectedStadium) { _ in
                fingerField = nil
                lastZoneName = ""
                fieldAudio.stop()
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color.gray.opacity(0.15))
    }

    // MARK: - Canvas

    private var canvasSection: some View {
        GeometryReader { geo in
            let layout = makeLayout(for: geo.size)
            Canvas { ctx, sz in
                drawField(ctx: ctx, size: sz, layout: layout)
            }
            .background(Color(red: 0.1, green: 0.15, blue: 0.1))
            .contentShape(Rectangle())
            .gesture(
                DragGesture(minimumDistance: 0, coordinateSpace: .local)
                    .onChanged { value in handleDrag(location: value.location, layout: layout) }
                    .onEnded { _ in handleDragEnd() }
            )
            // Gesture and accessibility must be on the same node for direct touch to work.
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(canvasAccessibilityLabel)
            .accessibilityHint("Direct touch area. Swipe to focus, then use the rotor to toggle Direct Touch on or off. Drag freely to explore. Audio pitch rises with distance from home plate; stereo pan follows left-right position.")
            .accessibilityAddTraits(.allowsDirectInteraction)
            .accessibilityDirectTouch(options: .silentOnTouch)
        }
        .frame(maxWidth: .infinity)
        .frame(height: 420)
        .clipped()
    }

    // MARK: - Layout computation

    private func makeLayout(for size: CGSize) -> FieldLayout {
        let st = selectedStadium
        let maxDepth = st.centerField + 20.0     // CF + padding
        let maxHalfWidth = st.rightFieldLine * sin(45 * Double.pi / 180) + 20.0

        let scaleH = (size.height - 42.0) / maxDepth   // reduced bottom margin: more field visible
        let scaleW = (size.width / 2.0 - 6.0) / maxHalfWidth  // tighter horizontal margin
        let scale = min(scaleH, scaleW)

        let homeX = size.width / 2.0
        let homeY = size.height - 18.0   // home plate closer to bottom edge
        return FieldLayout(homeScreen: CGPoint(x: homeX, y: homeY), scale: scale)
    }

    // MARK: - Field drawing

    private func drawField(ctx: GraphicsContext, size: CGSize, layout: FieldLayout) {
        let st = selectedStadium

        // wallArcPoints returns [(x: Double, y: Double)] in field-feet from home plate,
        // sampled from bearing −45° (LF line) to +45° (RF line) in 5° steps.
        let wallPoints = st.wallArcPoints  // [(x: Double, y: Double)]

        // The first and last arc points are at the foul poles.
        let leftWall  = wallPoints.first!   // (x<0, y>0) — left foul pole
        let rightWall = wallPoints.last!    // (x>0, y>0) — right foul pole
        let leftEdgeScreen  = layout.screenPoint(fx: leftWall.x,  fy: leftWall.y)
        let rightEdgeScreen = layout.screenPoint(fx: rightWall.x, fy: rightWall.y)

        // ── Fair territory (green) ──────────────────────────────────────────
        var fairPath = Path()
        fairPath.move(to: layout.homeScreen)
        fairPath.addLine(to: leftEdgeScreen)
        for pt in wallPoints { fairPath.addLine(to: layout.screenPoint(fx: pt.x, fy: pt.y)) }
        fairPath.addLine(to: rightEdgeScreen)
        fairPath.closeSubpath()
        ctx.fill(fairPath, with: .color(Color(red: 0.18, green: 0.38, blue: 0.18)))

        // ── Warning track (tan band, 15 ft inside wall) ───────────────────
        let warnTrack = 15.0   // feet
        var trackArcPath = Path()
        for (idx, pt) in wallPoints.enumerated() {
            let dist = hypot(pt.x, pt.y)
            guard dist > warnTrack else { continue }
            let ratio = (dist - warnTrack) / dist
            let inner = layout.screenPoint(fx: pt.x * ratio, fy: pt.y * ratio)
            if idx == 0 { trackArcPath.move(to: inner) } else { trackArcPath.addLine(to: inner) }
        }
        ctx.stroke(trackArcPath,
                   with: .color(Color(red: 0.72, green: 0.60, blue: 0.40).opacity(0.75)),
                   lineWidth: max(6, 15 * layout.scale))

        // ── Infield dirt circle ── (radius ≈ 95 ft)
        let dirtR = 95.0 * layout.scale
        let moundScreen = layout.screenPoint(fx: 0, fy: 0)
        ctx.fill(Path(ellipseIn: CGRect(
            x: moundScreen.x - dirtR,
            y: moundScreen.y - dirtR,
            width: dirtR * 2, height: dirtR * 2)),
            with: .color(Color(red: 0.68, green: 0.52, blue: 0.33).opacity(0.65)))

        // Infield grass (smaller green inset)
        let grassR = 66.0 * layout.scale
        ctx.fill(Path(ellipseIn: CGRect(
            x: moundScreen.x - grassR,
            y: moundScreen.y - grassR,
            width: grassR * 2, height: grassR * 2)),
            with: .color(Color(red: 0.16, green: 0.34, blue: 0.16)))

        // ── Pitcher's mound ── at 60.5 ft
        let moundPt = layout.screenPoint(fx: 0, fy: 60.5)
        let moundR = 9.0 * layout.scale
        ctx.fill(Path(ellipseIn: CGRect(
            x: moundPt.x - moundR, y: moundPt.y - moundR,
            width: moundR * 2, height: moundR * 2)),
            with: .color(Color(red: 0.72, green: 0.56, blue: 0.35)))

        // ── Foul lines ──────────────────────────────────────────────────
        let foulStyle = GraphicsContext.Shading.color(Color.white.opacity(0.8))
        ctx.stroke(Path { p in
            p.move(to: layout.homeScreen)
            p.addLine(to: leftEdgeScreen)
        }, with: foulStyle, lineWidth: 1.5)
        ctx.stroke(Path { p in
            p.move(to: layout.homeScreen)
            p.addLine(to: rightEdgeScreen)
        }, with: foulStyle, lineWidth: 1.5)

        // ── Wall arc ──────────────────────────────────────────────────────
        var wallArcPath = Path()
        for (idx, pt) in wallPoints.enumerated() {
            let sp = layout.screenPoint(fx: pt.x, fy: pt.y)
            if idx == 0 { wallArcPath.move(to: sp) } else { wallArcPath.addLine(to: sp) }
        }
        ctx.stroke(wallArcPath, with: .color(Color(red: 0.7, green: 0.55, blue: 0.25)), lineWidth: 3)

        // ── Bases ─────────────────────────────────────────────────────────
        drawBase(ctx: ctx, layout: layout, fx: 63.64, fy: 63.64, label: "1")   // 1B
        drawBase(ctx: ctx, layout: layout, fx: 0,     fy: 127.3, label: "2")   // 2B
        drawBase(ctx: ctx, layout: layout, fx: -63.64, fy: 63.64, label: "3")  // 3B

        // Home plate pentagon (simplified as square)
        let hpR = 6.0 * layout.scale
        ctx.fill(Path(CGRect(x: layout.homeScreen.x - hpR, y: layout.homeScreen.y - hpR,
                             width: hpR * 2, height: hpR * 2)),
                 with: .color(.white))

        // ── Distance markers (along center) ──────────────────────────────
        for dist in stride(from: 100.0, through: Double(st.centerField), by: 100.0) {
            let markerPt = layout.screenPoint(fx: 0, fy: dist)
            guard markerPt.y > 0 else { continue }
            ctx.draw(Text("\(Int(dist))'").font(.system(size: 9)).foregroundColor(Color.white.opacity(0.5)),
                     at: markerPt)
        }

        // Wall distance annotation at CF
        let cfPt = layout.screenPoint(fx: 0, fy: Double(st.centerField))
        if cfPt.y > 10 {
            ctx.draw(Text("CF \(Int(st.centerField))'").font(.system(size: 10, weight: .semibold)).foregroundColor(.yellow),
                     at: CGPoint(x: cfPt.x, y: cfPt.y - 14))
        }

        // ── Finger crosshair ──────────────────────────────────────────────
        if let ff = fingerField {
            let fScreen = layout.screenPoint(fx: ff.x, fy: ff.y)
            let lineColor = GraphicsContext.Shading.color(Color.white.opacity(0.85))
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fScreen.x - 18, y: fScreen.y))
                p.addLine(to: CGPoint(x: fScreen.x + 18, y: fScreen.y))
            }, with: lineColor, lineWidth: 1.5)
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fScreen.x, y: fScreen.y - 18))
                p.addLine(to: CGPoint(x: fScreen.x, y: fScreen.y + 18))
            }, with: lineColor, lineWidth: 1.5)
            ctx.fill(Path(ellipseIn: CGRect(x: fScreen.x - 4, y: fScreen.y - 4, width: 8, height: 8)),
                     with: .color(.white))
        }
    }

    private func drawBase(ctx: GraphicsContext, layout: FieldLayout,
                          fx: Double, fy: Double, label: String) {
        let pt = layout.screenPoint(fx: fx, fy: fy)
        let r = 5.0 * layout.scale
        ctx.fill(Path(CGRect(x: pt.x - r, y: pt.y - r, width: r * 2, height: r * 2)),
                 with: .color(.white))
        ctx.draw(Text(label).font(.system(size: 8, weight: .bold)).foregroundColor(.black),
                 at: pt)
    }

    // MARK: - Drag handling

    private func handleDrag(location: CGPoint, layout: FieldLayout) {
        let (fx, fy) = layout.fieldPoint(sx: location.x, sy: location.y)
        fingerField = CGPoint(x: fx, y: fy)

        let zone = selectedStadium.detectZone(fieldX: fx, fieldY: fy)

        // Haptic + chime on zone boundary crossing
        if zone.name != lastZoneName {
            lastZoneName = zone.name
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
            if zone.isLandmark {
                fieldAudio.playLandmark()
                UIAccessibility.post(notification: .announcement, argument: zone.name)
            }
        }

        // Continuous audio — no rate limit; FieldAudioEngine handles its own looping
        let maxHalfWidth = selectedStadium.rightFieldLine * sin(45 * Double.pi / 180) + 20.0
        let pan = Float((fx / maxHalfWidth).clamped(to: -1.0...1.0))
        fieldAudio.update(terrain: zone.terrain, pan: pan)
    }

    private func handleDragEnd() {
        // Announce location once when finger lifts
        if let ff = fingerField {
            let zone = selectedStadium.detectZone(fieldX: ff.x, fieldY: ff.y)
            UIAccessibility.post(notification: .announcement, argument: zone.name)
        }
        fingerField = nil
        fieldAudio.stop()
    }

    // MARK: - Status bar

    private var statusBar: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(selectedStadium.parkName)
                    .font(.caption.bold())
                    .foregroundColor(.yellow)
                Spacer()
                Text(selectedStadium.location)
                    .font(.caption2)
                    .foregroundColor(.gray)
            }

            if let ff = fingerField {
                let zone = selectedStadium.detectZone(fieldX: ff.x, fieldY: ff.y)
                Text(zone.name)
                    .font(.subheadline.bold())
                Text("\(zone.distanceFeet) feet from home plate")
                    .font(.caption)
                    .foregroundColor(.gray)
            } else {
                Text("Touch field to explore")
                    .font(.caption)
                    .foregroundColor(.gray)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color.gray.opacity(0.12))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(statusAccessibilityLabel)
    }

    // MARK: - Notable features

    private var featuresSection: some View {
        VStack(spacing: 0) {
            Button {
                withAnimation { showFeatures.toggle() }
            } label: {
                HStack {
                    Label("Notable features (\(selectedStadium.notableFeatures.count))",
                          systemImage: "star.fill")
                        .font(.caption.bold())
                    Spacer()
                    Image(systemName: showFeatures ? "chevron.up" : "chevron.down")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                .padding(.horizontal, 14)
                .padding(.vertical, 9)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .background(Color.gray.opacity(0.15))
            .accessibilityLabel("\(selectedStadium.notableFeatures.count) notable features. Tap to \(showFeatures ? "collapse" : "expand").")

            if showFeatures {
                ScrollView {
                    VStack(alignment: .leading, spacing: 6) {
                        ForEach(selectedStadium.notableFeatures, id: \.self) { feature in
                            HStack(alignment: .top, spacing: 8) {
                                Image(systemName: "diamond.fill")
                                    .font(.system(size: 7))
                                    .foregroundColor(.yellow)
                                    .padding(.top, 4)
                                Text(feature)
                                    .font(.caption)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                    .padding(.horizontal, 14)
                    .padding(.vertical, 8)
                }
                .frame(maxHeight: 160)
                .background(Color.gray.opacity(0.08))
            }
        }
    }

    // MARK: - Accessibility labels

    private var canvasAccessibilityLabel: String {
        "\(selectedStadium.parkName) field. Drag to explore. " +
        "Left field foul pole: \(Int(selectedStadium.leftFieldLine)) feet. " +
        "Center field: \(Int(selectedStadium.centerField)) feet. " +
        "Right field foul pole: \(Int(selectedStadium.rightFieldLine)) feet."
    }

    private var statusAccessibilityLabel: String {
        guard let ff = fingerField else {
            return "\(selectedStadium.parkName), \(selectedStadium.location). Touch field to explore."
        }
        let zone = selectedStadium.detectZone(fieldX: ff.x, fieldY: ff.y)
        return "\(zone.name). \(zone.distanceFeet) feet from home plate."
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        BaseballFieldTourView(
            preselectedStadium: StadiumGeometry.all.first(where: { $0.teamAbbreviation == "BOS" })
        )
        .navigationTitle("Field Tour")
        .navigationBarTitleDisplayMode(.inline)
    }
    .preferredColorScheme(.dark)
}
