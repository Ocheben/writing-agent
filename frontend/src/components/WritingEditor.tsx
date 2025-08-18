import React from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";
import CharacterCount from "@tiptap/extension-character-count";
import Focus from "@tiptap/extension-focus";
import { Color } from "@tiptap/extension-color";
import TextStyle from "@tiptap/extension-text-style";
import Highlight from "@tiptap/extension-highlight";

import { AIChanges } from "../extensions/AIChanges";
import { AIGenerations } from "../extensions/AIGenerations";
import { EditorToolbar } from "./EditorToolbar";
import { AIPanel } from "./AIPanel";
import { AIChange } from "../types";

interface WritingEditorProps {
  content: string;
  onContentChange: (content: string) => void;
  onAIRequest: (action: string, content: string, context?: any) => void;
  isGenerating: boolean;
  aiResponse: string;
}

export function WritingEditor({
  content,
  onContentChange,
  onAIRequest,
  isGenerating,
  aiResponse,
}: WritingEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: "Start writing or use AI to generate content...",
        emptyEditorClass: "is-editor-empty",
      }),
      CharacterCount.configure({
        limit: 100000,
      }),
      Focus.configure({
        className: "has-focus",
        mode: "all",
      }),
      Color,
      TextStyle,
      Highlight.configure({
        multicolor: true,
      }),
      AIChanges.configure({
        onAIRequest,
        onChangeAccepted: (change: AIChange) => {
          console.log("AI change accepted:", change);
        },
        onChangeRejected: (change: AIChange) => {
          console.log("AI change rejected:", change);
        },
      }),
      AIGenerations.configure({
        onAIRequest,
        onGenerationComplete: (text: string) => {
          console.log("AI generation completed:", text);
        },
      }),
    ],
    content,
    onUpdate: ({ editor }) => {
      onContentChange(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class:
          "prose prose-sm sm:prose-base lg:prose-lg xl:prose-2xl mx-auto focus:outline-none min-h-[500px] px-4 py-6",
      },
    },
  });

  // Handle AI response streaming
  const lastAiResponseRef = React.useRef("");
  React.useEffect(() => {
    if (aiResponse && editor && isGenerating) {
      // Only insert the new part of the response to avoid duplication
      const newPart = aiResponse.slice(lastAiResponseRef.current.length);

      if (newPart) {
        // Insert at current cursor position
        editor.commands.insertContent(newPart);
        lastAiResponseRef.current = aiResponse;
      }
    } else if (!isGenerating) {
      // Reset when generation is complete
      lastAiResponseRef.current = "";
    }
  }, [aiResponse, editor, isGenerating]);

  if (!editor) {
    return <div className="animate-pulse bg-muted h-[500px] rounded-md" />;
  }

  const characterCount = editor.storage.characterCount.characters();
  const wordCount = editor.storage.characterCount.words();

  return (
    <div className="w-full">
      {/* Editor Toolbar */}
      <EditorToolbar editor={editor} />

      <div className="flex gap-4">
        {/* Main Editor */}
        <div className="flex-1">
          <div className="border border-border rounded-lg overflow-hidden bg-card">
            <EditorContent
              editor={editor}
              className="min-h-[500px] focus-within:ring-2 focus-within:ring-ring"
            />

            {/* Status Bar */}
            <div className="border-t border-border px-4 py-2 bg-muted/50 flex justify-between items-center text-sm text-muted-foreground">
              <div className="flex gap-4">
                <span>{wordCount} words</span>
                <span>{characterCount} characters</span>
              </div>

              <div className="flex gap-2 items-center">
                {isGenerating && (
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                    <span>AI is writing...</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* AI Panel */}
        <AIPanel
          editor={editor}
          onAIRequest={onAIRequest}
          isGenerating={isGenerating}
        />
      </div>
    </div>
  );
}
