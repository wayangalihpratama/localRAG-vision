import React, { useState, useEffect } from "react";
import { Plus, Database, FileText, Settings, Upload, Trash2 } from "lucide-react";
import { ingestApi } from "../../lib/api-client";

interface KnowledgeLibraryProps {
  isOpen: boolean;
  onClose: () => void;
}

interface DocumentAsset {
  id: string;
  filename: string;
  status: "processing" | "completed" | "failed";
  created_at: string;
}

export const KnowledgeLibrary: React.FC<KnowledgeLibraryProps> = ({ isOpen, onClose }) => {
  const [files, setFiles] = useState<DocumentAsset[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const fetchFiles = async () => {
    // Only show full loading skeleton on first fetch
    if (files.length === 0) setIsLoading(true);
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
    // Poll for status updates every 5 seconds if there are processing files
    const interval = setInterval(() => {
      fetchFiles();
    }, 5000);
    return () => clearInterval(interval);
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

  const handleDelete = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await ingestApi.deleteFile(fileId);
      // Refresh list immediately
      fetchFiles();
    } catch (err) {
      console.error('Failed to delete file:', err);
      alert('Failed to delete document.');
    }
  };

  return (
    <aside className={`md:w-80 glass-panel md:border-r flex flex-col z-50 transition-all duration-300
      ${isOpen ? "translate-x-0 w-80" : "-translate-x-full w-0"}
      ${isOpen ? "fixed inset-y-0 left-0 md:relative" : "absolute"}`}>

      <div className="p-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center overflow-hidden">
            <img src="/logo.png" alt="LocalRAG Logo" className="w-full h-full object-cover" />
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

        {!isLoading && files.map((file) => (
          <div key={file.id} className="group p-3.5 rounded-2xl bg-brand/5 border border-brand/10 hover:bg-brand/10 hover:border-brand/30 cursor-pointer transition-all duration-300">
            <div className="flex items-center gap-4">
              <div className="p-2.5 bg-brand/20 rounded-xl text-brand group-hover:scale-110 transition-transform shadow-[0_0_15px_rgba(124,58,237,0.2)]">
                <FileText size={20} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold truncate tracking-tight text-foreground/90">{file.filename}</div>
                <div className="text-[10px] uppercase mt-1.5 flex items-center gap-2 font-bold">
                  {file.status === "processing" && (
                    <>
                      <div className="w-1.5 h-1.5 rounded-full bg-brand animate-pulse shadow-[0_0_8px_rgba(124,58,237,0.6)]"></div>
                      <span className="text-brand-vibrant">Analyzing</span>
                    </>
                  )}
                  {file.status === "completed" && (
                    <>
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
                      <span className="text-emerald-500">Indexed</span>
                    </>
                  )}
                  {file.status === "failed" && (
                    <>
                      <div className="w-1.5 h-1.5 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]"></div>
                      <span className="text-rose-500">Failed</span>
                    </>
                  )}
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(file.id);
                }}
                className="p-2 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 hover:text-red-400 text-foreground/40 rounded-lg transition-all"
                title="Delete Asset"
              >
                <Trash2 size={16} />
              </button>
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
