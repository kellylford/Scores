//
//  DatePickerView.swift
//  SportsScores
//
//  A sheet that lets the user pick a calendar date for scores browsing.
//  Uses SwiftUI's native DatePicker which is fully VoiceOver-compatible.
//

import SwiftUI

struct DatePickerView: View {
    @Environment(\.dismiss) private var dismiss

    let selectedDate: Date
    let onDateSelected: (Date) -> Void

    @State private var pickedDate: Date
    @State private var displayedYear: Int

    // ESPN has usable historical data from around 2000 onward.
    private static let earliestYear = 2000
    private static var earliestDate: Date {
        Calendar.current.date(from: DateComponents(year: earliestYear, month: 1, day: 1))!
    }
    private static var latestDate: Date {
        Calendar.current.date(byAdding: .day, value: 7, to: Date())!
    }

    init(selectedDate: Date, onDateSelected: @escaping (Date) -> Void) {
        self.selectedDate   = selectedDate
        self.onDateSelected = onDateSelected
        self._pickedDate    = State(initialValue: selectedDate)
        self._displayedYear = State(initialValue: Calendar.current.component(.year, from: selectedDate))
    }

    private var availableYears: [Int] {
        let currentYear = Calendar.current.component(.year, from: Date())
        return Array(Self.earliestYear...currentYear)
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {

                // ── Year stepper ─────────────────────────────────────────────
                HStack {
                    Button {
                        jumpYear(by: -1)
                    } label: {
                        Image(systemName: "chevron.left")
                            .font(.body.bold())
                            .frame(width: 44, height: 36)
                            .contentShape(Rectangle())
                    }
                    .disabled(displayedYear <= Self.earliestYear)
                    .accessibilityLabel("Previous year")

                    Spacer()

                    Menu {
                        ForEach(availableYears.reversed(), id: \.self) { year in
                            Button(String(year)) { jumpToYear(year) }
                        }
                    } label: {
                        HStack(spacing: 4) {
                            Text(String(displayedYear))
                                .font(.headline)
                            Image(systemName: "chevron.up.chevron.down")
                                .font(.caption)
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.secondary.opacity(0.12))
                        .cornerRadius(8)
                    }
                    .accessibilityLabel("Year: \(displayedYear). Tap to pick a different year.")

                    Spacer()

                    Button {
                        jumpYear(by: 1)
                    } label: {
                        Image(systemName: "chevron.right")
                            .font(.body.bold())
                            .frame(width: 44, height: 36)
                            .contentShape(Rectangle())
                    }
                    .disabled(displayedYear >= Calendar.current.component(.year, from: Date()))
                    .accessibilityLabel("Next year")
                }
                .padding(.horizontal)

                // ── Day picker — scoped to the displayed year ─────────────────
                DatePicker(
                    "Select Date",
                    selection: $pickedDate,
                    in: yearRange,
                    displayedComponents: .date
                )
                .datePickerStyle(.graphical)
                .padding(.horizontal)
                .accessibilityLabel("Date picker")
                .onChange(of: pickedDate) { _, newDate in
                    // Keep year stepper in sync if user swipes month across a year boundary
                    let y = Calendar.current.component(.year, from: newDate)
                    if y != displayedYear { displayedYear = y }
                }

                Button {
                    onDateSelected(pickedDate)
                    dismiss()
                } label: {
                    Label("Go to \(formattedDate(pickedDate))", systemImage: "arrow.right.circle.fill")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.accentColor)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
                .padding(.horizontal)

                Spacer()
            }
            .padding(.top)
            .navigationTitle("Choose Date")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Today") { jumpToDate(Date()) }
                        .disabled(Calendar.current.isDateInToday(pickedDate))
                }
            }
        }
        .presentationDetents([.large])
        .presentationDragIndicator(.visible)
    }

    // MARK: - Helpers

    /// ClosedRange for the DatePicker constrained to `displayedYear`.
    private var yearRange: ClosedRange<Date> {
        let cal = Calendar.current
        let currentYear = cal.component(.year, from: Date())
        let rawStart = cal.date(from: DateComponents(year: displayedYear, month: 1, day: 1))!
        let startOfYear = max(Self.earliestDate, min(Self.latestDate, rawStart))
        let endOfYear: Date
        if displayedYear == currentYear {
            endOfYear = Self.latestDate
        } else {
            endOfYear = cal.date(from: DateComponents(year: displayedYear, month: 12, day: 31))!
        }
        return startOfYear...endOfYear
    }

    private func jumpYear(by delta: Int) {
        jumpToYear(displayedYear + delta)
    }

    private func jumpToYear(_ year: Int) {
        let cal = Calendar.current
        let clamped = max(Self.earliestYear, min(cal.component(.year, from: Date()), year))
        displayedYear = clamped
        // Move pickedDate into the new year if it's currently in a different year
        let pickedYear = cal.component(.year, from: pickedDate)
        if pickedYear != clamped {
            var comps = cal.dateComponents([.month, .day], from: pickedDate)
            comps.year = clamped
            let fallback = cal.date(from: DateComponents(year: clamped, month: 1, day: 1))!
            pickedDate = cal.date(from: comps) ?? fallback
        }
    }

    private func jumpToDate(_ date: Date) {
        pickedDate = date
        displayedYear = Calendar.current.component(.year, from: date)
    }

    private func formattedDate(_ date: Date) -> String {
        let fmt = DateFormatter()
        fmt.dateFormat = "EEE, MMM d, yyyy"
        return fmt.string(from: date)
    }
}

#Preview {
    DatePickerView(selectedDate: Date()) { _ in }
}
