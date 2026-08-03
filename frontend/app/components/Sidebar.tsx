"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  LayoutDashboard,
  Building2,
  Briefcase,
  Newspaper,
  Eye,
  MessagesSquare,
  Bell,
  FlaskConical,
  CornerDownLeft,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/company", label: "Company Analysis", icon: Building2 },
  { href: "/portfolio", label: "Portfolio", icon: Briefcase },
  { href: "/news", label: "News", icon: Newspaper },
  { href: "/watchlists", label: "Watchlists", icon: Eye },
  { href: "/chat", label: "AI Chat", icon: MessagesSquare },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/backtesting", label: "Backtesting", icon: FlaskConical },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  // "/" focuses quick-jump from anywhere, unless typing in a field already
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const target = e.target as HTMLElement;
      const typing = ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName);
      if (e.key === "/" && !typing) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

  function handleJump(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    const match = navItems.find((item) => item.label.toLowerCase().includes(q.toLowerCase()));
    if (match) {
      router.push(match.href);
    } else {
      // Not a known page - treat it as a ticker symbol
      router.push(`/company?symbol=${encodeURIComponent(q.toUpperCase())}`);
    }
    setQuery("");
    inputRef.current?.blur();
  }

  return (
    <aside className="w-60 shrink-0 h-screen sticky top-0 border-r border-line bg-paper-raised flex flex-col">
      <Link href="/" className="flex items-center gap-2 px-5 h-16 border-b border-line shrink-0">
        <span className="w-2 h-2 rounded-full bg-signal" />
        <span className="font-display font-semibold text-[15px] tracking-tight text-ink">
          Fincast
        </span>
      </Link>

      <form onSubmit={handleJump} className="p-3 border-b border-line">
        <div className="relative">
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Jump to symbol or page"
            className="w-full pl-3 pr-8 py-2 text-sm rounded border border-line bg-paper focus:border-signal outline-none transition-colors placeholder:text-ink-faint"
          />
          <kbd className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-ink-faint border border-line rounded px-1 py-0.5 leading-none pointer-events-none">
            /
          </kbd>
        </div>
        {query && (
          <p className="mt-1.5 text-xs text-ink-faint flex items-center gap-1">
            <CornerDownLeft className="w-3 h-3" /> jump to {query.toUpperCase()}
          </p>
        )}
      </form>

      <nav className="flex-1 overflow-y-auto py-2">
        {navItems.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`relative flex items-center gap-2.5 mx-2 px-3 py-2 rounded text-sm transition-colors ${
                active
                  ? "bg-signal-soft text-signal font-medium"
                  : "text-ink-muted hover:text-ink hover:bg-paper"
              }`}
            >
              {active && (
                <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 rounded-full bg-signal -ml-2" />
              )}
              <Icon className="w-4 h-4 shrink-0" strokeWidth={1.75} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-line text-xs text-ink-faint leading-relaxed">
        Multi-agent research, not investment advice.
      </div>
    </aside>
  );
}
