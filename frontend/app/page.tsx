"use client";

import React, { useState, useEffect } from "react";
import {
  Plus,
  MessageSquare,
  FileText,
  Settings,
  Send,
  Sidebar as SidebarIcon,
  ChevronRight,
  Loader2,
  Database,
  Search
} from "lucide-react";

interface Citation {
  id: number;
  text: string;
  metadata: any;
}

interface Message {
  id: number;
  type: "user" | "ai";
  text: string;
  citations?: Citation[];
}

export default function Dashboard() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, type: "ai", text: "Welcome to LocalRAG Vision. Upload a document to start analyzing your data locally." }
  ]);
  const [query, setQuery] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeSource, setActiveSource] = useState<Citation | null>(null);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const currentQuery = query;
    const userMsg: Message = { id: Date.now(), type: "user", text: currentQuery };
    setMessages(prev => [...prev, userMsg]);
    setQuery("");

    // Add temporary AI message
    const aiMessageId = Date.now() + 1;
    setMessages(prev => [...prev, { id: aiMessageId, type: "ai", text: "", citations: [] }]);

    try {
      const response = await fetch("http://localhost:8000/api/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: currentQuery }),
      });

      if (!response.body) return;
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter(l => l.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            if (data.type === "citations") {
              setMessages(prev => prev.map(m =>
                m.id === aiMessageId ? { ...m, citations: data.data } : m
              ));
            } else if (data.type === "content") {
              accumulatedContent += data.data;
              setMessages(prev => prev.map(m =>
                m.id === aiMessageId ? { ...m, text: accumulatedContent } : m
              ));
            }
          } catch (e) {
            console.error("Error parsing stream line:", line);
          }
        }
      }
    } catch (error) {
      console.error("Chat failed:", error);
      setMessages(prev => prev.map(m =>
        m.id === aiMessageId ? { ...m, text: "Error connecting to AI engine. Please check if backend is running." } : m
      ));
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground transition-colors duration-300">
      {/* 1. Knowledge Library (Left) */}
      <aside className={`w-80 glass-panel border-r flex flex-col transition-all duration-300 ${isSidebarOpen ? "translate-x-0" : "-translate-x-full absolute"}`}>
        <div className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-brand rounded-lg flex items-center justify-center neon-glow">
              <Database className="text-white w-5 h-5" />
            </div>
            <h1 className="font-bold text-lg tracking-tight">LocalRAG</h1>
          </div>
        </div>

        <div className="px-4 mb-4">
          <button className="w-full bg-brand hover:bg-brand-vibrant text-white py-3 rounded-xl flex items-center justify-center gap-2 font-medium transition-all shadow-lg shadow-brand/20 active:scale-95">
            <Plus size={18} />
            <span>New Chat</span>
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-4 space-y-2">
          <div className="text-xs font-semibold text-foreground/40 uppercase tracking-widest px-2 mb-2">Documents</div>
          {/* Document Item Placeholder */}
          <div className="group p-3 rounded-xl hover:bg-foreground/5 cursor-pointer border border-transparent hover:border-foreground/10 transition-all">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-brand/10 rounded-lg text-brand group-hover:scale-110 transition-transform">
                <FileText size={20} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">2023 Annual Report.pdf</div>
                <div className="text-[10px] text-brand font-bold uppercase mt-1 flex items-center gap-1">
                  <div className="w-1 h-1 rounded-full bg-brand animate-pulse"></div>
                  Analyzing 85%
                </div>
              </div>
            </div>
          </div>
        </nav>

        <div className="p-4 border-t border-foreground/10 space-y-2">
          <button className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-foreground/5 text-foreground/60 transition-all">
            <Settings size={20} />
            <span className="text-sm font-medium">Settings</span>
          </button>
        </div>
      </aside>

      {/* 2. Conversation Nexus (Center) */}
      <main className="flex-1 flex flex-col relative min-w-0">
        <header className="h-16 glass-panel border-b flex items-center justify-between px-6 z-10">
          <div className="flex items-center gap-4">
            <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-foreground/5 rounded-lg text-foreground/60">
              <SidebarIcon size={20} />
            </button>
            <div className="flex flex-col">
              <span className="text-sm font-bold">RAG Vision</span>
              <span className="text-[10px] text-green-500 font-bold uppercase tracking-widest flex items-center gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                System Healthy
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-foreground/5 rounded-lg text-foreground/60">
              <Search size={20} />
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 space-y-8">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.type === "user" ? "justify-end" : "justify-start animate-in fade-in slide-in-from-bottom-4 duration-500"}`}>
              <div className={`max-w-[80%] p-5 rounded-2xl ${msg.type === "user" ? "bg-brand text-white shadow-xl shadow-brand/20" : "glass-panel neon-glow border-brand/20"}`}>
                <div className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</div>
                {msg.type === "ai" && msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-2 pt-4 border-t border-foreground/10">
                    {msg.citations.map((cite: any) => (
                      <button
                        key={cite.id}
                        onClick={() => setActiveSource(cite)}
                        className="text-[10px] font-bold uppercase tracking-wider bg-brand/10 text-brand px-2 py-1 rounded-md hover:bg-brand/20 transition-all"
                      >
                        [{cite.id}] {cite.metadata?.filename || "Source"}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <footer className="p-6 border-t border-foreground/10 glass-panel">
          <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto relative group">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything about your documents..."
              className="w-full bg-foreground/5 border border-foreground/10 focus:border-brand/50 focus:ring-4 focus:ring-brand/10 rounded-2xl py-4 pl-6 pr-16 text-sm outline-none transition-all placeholder:text-foreground/30"
            />
            <button className="absolute right-2 top-2 p-3 bg-brand hover:bg-brand-vibrant text-white rounded-xl transition-all shadow-lg shadow-brand/20 active:scale-90 group-focus-within:-translate-x-1">
              <Send size={18} />
            </button>
          </form>
          <div className="text-center mt-3 text-[10px] text-foreground/40 font-medium">
            LocalRAG Vision 2026 • Local Processing Active
          </div>
        </footer>
      </main>

      {/* 3. Source Preview (Right) - Collapsible */}
      {activeSource && (
        <aside className="w-96 glass-panel border-l flex flex-col animate-in slide-in-from-right duration-500">
          <header className="h-16 border-b flex items-center px-6 justify-between">
            <div className="flex items-center gap-2">
              <FileText size={18} className="text-brand" />
              <span className="text-sm font-bold">Source Context</span>
            </div>
            <button onClick={() => setActiveSource(null)} className="p-1 hover:bg-foreground/5 rounded-md">
               <Plus size={18} className="rotate-45" />
            </button>
          </header>
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            <div className="p-4 bg-brand/5 rounded-xl border border-brand/10">
              <div className="text-xs font-bold text-brand uppercase mb-2">Reference [{activeSource.id}]</div>
              <div className="text-sm leading-relaxed text-foreground/80 italic">
                "{activeSource.text}"
              </div>
            </div>

            {activeSource.metadata && (
              <div className="space-y-3">
                 <div className="text-xs font-bold text-foreground/40 uppercase tracking-widest">Metadata</div>
                 <div className="p-3 rounded-lg bg-foreground/5 border border-foreground/10 text-[10px] font-mono overflow-x-auto">
                    {JSON.stringify(activeSource.metadata, null, 2)}
                 </div>
              </div>
            )}
          </div>
        </aside>
      )}
    </div>
  );
}
