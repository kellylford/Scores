//
//  Collection+Safe.swift
//  SportsScores
//
//  Bounds-checked indexing, for reading ESPN's column-oriented payloads where
//  parallel arrays are not guaranteed to be the same length.
//

import Foundation

extension Collection {
    /// The element at `index`, or nil when the index is out of bounds.
    subscript(safe index: Index) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
