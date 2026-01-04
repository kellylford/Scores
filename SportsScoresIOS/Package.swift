// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "SportsScores",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "SportsScores",
            targets: ["SportsScores"])
    ],
    targets: [
        .target(
            name: "SportsScores",
            path: "SportsScores")
    ]
)
