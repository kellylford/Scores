//
//  BasketballCourtTourView.swift
//  SportsScores
//
//  Audio tour of a standard NBA basketball court.
//
//  Field coordinate system (feet, origin = center court)
//    fieldX : -25 → +25    (left sideline → right sideline)
//    fieldY : -47 → +47    (near baseline → far baseline)
//
//  Key landmarks (NBA specification, in feet from center)
//    Baskets          : (0, ±43)      — 4 ft from baseline
//    Paint/key        : x ∈ [-8,+8],  near baseline → free throw line
//    Free throw line  : y = ±28       — 15 ft from basket (19 ft from baseline)
//    3-point arc      : 23.75-ft radius from basket; corners clip to 22 ft
//    Center circle    : 6-ft radius
//

import SwiftUI
import UIKit

private struct BCLayout {
    let origin: CGPoint   // screen pt for (fieldX=-25, fieldY=-47)
    let scale: Double     // pt per foot
    func sp(_ fx: Double, _ fy: Double) -> CGPoint {
        CGPoint(x: origin.x + (fx + 25) * scale,
                y: origin.y + (47 - fy) * scale)   // near=bottom on screen
    }
    func fp(_ sx: CGFloat, _ sy: CGFloat) -> (Double, Double) {
        (Double(sx - origin.x) / scale - 25,
         47.0 - Double(sy - origin.y) / scale)
    }
}

private struct BCZone {
    let name: String
    let terrain: FieldTerrain
    var isLineCrossing: Bool = false
}

struct BasketballCourtTourView: View {

    private let courtW = 50.0    // ft
    private let courtL = 94.0    // ft
    private let halfW  = 25.0
    private let halfL  = 47.0

    // NBA dimensions
    private let basketY     = 43.0   // ft from center (4 ft from baseline)
    private let ftLineY     = 28.0   // ft from center (free throw line — 15 ft from basket, 19 ft from baseline)
    private let paintHalfW  = 8.0    // ft (16 ft wide key)
    private let threeArcR   = 23.75  // ft radius from basket
    private let cornerThree = 22.0   // ft from basket at corner
    private let centerCircR = 6.0    // ft
    private let ftCircR     = 6.0    // ft — free throw circle

    @StateObject private var fieldAudio = FieldAudioEngine()
    @State private var fingerField: CGPoint? = nil
    @State private var lastZoneName: String = ""
    @State private var lastLiveLabel: String = ""

    var body: some View {
        VStack(spacing: 0) {
            canvasSection
            statusBar
        }
        .background(Color(red: 0.16, green: 0.12, blue: 0.08))
        .foregroundColor(.white)
        .navigationTitle("Basketball Court")
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Canvas

    private var canvasSection: some View {
        GeometryReader { geo in
            let layout = makeLayout(geo.size)
            Canvas { ctx, sz in drawCourt(ctx: ctx, sz: sz, l: layout) }
                .background(Color(red: 0.64, green: 0.44, blue: 0.24))   // hardwood
                .contentShape(Rectangle())
                .gesture(
                    DragGesture(minimumDistance: 0, coordinateSpace: .local)
                        .onChanged { v in handleDrag(location: v.location, layout: layout) }
                        .onEnded { _ in handleDragEnd() }
                )
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("NBA basketball court, 94 feet long by 50 feet wide. Paint is 16 feet wide, free throw line 15 feet from each basket. 3-point arc begins at 23 feet 9 inches from either basket. Drag to explore — audio changes at the paint and out of bounds.")
                .accessibilityHint("Use the rotor to toggle Direct Touch on or off for this court area. Drag to explore. Chime at 3-point arc, free throw line, and half court.")
                .accessibilityDirectTouch(options: .silentOnTouch)
        }
        .frame(maxWidth: .infinity)
        .frame(height: 480)
        .clipped()
    }

    private func makeLayout(_ size: CGSize) -> BCLayout {
        let scaleW = (size.width - 12) / courtW
        let scaleH = (size.height - 12) / courtL
        let scale = min(scaleW, scaleH)
        let cW = courtW * scale; let cH = courtL * scale
        let ox = (size.width - cW) / 2; let oy = (size.height - cH) / 2
        return BCLayout(origin: CGPoint(x: ox, y: oy), scale: scale)
    }

    // MARK: - Drawing

    private func drawCourt(ctx: GraphicsContext, sz: CGSize, l: BCLayout) {
        let sc = l.scale
        let courtRect = CGRect(x: l.sp(-halfW, halfL).x,
                               y: l.sp(-halfW, halfL).y,
                               width: courtW * sc,
                               height: courtL * sc)

        // ── Court floor ──────────────────────────────────────────────
        let floorColor = Color(red: 0.80, green: 0.58, blue: 0.32)
        ctx.fill(Path(courtRect), with: .color(floorColor))
        ctx.stroke(Path(courtRect), with: .color(.white), lineWidth: 1.5)

        // ── Center circle & half-court line ──────────────────────────
        lineH(ctx, l, y: 0, color: .white, width: 1)
        circleStroke(ctx, l, cx: 0, cy: 0, r: centerCircR, color: .white, lineW: 1.2)
        dot(ctx, l, cx: 0, cy: 0, r: 1.5, color: .white)

        // ── Each end ──────────────────────────────────────────────────
        for eSign in [-1.0, 1.0] {
            drawEnd(ctx: ctx, l: l, sc: sc, eSign: eSign)
        }

        // ── Finger crosshair ──────────────────────────────────────────
        if let ff = fingerField {
            let fPt = l.sp(ff.x, ff.y)
            let lc = GraphicsContext.Shading.color(Color(white: 1, opacity: 0.85))
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fPt.x - 14, y: fPt.y))
                p.addLine(to: CGPoint(x: fPt.x + 14, y: fPt.y))
            }, with: lc, lineWidth: 1.5)
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fPt.x, y: fPt.y - 14))
                p.addLine(to: CGPoint(x: fPt.x, y: fPt.y + 14))
            }, with: lc, lineWidth: 1.5)
            ctx.fill(Path(ellipseIn: CGRect(x: fPt.x-3, y: fPt.y-3, width:6, height:6)),
                     with: .color(.white))
        }
    }

    private func drawEnd(ctx: GraphicsContext, l: BCLayout, sc: Double, eSign: Double) {
        let by = eSign * basketY     // basket Y (signed)
        let fty = eSign * ftLineY    // free throw line Y (signed)
        let baselineY = eSign * halfL

        // --- Paint rectangle ---
        // From baseline to free throw line
        let paintTop = eSign > 0 ? l.sp(-paintHalfW, baselineY).y : l.sp(-paintHalfW, fty).y
        let paintH   = abs(fty - baselineY) * sc
        let paintRect = CGRect(x: l.sp(-paintHalfW, by).x, y: paintTop,
                               width: paintHalfW * 2 * sc, height: paintH)
        ctx.fill(Path(paintRect), with: .color(Color(red: 0.72, green: 0.50, blue: 0.62).opacity(0.6)))
        ctx.stroke(Path(paintRect), with: .color(.white), lineWidth: 1)

        // --- Free throw line ---
        let ftA = l.sp(-paintHalfW, fty); let ftB = l.sp(paintHalfW, fty)
        ctx.stroke(Path { p in p.move(to: ftA); p.addLine(to: ftB) },
                   with: .color(.white), lineWidth: 1)

        // --- Free throw circle (dotted half) ---
        circleStroke(ctx, l, cx: 0, cy: fty, r: ftCircR, color: .white, lineW: 1)

        // --- 3-point arc ---
        let basketPt = l.sp(0, by)
        let arcR = threeArcR * sc
        // Corner cutoffs at 22 ft from basket → in screen coords
        // The arc starts at the corner distance along sides, goes over the top
        // Corner three line: vertical line from baseline at x = ±(22 ft from basket center)
        // Since basket is at (0, by), corner 3pt dist < 22 means |fx| ≥ some boundary
        // Simple approach: draw full arc and clip to court
        var arcPath = Path()
        // Start angle depends on sign (near/far)
        if eSign < 0 {
            // Near end: basket near bottom; arc faces up (toward center)
            arcPath.addArc(center: basketPt, radius: arcR,
                           startAngle: .degrees(0), endAngle: .degrees(180), clockwise: true)
        } else {
            arcPath.addArc(center: basketPt, radius: arcR,
                           startAngle: .degrees(180), endAngle: .degrees(0), clockwise: true)
        }
        ctx.stroke(arcPath, with: .color(.white), lineWidth: 1.5)

        // Corner 3-point straight lines
        // At x = ±(basket_x ± cornerThree) = ±cornerThree, from baseline to where arc begins
        for xSide in [-1.0, 1.0] {
            let cx = xSide * cornerThree
            let pA = l.sp(cx, baselineY)
            // Corner line runs from baseline to where the arc starts
            // Height = 0 since the corner x happens at the arc tangent point... 
            // In standard NBA, the corner 3 line runs from the baseline to a specific distance along the sideline
            // Corner 3 distance along sideline from baseline = sqrt(arcR^2 - cornerThree^2) from basket
            // If basket at (0, by): y_dist = sqrt(23.75^2 - 22^2) ≈ 7.9 ft → corner line endpoint y = by ∓ 7.9
            let yDist = sqrt(threeArcR * threeArcR - cornerThree * cornerThree)
            let pB = l.sp(cx, by + (-eSign) * yDist)   // walking toward center from basket
            ctx.stroke(Path { p in p.move(to: pA); p.addLine(to: pB) },
                       with: .color(.white), lineWidth: 1.5)
        }

        // --- Basket (circle) ---
        dot(ctx, l, cx: 0, cy: by, r: 0.75, color: Color(red: 1, green: 0.4, blue: 0.0))
        circleStroke(ctx, l, cx: 0, cy: by, r: 0.75, color: Color(red:1, green: 0.4, blue: 0.0), lineW: 1)

        // --- Backboard (6 ft wide, sits ~2 ft inside baseline, behind basket) ---
        let bbW = 6.0 * sc
        let bbY = eSign > 0 ? l.sp(0, halfL - 2).y : l.sp(0, -halfL + 2).y
        let bbA = CGPoint(x: l.sp(0, by).x - bbW/2, y: bbY)
        let bbB = CGPoint(x: l.sp(0, by).x + bbW/2, y: bbY)
        ctx.stroke(Path { p in p.move(to: bbA); p.addLine(to: bbB) },
                   with: .color(.white.opacity(0.7)), lineWidth: 2)
    }

    // MARK: - Draw helpers

    private func lineH(_ ctx: GraphicsContext, _ l: BCLayout, y: Double, color: Color, width: Double) {
        let a = l.sp(-halfW, y); let b = l.sp(halfW, y)
        ctx.stroke(Path { p in p.move(to: a); p.addLine(to: b) }, with: .color(color), lineWidth: width)
    }

    private func circleStroke(_ ctx: GraphicsContext, _ l: BCLayout, cx: Double, cy: Double,
                               r: Double, color: Color, lineW: Double) {
        let pt = l.sp(cx, cy); let rPt = r * l.scale
        ctx.stroke(Path(ellipseIn: CGRect(x: pt.x-rPt, y: pt.y-rPt,
                                          width: rPt*2, height: rPt*2)),
                   with: .color(color), lineWidth: lineW)
    }

    private func dot(_ ctx: GraphicsContext, _ l: BCLayout, cx: Double, cy: Double, r: Double, color: Color) {
        let pt = l.sp(cx, cy); let rPt = r * l.scale
        ctx.fill(Path(ellipseIn: CGRect(x: pt.x-rPt, y: pt.y-rPt, width: rPt*2, height: rPt*2)),
                 with: .color(color))
    }

    // MARK: - Zone detection

    private func distFromBasket(fx: Double, fy: Double, eSign: Double) -> Double {
        hypot(fx, fy - eSign * basketY)
    }

    private func detectZone(fx: Double, fy: Double) -> BCZone {
        // Out of bounds
        if abs(fx) > halfW + 0.5 || abs(fy) > halfL + 0.5 {
            return BCZone(name: "Out of bounds", terrain: .foul)
        }

        // Which end?
        let absFY = abs(fy)
        let endSign = fy >= 0 ? 1.0 : -1.0
        let endLabel = fy >= 0 ? "Far" : "Near"

        // Half-court
        if absFY < 2 {
            return BCZone(name: "Center court", terrain: .fair, isLineCrossing: absFY < 0.5)
        }
        if absFY < 7 {
            return BCZone(name: "Near mid-court, \(endLabel) side", terrain: .fair)
        }

        let distB = distFromBasket(fx: fx, fy: fy, eSign: endSign)
        let inPaint = abs(fx) <= paintHalfW && absFY >= ftLineY && absFY <= halfL

        // Corner 3 area
        let isCorner3 = abs(fx) >= cornerThree - 2 && absFY > basketY - 8

        // Paint
        if inPaint {
            let paintLabel = absFY < (ftLineY + halfL) / 2 - 2 ? "high post" : "low post / under basket"
            return BCZone(name: "\(endLabel) end paint — \(paintLabel)", terrain: .warningTrack,
                          isLineCrossing: abs(absFY - ftLineY) < 1)
        }

        // Free throw line extended (elbow area)
        if abs(absFY - ftLineY) < 2 && abs(fx) > paintHalfW && abs(fx) < paintHalfW + 10 {
            return BCZone(name: "\(endLabel) end — elbow, \(fx < 0 ? "left" : "right") side", terrain: .fair,
                          isLineCrossing: abs(absFY - ftLineY) < 0.5)
        }

        // 3-point territory vs inside
        if distB > threeArcR || (abs(fx) >= cornerThree && absFY > ftLineY) {
            if isCorner3 {
                return BCZone(name: "\(endLabel) end — corner 3, \(fx < 0 ? "left" : "right")", terrain: .fair,
                              isLineCrossing: abs(distB - threeArcR) < 2 || abs(abs(fx) - cornerThree) < 1)
            }
            let dir: String
            let bearing = atan2(fx, absFY - basketY) * 180 / .pi
            if bearing < -60 { dir = "left wing" }
            else if bearing < -20 { dir = "left of center" }
            else if bearing < 20 { dir = "top of the arc" }
            else if bearing < 60 { dir = "right of center" }
            else { dir = "right wing" }
            return BCZone(name: "\(endLabel) end — 3-point territory, \(dir)", terrain: .fair,
                          isLineCrossing: abs(distB - threeArcR) < 1.5)
        } else {
            // Inside arc but outside paint
            let dir: String
            if abs(fx) < 3 { dir = "center lane" }
            else { dir = fx < 0 ? "left side" : "right side" }
            return BCZone(name: "\(endLabel) end — inside arc, \(dir)", terrain: .fair)
        }
    }

    // MARK: - Drag

    private func handleDrag(location: CGPoint, layout: BCLayout) {
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

        // Live zone announcements while dragging
        let live = liveLabel(zone: zone, fy: fy)
        if live != lastLiveLabel {
            lastLiveLabel = live
            if !live.isEmpty {
                UIAccessibility.post(notification: .announcement, argument: live)
            }
        }
    }

    private func liveLabel(zone: BCZone, fy: Double) -> String {
        let n = zone.name
        if n.contains("paint") { return "Paint" }
        if n.contains("Center court") { return "Half court" }
        let absFY = abs(fy)
        if abs(absFY - ftLineY) < 2 { return "Free throw" }
        if zone.isLineCrossing && n.contains("3-point") { return "Three point" }
        return ""
    }

    private func handleDragEnd() {
        if let ff = fingerField {
            UIAccessibility.post(notification: .announcement,
                                 argument: detectZone(fx: ff.x, fy: ff.y).name)
        }
        lastLiveLabel = ""
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
                Text("Touch the court to explore").font(.caption).foregroundColor(.gray)
            }
            Text("NBA · 94 ft × 50 ft · Paint 16 ft wide · 3-point arc 23 ft 9 in")
                .font(.caption2).foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color.gray.opacity(0.12))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(fingerField.map { detectZone(fx: $0.x, fy: $0.y).name }
                            ?? "Touch the court above to explore.")
    }
}

#Preview {
    NavigationStack { BasketballCourtTourView() }
}
