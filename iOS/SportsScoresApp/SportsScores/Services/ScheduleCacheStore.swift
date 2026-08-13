//
//  ScheduleCacheStore.swift
//  SportsScores
//
//  Caches football season calendars and week date ranges.
//
//  An actor for the same reason as `TeamStatsStore`: these are read and written
//  from `ESPNAPIService`'s non-isolated async methods, whose continuations
//  resume on whatever thread is free. Concurrent scoreboard and week-navigation
//  fetches were mutating plain dictionaries at the same time, which corrupts
//  memory rather than merely losing a cache entry.
//

import Foundation

actor ScheduleCacheStore {

    /// A week's date span and display label, from ESPN's calendar.
    struct WeekRange {
        let start: Date
        let end: Date
        let text: String
    }

    /// Keyed by "{SportRawValue}-{season}"
    private var calendars: [String: SeasonCalendar] = [:]
    /// Keyed by "{SportRawValue}-{season}-{seasonType}-{week}"
    private var weekRanges: [String: WeekRange] = [:]

    // MARK: - Season calendars

    func calendar(forKey key: String) -> SeasonCalendar? {
        calendars[key]
    }

    func store(_ calendar: SeasonCalendar, forKey key: String) {
        calendars[key] = calendar
    }

    // MARK: - Week ranges

    func weekRange(forKey key: String) -> WeekRange? {
        weekRanges[key]
    }

    func store(_ range: WeekRange, forKey key: String) {
        weekRanges[key] = range
    }

    /// Seeds every week range carried by a calendar in one hop, so week
    /// navigation inside the live season needs no further Core API round-trips.
    func storeWeekRanges(from calendar: SeasonCalendar) {
        for typeInfo in calendar.seasonTypes {
            for week in typeInfo.weeks {
                let key = "\(calendar.sport.rawValue)-\(calendar.season)-\(typeInfo.type)-\(week.number)"
                weekRanges[key] = WeekRange(start: week.startDate, end: week.endDate, text: week.label)
            }
        }
    }
}
