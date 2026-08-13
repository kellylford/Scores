//
//  FootballFieldTourView.swift
//  SportsScores
//
//  Audio tour of a gridiron football field. The same view renders either the
//  NFL or the CFL field via a `FootballFieldVariant` — the two leagues use
//  notably different geometry.
//
//  Field coordinate system (yards, origin = near end zone back line, left sideline)
//    fieldX : 0 → width   (left sideline → right sideline)
//    fieldY : 0 → length  (near end zone back → far end zone back)
//
//  NFL: 120 × 53⅓ yds · 10-yard end zones · hashes 70 ft 9 in from sideline ·
//       goal posts at the back of the end zone, aligned with the hashes.
//  CFL: 150 × 65 yds · 20-yard end zones · hashes 24 yds from sideline ·
//       goal posts on the goal line, centred · centre is the 55-yard line.
//

import SwiftUI
import UIKit

// MARK: - League variant

struct FootballFieldVariant {
    let league: String              // "NFL" / "CFL"
    let width: Double               // yards, sideline to sideline
    let length: Double              // yards, back line to back line (incl. end zones)
    let endZoneDepth: Double        // yards
    let hashLeft: Double            // X of left hash (yards from left sideline)
    let hashRight: Double           // X of right hash
    let goalPostsOnGoalLine: Bool   // CFL: on the goal line; NFL: on the back line
    let goalPostLeftX: Double       // X of left upright marker
    let goalPostRightX: Double      // X of right upright marker
    let widthLabel: String          // "53⅓ yds" / "65 yds"

    // Info-page copy
    let lengthLabel: String
    let endZoneLabel: String
    let hashLabel: String
    let goalPostLabel: String
    let canvasAccessibility: String
    let statusSecondLine: String

    /// Distance between goal lines (the playing field), e.g. 100 (NFL) / 110 (CFL).
    var playLength: Double { length - 2 * endZoneDepth }
    /// The centre-line yard number: 50 (NFL) / 55 (CFL).
    var centerYard: Int { Int(playLength / 2) }
    /// fieldY of the centre line.
    var centerFY: Double { endZoneDepth + playLength / 2 }
    var nearGoalLine: Double { endZoneDepth }
    var farGoalLine: Double { length - endZoneDepth }
    var nearGoalPostY: Double { goalPostsOnGoalLine ? nearGoalLine : 0 }
    var farGoalPostY: Double { goalPostsOnGoalLine ? farGoalLine : length }

    static let nfl = FootballFieldVariant(
        league: "NFL",
        width: 53.333,
        length: 120.0,
        endZoneDepth: 10.0,
        hashLeft: 23.583,
        hashRight: 29.750,
        goalPostsOnGoalLine: false,
        goalPostLeftX: 23.583,      // NFL uprights align with the hashes
        goalPostRightX: 29.750,
        widthLabel: "53⅓ yds",
        lengthLabel: "120 yards (including end zones)",
        endZoneLabel: "10 yards deep at each end",
        hashLabel: "70 ft 9 in from each sideline",
        goalPostLabel: "Back of the end zone, aligned with the hash marks",
        canvasAccessibility: "NFL football field. 120 yards long including 10-yard end zones. 53 yards wide. Drag to explore. Chime at every 5-yard line; louder at 10-yard lines. Hash marks 70 feet 9 inches from sideline — same width as goal posts.",
        statusSecondLine: "NFL · 120 yds × 53⅓ yds · Hash marks align with goal posts"
    )

    static let cfl: FootballFieldVariant = {
        let width = 65.0
        let halfUpright = (18.5 / 3.0) / 2.0   // goal posts are 18 ft 6 in wide
        return FootballFieldVariant(
            league: "CFL",
            width: width,
            length: 150.0,
            endZoneDepth: 20.0,
            hashLeft: 24.0,
            hashRight: width - 24.0,            // 41.0
            goalPostsOnGoalLine: true,
            goalPostLeftX: width / 2 - halfUpright,
            goalPostRightX: width / 2 + halfUpright,
            widthLabel: "65 yds",
            lengthLabel: "150 yards (including end zones)",
            endZoneLabel: "20 yards deep at each end",
            hashLabel: "24 yards from each sideline",
            goalPostLabel: "On the goal line, centred (not on the hashes)",
            canvasAccessibility: "CFL football field. 150 yards long including 20-yard end zones. 65 yards wide. Drag to explore. Chime at every 5-yard line; louder at 10-yard lines. Hash marks 24 yards from each sideline. Goal posts stand on the goal line. Centre is the 55-yard line.",
            statusSecondLine: "CFL · 150 yds × 65 yds · 20-yd end zones · Goal posts on the goal line"
        )
    }()
}

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

    @EnvironmentObject private var appSettings: AppSettings

    private let variant: FootballFieldVariant

    init(variant: FootballFieldVariant = .nfl) {
        self.variant = variant
    }

    // Field dimensions (from variant)
    private var fW: Double { variant.width }
    private var fL: Double { variant.length }
    private var ezD: Double { variant.endZoneDepth }
    private var hashL: Double { variant.hashLeft }
    private var hashR: Double { variant.hashRight }

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
        .navigationTitle("\(variant.league) Field")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear  { fieldAudio.start() }
        .onDisappear { fieldAudio.stop() }
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
                .accessibilityLabel(variant.canvasAccessibility)
                .accessibilityHint("Double-tap to activate direct touch, then drag freely to explore. Chimes at every 5-yard line. Use the rotor to turn Direct Touch off.")
                .conditionalDirectTouch(appSettings.useDirectTouchForTours)
        }
        .frame(maxWidth: .infinity)
        .frame(maxHeight: .infinity)
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

        // ── Alternating 10-yard stripes (subtle) ──────────────────────
        let bandCount = Int(variant.playLength / 10)
        for band in 0..<bandCount {
            if band % 2 == 0 { continue }
            let y0 = ezD + Double(band) * 10.0
            ctx.fill(Path(CGRect(
                x: l.sp(0, y0).x, y: l.sp(0, y0 + 10).y,
                width: fW * sc, height: 10 * sc)),
                with: .color(Color.white.opacity(0.025)))
        }

        // ── Yard lines ────────────────────────────────────────────────
        for yd in stride(from: 5, through: Int(fL) - 5, by: 5) {
            let y = Double(yd)
            guard y > 0 && y < fL else { continue }
            // A "10-yard line" is a whole multiple of 10 yards from the goal line.
            let is10 = (yd - Int(ezD)) % 10 == 0
            let lineAlpha: Double = is10 ? 0.80 : 0.45
            let lineW: Double = is10 ? 1.5 : 0.8
            let p1 = l.sp(0, y); let p2 = l.sp(fW, y)
            ctx.stroke(Path { p in p.move(to: p1); p.addLine(to: p2) },
                       with: .color(Color.white.opacity(lineAlpha)), lineWidth: lineW)
        }

        // ── Goal lines ────────────────────────────────────────────────
        for gy in [variant.nearGoalLine, variant.farGoalLine] {
            ctx.stroke(Path { p in p.move(to: l.sp(0, gy)); p.addLine(to: l.sp(fW, gy)) },
                       with: .color(.white), lineWidth: 2)
        }

        // ── Hash marks — every yard between the goal lines ────────────
        let hashLen = max(4.0, sc * 0.6)   // physical: ~2 ft each side
        for yd in (Int(ezD) + 1)...(Int(fL - ezD) - 1) {
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

        // ── Yard numbers (every 10 yards from each goal line) ─────────
        for yd in stride(from: ezD + 10, through: fL - ezD - 10, by: 10) {
            // Label is distance from the nearer goal line.
            let dist = yd <= variant.centerFY ? yd - ezD : fL - ezD - yd
            let label = "\(Int(dist.rounded()))"
            let pt = l.sp(fW / 2, yd)
            ctx.draw(Text(label).font(.system(size: 10, weight: .bold)).foregroundColor(.white.opacity(0.6)),
                     at: pt)
        }

        // ── Goal post indicators ──────────────────────────────────────
        for gpY in [variant.nearGoalPostY, variant.farGoalPostY] {
            for gpX in [variant.goalPostLeftX, variant.goalPostRightX] {
                let pt = l.sp(gpX, gpY)
                let r = max(4.0, sc * 0.4)
                ctx.fill(Path(ellipseIn: CGRect(x: pt.x - r, y: pt.y - r, width: r*2, height: r*2)),
                         with: .color(.yellow))
                ctx.draw(Text("G").font(.system(size: 7, weight: .black)).foregroundColor(.black), at: pt)
            }
            // Crossbar between the uprights
            let gl = l.sp(variant.goalPostLeftX, gpY); let gr = l.sp(variant.goalPostRightX, gpY)
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

        // ── Sideline label ────────────────────────────────────────────
        let midY = l.sp(fW / 2, fL / 2)
        ctx.draw(Text("← \(variant.widthLabel) →").font(.system(size: 8)).foregroundColor(.white.opacity(0.35)),
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

        // Goal post zones
        for (gpY, side) in [(variant.nearGoalPostY, "Near"), (variant.farGoalPostY, "Far")] {
            if abs(fy - gpY) < 2 {
                if abs(fx - variant.goalPostLeftX) < 2 { return FFZone(name: "\(side) goal post, left upright", terrain: .foul, isGoalLine: true) }
                if abs(fx - variant.goalPostRightX) < 2 { return FFZone(name: "\(side) goal post, right upright", terrain: .foul, isGoalLine: true) }
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
        let yd = fy - ezD      // 0..playLength from near goal line
        let fromNear = Int(yd.rounded())
        let yardLine = min(fromNear, Int(variant.playLength) - fromNear)
        let side = Double(fromNear) <= variant.playLength / 2 ? "near" : "far"
        let yardLabel = yardLine == variant.centerYard ? "\(variant.centerYard) yard line" : "\(side.capitalized) \(yardLine) yard line"

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
                let bandFY = Double(band) * 5.0
                // Louder landmark at every whole 10-yard line from the goal line.
                let is10 = (Int(bandFY) - Int(ezD)) % 10 == 0
                if is10 {
                    fieldAudio.playLandmark()
                } else {
                    UIImpactFeedbackGenerator(style: .soft).impactOccurred()
                }
                // Announce yard number (playing field only)
                if bandFY >= ezD && bandFY <= fL - ezD {
                    let yardNum = min(Int(bandFY) - Int(ezD), Int(fL - ezD) - Int(bandFY))
                    TouchTourAnnouncementService.shared.announce("\(yardNum)")
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
            TouchTourAnnouncementService.shared.announce(zone.name)
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
            Text(variant.statusSecondLine)
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

// MARK: - Info / Landing Page

struct FootballTourInfoView: View {
    private let variant: FootballFieldVariant
    @State private var showCanvas = false

    init(variant: FootballFieldVariant = .nfl) {
        self.variant = variant
    }

    var body: some View {
        List {
            Section("Dimensions") {
                LabeledContent("Length", value: variant.lengthLabel)
                LabeledContent("Width", value: "\(variant.widthLabel.replacingOccurrences(of: " yds", with: " yards"))")
                LabeledContent("End zones", value: variant.endZoneLabel)
            }
            Section("Key Lines") {
                LabeledContent("Goal lines", value: "\(Int(variant.endZoneDepth)) yards from each end")
                LabeledContent("Hash marks", value: variant.hashLabel)
                LabeledContent("Goal posts", value: variant.goalPostLabel)
                LabeledContent("Centre line", value: "\(variant.centerYard) yard line")
                LabeledContent("Yard lines", value: "Every 5 yards; numbered every 10")
            }
            Section("About the Audio Tour") {
                Text("Drag across the field to explore with audio. A chime sounds at every 5-yard line, louder at every 10-yard line. Audio texture changes in the end zones.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
        }
        .navigationTitle("\(variant.league) Field")
        .navigationDestination(isPresented: $showCanvas) {
            FootballFieldTourView(variant: variant)
        }
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    showCanvas = true
                } label: {
                    Label("Touch the Field", systemImage: "hand.tap.fill")
                }
                .accessibilityHint("Opens the interactive field for audio touch exploration")
            }
        }
    }
}

#Preview {
    NavigationStack { FootballFieldTourView(variant: .cfl) }
}
