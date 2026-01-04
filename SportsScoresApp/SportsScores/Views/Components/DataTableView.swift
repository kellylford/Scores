//
//  DataTableView.swift
//  SportsScores
//
//  Created on 1/4/26.
//
//  Revolutionary three-view-mode table component
//  Supports: Table View, Quick List, Full List

import SwiftUI

struct DataTableView: View {
    let headers: [String]
    let rows: [[String]]
    @State private var viewMode: ViewMode = .table
    
    var body: some View {
        VStack(spacing: 0) {
            // View Mode Picker
            ViewModePicker(selectedMode: $viewMode)
                .padding(.vertical, 8)
            
            Divider()
            
            // Content based on view mode
            ScrollView {
                switch viewMode {
                case .table:
                    tableView
                case .quickList:
                    quickListView
                case .fullList:
                    fullListView
                }
            }
        }
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                ViewModeToggleButton(currentMode: $viewMode)
            }
        }
    }
    
    // MARK: - Table View
    private var tableView: some View {
        VStack(spacing: 0) {
            // Header Row
            HStack(spacing: 0) {
                ForEach(headers, id: \.self) { header in
                    Text(header)
                        .font(.caption)
                        .fontWeight(.bold)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(Color.secondary.opacity(0.2))
                }
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Table headers: \(headers.joined(separator: ", "))")
            
            Divider()
            
            // Data Rows
            ForEach(Array(rows.enumerated()), id: \.offset) { index, row in
                HStack(spacing: 0) {
                    ForEach(Array(row.enumerated()), id: \.offset) { colIndex, value in
                        Text(value)
                            .font(.caption)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 8)
                            .background(index % 2 == 0 ? Color.clear : Color.secondary.opacity(0.05))
                            .accessibilityLabel("\(headers[colIndex]): \(value)")
                    }
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel(createAccessibilityLabel(for: row, at: index))
                
                if index < rows.count - 1 {
                    Divider()
                }
            }
        }
    }
    
    // MARK: - Quick List View
    private var quickListView: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(Array(rows.enumerated()), id: \.offset) { index, row in
                VStack(alignment: .leading, spacing: 4) {
                    Text(row.joined(separator: ", "))
                        .font(.body)
                        .padding(.vertical, 8)
                        .padding(.horizontal, 12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(index % 2 == 0 ? Color.clear : Color.secondary.opacity(0.05))
                        .cornerRadius(6)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Row \(index + 1): \(row.joined(separator: ", "))")
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
    
    // MARK: - Full List View
    private var fullListView: some View {
        VStack(alignment: .leading, spacing: 16) {
            ForEach(Array(rows.enumerated()), id: \.offset) { index, row in
                VStack(alignment: .leading, spacing: 6) {
                    Text("Item \(index + 1)")
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    ForEach(Array(row.enumerated()), id: \.offset) { colIndex, value in
                        HStack(alignment: .top) {
                            Text("\(headers[colIndex]):")
                                .font(.caption)
                                .fontWeight(.semibold)
                                .foregroundColor(.secondary)
                                .frame(width: 100, alignment: .leading)
                            
                            Text(value)
                                .font(.caption)
                                .foregroundColor(.primary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                }
                .padding(12)
                .background(Color.secondary.opacity(0.05))
                .cornerRadius(8)
                .accessibilityElement(children: .combine)
                .accessibilityLabel(createFullAccessibilityLabel(for: row, at: index))
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
    
    // MARK: - Accessibility Helpers
    private func createAccessibilityLabel(for row: [String], at index: Int) -> String {
        let pairs = zip(headers, row).map { "\($0): \($1)" }
        return "Row \(index + 1). " + pairs.joined(separator: "; ")
    }
    
    private func createFullAccessibilityLabel(for row: [String], at index: Int) -> String {
        let pairs = zip(headers, row).map { "\($0): \($1)" }
        return "Item \(index + 1). " + pairs.joined(separator: "; ")
    }
}

// MARK: - Standings-Specific Table View
struct StandingsTableView: View {
    let standingsGroups: [StandingsGroup]
    @State private var viewMode: ViewMode = .table
    
    let headers = ["Rank", "Team", "Wins", "Losses", "Win%", "GB", "Streak", "Record"]
    
    var body: some View {
        VStack(spacing: 0) {
            ViewModePicker(selectedMode: $viewMode)
                .padding(.vertical, 8)
            
            Divider()
            
            ScrollView {
                ForEach(standingsGroups) { group in
                    VStack(alignment: .leading, spacing: 8) {
                        Text(group.name)
                            .font(.headline)
                            .padding(.horizontal)
                            .padding(.top, 12)
                        
                        switch viewMode {
                        case .table:
                            tableView(for: group)
                        case .quickList:
                            quickListView(for: group)
                        case .fullList:
                            fullListView(for: group)
                        }
                    }
                    .padding(.bottom, 16)
                }
            }
        }
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                ViewModeToggleButton(currentMode: $viewMode)
            }
        }
    }
    
    private func tableView(for group: StandingsGroup) -> some View {
        DataTableView(
            headers: headers,
            rows: group.entries.map { $0.tableRow }
        )
    }
    
    private func quickListView(for group: StandingsGroup) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            ForEach(Array(group.entries.enumerated()), id: \.element.id) { index, entry in
                Text(entry.quickListText)
                    .font(.body)
                    .padding(.vertical, 8)
                    .padding(.horizontal, 12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(index % 2 == 0 ? Color.clear : Color.secondary.opacity(0.05))
                    .cornerRadius(6)
                    .accessibilityLabel("Team \(index + 1): \(entry.quickListText)")
            }
        }
        .padding(.horizontal)
    }
    
    private func fullListView(for group: StandingsGroup) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(group.entries) { entry in
                VStack(alignment: .leading, spacing: 6) {
                    Text(entry.team.displayName)
                        .font(.headline)
                    
                    Text(entry.fullListText)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(12)
                .background(Color.secondary.opacity(0.05))
                .cornerRadius(8)
                .accessibilityLabel(entry.fullListText)
            }
        }
        .padding(.horizontal)
    }
}

// MARK: - Preview
#Preview {
    NavigationView {
        DataTableView(
            headers: ["Rank", "Team", "W", "L"],
            rows: [
                ["1", "LAD", "95", "67"],
                ["2", "ARI", "84", "78"],
                ["3", "SD", "82", "80"]
            ]
        )
        .navigationTitle("Example Table")
    }
}
