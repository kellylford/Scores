//
//  TouchTourAnnouncementService.swift
//  SportsScores
//
//  Announces touch-tour landmarks using VoiceOver when enabled,
//  otherwise falls back to iOS speech synthesis.
//

import Foundation
import AVFoundation
import UIKit

@MainActor
final class TouchTourAnnouncementService {
    static let shared = TouchTourAnnouncementService()

    private let synthesizer = AVSpeechSynthesizer()

    private init() {}

    func announce(_ text: String, interrupt: Bool = true) {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        if UIAccessibility.isVoiceOverRunning {
            UIAccessibility.post(notification: .announcement, argument: trimmed)
            return
        }

        if interrupt && synthesizer.isSpeaking {
            synthesizer.stopSpeaking(at: .immediate)
        }

        let utterance = AVSpeechUtterance(string: trimmed)
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate
        utterance.voice = AVSpeechSynthesisVoice(language: Locale.preferredLanguages.first)
        synthesizer.speak(utterance)
    }
}
