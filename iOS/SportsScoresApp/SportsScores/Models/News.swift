//
//  News.swift
//  SportsScores
//
//  Data model for ESPN news articles.
//

import Foundation

struct NewsItem: Identifiable {
    let id: String
    let headline: String
    let description: String?
    let byline: String?
    let published: Date?
    let articleURL: URL?
    let imageURL: URL?

    init(from api: NewsAPIResponse.APIArticle) {
        // ESPN returns id as an integer; convert to String for Identifiable.
        self.id          = api.id.map { String($0) } ?? UUID().uuidString
        self.headline    = api.headline
        self.description = api.description
        self.byline      = api.byline
        self.published   = api.published
        self.articleURL  = api.links?.web?.href.flatMap { URL(string: $0) }
        self.imageURL    = api.images?.first?.url.flatMap { URL(string: $0) }
    }
}

// MARK: - API Response Models

struct NewsAPIResponse: Codable {
    let articles: [APIArticle]

    struct APIArticle: Codable {
        /// ESPN returns article IDs as integers (e.g. 48040023).
        let id: Int?
        let headline: String
        let description: String?
        let byline: String?
        let published: Date?
        let links: Links?
        let images: [NewsImage]?

        struct Links: Codable {
            let web: WebLink?

            struct WebLink: Codable {
                let href: String?
            }
        }

        struct NewsImage: Codable {
            let url: String?
        }
    }
}
