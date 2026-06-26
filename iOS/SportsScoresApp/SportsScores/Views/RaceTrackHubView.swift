//
//  RaceTrackHubView.swift
//  SportsScores
//
//  Track picker and info page for race track audio tours.
//  The user selects a track, reviews its details, then launches the touch canvas.
//  Follows the same pattern as BaseballTourInfoView.
//

import SwiftUI

struct RaceTrackHubView: View {

    @State private var selectedTrack: RaceTrackGeometry = RaceTrackGeometry.all[0]
    @State private var showCanvas = false

    var body: some View {
        List {
            // Track picker
            Section {
                Picker("Track", selection: $selectedTrack) {
                    ForEach(RaceTrackGeometry.all) { track in
                        Text(track.name).tag(track)
                    }
                }
                .accessibilityLabel("Select a track")
            } header: {
                Text("Select a Track")
            }

            // Series badge
            Section {
                LabeledContent("Series", value: selectedTrack.series)
                LabeledContent("Location", value: selectedTrack.location)
                LabeledContent("Opened", value: String(selectedTrack.yearOpened))
                LabeledContent("Capacity", value: selectedTrack.capacity.formatted())
            } header: {
                Text("Track Info")
            }

            // Dimensions
            Section {
                LabeledContent("Length", value: String(format: "%.3f miles", selectedTrack.lengthMiles))
                LabeledContent("Turn banking", value: "\(selectedTrack.turnBankingDeg)°")
                LabeledContent("Straight banking",
                               value: selectedTrack.straightBankingDeg == 0
                                      ? "Flat" : "\(selectedTrack.straightBankingDeg)°")
                LabeledContent("Track width", value: "\(Int(selectedTrack.trackWidth)) feet")
            } header: {
                Text("Dimensions")
            }

            // Notable features
            if !selectedTrack.notableFeatures.isEmpty {
                Section {
                    ForEach(selectedTrack.notableFeatures, id: \.self) { feature in
                        Text(feature)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                } header: {
                    Text("Notable Features")
                }
            }

            // About the tour
            Section {
                Text("Drag across the track to explore with audio. " +
                     "Haptic feedback marks zone boundaries — turns, frontstretch, backstretch, pit road, and the start/finish line. " +
                     "High and low positions on the track reflect the banking angle.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            } header: {
                Text("About the Tour")
            }
        }
        .navigationTitle("Race Tracks")
        .navigationDestination(isPresented: $showCanvas) {
            RaceTrackTourView(track: selectedTrack)
        }
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    showCanvas = true
                } label: {
                    Label("Touch the Track", systemImage: "hand.tap.fill")
                }
                .accessibilityHint("Opens the interactive track for audio touch exploration.")
            }
        }
    }
}

#Preview {
    NavigationStack {
        RaceTrackHubView()
    }
}
