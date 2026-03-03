//
//  FootballFieldTourView.swift
//  SportsScores
//
//  Audio tour of an NFL football field.
//
//  Field coordinate system (yards, origin = near end zone back line, left sideline)
//    fieldX : 0 → 53.333   (left sideline → right sideline)
//    fieldY : 0 → 120      (near end zone back → far end zone back)
//
//  Key constants
//    End zones    : fieldY 0–10 (near) and 110–120 (far)
//    Goal lines   : fieldY 10 and 110
//    Hash marks   : fieldX 23.583 (left) and 29.750 (right) — 70 ft 9 in from sideline
//    Goal posts   : same X as hash marks (NFL uprights align with hashes), fieldY 0 / 120
//

import SwiftUI
import UIKit

// MARK: - Layout helper

private struct FFLayout {
    let originScreen: CGPoint   // screen coords of (fieldX=0, fieldY=0)
    let scale: Double           // pt per yard

    func sp(_ fx: Double, _ fy: Double) -> CGPoint {
        CGPoint(x: originScreen.x + fx * scale,
                y: originScreen.y - fy * scale)
    }
    func fp(_ sx: CGFloat, _ sy: CGFloat) -> (Double, Double) {
        (Double(sx - originScreen.x) / scale,
         Double(originScreen.y - sy) / scale)
    }
}

// MARK: - Zone result

private struct FFZone {
    let name: String
    let terrain: FieldTerrain
    var isGoalLine: Bool = false
}

// MARK: - Main View

struct FootballFieldTourView: View {

    // Field dimensions
    private let fW = 53.333     // yards wide
    private let fL = 120.0      // yards long
    private let ezD = 10.0      // end zone depth (yards)
    private let hashL = 23.583  // left hash X (yards from left sideline)
    private let hashR = 29.750  // right hash X
    // Goal posts: same X as hashes (NFL aligned), at y=0 and y=120

    @StateObject private var fieldAudio = FieldAudioEngine()

    @State private var fingerField: CGPoint? = nil
    @State private var lastZoneName: String = ""
    @State private var lastYardBand: Int = -1   // Int(fieldY/5) — for chime triggering

    var body: some View {
        VStack(spacing: 0) {
            canvasSection
            statusBar
        }
        .background(Color.black)
        .foregroundColor(.white)
        .navigationTitle("Football Field")
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Canvas

    private var canvasSection: some View {
        GeometryReader { geo in
            let layout = makeLayout(geo.size)
            Canvas { ctx, sz in drawField(ctx: ctx, sz: sz, l: layout) }
                .background(Color(red: 0.04, green: 0.20, blue: 0.06))
                .contentShape(Rectangle())
                .gesture(
                    DragGesture(minimumDistance: 0, coordinateSpace: .local)
                        .onChanged { v in handleDrag(location: v.location, layout: layout) }
                        .onEnded { _ in handleDragEnd() }
                )
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("NFL football field. 120 yards long including 10-yard end zones. 53 yards wide. Drag to explore. Chime at every 5-yard line; louder at 10-yard lines. Hash marks 70 feet 9 inches from sideline — same width as goal posts.")
                .accessibilityHint("Drag freely or flick up and down with VoiceOver.")
                .accessibilityDirectTouch(options: .silentOnTouch)
        }
        .frame(maxWidth: .infinity)
        .frame(height: 500)
        .clipped()
    }

    // MARK: - Layout

    private func makeLayout(_ size: CGSize) -> FFLayout {
        let scaleW = (size.width - 16) / fW
        let scaleH = (size.height - 16) / fL
        let scale = min(scaleW, scaleH)
        let fieldW = fW * scale
        let fieldH = fL * scale
        let ox = (size.width - fieldW) / 2
        let oy = (size.height + fieldH) / 2
        return FFLayout(originScreen: CGPoint(x: ox, y: oy), scale: scale)
    }

    // MARK: - Drawing

    private func drawField(ctx: GraphicsContext, sz: CGSize, l: FFLayout) {
        let sc = l.scale

        // ── Outer border (out-of-bounds surface) ─────────────────────
        let borderW = fW * sc + 24
        let borderH = fL * sc + 24
        let borderRect = CGRect(x: l.sp(0,0).x - 12, y: l.sp(0, fL).y - 12,
                                width: borderW, height: borderH)
        ctx.fill(Path(borderRect), with: .color(Color(red: 0.35, green: 0.35, blue: 0.35)))

        // ── End zones ─────────────────────────────────────────────────
        let ezColor = Color(red: 0.12, green: 0.45, blue: 0.15)

        // Near end zone (bottom)
        ctx.fill(Path(CGRect(
            x: l.sp(0, 0).x, y: l.sp(0, ezD).y,
            width: fW * sc, height: ezD * sc)), with: .color(ezColor))
        // Far end zone (top)
        ctx.fill(Path(CGRect(
            x: l.sp(0, fL - ezD).x, y: l.sp(0, fL).y,
            width: fW * sc, height: ezD * sc)), with: .color(ezColor))

        // ── Playing field (darker green) ──────────────────────────────
        ctx.fill(Path(CGRect(
            x: l.sp(0, ezD).x, y: l.sp(0, fL - ezD).y,
            width: fW * sc, height: (fL - 2 * ezD) * sc)),
            with: .color(Color(red: 0.10, green: 0.36, blue: 0.12)))

        // ── Alternating 5-yard stripes (subtle) ───────────────────────
        for band in 0..<10 {
            if band % 2 == 0 { continue }
            let y0 = ezD + Double(band) * 10.0
            ctx.fill(Path(CGRect(
                x: l.sp(0, y0).x, y: l.sp(0, y0 + 10).y,
                width: fW * sc, height: 10 * sc)),
                with: .color(Color.white.opacity(0.025)))
        }

        // ── Yard lines ────────────────────────────────────────────────
        for yd in stride(from: 5, through: 115, by: 5) {
            let y = Double(yd)
            guard y > 0 && y < fL else { continue }
            let is10 = yd % 10 == 0
            let lineAlpha: Double = is10 ? 0.80 : 0.45
            let lineW: Double = is10 ? 1.5 : 0.8
            let p1 = l.sp(0, y); let p2 = l.sp(fW, y)
            ctx.stroke(Path { p in p.move(to: p1); p.addLine(to: p2) },
                       with: .color(Color.white.opacity(lineAlpha)), lineWidth: lineW)
        }

        // ── Goal lines ────────────────────────────────────────────────
        for gy in [10.0, 110.0] {
            ctx.stroke(Path { p in p.move(to: l.sp(0, gy)); p.addLine(to: l.sp(fW, gy)) },
                       with: .color(.white), lineWidth: 2)
        }

        // ── Hash marks — every yard ───────────────────────────────────
        let hashLen = max(4.0, sc * 0.6)   // physical: ~2 ft each side
        for yd in 11...109 {
            let y = Double(yd)
            let lx = l.sp(hashL, y)
            let rx = l.sp(hashR, y)
            for hx in [lx.x, rx.x] {
                ctx.stroke(Path { p in
                    p.move(to: CGPoint(x: hx - hashLen, y: lx.y))
                    p.addLine(to: CGPoint(x: hx + hashLen, y: lx.y))
                }, with: .color(Color.white.opacity(0.60)), lineWidth: 0.8)
            }
        }

        // ── Yard numbers ──────────────────────────────────────────────
        for yd in [20, 30, 40, 50, 60, 70, 80, 90] {
            let y = Double(yd)
            guard y > ezD && y < fL - ezD else { continue }
            // Label is distance from nearest goal line (10..50..10)
            let dist = yd <= 60 ? yd - 10 : 110 - yd
            let label = "\(dist)"
            let pt = l.sp(fW / 2, y)
            ctx.draw(Text(label).font(.system(size: 10, weight: .bold)).foregroundColor(.white.opacity(0.6)),
                     at: pt)
        }

        // ── Goal post indicators (at back of each end zone) ───────────
        for (gpY, label) in [(0.0, "G"), (fL, "G")] {
            for gpX in [hashL, hashR] {
                let pt = l.sp(gpX, gpY)
                let r = max(4.0, sc * 0.4)
                ctx.fill(Path(ellipseIn: CGRect(x: pt.x - r, y: pt.y - r, width: r*2, height: r*2)),
                         with: .color(.yellow))
                ctx.draw(Text(label).font(.system(size: 7, weight: .black)).foregroundColor(.black), at: pt)
            }
            // Crossbar
            let gl = l.sp(hashL, gpY); let gr = l.sp(hashR, gpY)
            ctx.stroke(Path { p in p.move(to: gl); p.addLine(to: gr) },
                       with: .color(.yellow.opacity(0.7)), lineWidth: 1.5)
        }

        // ── "END ZONE" text ───────────────────────────────────────────
        let ezMidNear = l.sp(fW / 2, ezD / 2)
        let ezMidFar  = l.sp(fW / 2, fL - ezD / 2)
        for pt in [ezMidNear, ezMidFar] {
            ctx.draw(Text("END ZONE").font(.system(size: 9, weight: .bold)).foregroundColor(.white.opacity(0.5)),
                     at: pt)
        }

        // ── Sideline labels ───────────────────────────────────────────
        let midY = l.sp(fW / 2, fL / 2)
        ctx.draw(Text("← 53⅓ yds →").font(.system(size: 8)).foregroundColor(.white.opacity(0.35)),
                 at: CGPoint(x: midY.x, y: l.sp(0, fL).y - 8))

        // ── Finger crosshair ──────────────────────────────────────────
        if let ff = fingerField {
            let fScreen = l.sp(ff.x, ff.y)
            let lc = GraphicsContext.Shading.color(Color.white.opacity(0.85))
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fScreen.x - 16, y: fScreen.y))
                p.addLine(to: CGPoint(x: fScreen.x + 16, y: fScreen.y))
            }, with: lc, lineWidth: 1.5)
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fScreen.x, y: fScreen.y - 16))
                p.addLine(to: CGPoint(x: fScreen.x, y: fScreen.y + 16))
            }, with: lc, lineWidth: 1.5)
            ctx.fill(Path(ellipseIn: CGRect(x: fScreen.x-3.5, y: fScreen.y-3.5, width:7, height:7)),
                     with: .color(.white))
        }
    }

    // MARK: - Zone detection

    private func detectZone(fx: Double, fy: Double) -> FFZone {
        if fx < 0 || fx > fW || fy < 0 || fy > fL {
            return FFZone(name: "Out of bounds", terrain: .foul)
        }

        // Goal post zones at back of end zones
        for (gpY, side) in [(0.0, "Near"), (fL, "Far")] {
            if abs(fy - gpY) < 2 {
                if abs(fx - hashL) < 2 { return FFZone(name: "\(side) goal post, left upright", terrain: .foul, isGoalLine: true) }
                if abs(fx - hashR) < 2 { return FFZone(name: "\(side) goal post, right upright", terrain: .foul, isGoalLine: true) }
            }
        }

        // Near end zone
        if fy < ezD {
            let ftDeep = Int(fy * 3)
            return FFZone(name: "Near end zone, \(ftDeep) feet from back line", terrain: .warningTrack,
                          isGoalLine: fy < 0.5)
        }
        // Far end zone
        if fy > fL - ezD {
            let ftDeep = Int((fL - fy) * 3)
            return FFZone(name: "Far end zone, \(ftDeep) feet from back line", terrain: .warningTrack,
                          isGoalLine: fy > fL - 0.5)
        }

        // Playing field — yard line
        let yd = fy - ezD      // 0..100 from near goal line
        let fromNear = Int(yd.rounded())
        let yardLine = min(fromNear, 100 - fromNear)
        let side = fromNear <= 50 ? "near" : "far"
        let yardLabel = yardLine == 50 ? "50 yard line" : "\(side.capitalized) \(yardLine) yard line"

        // Hash/side position
        let posLabel: String
        if abs(fx - hashL) < 1.5 {
            posLabel = "Left hash mark"
        } else if abs(fx - hashR) < 1.5 {
            posLabel = "Right hash mark"
        } else if fx < hashL {
            posLabel = "Left side, outside hashes"
        } else if fx > hashR {
            posLabel = "Right side, outside hashes"
        } else {
            posLabel = "Between the hashes"
        }

        let isGoalLine = yardLine == 0
        return FFZone(name: "\(yardLabel) · \(posLabel)", terrain: .fair, isGoalLine: isGoalLine)
    }

    // MARK: - Drag handling

    private func handleDrag(location: CGPoint, layout: FFLayout) {
        let (fx, fy) = layout.fp(location.x, location.y)
        fingerField = CGPoint(x: fx, y: fy)

        let zone = detectZone(fx: fx, fy: fy)

        // Zone-crossing: haptic + audio update
        if zone.name != lastZoneName {
            lastZoneName = zone.name
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
            if zone.isGoalLine { fieldAudio.playLandmark() }
        }

        // 5-yard chimes + live yard announcements — only on playing field
        if zone.terrain == .fair {
            let band = Int(fy / 5)
            if band != lastYardBand {
                lastYardBand = band
                let is10 = Int(fy / 10) * 10 == Int(fy.rounded() / 5) * 5
                if is10 {
                    fieldAudio.playLandmark()
                } else {
                    UIImpactFeedbackGenerator(style: .soft).impactOccurred()
                }
                // Announce yard number (playing field only: fieldY 10–110)
                let bandFY = Double(band) * 5.0
                if bandFY >= 10 && bandFY <= 110 {
                    let yardNum = min(Int(bandFY) - 10, 110 - Int(bandFY))
                    UIAccessibility.post(notification: .announcement, argument: "\(yardNum)")
                }
            }
        }

        let maxHW = fW / 2
        let pan = Float(((fx - fW / 2) / maxHW).clamped(to: -1...1))
        fieldAudio.update(terrain: zone.terrain, pan: pan)
    }

    private func handleDragEnd() {
        if let ff = fingerField {
            let zone = detectZone(fx: ff.x, fy: ff.y)
            UIAccessibility.post(notification: .announcement, argument: zone.name)
        }
        fingerField = nil
        fieldAudio.stop()
        lastYardBand = -1
    }

    // MARK: - Status bar

    private var statusBar: some View {
        VStack(alignment: .leading, spacing: 4) {
            if let ff = fingerField {
                let zone = detectZone(fx: ff.x, fy: ff.y)
                Text(zone.name)
                    .font(.subheadline.bold())
            } else {
                Text("Touch field to explore")
                    .font(.caption).foregroundColor(.gray)
            }
            Text("NFL · 120 yds × 53⅓ yds · Hash marks align with goal posts")
                .font(.caption2).foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color.gray.opacity(0.12))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel({
            if let ff = fingerField { return detectZone(fx: ff.x, fy: ff.y).name }
            return "Touch the field above to explore. Chime at every 5-yard line."
        }())
    }
}

#Preview {
    NavigationStack { FootballFieldTourView() }
}
