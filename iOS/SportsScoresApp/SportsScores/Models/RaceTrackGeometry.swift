//
//  RaceTrackGeometry.swift
//  SportsScores
//
//  Geometry and zone detection for oval race tracks.
//
//  Coordinate system (feet, origin = center of oval)
//    x+ = right (Turn 1-2 side)
//    x- = left  (Turn 3-4 side)
//    y+ = backstretch (top of canvas)
//    y- = frontstretch / start-finish (bottom of canvas)
//
//  The oval is modelled as two concentric ellipses:
//    outer ellipse: (x/semiMinor)² + (y/semiMajor)² = 1   (outer wall)
//    inner ellipse: (x/innerSemiMinor)² + (y/innerSemiMajor)² = 1 (inner wall)
//  The racing surface lies between them.
//

import Foundation

// MARK: - Zone result

struct TrackZone {
    let name: String
    let terrain: FieldTerrain
    var isLandmark: Bool = false
    var detail: String = ""
}

// MARK: - Track geometry

struct RaceTrackGeometry: Identifiable, Equatable, Hashable {

    let id: String
    let name: String          // "Daytona International Speedway"
    let shortName: String     // "Daytona"
    let location: String      // "Daytona Beach, Florida"
    let series: String        // "NASCAR", "IndyCar", "NASCAR · IndyCar"

    // Oval half-axes in feet (from center of oval)
    let semiMajor: Double     // frontstretch–backstretch direction
    let semiMinor: Double     // turn-to-turn direction
    let trackWidth: Double    // racing surface width in feet

    // Track characteristics (for display and status bar)
    let lengthMiles: Double
    let turnBankingDeg: Int
    let straightBankingDeg: Int
    let yearOpened: Int
    let capacity: Int
    let notableFeatures: [String]

    // MARK: - Derived geometry

    var innerSemiMajor: Double { max(semiMajor - trackWidth, 1) }
    var innerSemiMinor: Double { max(semiMinor - trackWidth, 1) }

    // MARK: - Zone detection

    func detectZone(x: Double, y: Double) -> TrackZone {
        // Ellipse distance from center, normalised so 1.0 = exactly on that wall.
        let dOuter = sqrt(pow(x / semiMinor, 2) + pow(y / semiMajor, 2))
        let dInner = sqrt(pow(x / innerSemiMinor, 2) + pow(y / innerSemiMajor, 2))

        // Beyond outer wall
        if dOuter > 1.05 { return TrackZone(name: "Outside the track", terrain: .silent) }

        // Outer wall concrete (between the outer ellipse and 5% beyond)
        if dOuter >= 1.0 {
            return TrackZone(name: "Outer wall — \(sectionName(x: x, y: y))", terrain: .foul)
        }

        // Infield (inside the inner wall ellipse)
        if dInner <= 1.0 {
            let nx = x / semiMinor
            let ny = y / semiMajor
            let theta = atan2(nx, -ny) * 180.0 / .pi
            if abs(theta) < 50 && dInner > 0.45 {
                return TrackZone(name: "Pit road", terrain: .warningTrack, isLandmark: true,
                                 detail: "Cars stop here for tires, fuel, and repairs")
            }
            return infieldZone(theta: theta, dInner: dInner)
        }

        // Racing surface (dOuter < 1.0 AND dInner > 1.0) — the actual track
        return racingSurfaceZone(x: x, y: y, dOuter: dOuter, dInner: dInner)
    }

    // MARK: - Private zone helpers

    private func infieldZone(theta: Double, dInner: Double) -> TrackZone {
        // Very center of oval
        if dInner < 0.35 {
            return TrackZone(name: "Infield center", terrain: .foul,
                             detail: "Center of the oval, well inside the racing surface")
        }
        // Near frontstretch but inside pit road zone
        if abs(theta) < 50 {
            return TrackZone(name: "Infield — frontstretch end", terrain: .foul,
                             detail: "Near start/finish line, inside the pit wall")
        }
        // Backstretch side
        if abs(theta) > 130 {
            return TrackZone(name: "Infield — backstretch", terrain: .foul,
                             detail: "Inside the backstretch, opposite start/finish")
        }
        // Turn 1-2 side (theta positive = right side of canvas)
        if theta > 0 {
            return TrackZone(name: "Infield — Turn 1 and 2 side", terrain: .foul,
                             detail: "Infield alongside Turns 1 and 2")
        }
        return TrackZone(name: "Infield — Turn 3 and 4 side", terrain: .foul,
                         detail: "Infield alongside Turns 3 and 4")
    }

    // Fractional position across track width: 0.0 = at inner wall, 1.0 = at outer wall.
    private func groovePosition(dOuter: Double, dInner: Double) -> String {
        let span = dInner - dOuter
        guard span > 0.001 else { return "mid" }
        let frac = (dInner - 1.0) / span   // 0 = inner side, 1 = outer side
        if frac > 0.70 { return "high" }
        if frac < 0.30 { return "low" }
        return "mid"
    }

    private func racingSurfaceZone(x: Double, y: Double, dOuter: Double, dInner: Double) -> TrackZone {
        let nx = x / semiMinor
        let ny = y / semiMajor
        let theta = atan2(nx, -ny) * 180.0 / .pi   // 0° = frontstretch, ±90° = sides
        let pos = groovePosition(dOuter: dOuter, dInner: dInner)

        // Start/Finish line: narrow angle band across the full track width
        if abs(theta) < 6 {
            return TrackZone(name: "Start/Finish line", terrain: .fair, isLandmark: true,
                             detail: "Timing line — where each lap begins and ends")
        }

        switch theta {
        case -35..<35:
            return TrackZone(name: "Frontstretch — \(pos)", terrain: .fair,
                             detail: "Main straight — start/finish area, \(straightBankingDeg)° banking")

        case 35..<90:
            return TrackZone(name: "Turn 1 — \(pos) — \(turnBankingDeg)° banking", terrain: .fair,
                             isLandmark: abs(theta - 62) < 12,
                             detail: "First left turn exiting the frontstretch, \(turnBankingDeg)° banking")

        case 90..<145:
            return TrackZone(name: "Turn 2 — \(pos) — \(turnBankingDeg)° banking", terrain: .fair,
                             isLandmark: abs(theta - 117) < 12,
                             detail: "Second left turn entering the backstretch, \(turnBankingDeg)° banking")

        case 145...180, -180 ..< -145:
            return TrackZone(name: "Backstretch — \(pos)", terrain: .fair,
                             detail: "Back straight opposite start/finish, \(straightBankingDeg)° banking")

        case -145 ..< -90:
            return TrackZone(name: "Turn 3 — \(pos) — \(turnBankingDeg)° banking", terrain: .fair,
                             isLandmark: abs(theta + 117) < 12,
                             detail: "Third left turn exiting the backstretch, \(turnBankingDeg)° banking")

        case -90 ..< -35:
            return TrackZone(name: "Turn 4 — \(pos) — \(turnBankingDeg)° banking", terrain: .fair,
                             isLandmark: abs(theta + 62) < 12,
                             detail: "Fourth left turn returning to the frontstretch, \(turnBankingDeg)° banking")

        default:
            return TrackZone(name: "Racing surface", terrain: .fair,
                             detail: "On the racing surface")
        }
    }

    private func sectionName(x: Double, y: Double) -> String {
        let nx = x / semiMinor
        let ny = y / semiMajor
        let theta = atan2(nx, -ny) * 180.0 / .pi
        switch theta {
        case -35..<35:      return "frontstretch"
        case 35..<145:      return "Turn 1-2"
        case -145 ..< -35:  return "Turn 3-4"
        default:            return "backstretch"
        }
    }
}

// MARK: - Static track list

extension RaceTrackGeometry {

    // All five major oval tracks included in the touch tour.
    static let all: [RaceTrackGeometry] = [
        .indianapolisMotorSpeedway,
        .daytonaInternationalSpeedway,
        .talladegaSuperspeedway,
        .bristolMotorSpeedway,
        .charlotteMotorSpeedway,
    ]

    // MARK: Indianapolis Motor Speedway

    static let indianapolisMotorSpeedway = RaceTrackGeometry(
        id: "ims",
        name: "Indianapolis Motor Speedway",
        shortName: "Indianapolis",
        location: "Speedway, Indiana",
        series: "IndyCar · NASCAR",
        semiMajor: 2_200,
        semiMinor: 920,
        trackWidth: 50,
        lengthMiles: 2.500,
        turnBankingDeg: 9,
        straightBankingDeg: 0,
        yearOpened: 1909,
        capacity: 257_325,
        notableFeatures: [
            "Yard of Bricks — original brick surface at Start/Finish line",
            "Host of the Indianapolis 500 since 1911",
            "9° banking in turns — flat compared to most superspeedways",
            "Rectangular layout with short chutes connecting turns to long straights",
        ]
    )

    // MARK: Daytona International Speedway

    static let daytonaInternationalSpeedway = RaceTrackGeometry(
        id: "daytona",
        name: "Daytona International Speedway",
        shortName: "Daytona",
        location: "Daytona Beach, Florida",
        series: "NASCAR",
        semiMajor: 1_750,
        semiMinor: 1_050,
        trackWidth: 60,
        lengthMiles: 2.500,
        turnBankingDeg: 31,
        straightBankingDeg: 3,
        yearOpened: 1959,
        capacity: 101_500,
        notableFeatures: [
            "Tri-oval shape — unique slight bend in the frontstretch",
            "31° banking in turns — cars can hold wide-open throttle",
            "Host of the Daytona 500, NASCAR's most prestigious race",
            "Lake Lloyd occupies much of the infield",
        ]
    )

    // MARK: Talladega Superspeedway

    static let talladegaSuperspeedway = RaceTrackGeometry(
        id: "talladega",
        name: "Talladega Superspeedway",
        shortName: "Talladega",
        location: "Lincoln, Alabama",
        series: "NASCAR",
        semiMajor: 1_950,
        semiMinor: 1_050,
        trackWidth: 65,
        lengthMiles: 2.660,
        turnBankingDeg: 33,
        straightBankingDeg: 2,
        yearOpened: 1969,
        capacity: 78_000,
        notableFeatures: [
            "Longest oval on the NASCAR Cup circuit at 2.66 miles",
            "33° banking — highest of any NASCAR superspeedway",
            "Wide 65-foot racing surface enables five-wide racing",
            "Restrictor plates required to limit speeds",
        ]
    )

    // MARK: Bristol Motor Speedway

    static let bristolMotorSpeedway = RaceTrackGeometry(
        id: "bristol",
        name: "Bristol Motor Speedway",
        shortName: "Bristol",
        location: "Bristol, Tennessee",
        series: "NASCAR",
        semiMajor: 475,
        semiMinor: 415,
        trackWidth: 45,
        lengthMiles: 0.533,
        turnBankingDeg: 28,
        straightBankingDeg: 6,
        yearOpened: 1961,
        capacity: 162_000,
        notableFeatures: [
            "Thunder Valley — one of NASCAR's most iconic short tracks",
            "Concrete surface (not asphalt)",
            "Near-circular shape — only 530 feet from turn to turn",
            "28° banking in turns — unusually steep for a short track",
        ]
    )

    // MARK: Charlotte Motor Speedway

    static let charlotteMotorSpeedway = RaceTrackGeometry(
        id: "charlotte",
        name: "Charlotte Motor Speedway",
        shortName: "Charlotte",
        location: "Concord, North Carolina",
        series: "NASCAR",
        semiMajor: 1_100,
        semiMinor: 760,
        trackWidth: 55,
        lengthMiles: 1.500,
        turnBankingDeg: 24,
        straightBankingDeg: 5,
        yearOpened: 1960,
        capacity: 89_000,
        notableFeatures: [
            "Quad-oval configuration — slight dogleg in the frontstretch",
            "Host of the Coca-Cola 600, NASCAR's longest race",
            "NASCAR's most-visited track — home to many teams' headquarters",
            "All-Star Race held here annually",
        ]
    )
}
