//
//  DatePickerView.swift
//  SportsScores
//
//  A sheet that lets the user pick a calendar date for scores browsing.
//  Uses separate Picker controls for year, month, and day for better VoiceOver accessibility.
//

import SwiftUI

struct DatePickerView: View {
    @Environment(\.dismiss) private var dismiss

    let selectedDate: Date
    let onDateSelected: (Date) -> Void

    @State private var selectedYear: Int
    @State private var selectedMonth: Int
    @State private var selectedDay: Int

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
        
        let cal = Calendar.current
        self._selectedYear = State(initialValue: cal.component(.year, from: selectedDate))
        self._selectedMonth = State(initialValue: cal.component(.month, from: selectedDate))
        self._selectedDay = State(initialValue: cal.component(.day, from: selectedDate))
    }

    private var availableYears: [Int] {
        let currentYear = Calendar.current.component(.year, from: Date())
        return Array(Self.earliestYear...currentYear)
    }
    
    private var availableMonths: [Int] {
        Array(1...12)
    }
    
    private var availableDays: [Int] {
        let daysInMonth = Calendar.current.range(of: .day, in: .month, for: constructedDate ?? Date())?.count ?? 31
        return Array(1...daysInMonth)
    }
    
    private var constructedDate: Date? {
        Calendar.current.date(from: DateComponents(year: selectedYear, month: selectedMonth, day: selectedDay))
    }
    
    private var isDateValid: Bool {
        constructedDate != nil
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                
                Text("Select Date")
                    .font(.headline)
                    .padding(.top)
                
                // ── Date Component Pickers ─────────────────────────────────────
                VStack(spacing: 20) {
                    // Year Picker
                    HStack {
                        Text("Year:")
                            .font(.body)
                            .frame(width: 80, alignment: .leading)
                        
                        Picker("Year", selection: $selectedYear) {
                            ForEach(availableYears.reversed(), id: \.self) { year in
                                Text(String(year)).tag(year)
                            }
                        }
                        .pickerStyle(.wheel)
                        .frame(maxWidth: .infinity)
                        .accessibilityLabel("Select year")
                        .accessibilityValue(String(selectedYear))
                    }
                    .frame(height: 100)
                    
                    // Month Picker
                    HStack {
                        Text("Month:")
                            .font(.body)
                            .frame(width: 80, alignment: .leading)
                        
                        Picker("Month", selection: $selectedMonth) {
                            ForEach(availableMonths, id: \.self) { month in
                                Text(monthName(month)).tag(month)
                            }
                        }
                        .pickerStyle(.wheel)
                        .frame(maxWidth: .infinity)
                            .accessibilityLabel("Select month")
                        .accessibilityValue(monthName(selectedMonth))
                        .onChange(of: selectedMonth) { _, _ in
                            // Adjust day if it exceeds the new month's maximum
                            adjustDayIfNeeded()
                        }
                    }
                    .frame(height: 100)
                    
                    // Day Picker
                    HStack {
                        Text("Day:")
                            .font(.body)
                            .frame(width: 80, alignment: .leading)
                        
                        Picker("Day", selection: $selectedDay) {
                            ForEach(availableDays, id: \.self) { day in
                                Text(String(day)).tag(day)
                            }
                        }
                        .pickerStyle(.wheel)
                        .frame(maxWidth: .infinity)
                        .accessibilityLabel("Select day")
                        .accessibilityValue(String(selectedDay))
                    }
                    .frame(height: 100)
                }
                .padding(.horizontal)
                
                // Selected date display
                if let date = constructedDate {
                    Text(formattedDate(date))
                        .font(.title3)
                        .foregroundColor(.secondary)
                        .padding(.top, 8)
                        .accessibilityLabel("Selected date: \(formattedDate(date))")
                }

                Button {
                    if let date = constructedDate {
                        onDateSelected(date)
                        dismiss()
                    }
                } label: {
                    Label("Go to Date", systemImage: "arrow.right.circle.fill")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(isDateValid ? Color.accentColor : Color.gray)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
                .disabled(!isDateValid)
                .padding(.horizontal)
                .accessibilityLabel(isDateValid ? "Go to selected date" : "Invalid date selected")

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
                    Button("Today") { jumpToToday() }
                }
            }
        }
        .presentationDetents([.large])
        .presentationDragIndicator(.visible)
    }

    // MARK: - Helpers
    
    private func monthName(_ month: Int) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMMM"
        guard let date = Calendar.current.date(from: DateComponents(year: 2000, month: month, day: 1)) else {
            return String(month)
        }
        return formatter.string(from: date)
    }
    
    private func adjustDayIfNeeded() {
        let maxDays = availableDays.count
        if selectedDay > maxDays {
            selectedDay = maxDays
        }
    }

    private func jumpToToday() {
        let cal = Calendar.current
        let today = Date()
        selectedYear = cal.component(.year, from: today)
        selectedMonth = cal.component(.month, from: today)
        selectedDay = cal.component(.day, from: today)
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
