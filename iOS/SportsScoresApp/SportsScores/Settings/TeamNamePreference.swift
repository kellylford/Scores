//
//  TeamNamePreference.swift
//  SportsScores
//
//  Controls how team names are announced in VoiceOver labels.
//  Visual display always uses abbreviations; this preference
//  affects only the accessibility label text.
//

import Foundation

/// The four ways VoiceOver can announce a team name.
///
/// The user chooses one in Settings. The choice is applied uniformly
/// across all sports and all screen contexts that have a VoiceOver label.
enum TeamNamePreference: String, CaseIterable, Identifiable {
    /// Full city + mascot / school + nickname: "Milwaukee Brewers", "Wisconsin Badgers"
    case full         = "full"
    /// Mascot or nickname only: "Brewers", "Badgers"
    case mascot       = "mascot"
    /// City or school name only: "Milwaukee", "Wisconsin"
    case city         = "city"
    /// Short abbreviation: "MIL", "WIS"
    case abbreviation = "abbreviation"

    var id: String { rawValue }

    /// Display label shown in the Settings picker.
    var settingsLabel: String {
        switch self {
        case .full:         return "Full Name"
        case .mascot:       return "Mascot / Nickname"
        case .city:         return "City / School"
        case .abbreviation: return "Abbreviation"
        }
    }

    /// A concrete example using the Milwaukee Brewers so users can hear the difference.
    var exampleText: String {
        switch self {
        case .full:         return "Milwaukee Brewers"
        case .mascot:       return "Brewers"
        case .city:         return "Milwaukee"
        case .abbreviation: return "MIL"
        }
    }

    /// The description shown beneath each option in Settings.
    var settingsDescription: String {
        switch self {
        case .full:         return "VoiceOver says the full city and team name."
        case .mascot:       return "VoiceOver says the mascot or nickname only."
        case .city:         return "VoiceOver says the city or school name only."
        case .abbreviation: return "VoiceOver uses the short abbreviation."
        }
    }
}
