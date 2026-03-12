//
//  SoccerPitchTourView.swift
//  SportsScores
//
//  Audio tour of a standard FIFA soccer pitch.
//
//  Field coordinate system (meters, origin = center spot)
//    fieldX : -34   → +34    (left touchline → right touchline)
//    fieldY : -52.5 → +52.5  (near goal line → far goal line)
//
//  Key landmarks (meters from center)
//    Goal lines          : fieldY = ±52.5
//    Penalty areas       : 16.5 m deep × 40.32 m wide (centered on goal line)
//                          |fieldX| ≤ 20.16, |fieldY| ∈ (36.0, 52.5)
//    6-yard boxes        :  5.5 m deep × 18.32 m wide (centered on goal)
//                          |fieldX| ≤  9.16, |fieldY| ∈ (47.0, 52.5)
//    Goals               : 7.32 m wide, 2.44 m deep, centered on goal line
//    Penalty spots       : fieldY = ±41.5  (11 m from goal line)
//    Center circle       : 9.15 m radius at (0,0)
//    Center mark         : (0,0)
//    Corner arcs         : 1 m radius at (±34, ±52.5)
//    Touchlines          : |fieldX| = 34
//
//  Terrain mapping
//    .foul         — out of pitch bounds
//    .warningTrack — penalty area, 6-yard box
//    .fair         — everywhere else in play
//

import SwiftUI
import UIKit

private struct SPLayout {
    let origin: CGPoint   // screen point for (fieldX = -34, fieldY = -52.5)
    let scale: Double     // pts per meter

    /// Field coords → screen point.  Y-inversion: near goal (fieldY=-52.5) maps to bottom.
    func sp(_ fx: Double, _ fy: Double) -> CGPoint {
        CGPoint(x: origin.x + (fx + 34.0) * scale,
                y: origin.y + (52.5 - fy) * scale)
    }

    /// Screen point → field coords.
    func fp(_ sx: CGFloat, _ sy: CGFloat) -> (Double, Double) {
        (Double(sx - origin.x) / scale - 34.0,
         52.5 - Double(sy - origin.y) / scale)
    }
}

private struct SPZone {
    let name: String
    let terrain: FieldTerrain
    var isLineCrossing: Bool = false
}

struct SoccerPitchTourView: View {

    @EnvironmentObject private var appSettings: AppSettings

    // FIFA standard pitch dimensions (meters)
    private let pitchW = 68.0
    private let pitchL = 105.0
    private let halfW  = 34.0
    private let halfL  = 52.5

    // Penalty area: extends 16.5 m from goal line, 40.32 m wide (±20.16 m from center)
    private let penAreaDepth = 16.5
    private let penAreaHalfW = 20.16

    // 6-yard box: extends 5.5 m from goal line, 18.32 m wide (±9.16 m from center)
    private let sixYardDepth  = 5.5
    private let sixYardHalfW  = 9.16

    // Penalty spot: 11 m from goal line → 52.5 - 11 = 41.5 from center
    private let penSpotY = 41.5

    // Center circle radius
    private let centerCircleR = 9.15

    // Corner arc radius
    private let cornerArcR = 1.0

    // Goal: 7.32 m wide, 2.44 m deep
    private let goalHalfW = 3.66
    private let goalDepth = 2.44

    @StateObject private var fieldAudio = FieldAudioEngine()

    @State private var fingerField: CGPoint? = nil   // (fieldX, fieldY) in meters
    @State private var lastZoneName: String = ""
    @State private var lastLineAnnouncement: String = ""

    var body: some View {
        VStack(spacing: 0) {
            canvasSection
            statusBar
        }
        .background(Color.black)
        .foregroundColor(.white)
        .navigationTitle("Soccer Pitch")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear  { fieldAudio.start() }
        .onDisappear { fieldAudio.stop() }
    }

    // MARK: - Canvas

    private var canvasSection: some View {
        GeometryReader { geo in
            let layout = makeLayout(geo.size)
            Canvas { ctx, _ in drawPitch(ctx: ctx, l: layout) }
                .background(Color(red: 0.13, green: 0.55, blue: 0.13))   // grass green
                .contentShape(Rectangle())
                .gesture(
                    DragGesture(minimumDistance: 0, coordinateSpace: .local)
                        .onChanged { v in handleDrag(location: v.location, layout: layout) }
                        .onEnded { _ in handleDragEnd() }
                )
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(
                    "FIFA soccer pitch, 105 meters long by 68 meters wide. " +
                    "Center circle 9.15 meters radius. " +
                    "Penalty areas 16.5 meters deep on each end. " +
                    "Goals centered on each goal line. " +
                    "Drag to explore — audio changes in the penalty areas."
                )
                .accessibilityHint(
                    "Use the rotor to toggle Direct Touch on or off for this pitch area. " +
                    "Drag to explore. Chime at the center line, penalty spots, and goal lines."
                )
                .conditionalDirectTouch(appSettings.useDirectTouchForTours)
        }
        .frame(maxWidth: .infinity)
        .frame(height: 480)
        .clipped()
    }

    // MARK: - Layout

    private func makeLayout(_ size: CGSize) -> SPLayout {
        let scaleW = (size.width - 12) / pitchW
        let scaleH = (size.height - 12) / pitchL
        let scale  = min(scaleW, scaleH)
        let pW = pitchW * scale
        let pH = pitchL * scale
        let ox = (size.width  - pW) / 2
        let oy = (size.height - pH) / 2
        return SPLayout(origin: CGPoint(x: ox, y: oy), scale: scale)
    }

    // MARK: - Drawing

    private func drawPitch(ctx: GraphicsContext, l: SPLayout) {
        let sc = l.scale

        // ── Pitch outline ───────────────────────────────────────────────
        let pitchRect = CGRect(x: l.sp(-halfW, halfL).x,
                               y: l.sp(-halfW, halfL).y,
                               width: pitchW * sc,
                               height: pitchL * sc)
        ctx.stroke(Path(pitchRect), with: .color(.white), lineWidth: 2)

        // ── Halfway line ────────────────────────────────────────────────
        lineH(ctx, l, y: 0.0, color: .white, width: 2)

        // ── Center circle & spot ────────────────────────────────────────
        circle(ctx, l, cx: 0, cy: 0, r: centerCircleR, color: .white, lineW: 1.5)
        dot(ctx, l, cx: 0, cy: 0, r: 0.4, color: .white)

        // ── End zones (near = negative y, far = positive y) ─────────────
        for eSign in [-1.0, 1.0] {
            let goalLineY = eSign * halfL   // ±52.5

            // Goal line is the pitch outline — already drawn. Just draw penalty structures.

            // Penalty area
            let penAreaNearY = eSign * (halfL - penAreaDepth)   // inner edge from center
            let penRect = CGRect(
                x: l.sp(-penAreaHalfW, max(goalLineY, penAreaNearY)).x,
                y: l.sp(-penAreaHalfW, max(goalLineY, penAreaNearY)).y,
                width: penAreaHalfW * 2 * sc,
                height: penAreaDepth * sc
            )
            ctx.stroke(Path(penRect), with: .color(.white), lineWidth: 1.5)

            // 6-yard box
            let sixNearY = eSign * (halfL - sixYardDepth)
            let sixRect = CGRect(
                x: l.sp(-sixYardHalfW, max(goalLineY, sixNearY)).x,
                y: l.sp(-sixYardHalfW, max(goalLineY, sixNearY)).y,
                width: sixYardHalfW * 2 * sc,
                height: sixYardDepth * sc
            )
            ctx.stroke(Path(sixRect), with: .color(.white), lineWidth: 1.5)

            // Penalty spot
            dot(ctx, l, cx: 0, cy: eSign * penSpotY, r: 0.4, color: .white)

            // Penalty arc (the arc outside the penalty area centered on penalty spot, r=9.15)
            // Arc: centered on penalty spot, showing part that lies outside the penalty area
            let penSpotPt = l.sp(0, eSign * penSpotY)
            let arcR = centerCircleR * sc
            // The arc extends toward center. For eSign=1 (far), arc goes toward negative y (center).
            // We draw a full circle but clip to outside the penalty area.
            // Simplified: draw a partial arc ~60° centered facing center
            let arcStart: Double = eSign > 0 ? 200 : 20
            let arcEnd:   Double = eSign > 0 ? 340 : 160
            var arcPath = Path()
            arcPath.addArc(center: penSpotPt,
                           radius: arcR,
                           startAngle: .degrees(arcStart),
                           endAngle:   .degrees(arcEnd),
                           clockwise:  false)
            ctx.stroke(arcPath, with: .color(.white), lineWidth: 1.5)

            // Goal (behind goal line)
            let goalNearY  = eSign * (halfL + goalDepth)
            let goalOriginY = eSign > 0 ? goalLineY : goalNearY
            let goalRect = CGRect(
                x: l.sp(-goalHalfW, goalOriginY).x,
                y: l.sp(-goalHalfW, max(goalLineY, goalNearY)).y,
                width: goalHalfW * 2 * sc,
                height: goalDepth * sc
            )
            ctx.fill(Path(goalRect), with: .color(Color.white.opacity(0.15)))
            ctx.stroke(Path(goalRect), with: .color(.white), lineWidth: 1.5)

            // Corner arcs (4 corners)
            for xSign in [-1.0, 1.0] {
                let cornerPt = l.sp(xSign * halfW, goalLineY)
                var cArc = Path()
                // Arc sweeps inward from the corner
                let cStart: Double = xSign > 0 ? (eSign > 0 ? 180 : 90) : (eSign > 0 ? 270 : 0)
                cArc.addArc(center: cornerPt,
                            radius: cornerArcR * sc,
                            startAngle: .degrees(cStart),
                            endAngle:   .degrees(cStart + 90),
                            clockwise:  false)
                ctx.stroke(cArc, with: .color(.white), lineWidth: 1.5)
            }
        }

        // ── Finger crosshair ─────────────────────────────────────────────
        if let ff = fingerField {
            let fPt = l.sp(ff.x, ff.y)
            let lc  = GraphicsContext.Shading.color(Color(white: 1.0, opacity: 0.85))
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fPt.x - 14, y: fPt.y))
                p.addLine(to: CGPoint(x: fPt.x + 14, y: fPt.y))
            }, with: lc, lineWidth: 1.5)
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fPt.x, y: fPt.y - 14))
                p.addLine(to: CGPoint(x: fPt.x, y: fPt.y + 14))
            }, with: lc, lineWidth: 1.5)
            ctx.fill(
                Path(ellipseIn: CGRect(x: fPt.x - 3, y: fPt.y - 3, width: 6, height: 6)),
                with: .color(.white)
            )
        }
    }

    // MARK: - Draw helpers

    private func lineH(_ ctx: GraphicsContext, _ l: SPLayout, y: Double,
                        color: Color, width: Double) {
        let a = l.sp(-halfW, y); let b = l.sp(halfW, y)
        ctx.stroke(Path { p in p.move(to: a); p.addLine(to: b) },
                   with: .color(color), lineWidth: width)
    }

    private func circle(_ ctx: GraphicsContext, _ l: SPLayout, cx: Double, cy: Double,
                         r: Double, color: Color, lineW: Double) {
        let pt   = l.sp(cx, cy)
        let rPts = r * l.scale
        ctx.stroke(
            Path(ellipseIn: CGRect(x: pt.x - rPts, y: pt.y - rPts,
                                   width: rPts * 2, height: rPts * 2)),
            with: .color(color), lineWidth: lineW
        )
    }

    private func dot(_ ctx: GraphicsContext, _ l: SPLayout, cx: Double, cy: Double,
                      r: Double, color: Color) {
        let pt   = l.sp(cx, cy)
        let rPts = r * l.scale
        ctx.fill(
            Path(ellipseIn: CGRect(x: pt.x - rPts, y: pt.y - rPts,
                                   width: rPts * 2, height: rPts * 2)),
            with: .color(color)
        )
    }

    // MARK: - Zone detection

    private func detectZone(fx: Double, fy: Double) -> SPZone {
        // Out of bounds
        if abs(fx) > halfW || abs(fy) > halfL {
            return SPZone(name: "Out of play", terrain: .foul)
        }

        let absFY  = abs(fy)
        let endSide = fy >= 0 ? "Far" : "Near"

        // 6-yard box
        if absFY > halfL - sixYardDepth && abs(fx) <= sixYardHalfW {
            let mFromLine = Int((halfL - absFY).rounded())
            return SPZone(name: "\(endSide) 6-yard box — \(mFromLine) m from goal line",
                          terrain: .warningTrack)
        }

        // Penalty area
        if absFY > halfL - penAreaDepth && abs(fx) <= penAreaHalfW {
            let mFromLine = Int((halfL - absFY).rounded())
            return SPZone(name: "\(endSide) penalty area — \(mFromLine) m from goal line",
                          terrain: .warningTrack,
                          isLineCrossing: abs(absFY - (halfL - penAreaDepth)) < 1)
        }

        // Lateral label
        let lateral: String
        let absFX = abs(fx)
        if absFX > 28 { lateral = fx < 0 ? "near left touchline" : "near right touchline" }
        else if absFX > 20 { lateral = fx < 0 ? "left flank" : "right flank" }
        else if absFX > 10 { lateral = fx < 0 ? "inside left channel" : "inside right channel" }
        else { lateral = "center" }

        // Center circle
        let distFromCenter = hypot(fx, fy)
        if distFromCenter < centerCircleR {
            let mOut = Int(distFromCenter.rounded())
            return SPZone(name: "Center circle — \(mOut) m from center spot — \(lateral)",
                          terrain: .fair,
                          isLineCrossing: distFromCenter < 1.5)
        }

        // Longitudinal zones
        if absFY < 5 {
            return SPZone(name: "Halfway — \(lateral)", terrain: .fair,
                          isLineCrossing: absFY < 1.5)
        }
        if absFY < halfL - penAreaDepth {
            let distFromHalf = Int(absFY.rounded())
            return SPZone(name: "\(endSide) half — \(distFromHalf) m from center — \(lateral)",
                          terrain: .fair)
        }

        // Between penalty area and goal line (but outside pen area width)
        return SPZone(name: "\(endSide) end — \(lateral)", terrain: .fair)
    }

    // MARK: - Drag handling

    private func handleDrag(location: CGPoint, layout: SPLayout) {
        let (fx, fy) = layout.fp(location.x, location.y)
        fingerField = CGPoint(x: fx, y: fy)

        let zone = detectZone(fx: fx, fy: fy)
        if zone.name != lastZoneName {
            lastZoneName = zone.name
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
            if zone.isLineCrossing { fieldAudio.playLandmark() }
        }

        let pan = Float((fx / halfW).clamped(to: -1 ... 1))
        fieldAudio.update(terrain: zone.terrain, pan: pan)

        let lineLabel = namedLine(fy: fy, fx: fx)
        if lineLabel != lastLineAnnouncement {
            lastLineAnnouncement = lineLabel
            if !lineLabel.isEmpty {
                TouchTourAnnouncementService.shared.announce(lineLabel)
            }
        }
    }

    private func namedLine(fy: Double, fx: Double) -> String {
        let absFY = abs(fy)
        if absFY < 2                          { return "Halfway line" }
        if abs(absFY - penSpotY) < 1.5        { return "Penalty spot" }
        if absFY > halfL - 2                  { return "Goal line" }
        if absFY > halfL - penAreaDepth - 1.5
           && absFY < halfL - penAreaDepth + 1.5
           && abs(fx) <= penAreaHalfW + 1     { return "Penalty area line" }
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
                Text(String(format: "%.1f m from center", hypot(ff.x, ff.y)))
                    .font(.caption).foregroundColor(.gray)
            } else {
                Text("Touch pitch to explore")
                    .font(.caption).foregroundColor(.gray)
            }
            Text("FIFA · 105 m × 68 m · Penalty areas ±36.0–52.5 m · Penalty spots ±41.5 m")
                .font(.caption2).foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color.gray.opacity(0.12))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(fingerField.map { detectZone(fx: $0.x, fy: $0.y).name }
                            ?? "Touch the pitch above to explore.")
    }
}

#Preview {
    NavigationStack { SoccerPitchTourView() }
}
