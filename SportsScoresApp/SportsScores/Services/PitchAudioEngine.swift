//
//  PitchAudioEngine.swift
//  SportsScores
//
//  Stereo sine-wave tone generator for baseball pitch sonification.
//
//  Mirrors the Python stereo_audio_mapper.py approach:
//    • Y coordinate → frequency  (top of zone = high pitch, bottom = low pitch)
//    • X coordinate → stereo pan (inside/outside relative to batter handedness)
//    • Velocity      → duration  (faster pitch = shorter tone, 0.3–0.7 s)
//
//  Uses AVAudioEngine + AVAudioSourceNode (no third-party deps, iOS 13+).
//  Constant-power (sin/cos) panning gives a natural left↔right sweep.
//

import AVFoundation
import Foundation

@MainActor
final class PitchAudioEngine: ObservableObject {
    
    // MARK: - Published State
    
    @Published var isPlaying = false
    @Published var statusMessage = ""
    
    // MARK: - Private
    
    private var engine: AVAudioEngine?
    private var sequenceTask: Task<Void, Never>?
    
    private let sampleRate: Double = 44100
    
    // MARK: - Public API
    
    /// Play the audio tone for a single pitch.
    func play(_ pitch: GameDetails.Play) {
        guard let coord = pitch.pitchCoordinate else { return }
        sequenceTask?.cancel()
        let (freq, pan, dur) = audioParams(coord: coord, velocity: pitch.pitchVelocity)
        let desc  = pitch.locationDescription(batterHand: pitch.bats?.abbreviation)
        let vel   = pitch.pitchVelocity.map { "\($0) mph" } ?? ""
        let ptype = pitch.pitchType?.text ?? ""
        statusMessage = [ptype, vel, desc].filter { !$0.isEmpty }.joined(separator: " · ")
        
        sequenceTask = Task { await self.tone(frequency: freq, pan: pan, duration: dur) }
    }
    
    /// Play every pitch in `pitches` sequentially with a short gap between tones.
    func playSequence(_ pitches: [GameDetails.Play]) {
        sequenceTask?.cancel()
        sequenceTask = Task {
            for (i, pitch) in pitches.enumerated() {
                guard !Task.isCancelled else { break }
                guard let coord = pitch.pitchCoordinate else { continue }
                let (freq, pan, dur) = self.audioParams(coord: coord, velocity: pitch.pitchVelocity)
                let label = pitch.pitchType?.abbreviation ?? "–"
                await MainActor.run {
                    self.statusMessage = "Pitch \(i + 1): \(label) · \(pitch.locationDescription(batterHand: nil))"
                }
                await self.tone(frequency: freq, pan: pan, duration: dur)
                // 200 ms gap between pitches
                try? await Task.sleep(nanoseconds: 200_000_000)
            }
            await MainActor.run { self.statusMessage = "Sequence complete" }
        }
    }
    
    /// Stop any playing tone / sequence immediately.
    func stop() {
        sequenceTask?.cancel()
        engine?.stop()
        engine = nil
        isPlaying = false
        statusMessage = ""
    }
    
    // MARK: - Audio Parameter Mapping
    
    /// Convert pitch coordinates + velocity to (frequency, pan, duration).
    ///
    /// Matches the Python stereo_audio_mapper.py calibration:
    ///   - freq:  800 Hz base ± 300 Hz based on vertical position
    ///   - pan:   –1.0 (left) … +1.0 (right) from x coordinate
    ///   - dur:   0.3–0.7 s based on velocity (faster = shorter)
    func audioParams(
        coord: GameDetails.Play.PitchCoordinate,
        velocity: Int?
    ) -> (frequency: Double, pan: Float, duration: Double) {
        
        let xNorm = Double(coord.x) / 255.0          // 0 = catcher's left, 1 = catcher's right
        let yNorm = Double(coord.y) / 255.0          // 0 = top of zone, 1 = bottom
        
        // Frequency: top of strike zone (low y) → high tone, bottom → low tone
        let frequency = (800.0 + 600.0 * (0.5 - yNorm)).clamped(to: 200...2000)
        
        // Stereo pan: x maps directly to left↔right (–1 … +1)
        let pan = Float((xNorm * 2.0 - 1.0).clamped(to: -1.0...1.0))
        
        // Duration: 60–105 mph → 0.7–0.3 s (faster pitch = shorter tone)
        let duration: Double
        if let vel = velocity {
            let velNorm = Double(vel - 60) / 45.0
            duration = (0.3 + 0.4 * (1.0 - velNorm.clamped(to: 0...1)))
        } else {
            duration = 0.5
        }
        
        return (frequency, pan, duration)
    }
    
    // MARK: - Tone Generation
    
    /// Generate and play a sine-wave tone with constant-power stereo panning.
    /// Uses AVAudioPlayerNode + AVAudioPCMBuffer — fully compatible with iOS and Mac Catalyst.
    private func tone(frequency: Double, pan: Float, duration: Double) async {
        await MainActor.run { isPlaying = true }
        
        // Activate audio session (iOS / Mac Catalyst)
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default)
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            await MainActor.run {
                statusMessage = "Audio session error: \(error.localizedDescription)"
                isPlaying = false
            }
            return
        }
        
        let newEngine = AVAudioEngine()
        engine = newEngine
        let playerNode = AVAudioPlayerNode()
        newEngine.attach(playerNode)
        
        let format = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 2)!
        newEngine.connect(playerNode, to: newEngine.mainMixerNode, format: format)
        
        // Build the PCM buffer with a stereo sine wave
        let totalFrames = AVAudioFrameCount(sampleRate * duration)
        let fadeSamples  = AVAudioFrameCount(sampleRate * 0.05)   // 50 ms fade
        
        guard let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: totalFrames) else {
            await MainActor.run { isPlaying = false }
            return
        }
        buffer.frameLength = totalFrames
        
        // Constant-power panning: pan –1…+1 → angle 0…π/2
        let angle      = Double((pan + 1.0) / 2.0) * .pi / 2.0
        let leftGain   = Float(cos(angle))
        let rightGain  = Float(sin(angle))
        let phaseStep  = 2.0 * Double.pi * frequency / sampleRate
        var phase      = 0.0
        
        if let leftData  = buffer.floatChannelData?[0],
           let rightData = buffer.floatChannelData?[1] {
            for i in 0..<Int(totalFrames) {
                // Amplitude envelope (fade in / fade out to avoid clicks)
                let envelope: Float
                let fi = AVAudioFrameCount(i)
                if fi < fadeSamples {
                    envelope = Float(fi) / Float(fadeSamples)
                } else if fi >= totalFrames - fadeSamples {
                    let rem = totalFrames - fi
                    envelope = Float(rem) / Float(fadeSamples)
                } else {
                    envelope = 1.0
                }
                
                let mono = Float(sin(phase)) * envelope * 0.75
                phase += phaseStep
                if phase > 2 * .pi { phase -= 2 * .pi }
                
                leftData[i]  = mono * leftGain
                rightData[i] = mono * rightGain
            }
        }
        
        do {
            try newEngine.start()
        } catch {
            await MainActor.run {
                isPlaying = false
                statusMessage = "Engine start error: \(error.localizedDescription)"
            }
            return
        }
        
        playerNode.play()
        // async variant waits until the buffer finishes playing — no manual sleep needed
        await playerNode.scheduleBuffer(buffer)
        
        newEngine.stop()
        if engine === newEngine { engine = nil }
        
        await MainActor.run {
            if !(sequenceTask?.isCancelled ?? true) { isPlaying = false }
        }
    }
}

// MARK: - Helpers

private extension Comparable {
    func clamped(to range: ClosedRange<Self>) -> Self {
        Swift.min(Swift.max(self, range.lowerBound), range.upperBound)
    }
}
