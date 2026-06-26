//
//  RaceTrackTourView.swift
//  SportsScores
//
//  Audio touch tour of an oval race track.
//
//  Coordinate system: feet from center of oval.
//    x+ = right (Turn 1-2), x- = left (Turn 3-4)
//    y+ = backstretch (top), y- = frontstretch (bottom)
//
//  Drag anywhere on the canvas to hear terrain audio and feel zone-crossing haptics.
//  Lift finger to hear the current zone announced by VoiceOver.
//

import SwiftUI
import UIKit

// MARK: - Layout helper

private struct TrackLayout {
    let center: CGPoint   // screen position of oval center
    let scale: Double     // screen points per foot

    func sp(_ fx: Double, _ fy: Double) -> CGPoint {
        CGPoint(x: center.x + fx * scale,
                y: center.y - fy * scale)   // y inverted: +fy = backstretch = up on screen
    }

    func fp(_ sx: CGFloat, _ sy: CGFloat) -> (Double, Double) {
        (Double(sx - center.x) / scale,
         Double(center.y - sy) / scale)
    }
}

// MARK: - View

struct RaceTrackTourView: View {

    let track: RaceTrackGeometry

    @EnvironmentObject private var appSettings: AppSettings
    @StateObject private var fieldAudio = FieldAudioEngine()

    @State private var fingerField: CGPoint? = nil
    @State private var lastZoneName: String = ""

    var body: some View {
        VStack(spacing: 0) {
            canvasSection
            statusBar
        }
        .background(Color.black)
        .foregroundColor(.white)
        .navigationTitle(track.shortName)
        .navigationBarTitleDisplayMode(.inline)
        .onAppear  { fieldAudio.start() }
        .onDisappear { fieldAudio.stop() }
    }

    // MARK: - Canvas

    private var canvasSection: some View {
        GeometryReader { geo in
            let layout = makeLayout(geo.size)
            Canvas { ctx, _ in drawTrack(ctx: ctx, layout: layout) }
                .background(Color(white: 0.05))
                .contentShape(Rectangle())
                .gesture(
                    DragGesture(minimumDistance: 0, coordinateSpace: .local)
                        .onChanged { v in handleDrag(location: v.location, layout: layout) }
                        .onEnded { _ in handleDragEnd() }
                )
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(canvasAccessibilityLabel)
                .accessibilityHint("Double-tap to activate direct touch, then drag to explore. Haptic and audio feedback mark zone boundaries. Lift finger to hear the zone name.")
                .conditionalDirectTouch(appSettings.useDirectTouchForTours)
        }
        .frame(maxWidth: .infinity)
        .frame(maxHeight: .infinity)
        .clipped()
    }

    // MARK: - Layout

    private func makeLayout(_ size: CGSize) -> TrackLayout {
        let scaleW = (size.width - 24) / (2 * track.semiMinor)
        let scaleH = (size.height - 24) / (2 * track.semiMajor)
        let scale = min(scaleW, scaleH)
        return TrackLayout(
            center: CGPoint(x: size.width / 2, y: size.height / 2),
            scale: scale
        )
    }

    // MARK: - Drawing

    private func drawTrack(ctx: GraphicsContext, layout: TrackLayout) {
        let sc = layout.scale
        let cx = layout.center.x
        let cy = layout.center.y

        // Outer ellipse rect (entire oval envelope including wall)
        let outerW = 2 * track.semiMinor * sc
        let outerH = 2 * track.semiMajor * sc
        let outerRect = CGRect(x: cx - outerW/2, y: cy - outerH/2, width: outerW, height: outerH)

        // Inner ellipse rect (infield boundary)
        let innerW = 2 * track.innerSemiMinor * sc
        let innerH = 2 * track.innerSemiMajor * sc
        let innerRect = CGRect(x: cx - innerW/2, y: cy - innerH/2, width: innerW, height: innerH)

        // ── Racing surface (fill outer oval with asphalt) ──────────────────────
        ctx.fill(Path(ellipseIn: outerRect), with: .color(Color(white: 0.28)))

        // ── Infield (fill inner oval with green grass) ─────────────────────────
        ctx.fill(Path(ellipseIn: innerRect), with: .color(Color(red: 0.05, green: 0.20, blue: 0.06)))

        // ── Pit road lane (lighter band inside frontstretch infield boundary) ──
        drawPitRoad(ctx: ctx, layout: layout)

        // ── Inner wall (white stripe) ──────────────────────────────────────────
        ctx.stroke(Path(ellipseIn: innerRect), with: .color(Color.white.opacity(0.75)), lineWidth: 2)

        // ── Outer wall (white) ─────────────────────────────────────────────────
        ctx.stroke(Path(ellipseIn: outerRect), with: .color(Color.white.opacity(0.9)), lineWidth: 3)

        // ── Start/Finish line (white band at bottom center of frontstretch) ────
        let sfPt = layout.sp(0, -track.semiMajor + track.trackWidth * 0.5)
        let sfHalf: Double = track.trackWidth * 0.5 * sc
        ctx.fill(Path { p in
            p.move(to: CGPoint(x: sfPt.x - sfHalf, y: sfPt.y - 2))
            p.addLine(to: CGPoint(x: sfPt.x + sfHalf, y: sfPt.y - 2))
            p.addLine(to: CGPoint(x: sfPt.x + sfHalf, y: sfPt.y + 2))
            p.addLine(to: CGPoint(x: sfPt.x - sfHalf, y: sfPt.y + 2))
            p.closeSubpath()
        }, with: .color(.white))

        // ── Track name label in infield ────────────────────────────────────────
        var labelText = Text(track.shortName)
            .font(.system(size: max(8, min(14, innerW * 0.08))))
            .foregroundColor(.white.opacity(0.5))
        ctx.draw(labelText, at: CGPoint(x: cx, y: cy), anchor: .center)

        // ── Finger crosshair ───────────────────────────────────────────────────
        if let ff = fingerField {
            let fPt = layout.sp(ff.x, ff.y)
            let lc = GraphicsContext.Shading.color(Color.yellow.opacity(0.9))
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fPt.x - 16, y: fPt.y))
                p.addLine(to: CGPoint(x: fPt.x + 16, y: fPt.y))
            }, with: lc, lineWidth: 1.5)
            ctx.stroke(Path { p in
                p.move(to: CGPoint(x: fPt.x, y: fPt.y - 16))
                p.addLine(to: CGPoint(x: fPt.x, y: fPt.y + 16))
            }, with: lc, lineWidth: 1.5)
            ctx.fill(Path(ellipseIn: CGRect(x: fPt.x-3.5, y: fPt.y-3.5, width:7, height:7)),
                     with: .color(.yellow))
        }
    }

    private func drawPitRoad(ctx: GraphicsContext, layout: TrackLayout) {
        let sc = layout.scale
        let cx = layout.center.x
        let cy = layout.center.y

        // Pit road runs inside the inner wall along the frontstretch (bottom).
        // Width = 1.5× track width; length ≈ 60% of inner oval width.
        let pitW = track.innerSemiMinor * 0.65 * sc
        let pitH = track.trackWidth * 1.4 * sc
        let pitTop = cy + (track.innerSemiMajor - track.trackWidth * 0.3) * sc
        let pitRect = CGRect(x: cx - pitW, y: pitTop, width: pitW * 2, height: pitH)

        ctx.fill(Path(pitRect), with: .color(Color(white: 0.36)))
        // Pit wall (inner edge)
        ctx.stroke(Path { p in
            p.move(to: CGPoint(x: cx - pitW, y: pitTop))
            p.addLine(to: CGPoint(x: cx + pitW, y: pitTop))
        }, with: .color(Color.white.opacity(0.5)), lineWidth: 1.5)
    }

    // MARK: - Gesture handling

    private func handleDrag(location: CGPoint, layout: TrackLayout) {
        let (fx, fy) = layout.fp(location.x, location.y)
        fingerField = CGPoint(x: fx, y: fy)

        let zone = track.detectZone(x: fx, y: fy)

        if zone.name != lastZoneName {
            lastZoneName = zone.name
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
            if zone.isLandmark { fieldAudio.playLandmark() }
        }

        let pan = Float((fx / track.semiMinor).clamped(to: -1.0...1.0))
        fieldAudio.update(terrain: zone.terrain, pan: pan)
    }

    private func handleDragEnd() {
        if let ff = fingerField {
            let zone = track.detectZone(x: ff.x, y: ff.y)
            TouchTourAnnouncementService.shared.announce(zone.name)
        }
        fingerField = nil
        fieldAudio.stop()
    }

    // MARK: - Status bar

    private var statusBar: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(track.name)
                    .font(.caption.bold())
                    .foregroundColor(.yellow)
                Spacer()
                Text(track.location)
                    .font(.caption2)
                    .foregroundColor(.gray)
            }

            if let ff = fingerField {
                Text(track.detectZone(x: ff.x, y: ff.y).name)
                    .font(.subheadline.bold())
            } else {
                Text("Touch track to explore")
                    .font(.caption)
                    .foregroundColor(.gray)
            }

            Text("\(track.series) · \(String(format: "%.3f", track.lengthMiles)) miles · Turns \(track.turnBankingDeg)° banking")
                .font(.caption2)
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color.gray.opacity(0.12))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(statusAccessibilityLabel)
    }

    // MARK: - Accessibility helpers

    private var canvasAccessibilityLabel: String {
        "\(track.name). \(track.lengthMiles) mile oval. \(track.turnBankingDeg)-degree banking in turns. " +
        "Frontstretch and start/finish line at the bottom. " +
        "Turn 1-2 on the right, backstretch at the top, Turn 3-4 on the left. " +
        "Pit road runs inside the frontstretch wall."
    }

    private var statusAccessibilityLabel: String {
        guard let ff = fingerField else {
            return "\(track.name). Touch the track to explore."
        }
        return track.detectZone(x: ff.x, y: ff.y).name
    }
}

#Preview {
    NavigationStack {
        RaceTrackTourView(track: .daytonaInternationalSpeedway)
    }
    .environmentObject(AppSettings())
}
