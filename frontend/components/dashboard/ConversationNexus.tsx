import React from "react";
import { Sidebar as SidebarIcon, Search, FileText, Send } from "lucide-react";
import { Message, Citation } from "../../types";

interface ConversationNexusProps {
  messages: Message[];
  query: string;
  setQuery: (q: string) => void;
  onSendMessage: (e: React.FormEvent) => void;
  onToggleSidebar: () => void;
  onSelectCitation: (cite: Citation) => void;
  activeSource: Citation | null;
}

export const ConversationNexus: React.FC<ConversationNexusProps> = ({
  messages,
  query,
  setQuery,
  onSendMessage,
  onToggleSidebar,
  onSelectCitation,
  activeSource
}) => {
  return (
    <main className="flex-1 flex flex-col relative min-w-0 w-full">
      <header className="h-16 glass-panel border-b flex items-center justify-between px-4 md:px-6 z-10">
        <div className="flex items-center gap-2 md:gap-4">
          <button onClick={onToggleSidebar} className="p-2 hover:bg-foreground/5 rounded-lg text-foreground/60 transition-colors">
            <SidebarIcon size={20} />
          </button>
        </div>

        <div className="flex flex-col items-center">
          <span className="text-sm font-bold tracking-tight">LocalRAG Vision</span>
          <span className="text-[9px] text-green-500 font-bold uppercase tracking-widest flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
            System Active
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-foreground/5 rounded-lg text-foreground/60 md:hidden transition-colors">
             <FileText size={20} onClick={() => activeSource && onSelectCitation(activeSource)} />
          </button>
          <button className="p-2 hover:bg-foreground/5 rounded-lg text-foreground/60 transition-colors">
            <Search size={20} />
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.type === "user" ? "justify-end" : "justify-start animate-in fade-in slide-in-from-bottom-4 duration-500"}`}>
            <div className={`max-w-[90%] md:max-w-[80%] p-4 md:p-6 rounded-2xl ${
              msg.type === "user"
                ? "bg-brand text-white shadow-xl shadow-brand/20"
                : "glass-panel border-brand/30 shadow-[0_0_20px_rgba(124,58,237,0.05)]"
            }`}>
              <div className="text-sm md:text-[15px] leading-relaxed whitespace-pre-wrap tracking-tight text-foreground/90">{msg.text}</div>
              {msg.type === "ai" && msg.citations && msg.citations.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2 pt-4 border-t border-foreground/10">
                  {msg.citations.map((cite: any) => (
                    <button
                      key={cite.id}
                      onClick={() => onSelectCitation(cite)}
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

      <footer className="p-4 md:p-6 border-t border-foreground/10 glass-panel">
        <form onSubmit={onSendMessage} className="max-w-4xl mx-auto relative group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything..."
            className="w-full bg-foreground/5 border border-foreground/10 focus:border-brand/50 focus:ring-4 focus:ring-brand/10 rounded-2xl py-3 md:py-4 pl-5 md:pl-6 pr-14 md:pr-16 text-sm outline-none transition-all placeholder:text-foreground/30"
          />
          <button className="absolute right-2 top-2 p-2.5 md:p-3 bg-brand hover:bg-brand-vibrant text-white rounded-xl transition-all shadow-lg shadow-brand/20 active:scale-90 group-focus-within:-translate-x-1">
            <Send size={18} />
          </button>
        </form>
        <div className="text-center mt-3 text-[10px] text-foreground/40 font-medium">
          LocalRAG 2026 • Local
        </div>
      </footer>
    </main>
  );
};
