import { Extension } from "@tiptap/core";
import { Plugin, PluginKey } from "@tiptap/pm/state";
import { Decoration, DecorationSet } from "@tiptap/pm/view";
import { AIChange, EditorSelection } from "../types";

export interface AIChangesOptions {
  onAIRequest: (action: string, content: string, context?: any) => void;
  onChangeAccepted: (change: AIChange) => void;
  onChangeRejected: (change: AIChange) => void;
}

declare module "@tiptap/core" {
  interface Commands<ReturnType> {
    aiChanges: {
      /**
       * Request AI suggestions for selected text
       */
      requestAISuggestions: (focus?: string) => ReturnType;
      /**
       * Accept an AI change
       */
      acceptAIChange: (changeId: string) => ReturnType;
      /**
       * Reject an AI change
       */
      rejectAIChange: (changeId: string) => ReturnType;
      /**
       * Request AI improvements for the entire document
       */
      requestAIImprovements: (aspect?: string) => ReturnType;
    };
  }
}

export const AIChanges = Extension.create<AIChangesOptions>({
  name: "aiChanges",

  addOptions() {
    return {
      onAIRequest: () => {},
      onChangeAccepted: () => {},
      onChangeRejected: () => {},
    };
  },

  addStorage() {
    return {
      changes: new Map<string, AIChange>(),
      decorations: DecorationSet.empty,
    };
  },

  addCommands() {
    return {
      requestAISuggestions:
        (focus?: string) =>
        ({ state, dispatch }) => {
          const { selection } = state;
          const { from, to } = selection;

          if (from === to) {
            return false; // No selection
          }

          const selectedText = state.doc.textBetween(from, to);

          // Create context with selection info
          const context = {
            focus: focus || "general",
            selection: {
              from,
              to,
              text: selectedText,
            },
          };

          // Request AI suggestions
          this.options.onAIRequest("edit", selectedText, context);

          return true;
        },

      acceptAIChange:
        (changeId: string) =>
        ({ state, dispatch, tr }) => {
          const change = this.storage.changes.get(changeId);
          if (!change) return false;

          // Apply the suggested text
          tr.replaceWith(
            change.position.from,
            change.position.to,
            state.schema.text(change.suggestedText)
          );

          // Remove the change from storage
          this.storage.changes.delete(changeId);

          // Trigger decoration update by setting meta
          tr.setMeta("aiChangesUpdate", true);

          // Notify parent component
          this.options.onChangeAccepted(change);

          if (dispatch) dispatch(tr);
          return true;
        },

      rejectAIChange:
        (changeId: string) =>
        ({ tr, dispatch }) => {
          const change = this.storage.changes.get(changeId);
          if (!change) return false;

          // Remove the change from storage
          this.storage.changes.delete(changeId);

          // Trigger decoration update by setting meta
          tr.setMeta("aiChangesUpdate", true);

          // Notify parent component
          this.options.onChangeRejected(change);

          if (dispatch) dispatch(tr);
          return true;
        },

      requestAIImprovements:
        (aspect?: string) =>
        ({ state }) => {
          const fullText = state.doc.textContent;

          const context = {
            aspect: aspect || "general",
            fullDocument: true,
          };

          // Request AI improvements for the entire document
          this.options.onAIRequest("improve", fullText, context);

          return true;
        },
    };
  },

  addProseMirrorPlugins() {
    const pluginKey = new PluginKey("aiChanges");

    // Helper function to add change decorations (moved outside to be accessible)
    const addChangeDecorations = (
      decorationSet: DecorationSet,
      changes: AIChange[],
      doc: any
    ) => {
      changes.forEach((change) => {
        const decoration = Decoration.inline(
          change.position.from,
          change.position.to,
          {
            class: `ai-change ai-change-${change.type}`,
            "data-change-id": change.id,
            "data-original-text": change.originalText,
            "data-suggested-text": change.suggestedText,
            "data-reason": change.reason,
          },
          {
            inclusiveStart: true,
            inclusiveEnd: true,
          }
        );

        decorationSet = decorationSet.add(doc, [decoration]);
      });

      return decorationSet;
    };

    return [
      new Plugin({
        key: pluginKey,

        state: {
          init() {
            return DecorationSet.empty;
          },

          apply: (tr, decorationSet) => {
            // Map decorations through the transaction
            decorationSet = decorationSet.map(tr.mapping, tr.doc);

            // Check for new changes in meta
            const newChanges = tr.getMeta("aiChanges");
            if (newChanges) {
              decorationSet = addChangeDecorations(
                decorationSet,
                newChanges,
                tr.doc
              );
            }

            return decorationSet;
          },
        },

        props: {
          decorations: (state) => {
            return pluginKey.getState(state);
          },
        },
      }),
    ];
  },

  // Helper methods
  addChange(change: AIChange) {
    this.storage.changes.set(change.id, change);
  },

  addChangeDecorations(
    decorationSet: DecorationSet,
    changes: AIChange[],
    doc: any
  ) {
    changes.forEach((change) => {
      const decoration = Decoration.inline(
        change.position.from,
        change.position.to,
        {
          class: `ai-change ai-change-${change.type}`,
          "data-change-id": change.id,
          "data-original-text": change.originalText,
          "data-suggested-text": change.suggestedText,
          "data-reason": change.reason,
        },
        {
          inclusiveStart: true,
          inclusiveEnd: true,
        }
      );

      decorationSet = decorationSet.add(doc, [decoration]);
    });

    return decorationSet;
  },

  updateDecorations(tr: any) {
    // Remove decorations for deleted changes
    const validChanges = Array.from(
      this.storage.changes.values()
    ) as AIChange[];
    const decorations = validChanges.map((change) =>
      Decoration.inline(change.position.from, change.position.to, {
        class: `ai-change ai-change-${change.type}`,
        "data-change-id": change.id,
      })
    );

    tr.setMeta("aiChanges", decorations);
  },

  // Public API for adding changes from external sources
  addAIChange(change: AIChange) {
    this.addChange(change);

    // Update the editor with new decorations
    const { view } = this.editor;
    if (view) {
      const tr = view.state.tr;
      this.updateDecorations(tr);
      view.dispatch(tr);
    }
  },

  // Get current selection info
  getSelection(): EditorSelection {
    const { state } = this.editor;
    const { selection } = state;
    const { from, to } = selection;

    return {
      from,
      to,
      text: state.doc.textBetween(from, to),
      isEmpty: from === to,
    };
  },
});
