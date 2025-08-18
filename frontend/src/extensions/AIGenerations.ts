import { Extension } from "@tiptap/core";
import { Plugin, PluginKey } from "@tiptap/pm/state";
import { Decoration, DecorationSet } from "@tiptap/pm/view";
import { GenerationOptions } from "../types";

export interface AIGenerationsOptions {
  onAIRequest: (action: string, content: string, context?: any) => void;
  onGenerationComplete: (text: string) => void;
}

declare module "@tiptap/core" {
  interface Commands<ReturnType> {
    aiGenerations: {
      /**
       * Generate text based on a prompt
       */
      generateText: (prompt: string, options?: GenerationOptions) => ReturnType;
      /**
       * Continue writing from the current cursor position
       */
      continueWriting: (options?: GenerationOptions) => ReturnType;
      /**
       * Generate text for an empty document
       */
      generateFromScratch: (
        prompt: string,
        options?: GenerationOptions
      ) => ReturnType;
      /**
       * Insert generated text at cursor position
       */
      insertGeneratedText: (text: string) => ReturnType;
    };
  }
}

export const AIGenerations = Extension.create<AIGenerationsOptions>({
  name: "aiGenerations",

  addOptions() {
    return {
      onAIRequest: () => {},
      onGenerationComplete: () => {},
    };
  },

  addStorage() {
    return {
      isGenerating: false,
      currentPrompt: "",
      generationPosition: null,
    };
  },

  addCommands() {
    return {
      generateText:
        (prompt: string, options?: GenerationOptions) =>
        ({ state, dispatch }) => {
          const { selection } = state;
          const { from } = selection;

          // Store generation context
          this.storage.isGenerating = true;
          this.storage.currentPrompt = prompt;
          this.storage.generationPosition = from;

          // Create context for AI request
          const context = {
            ...options,
            prompt,
            cursorPosition: from,
            precedingText: state.doc.textBetween(Math.max(0, from - 100), from),
          };

          // Request AI generation
          this.options.onAIRequest("generate", prompt, context);

          return true;
        },

      continueWriting:
        (options?: GenerationOptions) =>
        ({ state, dispatch }) => {
          const { selection } = state;
          const { from } = selection;

          // Get preceding text for context
          const precedingText = state.doc.textBetween(
            Math.max(0, from - 200),
            from
          );

          if (!precedingText.trim()) {
            return false; // No context to continue from
          }

          // Store generation context
          this.storage.isGenerating = true;
          this.storage.currentPrompt = "continue";
          this.storage.generationPosition = from;

          // Create context for AI request
          const context = {
            ...options,
            continueFrom: precedingText,
            cursorPosition: from,
            type: "continuation",
          };

          // Request AI generation to continue writing
          this.options.onAIRequest(
            "generate",
            `Continue this text: ${precedingText}`,
            context
          );

          return true;
        },

      generateFromScratch:
        (prompt: string, options?: GenerationOptions) =>
        ({ state, dispatch }) => {
          // Check if document is mostly empty
          const content = state.doc.textContent.trim();
          if (content.length > 50) {
            return false; // Document already has substantial content
          }

          // Clear existing content and generate new
          const tr = state.tr;
          tr.delete(0, state.doc.content.size);

          // Store generation context
          this.storage.isGenerating = true;
          this.storage.currentPrompt = prompt;
          this.storage.generationPosition = 0;

          // Create context for AI request
          const context = {
            ...options,
            prompt,
            type: "from_scratch",
            fullDocument: true,
          };

          // Request AI generation
          this.options.onAIRequest("generate", prompt, context);

          if (dispatch) dispatch(tr);
          return true;
        },

      insertGeneratedText:
        (text: string) =>
        ({ state, dispatch, tr }) => {
          const position =
            this.storage.generationPosition || state.selection.from;

          // Insert the generated text
          tr.insertText(text, position);

          // Reset generation state
          this.storage.isGenerating = false;
          this.storage.currentPrompt = "";
          this.storage.generationPosition = null;

          // Notify completion
          this.options.onGenerationComplete(text);

          if (dispatch) dispatch(tr);
          return true;
        },
    };
  },

  addProseMirrorPlugins() {
    const pluginKey = new PluginKey("aiGenerations");

    return [
      new Plugin({
        key: pluginKey,

        state: {
          init() {
            return {
              isGenerating: false,
              placeholder: null,
            };
          },

          apply: (tr, state) => {
            // Check for generation state changes
            const isGenerating = tr.getMeta("isGenerating");
            const placeholder = tr.getMeta("generationPlaceholder");

            return {
              isGenerating:
                isGenerating !== undefined ? isGenerating : state.isGenerating,
              placeholder:
                placeholder !== undefined ? placeholder : state.placeholder,
            };
          },
        },

        props: {
          decorations: (state) => {
            const pluginState = pluginKey.getState(state);

            if (pluginState.isGenerating && pluginState.placeholder) {
              // Add loading decoration at generation position
              return DecorationSet.create(state.doc, [
                Decoration.widget(
                  pluginState.placeholder.position,
                  () => {
                    const span = document.createElement("span");
                    span.className = "ai-generating";
                    span.textContent = "✨ Generating...";
                    return span;
                  },
                  { side: 1 }
                ),
              ]);
            }

            return DecorationSet.empty;
          },
        },
      }),
    ];
  },

  // Public API methods
  startGeneration(prompt: string, position: number) {
    this.storage.isGenerating = true;
    this.storage.currentPrompt = prompt;
    this.storage.generationPosition = position;

    // Update plugin state
    const { view } = this.editor;
    if (view) {
      const tr = view.state.tr;
      tr.setMeta("isGenerating", true);
      tr.setMeta("generationPlaceholder", { position });
      view.dispatch(tr);
    }
  },

  completeGeneration(text: string) {
    if (!this.storage.isGenerating) return;

    // Insert the generated text
    this.editor.commands.insertGeneratedText(text);

    // Update plugin state
    const { view } = this.editor;
    if (view) {
      const tr = view.state.tr;
      tr.setMeta("isGenerating", false);
      tr.setMeta("generationPlaceholder", null);
      view.dispatch(tr);
    }
  },

  cancelGeneration() {
    this.storage.isGenerating = false;
    this.storage.currentPrompt = "";
    this.storage.generationPosition = null;

    // Update plugin state
    const { view } = this.editor;
    if (view) {
      const tr = view.state.tr;
      tr.setMeta("isGenerating", false);
      tr.setMeta("generationPlaceholder", null);
      view.dispatch(tr);
    }
  },

  isCurrentlyGenerating(): boolean {
    return this.storage.isGenerating;
  },

  // Helper methods for different generation types
  generateBasedOnSelection(options?: GenerationOptions) {
    const selection = this.editor.state.selection;
    const selectedText = this.editor.state.doc.textBetween(
      selection.from,
      selection.to
    );

    if (selectedText) {
      // Generate based on selection
      return this.editor.commands.generateText(
        `Expand on this: ${selectedText}`,
        options
      );
    } else {
      // Continue from cursor position
      return this.editor.commands.continueWriting(options);
    }
  },

  generateWithStyle(prompt: string, style: GenerationOptions["style"]) {
    return this.editor.commands.generateText(prompt, { style });
  },

  generateWithLength(prompt: string, length: GenerationOptions["length"]) {
    return this.editor.commands.generateText(prompt, { length });
  },
});
