import React from "react";
import { FileText, Plus } from "lucide-react";
import { Citation } from "../../types";

interface SourcePreviewProps {
  activeSource: Citation | null;
  onClose: () => void;
}

export const SourcePreview: React.FC<SourcePreviewProps> = ({ activeSource, onClose }) => {
  if (!activeSource) return null;

  return (
    <aside className="fixed inset-0 z-50 md:relative md:inset-auto md:w-96 bg-background/80 backdrop-blur-xl md:bg-transparent md:backdrop-blur-none md:glass-panel md:border-l flex flex-col animate-in slide-in-from-right md:slide-in-from-right duration-500">
      {/* Mobile Pull Handle */}
      <div className="md:hidden flex justify-center pt-2 pb-1">
        <div className="w-12 h-1.5 bg-foreground/10 rounded-full"></div>
      </div>
      <header className="h-16 border-b flex items-center px-6 justify-between">
        <div className="flex items-center gap-2">
          <FileText size={18} className="text-brand" />
          <span className="text-sm font-bold">Source Context</span>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-foreground/5 rounded-md">
          <Plus size={18} className="rotate-45" />
        </button>
      </header>
      <div className="flex-1 p-6 overflow-y-auto space-y-6">
        <div className="p-4 bg-brand/5 rounded-xl border border-brand/10">
          <div className="flex items-center justify-between mb-2">
            <div className="text-xs font-bold text-brand uppercase">
              Reference [{activeSource.id}]
            </div>
            {activeSource.metadata?.modality === "video" && (
              <div className="px-2 py-0.5 bg-brand text-white text-[9px] font-bold rounded uppercase tracking-tighter">
                Video Scene
              </div>
            )}
          </div>
          <div className="text-sm leading-relaxed text-foreground/80 italic">
            "{activeSource.text}"
          </div>
        </div>

        {activeSource.metadata && (
          <div className="space-y-4">
            <div className="text-xs font-bold text-foreground/40 uppercase tracking-widest">
              Metadata
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-foreground/5 border border-foreground/10">
                <div className="text-[9px] text-foreground/40 uppercase font-bold mb-1">
                  File
                </div>
                <div className="text-xs font-medium truncate">
                  {activeSource.metadata.file || "Unknown"}
                </div>
              </div>
              {activeSource.metadata.start_time !== undefined && (
                <div className="p-3 rounded-lg bg-foreground/5 border border-foreground/10">
                  <div className="text-[9px] text-foreground/40 uppercase font-bold mb-1">
                    Timestamp
                  </div>
                  <div className="text-xs font-medium text-brand">
                    {Math.floor(activeSource.metadata.start_time / 60)
                      .toString()
                      .padStart(2, "0")}
                    :
                    {Math.floor(activeSource.metadata.start_time % 60)
                      .toString()
                      .padStart(2, "0")}
                  </div>
                </div>
              )}
            </div>
            <div className="p-3 rounded-lg bg-foreground/5 border border-foreground/10 text-[9px] font-mono overflow-x-auto whitespace-pre">
              {JSON.stringify(activeSource.metadata, null, 2)}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
