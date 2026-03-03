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

    init(selectedDate: Date, onDateSelected: @escaping (Date) -> Void) {
        self.selectedDate    = selectedDate
        self.onDateSelected  = onDateSelected
        self._pickedDate     = State(initialValue: selectedDate)
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                DatePicker(
                    "Select Date",
                    selection: $pickedDate,
                    in: ...Calendar.current.date(byAdding: .day, value: 7, to: Date())!,
                    displayedComponents: .date
                )
                .datePickerStyle(.graphical)
                .padding(.horizontal)
                .accessibilityLabel("Date picker")

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
            }
        }
        .presentationDetents([.medium])
        .presentationDragIndicator(.visible)
    }

    private func formattedDate(_ date: Date) -> String {
        let fmt = DateFormatter()
        fmt.dateFormat = "EEE, MMM d"
        return fmt.string(from: date)
    }
}

#Preview {
    DatePickerView(selectedDate: Date()) { _ in }
}
