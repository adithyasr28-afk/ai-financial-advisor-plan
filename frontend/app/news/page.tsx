"use client";

import { useState, useEffect } from "react";
import { Newspaper, Search } from "lucide-react";
import { API_BASE_URL } from "../lib/api";
import { Card } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Skeleton, SkeletonLine } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";

interface NewsArticle {
  title: string;
  link: string;
  source: string;
  published: string | null;
}

export default function News() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [live, setLive] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    async function fetchNews() {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE_URL}/api/v1/news?limit=20`);
        if (!res.ok) throw new Error("Failed to fetch");
        const data = await res.json();
        setArticles(data.articles);
        setLive(Boolean(data.live));
      } catch {
        setError("Couldn't load news. Check that the backend is reachable and try again.");
      } finally {
        setLoading(false);
      }
    }
    fetchNews();
  }, []);

  const filteredArticles = articles.filter(
    (a) =>
      a.title.toLowerCase().includes(filter.toLowerCase()) ||
      a.source.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">News</h1>
          <p className="text-sm text-ink-muted mt-1 flex items-center gap-2">
            {articles.length} articles from the latest feed pull.
            {!loading && (
              <span className={`inline-flex items-center gap-1 text-[10px] font-medium uppercase tracking-wide ${live ? "text-gain" : "text-ink-faint"}`}>
                <span className={`h-1.5 w-1.5 rounded-full ${live ? "bg-gain" : "bg-ink-faint"}`} />
                {live ? "Live" : "Cached"}
              </span>
            )}
          </p>
        </div>
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-ink-faint absolute left-3 top-1/2 -translate-y-1/2" />
          <Input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter by keyword or source"
            className="w-64 pl-8"
          />
        </div>
      </div>

      {error && <Card className="border-loss/30 bg-loss-soft text-loss text-sm">{error}</Card>}

      {loading ? (
        <div className="space-y-3">
          {[0, 1, 2, 3].map((i) => (
            <Card key={i}>
              <SkeletonLine width="70%" />
              <div className="mt-2">
                <SkeletonLine width="25%" />
              </div>
            </Card>
          ))}
        </div>
      ) : filteredArticles.length > 0 ? (
        <div className="space-y-2.5">
          {filteredArticles.map((article, idx) => (
            <a
              key={idx}
              href={article.link}
              target="_blank"
              rel="noopener noreferrer"
              className="block"
            >
              <Card className="hover:border-line-strong transition-colors">
                <h2 className="font-medium text-ink mb-1.5">{article.title}</h2>
                <div className="flex items-center gap-3 text-xs text-ink-faint">
                  <span>{article.source}</span>
                  {article.published && <span>{new Date(article.published).toLocaleDateString()}</span>}
                </div>
              </Card>
            </a>
          ))}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={Newspaper}
            title={filter ? "No articles match that filter" : "No articles yet"}
            description={filter ? "Try a different keyword or clear the filter." : "Check back once the news feed has ingested articles."}
          />
        </Card>
      )}
    </div>
  );
}
