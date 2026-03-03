//
//  FieldAudioEngine.swift
//  SportsScores
//
//  Continuous terrain-based audio engine for the Baseball Field Tour.
//
//  Architecture:
//    Three AVAudioPlayerNodes loop simultaneously — one per terrain type.
//    Each plays a different noise texture baked at buffer-build time.
//    Zone blending: instant volume switch on the active player (others silent).
//    Spatial pan: all three player positions share the same AVAudioEnvironmentNode
//    x-axis value, updated on every drag tick — no gaps, no engine restarts.
//
//  Terrain textures:
//    fair          — heavy low-pass white noise → soft grass swish
//    warningTrack  — medium low-pass + slow AM → cinder/gravel rustle
//    foul          — barely averaged white noise → rough concrete scrape
//

import AVFoundation
import Foundation

@MainActor
final class FieldAudioEngine: ObservableObject {

    // MARK: - Private audio graph

    private let sampleRate: Double = 44100
    private let loopSeconds: Double = 3.0   // seamless loop length; prime-ish avoids flutter beating

    private var engine:      AVAudioEngine?
    private var fairPlayer:  AVAudioPlayerNode?
    private var warnPlayer:  AVAudioPlayerNode?
    private var foulPlayer:  AVAudioPlayerNode?
    private var environment: AVAudioEnvironmentNode?

    // Buffers built once, reused across start/stop cycles
    private var fairBuffer: AVAudioPCMBuffer?
    private var warnBuffer: AVAudioPCMBuffer?
    private var foulBuffer: AVAudioPCMBuffer?

    var isRunning: Bool { engine?.isRunning ?? false }

    // MARK: - Lifecycle

    /// Start the engine and begin looping all three terrain buffers (silent until update() called).
    func start() {
        guard !isRunning else { return }

        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default,
                                                            options: .duckOthers)
            try AVAudioSession.sharedInstance().setActive(true)
        } catch { return }

        let eng   = AVAudioEngine()
        let mono  = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 1)!
        let stereo = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 2)!

        let fp = AVAudioPlayerNode()
        let wp = AVAudioPlayerNode()
        let lp = AVAudioPlayerNode()
        let env = AVAudioEnvironmentNode()

        eng.attach(fp); eng.attach(wp); eng.attach(lp); eng.attach(env)

        // All three mono players → shared environment node → stereo output
        eng.connect(fp,  to: env, format: mono)
        eng.connect(wp,  to: env, format: mono)
        eng.connect(lp,  to: env, format: mono)
        eng.connect(env, to: eng.mainMixerNode, format: stereo)

        // Listener at origin; sounds positioned 1 unit "in front" — panning moves along x-axis
        env.listenerPosition = AVAudio3DPoint(x: 0, y: 0, z: 0)

        // Build buffers once
        let fb = fairBuffer ?? makeFairBuffer(fmt: mono)
        let wb = warnBuffer ?? makeWarnBuffer(fmt: mono)
        let lb = foulBuffer ?? makeFoulBuffer(fmt: mono)
        fairBuffer = fb; warnBuffer = wb; foulBuffer = lb

        guard (try? eng.start()) != nil else { return }

        // Schedule looping; start fully silent — caller drives volumes
        fp.scheduleBuffer(fb, at: nil, options: .loops)
        wp.scheduleBuffer(wb, at: nil, options: .loops)
        lp.scheduleBuffer(lb, at: nil, options: .loops)
        fp.play(); wp.play(); lp.play()
        fp.volume = 0; wp.volume = 0; lp.volume = 0

        // Default center pan
        let center = AVAudio3DPoint(x: 0, y: 0, z: -1)
        fp.position = center; wp.position = center; lp.position = center

        engine = eng
        fairPlayer = fp; warnPlayer = wp; foulPlayer = lp
        environment = env
    }

    /// Update the active terrain sound and stereo pan. Call on every drag-changed event — no throttle needed.
    func update(terrain: FieldTerrain, pan: Float) {
        if !isRunning { start() }
        guard isRunning else { return }

        // Pan: ±4 units of offset gives clearly perceivable stereo without exaggerating HRTF
        let x = pan * 4.0   // pan is Float; literal inferred as Float
        let pos = AVAudio3DPoint(x: x, y: 0, z: -1)
        fairPlayer?.position = pos
        warnPlayer?.position = pos
        foulPlayer?.position = pos

        // Terrain volumes — instant switch between terrain layers.
        // Small bleed values let one layer carry through slightly at boundaries.
        switch terrain {
        case .fair:
            fairPlayer?.volume = 0.45
            warnPlayer?.volume = 0
            foulPlayer?.volume = 0
        case .warningTrack:
            fairPlayer?.volume = 0.12   // floor softens transition from grass
            warnPlayer?.volume = 0.45
            foulPlayer?.volume = 0
        case .foul:
            fairPlayer?.volume = 0
            warnPlayer?.volume = 0
            foulPlayer?.volume = 0.50
        case .silent:
            fairPlayer?.volume = 0
            warnPlayer?.volume = 0
            foulPlayer?.volume = 0
        }
    }

    /// Stop the engine immediately (called when finger lifts).
    func stop() {
        fairPlayer?.stop(); warnPlayer?.stop(); foulPlayer?.stop()
        engine?.stop()
        engine = nil; fairPlayer = nil; warnPlayer = nil
        foulPlayer = nil; environment = nil
        try? AVAudioSession.sharedInstance().setActive(false,
                                                       options: .notifyOthersOnDeactivation)
    }

    // MARK: - Buffer generation

    /// Grass swish — aggressive low-pass (20-sample running average) → nearly tonal hiss,
    /// very soft and smooth. Think wind through outfield grass.
    private func makeFairBuffer(fmt: AVAudioFormat) -> AVAudioPCMBuffer {
        let frames = AVAudioFrameCount(sampleRate * loopSeconds)
        let buf = AVAudioPCMBuffer(pcmFormat: fmt, frameCapacity: frames)!
        buf.frameLength = frames
        let data = buf.floatChannelData![0]
        let w = 20
        var raw = [Float](repeating: 0, count: Int(frames) + w)
        for i in raw.indices { raw[i] = Float.random(in: -1...1) }
        for i in 0..<Int(frames) {
            let sum: Float = (0..<w).reduce(0) { $0 + raw[i + $1] }
            data[i] = (sum / Float(w)) * 0.55
        }
        return buf
    }

    /// Warning track — 6-sample average (more texture than grass) + 5 Hz amplitude modulation
    /// that gives a slight crunch/scrape quality, like dragging a foot through cinder.
    private func makeWarnBuffer(fmt: AVAudioFormat) -> AVAudioPCMBuffer {
        let frames = AVAudioFrameCount(sampleRate * loopSeconds)
        let buf = AVAudioPCMBuffer(pcmFormat: fmt, frameCapacity: frames)!
        buf.frameLength = frames
        let data = buf.floatChannelData![0]
        let w = 6
        var raw = [Float](repeating: 0, count: Int(frames) + w)
        for i in raw.indices { raw[i] = Float.random(in: -1...1) }
        for i in 0..<Int(frames) {
            let sum: Float = (0..<w).reduce(0) { $0 + raw[i + $1] }
            let filtered = sum / Float(w)
            // 5 Hz AM → coarse crunch texture
            let am = Float(0.72 + 0.28 * sin(Double(i) / sampleRate * 2 * .pi * 5.0))
            data[i] = filtered * am * 0.55
        }
        return buf
    }

    /// Foul territory — barely averaged (2-sample) white noise → rough, full-spectrum scrape.
    /// More high-frequency content than fair/warning, clearly harsher to the ear.
    private func makeFoulBuffer(fmt: AVAudioFormat) -> AVAudioPCMBuffer {
        let frames = AVAudioFrameCount(sampleRate * loopSeconds)
        let buf = AVAudioPCMBuffer(pcmFormat: fmt, frameCapacity: frames)!
        buf.frameLength = frames
        let data = buf.floatChannelData![0]
        var raw = [Float](repeating: 0, count: Int(frames) + 2)
        for i in raw.indices { raw[i] = Float.random(in: -1...1) }
        for i in 0..<Int(frames) {
            data[i] = ((raw[i] + raw[i + 1]) * 0.5) * 0.60
        }
        return buf
    }
}
