"use client";

import { useState, useRef, useEffect } from "react";
import { Send, MessagesSquare, AlertTriangle } from "lucide-react";
import { API_BASE_URL } from "../lib/api";
import { Card } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";
import { ConsensusStrip } from "../components/ui/ConsensusStrip";

interface AgentResult {
  agent: string;
  stance: string | null;
  confidence: number;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  consensus?: AgentResult[];
  isError?: boolean;
}

const SUGGESTIONS = ["AAPL comprehensive report", "latest news for Apple", "portfolio risk assessment"];

export default function AIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function ask(query: string) {
    if (!query.trim() || loading) return;
    setInput("");
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: query }]);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/orchestrate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      if (!res.ok) throw new Error("Request failed");
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "",
          consensus: data.results.map((r: any) => ({
            agent: r.agent,
            stance: r.stance,
            confidence: r.confidence,
          })),
        },
      ]);

      for (const result of data.results) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `${result.agent.replace(/_/g, " ")} · ${Math.round(result.confidence * 100)}% confidence${
              result.stance ? ` · ${result.stance}` : ""
            }\n${result.summary}`,
          },
        ]);
        await new Promise((r) => setTimeout(r, 60));
      }

      if (data.disagreements.length > 0) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            isError: true,
            content: `Disagreement detected: ${data.disagreements[0].message}\nStances: ${data.disagreements[0].stances.join(", ")}`,
          },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", isError: true, content: "Couldn't reach the agents. Confirm the backend is running and try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-h-[900px]">
      <div className="mb-4">
        <h1 className="font-display text-2xl font-semibold text-ink">AI Chat</h1>
        <p className="text-sm text-ink-muted mt-1">Ask a financial question — every agent analyzes and reports back.</p>
      </div>

      <Card padded={false} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-6">
            <MessagesSquare className="w-8 h-8 text-ink-faint mb-3" strokeWidth={1.5} />
            <p className="font-medium text-ink mb-3">Start a conversation</p>
            <div className="flex flex-col gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => ask(s)}
                  className="text-sm px-3 py-1.5 rounded border border-line text-ink-muted hover:border-signal hover:text-signal transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) =>
          msg.consensus ? (
            <div key={idx} className="max-w-[85%]">
              <ConsensusStrip results={msg.consensus} />
            </div>
          ) : (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[85%] px-4 py-2.5 rounded text-sm whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-signal text-white"
                    : msg.isError
                    ? "bg-loss-soft text-loss flex items-start gap-2"
                    : "bg-paper text-ink"
                }`}
              >
                {msg.isError && <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />}
                <span>{msg.content}</span>
              </div>
            </div>
          )
        )}
        <div ref={messagesEndRef} />
      </Card>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
        className="mt-4 flex gap-2"
      >
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a financial question…"
          disabled={loading}
          className="flex-1"
        />
        <Button type="submit" disabled={loading || !input.trim()}>
          <Send className="w-4 h-4" /> {loading ? "Thinking…" : "Send"}
        </Button>
      </form>
    </div>
  );
}
