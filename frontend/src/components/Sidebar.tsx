import React from "react";
import { X, FileText, Settings, Sparkles } from "lucide-react";
import { WritingDocument } from "../types";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  document: WritingDocument;
  onDocumentChange: (document: WritingDocument) => void;
}

export function Sidebar({
  isOpen,
  onClose,
  document,
  onDocumentChange,
}: SidebarProps) {
  if (!isOpen) return null;

  return (
    <div className="w-80 border-r border-border bg-card flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-border">
        <h2 className="font-semibold">Document Tools</h2>
        <button onClick={onClose} className="p-1 hover:bg-accent rounded">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="flex-1 p-4 space-y-4">
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground">
            Quick Actions
          </h3>
          <div className="space-y-1">
            <button className="w-full text-left p-2 rounded hover:bg-accent flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Generate Ideas
            </button>
            <button className="w-full text-left p-2 rounded hover:bg-accent flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Improve Writing
            </button>
            <button className="w-full text-left p-2 rounded hover:bg-accent flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
