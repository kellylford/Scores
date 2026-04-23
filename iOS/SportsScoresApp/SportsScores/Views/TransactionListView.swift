//
//  TransactionListView.swift
//  SportsScores
//
//  Paginated transaction list grouped by date, with a month/year jump picker.
//

import SwiftUI

struct TransactionListView: View {
    @StateObject private var viewModel: TransactionViewModel
    @State private var showingDatePicker = false
    @State private var pickerMonth: Int
    @State private var pickerYear: Int

    init(sport: Sport, team: TransactionTeam?) {
        let vm = TransactionViewModel(sport: sport, team: team)
        _viewModel = StateObject(wrappedValue: vm)
        _pickerMonth = State(initialValue: vm.selectedMonth)
        _pickerYear  = State(initialValue: vm.selectedYear)
    }

    var body: some View {
        VStack(spacing: 0) {
            // Month/year header bar
            dateHeaderBar

            Group {
                if viewModel.isLoading {
                    loadingView
                } else if let error = viewModel.errorMessage {
                    errorView(error)
                } else if viewModel.noDataForSport {
                    emptyView("No transactions are available for \(viewModel.sport.displayName).")
                } else if viewModel.transactions.isEmpty {
                    emptyView("No transactions found for \(viewModel.monthYearLabel).")
                } else {
                    transactionList
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .navigationTitle(viewModel.listTitle)
        .navigationBarTitleDisplayMode(.inline)
        .task { await viewModel.loadTransactions() }
        .sheet(isPresented: $showingDatePicker) {
            datePickerSheet
        }
    }

    // MARK: - Date header bar

    private var dateHeaderBar: some View {
        HStack {
            // Prev month button
            Button {
                Task {
                    var m = viewModel.selectedMonth - 1
                    var y = viewModel.selectedYear
                    if m < 1 { m = 12; y -= 1 }
                    await viewModel.jumpToMonthYear(month: m, year: y)
                    pickerMonth = viewModel.selectedMonth
                    pickerYear  = viewModel.selectedYear
                }
            } label: {
                Image(systemName: "chevron.left")
                    .font(.headline)
                    .padding(.horizontal, 8)
            }
            .disabled(viewModel.selectedYear <= TransactionViewModel.earliestYear && viewModel.selectedMonth <= 1)
            .accessibilityLabel("Previous month")

            Spacer()

            Button {
                pickerMonth = viewModel.selectedMonth
                pickerYear  = viewModel.selectedYear
                showingDatePicker = true
            } label: {
                HStack(spacing: 4) {
                    Text(viewModel.monthYearLabel)
                        .font(.subheadline.weight(.semibold))
                    Image(systemName: "calendar")
                        .font(.subheadline)
                }
            }
            .accessibilityLabel("Jump to month. Currently \(viewModel.monthYearLabel)")

            Spacer()

            // Next month button
            Button {
                Task {
                    var m = viewModel.selectedMonth + 1
                    var y = viewModel.selectedYear
                    if m > 12 { m = 1; y += 1 }
                    let now = Date()
                    let curYear  = Calendar.current.component(.year,  from: now)
                    let curMonth = Calendar.current.component(.month, from: now)
                    guard y < curYear || (y == curYear && m <= curMonth) else { return }
                    await viewModel.jumpToMonthYear(month: m, year: y)
                    pickerMonth = viewModel.selectedMonth
                    pickerYear  = viewModel.selectedYear
                }
            } label: {
                Image(systemName: "chevron.right")
                    .font(.headline)
                    .padding(.horizontal, 8)
            }
            .disabled({
                let now = Date()
                let curYear  = Calendar.current.component(.year,  from: now)
                let curMonth = Calendar.current.component(.month, from: now)
                return viewModel.selectedYear >= curYear && viewModel.selectedMonth >= curMonth
            }())
            .accessibilityLabel("Next month")
        }
        .padding(.vertical, 10)
        .padding(.horizontal)
        .background(Color(.systemGroupedBackground))
    }

    // MARK: - Transaction list

    private var transactionList: some View {
        List {
            ForEach(viewModel.groupedTransactions, id: \.date) { group in
                Section(group.date) {
                    ForEach(group.items) { item in
                        transactionRow(item)
                    }
                }
            }

            // Page navigation (all-sport view only)
            if viewModel.isPaginated && viewModel.pageCount > 1 {
                Section {
                    HStack {
                        Button {
                            Task { await viewModel.previousPage() }
                        } label: {
                            Label("Previous", systemImage: "chevron.left")
                        }
                        .disabled(viewModel.currentPage <= 1)

                        Spacer()

                        Text("Page \(viewModel.currentPage) of \(viewModel.pageCount)")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        Spacer()

                        Button {
                            Task { await viewModel.nextPage() }
                        } label: {
                            Label("Next", systemImage: "chevron.right")
                                .labelStyle(.titleAndIcon)
                        }
                        .disabled(viewModel.currentPage >= viewModel.pageCount)
                    }
                }
            }
        }
        .listStyle(.insetGrouped)
    }

    // MARK: - Transaction row

    @ViewBuilder
    private func transactionRow(_ item: TransactionItem) -> some View {
        HStack(alignment: .top, spacing: 10) {
            // Team abbreviation badge
            Text(item.team.abbreviation)
                .font(.caption.weight(.bold))
                .foregroundColor(.white)
                .padding(.horizontal, 5)
                .padding(.vertical, 3)
                .background(colorFromHex(item.team.color))
                .cornerRadius(4)
                .fixedSize()

            Text(item.description)
                .font(.body)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(.vertical, 2)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(item.team.displayName): \(item.description)")
    }

    // MARK: - State views

    private var loadingView: some View {
        VStack {
            Spacer()
            ProgressView("Loading transactions…")
            Spacer()
        }
        .accessibilityLabel("Loading transactions")
    }

    private func errorView(_ message: String) -> some View {
        VStack(spacing: 12) {
            Spacer()
            Image(systemName: "exclamationmark.triangle")
                .font(.largeTitle)
                .foregroundColor(.secondary)
            Text(message)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding()
            Button("Try Again") {
                Task { await viewModel.loadTransactions() }
            }
            Spacer()
        }
    }

    private func emptyView(_ message: String) -> some View {
        VStack {
            Spacer()
            Text(message)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding()
            Spacer()
        }
    }

    // MARK: - Month/Year picker sheet

    private var datePickerSheet: some View {
        NavigationStack {
            Form {
                Picker("Month", selection: $pickerMonth) {
                    ForEach(1...12, id: \.self) { month in
                        Text(monthName(month)).tag(month)
                    }
                }

                Picker("Year", selection: $pickerYear) {
                    ForEach(Array(stride(from: currentYear(), through: TransactionViewModel.earliestYear, by: -1)), id: \.self) { year in
                        Text(String(year)).tag(year)
                    }
                }
            }
            .navigationTitle("Jump To")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Go") {
                        showingDatePicker = false
                        Task { await viewModel.jumpToMonthYear(month: pickerMonth, year: pickerYear) }
                    }
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { showingDatePicker = false }
                }
            }
        }
        .presentationDetents([.medium])
    }

    // MARK: - Helpers

    private func colorFromHex(_ hex: String?) -> Color {
        guard let hex = hex, hex.count == 6,
              let value = UInt64(hex, radix: 16) else {
            return Color.secondary
        }
        let r = Double((value >> 16) & 0xFF) / 255
        let g = Double((value >> 8)  & 0xFF) / 255
        let b = Double( value        & 0xFF) / 255
        return Color(red: r, green: g, blue: b)
    }

    private func monthName(_ month: Int) -> String {
        let df = DateFormatter()
        df.locale = Locale(identifier: "en_US_POSIX")
        return df.monthSymbols[month - 1]
    }

    private func currentYear() -> Int {
        Calendar.current.component(.year, from: Date())
    }
}

#Preview {
    NavigationStack { TransactionListView(sport: .mlb, team: nil) }
}
