import React, { useState } from "react";
import { Sparkles, Wand2, RefreshCw } from "lucide-react";

interface AIPanelProps {
  editor: any;
  onAIRequest: (action: string, content: string, context?: any) => void;
  isGenerating: boolean;
}

export function AIPanel({ editor, onAIRequest, isGenerating }: AIPanelProps) {
  const [prompt, setPrompt] = useState("");

  const handleGenerate = () => {
    if (!prompt.trim()) return;
    onAIRequest("generate", prompt);
    setPrompt("");
  };

  const handleImprove = () => {
    if (!editor) return;
    const content = editor.getHTML();
    onAIRequest("improve", content);
  };

  const handleContinue = () => {
    if (!editor) return;
    editor.commands.continueWriting();
  };

  return (
    <div className="w-80 border border-border rounded-lg bg-card p-4 h-fit">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="h-5 w-5 text-primary" />
        <h3 className="font-semibold">AI Assistant</h3>
      </div>

      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium text-muted-foreground">
            Generate Content
          </label>
          <div className="mt-1 space-y-2">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe what you want to write..."
              className="w-full p-2 border border-border rounded resize-none focus:outline-none focus:ring-2 focus:ring-ring"
              rows={3}
              disabled={isGenerating}
            />
            <button
              onClick={handleGenerate}
              disabled={!prompt.trim() || isGenerating}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles className="h-4 w-4" />
              {isGenerating ? "Generating..." : "Generate"}
            </button>
          </div>
        </div>

        <div className="space-y-2">
          <button
            onClick={handleContinue}
            disabled={isGenerating}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 border border-border rounded hover:bg-accent disabled:opacity-50"
          >
            <Wand2 className="h-4 w-4" />
            Continue Writing
          </button>

          <button
            onClick={handleImprove}
            disabled={isGenerating}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 border border-border rounded hover:bg-accent disabled:opacity-50"
          >
            <RefreshCw className="h-4 w-4" />
            Improve Text
          </button>
        </div>

        {isGenerating && (
          <div className="text-center text-sm text-muted-foreground">
            AI is working on your request...
          </div>
        )}
      </div>
    </div>
  );
}
