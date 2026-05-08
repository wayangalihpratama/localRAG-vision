"use client";

import React, { useState } from "react";
import { Message, Citation } from "../types";
import { KnowledgeLibrary } from "../components/dashboard/KnowledgeLibrary";
import { ConversationNexus } from "../components/dashboard/ConversationNexus";
import { SourcePreview } from "../components/dashboard/SourcePreview";

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
      <KnowledgeLibrary
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      <ConversationNexus
        messages={messages}
        query={query}
        setQuery={setQuery}
        onSendMessage={handleSendMessage}
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        onSelectCitation={setActiveSource}
        activeSource={activeSource}
      />

      <SourcePreview
        activeSource={activeSource}
        onClose={() => setActiveSource(null)}
      />
    </div>
  );
}
