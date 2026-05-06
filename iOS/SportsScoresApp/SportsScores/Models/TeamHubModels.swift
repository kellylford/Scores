//
//  TeamHubModels.swift
//  SportsScores
//
//  Data models for the Team Hub feature.
//

import Foundation

// MARK: - Team Info (Info tab display model)

struct TeamHubTeamInfo {
    let teamId: String
    let displayName: String
    let abbreviation: String
    let location: String
    let color: String?           // hex without "#", e.g. "132448"
    let alternateColor: String?
    let primaryLogoURL: URL?
    let overallRecord: String?   // e.g. "25-11"
    let homeRecord: String?      // e.g. "13-5"
    let awayRecord: String?      // e.g. "12-6"
    let standingSummary: String? // e.g. "1st in AL East"
    let venueName: String?
    let venueCity: String?
    let coachName: String?
    let nextGame: TeamHubNextGame?
}

struct TeamHubNextGame {
    let gameId: String
    let date: Date
    let opponentDisplayName: String
    let opponentAbbreviation: String
    let isHome: Bool
}

// MARK: - Roster Player (Roster tab display model)

struct RosterPlayer: Identifiable {
    let id: String
    let jerseyNumber: String
    let displayName: String
    let positionAbbreviation: String
    let age: String
}

// MARK: - Decodable API Response: Team Info endpoint (/teams/{id})

struct TeamInfoAPIResponse: Decodable {
    let team: TeamInfoTeamData

    struct TeamInfoTeamData: Decodable {
        let id: String
        let location: String?
        let name: String?
        let abbreviation: String
        let displayName: String
        let color: String?
        let alternateColor: String?
        let logos: [TeamInfoLogo]?
        let record: TeamInfoRecord?
        let franchise: TeamInfoFranchise?
        let nextEvent: [TeamInfoNextEvent]?
        let standingSummary: String?
    }

    struct TeamInfoLogo: Decodable {
        let href: String
        let rel: [String]?
    }

    struct TeamInfoRecord: Decodable {
        let items: [TeamInfoRecordItem]?

        struct TeamInfoRecordItem: Decodable {
            let description: String?
            let summary: String?
        }
    }

    struct TeamInfoFranchise: Decodable {
        let venue: TeamInfoVenue?

        struct TeamInfoVenue: Decodable {
            let fullName: String?
            let address: TeamInfoAddress?

            struct TeamInfoAddress: Decodable {
                let city: String?
                let state: String?
            }
        }
    }

    struct TeamInfoNextEvent: Decodable {
        let id: String
        let date: String   // multi-format ISO8601 (may lack seconds)
        let competitions: [TeamInfoCompetition]?

        struct TeamInfoCompetition: Decodable {
            let competitors: [TeamInfoCompetitor]?

            struct TeamInfoCompetitor: Decodable {
                let homeAway: String?
                let team: TeamInfoCompetitorTeam?

                struct TeamInfoCompetitorTeam: Decodable {
                    let id: String?
                    let displayName: String?
                    let abbreviation: String?
                }
            }
        }
    }
}

// MARK: - Decodable API Response: Roster endpoint (/teams/{id}/roster)

struct RosterAPIResponse: Decodable {
    let athletes: [RosterPositionGroup]?
    let coach: [RosterCoach]?

    struct RosterPositionGroup: Decodable {
        let position: String?
        let items: [RosterAthlete]
    }

    struct RosterAthlete: Decodable {
        let id: String
        let displayName: String?
        let jersey: String?
        let age: Int?
        let position: RosterAthletePosition?
        let status: RosterAthleteStatus?

        struct RosterAthletePosition: Decodable {
            let abbreviation: String?
        }

        struct RosterAthleteStatus: Decodable {
            let name: String?
        }
    }

    struct RosterCoach: Decodable {
        let firstName: String?
        let lastName: String?
    }
}
