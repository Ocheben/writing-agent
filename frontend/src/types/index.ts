export interface AIRequest {
  action: "generate" | "edit" | "improve";
  content: string;
  context?: {
    style?: string;
    length?: string;
    focus?: string;
    aspect?: string;
    selection?: {
      from: number;
      to: number;
      text: string;
    };
  };
}

export interface AIResponse {
  type:
    | "generation_start"
    | "generation_chunk"
    | "generation_complete"
    | "edit_start"
    | "edit_chunk"
    | "edit_complete"
    | "improve_start"
    | "improve_chunk"
    | "improve_complete"
    | "error";
  content?: string;
  message?: string;
}

export interface WritingDocument {
  id?: string;
  title: string;
  content: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface AIChange {
  id: string;
  type: "suggestion" | "improvement" | "generation";
  originalText: string;
  suggestedText: string;
  reason: string;
  position: {
    from: number;
    to: number;
  };
  status: "pending" | "accepted" | "rejected";
}

export interface EditorSelection {
  from: number;
  to: number;
  text: string;
  isEmpty: boolean;
}

export interface WebSocketMessage {
  action: string;
  content: string;
  context?: any;
}

export interface GenerationOptions {
  style?: "formal" | "casual" | "creative" | "technical";
  length?: "short" | "medium" | "long";
  tone?: "professional" | "friendly" | "persuasive" | "informative";
}

export interface EditOptions {
  focus?: "grammar" | "clarity" | "structure" | "style";
  preserveLength?: boolean;
  preserveTone?: boolean;
}

export interface ImprovementOptions {
  aspect?: "readability" | "engagement" | "coherence" | "impact";
  target?: "general" | "academic" | "business" | "creative";
}
