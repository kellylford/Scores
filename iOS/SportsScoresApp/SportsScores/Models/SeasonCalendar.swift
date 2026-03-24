//
//  SeasonCalendar.swift
//  SportsScores
//
//  Lightweight model for a football season's week structure.
//  Populated from the ESPN Core API and used to power historical
//  week navigation (week bounds, season type switching) without
//  relying on the site scoreboard endpoint, which returns errors
//  when a `season=` param is appended to historical queries.
//

import Foundation

// MARK: - SeasonTypeInfo

/// One season-type bucket (preseason / regular / postseason) and the number of
/// weeks it contains for a given sport+season year.
struct SeasonTypeInfo: Identifiable, Equatable {
    /// ESPN season type code: 1 = preseason, 2 = regular, 3 = postseason.
    let type: Int
    /// Total number of weeks in this season type.
    let weekCount: Int

    var id: Int { type }

    /// Full label used in menus (e.g. "Preseason").
    var label: String {
        switch type {
        case 1: return "Preseason"
        case 2: return "Regular"
        case 3: return "Postseason"
        default: return "Type \(type)"
        }
    }

    /// Compact label used in the nav bar badge (e.g. "Pre").
    var shortLabel: String {
        switch type {
        case 1: return "Pre"
        case 2: return "Reg"
        case 3: return "Post"
        default: return "\(type)"
        }
    }
}

// MARK: - SeasonCalendar

/// The complete week-structure for a football sport + season year.
/// Contains all available season types and their respective week counts.
struct SeasonCalendar {
    let sport: Sport
    /// ESPN calendar year (e.g. 2022 for the 2022 NFL season).
    let season: Int
    /// All season types available for this season, sorted by type value (1 → 2 → 3).
    let seasonTypes: [SeasonTypeInfo]

    /// Convenience: the regular-season entry, if one exists.
    var regularSeason: SeasonTypeInfo? {
        seasonTypes.first { $0.type == 2 }
    }

    /// Number of weeks for the given season type; 0 if the type isn't present.
    func weekCount(for seasonType: Int) -> Int {
        seasonTypes.first { $0.type == seasonType }?.weekCount ?? 0
    }

    /// Whether the calendar contains data for the given season type.
    func hasSeasonType(_ type: Int) -> Bool {
        seasonTypes.contains { $0.type == type }
    }
}
