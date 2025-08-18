import React from "react";
import { Bold, Italic, Underline, Sparkles } from "lucide-react";

interface EditorToolbarProps {
  editor: any;
}

export function EditorToolbar({ editor }: EditorToolbarProps) {
  if (!editor) return null;

  return (
    <div className="border border-border rounded-lg p-2 mb-4 bg-card flex items-center gap-1">
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        className={`p-2 rounded hover:bg-accent ${
          editor.isActive("bold") ? "bg-accent" : ""
        }`}
      >
        <Bold className="h-4 w-4" />
      </button>

      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        className={`p-2 rounded hover:bg-accent ${
          editor.isActive("italic") ? "bg-accent" : ""
        }`}
      >
        <Italic className="h-4 w-4" />
      </button>

      <div className="w-px h-6 bg-border mx-1" />

      <button
        onClick={() => editor.commands.generateBasedOnSelection()}
        className="p-2 rounded hover:bg-accent flex items-center gap-1"
      >
        <Sparkles className="h-4 w-4" />
        <span className="text-sm">AI Generate</span>
      </button>
    </div>
  );
}
