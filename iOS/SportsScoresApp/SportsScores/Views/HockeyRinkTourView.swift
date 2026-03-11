//
//  HockeyRinkTourView.swift
//  SportsScores
//
//  Audio tour of a standard NHL ice hockey rink.
//
//  Field coordinate system (feet, origin = center ice)
//    fieldX : -42.5 → +42.5   (left boards → right boards)
//    fieldY : -100  → +100    (near end board → far end board)
//
//  Key landmarks (all in feet from center)
//    Blue lines          : fieldY = ±25
//    Red center line     : fieldY = 0
//    Goal lines          : fieldY = ±89  (11 ft from end boards)
//    Near/far creases    : 6-ft radius semicircles at goal mouth (0, ±89)
//    Face-off circles    : 15-ft radius; near/far dots at (±22, ±69)
//    Center face-off     : 15-ft radius at (0,0)
//

import SwiftUI
import UIKit

private struct HRLayout {
    let origin: CGPoint   // screen pt for (fieldX=-42.5, fieldY=-100)
    let scale: Double     // pt per foot
    func sp(_ fx: Double, _ fy: Double) -> CGPoint {
        CGPoint(x: origin.x + (fx + 42.5) * scale,
                y: origin.y + (100 - fy) * scale)   // screen y inverted: near=bottom
    }
    func fp(_ sx: CGFloat, _ sy: CGFloat) -> (Double, Double) {
        (Double(sx - origin.x) / scale - 42.5,
         100.0 - Double(sy - origin.y) / scale)
    }
}

private struct HRZone {
    let name: String
    let terrain: FieldTerrain
    var isLineCrossing: Bool = false
}

struct HockeyRinkTourView: View {

    private let rinkW = 85.0     // ft, total width
    private let rinkL = 200.0   // ft, total length
    private let halfW = 42.5
    private let halfL = 100.0
    private let blueLineY = 25.0   // ft from center
    private let goalLineY = 89.0   // ft from center (11 ft from boards)
    private let creaseR  = 6.0
    private let circleR  = 15.0
    private let dotLat   = 22.0   // lateral position of end-zone face-off dots
    private let dotY     = 69.0   // longitudinal position (20 ft from goal line)

    @StateObject private var fieldAudio = FieldAudioEngine()

    @State private var fingerField: CGPoint? = nil  // (x ft, y ft from center)
    @State private var lastZoneName: String = ""
    @State private var lastLineAnnouncement: String = ""

    var body: some View {
        VStack(spacing: 0) {
            canvasSection
            statusBar
        }
        .background(Color.black)
        .foregroundColor(.white)
        .navigationTitle("Hockey Rink")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear  { fieldAudio.start() }
        .onDisappear { fieldAudio.stop() }
    }

    // MARK: - Canvas

    private var canvasSection: some View {
        GeometryReader { geo in
            let layout = makeLayout(geo.size)
            Canvas { ctx, sz in drawRink(ctx: ctx, sz: sz, l: layout) }
                .background(Color(red: 0.85, green: 0.90, blue: 0.95))   // ice tint
                .contentShape(Rectangle())
                .gesture(
                    DragGesture(minimumDistance: 0, coordinateSpace: .local)
                        .onChanged { v in handleDrag(location: v.location, layout: layout) }
                        .onEnded { _ in handleDragEnd() }
                )
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("NHL hockey rink, 200 feet long by 85 feet wide. Blue lines 25 feet from center on each side. Goal lines 89 feet from center. Drag to explore — audio terrain softens in creases and roughens at the boards.")
                .accessibilityHint("Use the rotor to toggle Direct Touch on or off for this rink area. Drag to explore. Chime at blue lines and goal lines.")
                .accessibilityDirectTouch(options: .silentOnTouch)
        }
        .frame(maxWidth: .infinity)
        .frame(height: 480)
        .clipped()
    }

    // MARK: - Layout

    private func makeLayout(_ size: CGSize) -> HRLayout {
        let scaleW = (size.width - 12) / rinkW
        let scaleH = (size.height - 12) / rinkL
        let scale = min(scaleW, scaleH)
        let rW = rinkW * scale
        let rH = rinkL * scale
        let ox = (size.width - rW) / 2
        let oy = (size.height - rH) / 2
        return HRLayout(origin: CGPoint(x: ox, y: oy), scale: scale)
    }

    // MARK: - Drawing

    private func drawRink(ctx: GraphicsContext, sz: CGSize, l: HRLayout) {
        let sc = l.scale
        let cornerR = min(28.0 * sc, 30.0)   // rounded corners ≈ 28 ft radius

        // ── Ice surface ──────────────────────────────────────────────
        var rinkPath = Path()
        rinkPath.addRoundedRect(in: CGRect(x: l.sp(-halfW, halfL).x,
                                           y: l.sp(-halfW, halfL).y,
                                           width: rinkW * sc,
                                           height: rinkL * sc),
                                cornerSize: CGSize(width: cornerR, height: cornerR))
        ctx.fill(rinkPath, with: .color(Color(red: 0.92, green: 0.96, blue: 1.00)))
        ctx.stroke(rinkPath, with: .color(.red), lineWidth: 2)   // boards

        // ── Center ice ────────────────────────────────────────────────
        // Red center line
        lineH(ctx, l, y: 0.0, color: .red, width: 2)

        // Center face-off circle (15 ft radius)
        circle(ctx, l, cx: 0, cy: 0, r: circleR, color: .blue, lineW: 1.5)
        dot(ctx, l, cx: 0, cy: 0, r: 1.5, color: .blue)

        // ── Blue lines ────────────────────────────────────────────────
        for side in [-1.0, 1.0] {
            lineH(ctx, l, y: side * blueLineY, color: .blue, width: 2.5)
        }

        // ── Neutral zone face-off dots ─────────────────────────────────
        for sx in [-dotLat, dotLat] {
            for sy in [-22.0, 22.0] {
                dot(ctx, l, cx: sx, cy: sy, r: 1.5, color: .red)
            }
        }

        // ── End zones ─────────────────────────────────────────────────
        for eSign in [-1.0, 1.0] {
            // Goal line
            lineH(ctx, l, y: eSign * goalLineY, color: .red, width: 1.5)

            // Face-off circles
            for sx in [-dotLat, dotLat] {
                circle(ctx, l, cx: sx, cy: eSign * dotY, r: circleR, color: .red, lineW: 1.5)
                dot(ctx, l, cx: sx, cy: eSign * dotY, r: 1.5, color: .red)
            }

            // Goal crease (6-ft semicircle in front of goal, toward center)
            let gCenterY = eSign * goalLineY
            let gCenterPt = l.sp(0, gCenterY)
            let cr = creaseR * sc
            // Crease is toward center — if eSign=1 (far goal), crease toward y<89; if eSign=-1 (near), toward y>-89
            let crAngleStart: Double = eSign > 0 ? 180 : 0
            var creasePath = Path()
            creasePath.addArc(center: gCenterPt,
                              radius: cr,
                              startAngle: .degrees(crAngleStart),
                              endAngle: .degrees(crAngleStart + 180),
                              clockwise: eSign > 0)
            creasePath.closeSubpath()
            ctx.fill(creasePath, with: .color(Color.blue.opacity(0.25)))
            ctx.stroke(creasePath, with: .color(.red.opacity(0.7)), lineWidth: 1)

            // Goal (6 ft wide, 4 ft deep)
            let goalW = 6.0 * sc
            let goalD = 4.0 * sc
            let goalTop = eSign > 0 ? gCenterPt.y : gCenterPt.y - goalD
            let goalRect = CGRect(x: gCenterPt.x - goalW/2, y: goalTop, width: goalW, height: goalD)
            ctx.fill(Path(goalRect), with: .color(Color.red.opacity(0.5)))
            ctx.stroke(Path(goalRect), with: .color(.red), lineWidth: 1.5)
        }

        // ── Finger crosshair ──────────────────────────────────────────
        if let ff = fingerField {
            let fPt = l.sp(ff.x, ff.y)
            let lc = GraphicsContext.Shading.color(Color(red: 0.1, green: 0.1, blue: 0.6, opacity: 0.9))
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fPt.x - 14, y: fPt.y))
                p.addLine(to: CGPoint(x: fPt.x + 14, y: fPt.y))
            }, with: lc, lineWidth: 1.5)
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fPt.x, y: fPt.y - 14))
                p.addLine(to: CGPoint(x: fPt.x, y: fPt.y + 14))
            }, with: lc, lineWidth: 1.5)
            ctx.fill(Path(ellipseIn: CGRect(x: fPt.x-3, y: fPt.y-3, width:6, height:6)),
                     with: .color(Color(red: 0.1, green: 0.1, blue: 0.8)))
        }
    }

    // MARK: - Draw helpers

    private func lineH(_ ctx: GraphicsContext, _ l: HRLayout, y: Double,
                        color: Color, width: Double) {
        let a = l.sp(-halfW, y); let b = l.sp(halfW, y)
        ctx.stroke(Path { p in p.move(to: a); p.addLine(to: b) },
                   with: .color(color), lineWidth: width)
    }

    private func circle(_ ctx: GraphicsContext, _ l: HRLayout, cx: Double, cy: Double,
                         r: Double, color: Color, lineW: Double) {
        let pt = l.sp(cx, cy)
        let rPt = r * l.scale
        ctx.stroke(Path(ellipseIn: CGRect(x: pt.x-rPt, y: pt.y-rPt, width: rPt*2, height: rPt*2)),
                   with: .color(color), lineWidth: lineW)
    }

    private func dot(_ ctx: GraphicsContext, _ l: HRLayout, cx: Double, cy: Double,
                      r: Double, color: Color) {
        let pt = l.sp(cx, cy)
        let rPt = r * l.scale
        ctx.fill(Path(ellipseIn: CGRect(x: pt.x-rPt, y: pt.y-rPt, width: rPt*2, height: rPt*2)),
                 with: .color(color))
    }

    // MARK: - Zone detection

    private func detectZone(fx: Double, fy: Double) -> HRZone {
        // Out of bounds / in the boards
        if abs(fx) > halfW || abs(fy) > halfL {
            return HRZone(name: "In the boards", terrain: .foul)
        }

        // Crease zones
        for (eSign, label) in [(1.0, "Far"), (-1.0, "Near")] {
            let distToGoal = hypot(fx, fy - eSign * goalLineY)
            if distToGoal < creaseR {
                return HRZone(name: "\(label) goal crease", terrain: .warningTrack, isLineCrossing: false)
            }
        }

        // Lateral position
        let lateral: String
        if fx < -dotLat - 5 { lateral = "left boards" }
        else if fx < -dotLat + 5 { lateral = "left face-off dot area" }
        else if fx > dotLat + 5 { lateral = "right boards" }
        else if fx > dotLat - 5 { lateral = "right face-off dot area" }
        else { lateral = "center" }

        // Longitudinal zones
        let absFY = abs(fy)
        let endSide = fy >= 0 ? "Far" : "Near"

        if absFY < 5 {
            return HRZone(name: "Center ice — \(lateral)", terrain: .fair, isLineCrossing: absFY < 1)
        }
        if absFY < blueLineY {
            return HRZone(name: "Neutral zone, \(endSide) side — \(lateral)", terrain: .fair,
                          isLineCrossing: abs(absFY - blueLineY) < 1)
        }
        if absFY < goalLineY {
            let distFromBlue = Int((absFY - blueLineY).rounded())
            return HRZone(name: "\(endSide) end zone — \(distFromBlue) ft past blue line — \(lateral)",
                          terrain: .fair, isLineCrossing: abs(absFY - goalLineY) < 1)
        }
        // Behind the net
        let ftBehind = Int((absFY - goalLineY).rounded())
        return HRZone(name: "\(endSide) net — \(ftBehind) feet behind goal line — \(lateral)", terrain: .fair)
    }

    // MARK: - Drag handling

    private func handleDrag(location: CGPoint, layout: HRLayout) {
        let (fx, fy) = layout.fp(location.x, location.y)
        fingerField = CGPoint(x: fx, y: fy)

        let zone = detectZone(fx: fx, fy: fy)
        if zone.name != lastZoneName {
            lastZoneName = zone.name
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
            if zone.isLineCrossing { fieldAudio.playLandmark() }
        }

        let pan = Float((fx / halfW).clamped(to: -1...1))
        fieldAudio.update(terrain: zone.terrain, pan: pan)

        // Live named-line announcements
        let lineLabel = namedLine(fy: fy)
        if lineLabel != lastLineAnnouncement {
            lastLineAnnouncement = lineLabel
            if !lineLabel.isEmpty {
                TouchTourAnnouncementService.shared.announce(lineLabel)
            }
        }
    }

    private func namedLine(fy: Double) -> String {
        let absFY = abs(fy)
        if absFY < 3 { return "Red line" }
        if abs(absFY - blueLineY) < 3 { return "Blue line" }
        if abs(absFY - goalLineY) < 3 { return "Goal line" }
        return ""
    }

    private func handleDragEnd() {
        if let ff = fingerField {
            TouchTourAnnouncementService.shared.announce(detectZone(fx: ff.x, fy: ff.y).name)
        }
        lastLineAnnouncement = ""
        fingerField = nil
        fieldAudio.stop()
    }

    // MARK: - Status bar

    private var statusBar: some View {
        VStack(alignment: .leading, spacing: 4) {
            if let ff = fingerField {
                Text(detectZone(fx: ff.x, fy: ff.y).name)
                    .font(.subheadline.bold())
            } else {
                Text("Touch ice to explore")
                    .font(.caption).foregroundColor(.gray)
            }
            Text("NHL · 200 ft × 85 ft · Blue lines ±25 ft · Goal lines ±89 ft from center")
                .font(.caption2).foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color.gray.opacity(0.12))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(fingerField.map { detectZone(fx: $0.x, fy: $0.y).name }
                            ?? "Touch the rink above to explore.")
    }
}

#Preview {
    NavigationStack { HockeyRinkTourView() }
}
