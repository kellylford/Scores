//
//  HomeViewModel.swift
//  SportsScores
//

import Foundation

@MainActor
final class HomeViewModel: ObservableObject {
    @Published var gameCounts: [Sport: Int] = [:]
    @Published var isLoading = true
    @Published var selectedDate: Date = Calendar.current.startOfDay(for: Date())

    private let api = ESPNAPIService.shared

    func load() async {
        isLoading = true

        await withTaskGroup(of: (Sport, Int).self) { group in
            for sport in Sport.allCases {
                group.addTask {
                    let count = (try? await self.api.fetchGames(for: sport, date: self.selectedDate))
                        .map { $0.count } ?? 0
                    return (sport, count)
                }
            }
            for await (sport, count) in group {
                gameCounts[sport] = count
            }
        }
        isLoading = false
    }

    // Navigation window: today ± 7 days
    private var navigationWindowStart: Date {
        let today = Calendar.current.startOfDay(for: Date())
        return Calendar.current.date(byAdding: .day, value: -7, to: today) ?? today
    }

    private var navigationWindowEnd: Date {
        let today = Calendar.current.startOfDay(for: Date())
        return Calendar.current.date(byAdding: .day, value: 7, to: today) ?? today
    }

    var canNavigateBackward: Bool {
        selectedDate > navigationWindowStart
    }

    var canNavigateForward: Bool {
        selectedDate < navigationWindowEnd
    }

    func goBack() async {
        let prevDate = Calendar.current.date(byAdding: .day, value: -1, to: selectedDate) ?? selectedDate
        selectedDate = max(prevDate, navigationWindowStart)
        await load()
    }

    func goForward() async {
        let nextDate = Calendar.current.date(byAdding: .day, value: 1, to: selectedDate) ?? selectedDate
        selectedDate = min(nextDate, navigationWindowEnd)
        await load()
    }

    func goToToday() async {
        selectedDate = Calendar.current.startOfDay(for: Date())
        await load()
    }
}
