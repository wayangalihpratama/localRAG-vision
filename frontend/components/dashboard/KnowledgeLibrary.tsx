import React, { useState, useEffect } from "react";
import { Plus, Database, FileText, Settings, Upload } from "lucide-react";
import { ingestApi } from "../../lib/api-client";

interface KnowledgeLibraryProps {
  isOpen: boolean;
  onClose: () => void;
}

export const KnowledgeLibrary: React.FC<KnowledgeLibraryProps> = ({ isOpen, onClose }) => {
  const [files, setFiles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const fetchFiles = async () => {
    setIsLoading(true);
    try {
      const response = await ingestApi.listFiles();
      if (response.status === 200) {
        setFiles(response.data);
      }
    } catch (error) {
      console.error("Failed to fetch files:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const response = await ingestApi.uploadFile(file);
      if (response.status === 200 || response.status === 202) {
        console.log("Upload successful", response.data);
        // Refresh list after a short delay to allow for processing
        setTimeout(fetchFiles, 2000);
      }
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  return (
    <aside className={`md:w-80 glass-panel md:border-r flex flex-col z-50 transition-all duration-300
      ${isOpen ? "translate-x-0 w-80" : "-translate-x-full w-0"}
      ${isOpen ? "fixed inset-y-0 left-0 md:relative" : "absolute"}`}>

      <div className="p-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brand rounded-lg flex items-center justify-center neon-glow">
            <Database className="text-white w-5 h-5" />
          </div>
          <h1 className="font-bold text-lg tracking-tight">LocalRAG</h1>
        </div>
        <button onClick={onClose} className="md:hidden p-2 hover:bg-foreground/5 rounded-lg">
          <Plus size={18} className="rotate-45" />
        </button>
      </div>

      <div className="px-4 space-y-2 mb-4">
        <button className="w-full bg-brand hover:bg-brand-vibrant text-white py-3 rounded-xl flex items-center justify-center gap-2 font-medium transition-all shadow-lg shadow-brand/20 active:scale-95">
          <Plus size={18} />
          <span>New Chat</span>
        </button>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept=".pdf,.txt,.docx,.png,.jpg"
        />
        <button
          onClick={handleUploadClick}
          className="w-full bg-foreground/5 hover:bg-foreground/10 text-foreground py-3 rounded-xl flex items-center justify-center gap-2 font-medium transition-all border border-foreground/10 active:scale-95"
        >
          <Upload size={18} />
          <span>Upload Document</span>
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-4 space-y-3 py-4">
        <div className="text-[10px] font-bold text-foreground/30 uppercase tracking-[0.2em] px-3 mb-2">Knowledge Assets</div>

        {isLoading && (
          <div className="flex flex-col gap-3 px-2">
            {[1, 2].map((i) => (
              <div key={i} className="h-16 w-full rounded-2xl bg-foreground/5 animate-pulse" />
            ))}
          </div>
        )}

        {!isLoading && files.length === 0 && (
          <div className="px-3 py-8 text-center border border-dashed border-foreground/10 rounded-2xl">
            <p className="text-xs text-foreground/40 font-medium">No documents uploaded yet.</p>
          </div>
        )}

        {!isLoading && files.map((fileName, idx) => (
          <div key={idx} className="group p-3.5 rounded-2xl bg-brand/5 border border-brand/10 hover:bg-brand/10 hover:border-brand/30 cursor-pointer transition-all duration-300">
            <div className="flex items-center gap-4">
              <div className="p-2.5 bg-brand/20 rounded-xl text-brand group-hover:scale-110 transition-transform shadow-[0_0_15px_rgba(124,58,237,0.2)]">
                <FileText size={20} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold truncate tracking-tight text-foreground/90">{fileName}</div>
                <div className="text-[10px] text-brand-vibrant font-bold uppercase mt-1.5 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-brand shadow-[0_0_8px_rgba(124,58,237,0.6)]"></div>
                  Indexed
                </div>
              </div>
            </div>
          </div>
        ))}
      </nav>

      <div className="p-4 border-t border-foreground/10 space-y-2">
        <button className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-foreground/5 text-foreground/60 transition-all">
          <Settings size={20} />
          <span className="text-sm font-medium">Settings</span>
        </button>
      </div>
    </aside>
  );
};
