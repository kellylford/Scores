//
//  TeamNewsTabView.swift
//  SportsScores
//
//  News tab for Team Hub — team-filtered articles.
//

import SwiftUI

struct TeamNewsTabView: View {
    @ObservedObject var viewModel: TeamHubViewModel

    var body: some View {
        Group {
            if viewModel.isLoadingNews {
                ProgressView("Loading news…")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = viewModel.errorNews, viewModel.news.isEmpty {
                errorState(message: error)
            } else if viewModel.news.isEmpty {
                emptyState
            } else {
                List(viewModel.news) { article in
                    NewsRow(article: article)
                        .listRowSeparator(.visible)
                        .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
                }
                .listStyle(.plain)
            }
        }
        .navigationTitle("News")
        .navigationBarTitleDisplayMode(.inline)
        .task { await viewModel.loadNews() }
        .refreshable { await viewModel.loadNews() }
    }

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "newspaper")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("No news available")
                .font(.headline)
                .foregroundColor(.secondary)
        }
    }

    private func errorState(message: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 40))
                .foregroundColor(.secondary)
            Text(message)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            Button("Retry") { Task { await viewModel.loadNews() } }
                .buttonStyle(.borderedProminent)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
