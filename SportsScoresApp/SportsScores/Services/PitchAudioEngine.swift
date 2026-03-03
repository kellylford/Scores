//
//  PitchAudioEngine.swift
//  SportsScores
//
//  Pitch sonification engine for baseball play-by-play.
//
//  Design goals:
//   • Sound *musical*, not synthetic — uses a harmonic-rich waveform (fundamental +
//     2nd + 3rd partial, like a vibraphone/marimba) rather than a raw sine wave.
//   • Pitch height maps to the A-minor pentatonic scale (always harmonious together).
//   • Stereo pan from X coordinate positions the pitch left↔right on the plate.
//   • Plate velocity → note sustain length (faster = shorter).
//   • AVAudioUnitReverb adds spatial depth identical to what Apple uses in AudioGraph.
//
//  Audio graph:  playerNode ──► reverb ──► mainMixerNode ──► output
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
    
    // A-minor pentatonic across 3 octaves — always harmonious when played together.
    // Maps the strike zone from bottom (lowest note) to top (highest note).
    private let pentatonicHz: [Double] = [
        // Octave 3: A C D E G
        220.00, 261.63, 293.66, 329.63, 392.00,
        // Octave 4: A C D E G
        440.00, 523.25, 587.33, 659.25, 784.00,
        // Octave 5: A C D E G
        880.00, 1046.50, 1174.66, 1318.51, 1567.98
    ]
    
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
                try? await Task.sleep(nanoseconds: 180_000_000)   // 180 ms gap
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

    // MARK: - Zone Explorer / Field Tour audio

    /// Play a short tone for an arbitrary ESPN 0–255 coordinate.
    /// Designed for rate-limited continuous-drag use in the Zone Explorer.
    /// Callers must throttle — calling this more than ~8 times/sec produces overlapping tones.
    func playCoordinate(espnX: Int, espnY: Int, velocity: Int? = nil) {
        let coord = GameDetails.Play.PitchCoordinate(x: espnX, y: espnY)
        let (freq, pan, _) = audioParams(coord: coord, velocity: velocity)
        // Short fixed duration so tones don't pile up during a drag
        Task { await self.tone(frequency: freq, pan: pan, duration: 0.18) }
    }

    /// Play a spatial tone mapped from real-world field coordinates (feet from home plate).
    /// `fieldX`: left (−) / right (+) in feet. `fieldY`: distance toward CF in feet.
    /// Audio mapping: x → stereo pan; distance from home → frequency (closer = lower, farther = higher).
    func playFieldCoordinate(fieldX: Double, fieldY: Double,
                             maxHalfWidth: Double, maxDepth: Double) {
        // Map fieldX → pan (−1.0 left … +1.0 right)
        let pan = Float((fieldX / maxHalfWidth).clamped(to: -1.0...1.0))
        // Map distance from home → pentatonic index (near home = low, deep OF = high)
        let dist = (fieldX * fieldX + fieldY * fieldY).squareRoot()
        let distNorm = (dist / maxDepth).clamped(to: 0.0...1.0)
        let noteIndex = Int(distNorm * Double(pentatonicHz.count - 1))
            .clamped(to: 0..<pentatonicHz.count)
        let freq = pentatonicHz[noteIndex]
        Task { await self.tone(frequency: freq, pan: pan, duration: 0.20) }
    }
    
    // MARK: - Parameter Mapping
    
    /// Convert pitch coordinates + velocity to (frequency, pan, duration).
    func audioParams(
        coord: GameDetails.Play.PitchCoordinate,
        velocity: Int?
    ) -> (frequency: Double, pan: Float, duration: Double) {
        
        // Y  0 = top of zone (high pitch), 255 = bottom (low pitch) — invert
        let yNorm = 1.0 - (Double(coord.y) / 255.0).clamped(to: 0...1)
        let xNorm = (Double(coord.x) / 255.0).clamped(to: 0...1)
        
        // Snap to the nearest pentatonic note
        let noteIndex = Int(yNorm * Double(pentatonicHz.count - 1)).clamped(to: 0..<pentatonicHz.count)
        let frequency = pentatonicHz[noteIndex]
        
        // Stereo pan: x → –1.0 (left) … +1.0 (right)
        let pan = Float((xNorm * 2.0 - 1.0).clamped(to: -1.0...1.0))
        
        // Duration: 60–105 mph → 0.55–0.25 s (faster pitch = shorter, crisper note)
        let duration: Double
        if let vel = velocity {
            let velNorm = ((Double(vel) - 60.0) / 45.0).clamped(to: 0...1)
            duration = 0.25 + 0.30 * (1.0 - velNorm)
        } else {
            duration = 0.40
        }
        
        return (frequency, pan, duration)
    }
    
    // MARK: - Tone Generation
    
    /// Generate and play a musical tone with:
    ///   • harmonic-rich waveform  (fundamental + 30% 2nd + 10% 3rd partial → vibraphone-like)
    ///   • reverb                  (smallRoom preset, 35% wet)
    ///   • constant-power stereo pan
    ///   • smooth ADSR envelope    (30 ms attack, exponential decay tail)
    private func tone(frequency: Double, pan: Float, duration: Double) async {
        await MainActor.run { isPlaying = true }
        
        // iOS / Mac Catalyst audio session
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default)
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            await MainActor.run { isPlaying = false }
            return
        }
        
        let newEngine = AVAudioEngine()
        engine = newEngine
        let playerNode = AVAudioPlayerNode()
        
        // Reverb — adds the spatial quality Apple uses in built-in AudioGraph tones
        let reverb = AVAudioUnitReverb()
        reverb.loadFactoryPreset(.smallRoom)
        reverb.wetDryMix = 35
        
        newEngine.attach(playerNode)
        newEngine.attach(reverb)
        
        let format = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 2)!
        newEngine.connect(playerNode, to: reverb, format: format)
        newEngine.connect(reverb, to: newEngine.mainMixerNode, format: format)
        
        // Build PCM buffer
        let totalFrames = AVAudioFrameCount(sampleRate * duration)
        let attackFrames = AVAudioFrameCount(sampleRate * 0.03)   // 30 ms attack
        let releaseFrames = AVAudioFrameCount(sampleRate * 0.06)   // 60 ms release
        
        guard let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: totalFrames) else {
            await MainActor.run { isPlaying = false }
            return
        }
        buffer.frameLength = totalFrames
        
        // Constant-power panning
        let angle     = Double((pan + 1.0) / 2.0) * .pi / 2.0
        let leftGain  = Float(cos(angle))
        let rightGain = Float(sin(angle))
        
        // Phase increment for fundamental (harmonics derive from phase * 2, phase * 3 —
        // correct even across wrap boundaries because sin is 2π-periodic)
        let phaseStep = 2.0 * Double.pi * frequency / sampleRate
        var phase = 0.0
        
        if let leftData  = buffer.floatChannelData?[0],
           let rightData = buffer.floatChannelData?[1] {
            for i in 0..<Int(totalFrames) {
                // Envelope: attack ramp → exponential decay (marimba-style)
                let fi = AVAudioFrameCount(i)
                let envelope: Float
                if fi < attackFrames {
                    // Linear attack
                    envelope = Float(fi) / Float(attackFrames)
                } else {
                    // Exponential decay from 1 → near-zero over the remaining duration
                    let t = Double(fi - attackFrames) / Double(totalFrames - attackFrames)
                    let decayedAmp = pow(1.0 - t, 1.8)   // slightly faster than linear
                    // Smooth release window at the very end to avoid click
                    let rel = totalFrames - releaseFrames
                    if fi >= rel {
                        let r = Float(totalFrames - fi) / Float(releaseFrames)
                        envelope = Float(decayedAmp) * r
                    } else {
                        envelope = Float(decayedAmp)
                    }
                }
                
                // Harmonic mix: fundamental + 2nd (30%) + 3rd (10%) — vibraphone timbre
                let h1 = sin(phase)
                let h2 = sin(phase * 2.0) * 0.30
                let h3 = sin(phase * 3.0) * 0.10
                let mono = Float((h1 + h2 + h3) / 1.40) * envelope * 0.80
                
                phase += phaseStep
                if phase > 2 * .pi { phase -= 2 * .pi }
                
                leftData[i]  = mono * leftGain
                rightData[i] = mono * rightGain
            }
        }
        
        do { try newEngine.start() } catch {
            await MainActor.run { isPlaying = false }
            return
        }
        
        playerNode.play()
        await playerNode.scheduleBuffer(buffer)
        
        newEngine.stop()
        if engine === newEngine { engine = nil }
        
        await MainActor.run {
            if !(sequenceTask?.isCancelled ?? true) { isPlaying = false }
        }
    }
}

// MARK: - Comparable clamp helper

extension Double {
    func clamped(to range: ClosedRange<Double>) -> Double {
        Swift.min(Swift.max(self, range.lowerBound), range.upperBound)
    }
}

extension Int {
    func clamped(to range: Range<Int>) -> Int {
        Swift.min(Swift.max(self, range.lowerBound), range.upperBound - 1)
    }
}


