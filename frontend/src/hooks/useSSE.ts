import { useState, useCallback, useRef } from "react";

interface UseSSEReturn {
  isConnected: boolean;
  sendMessage: (action: string, content: string, context?: any) => void;
  isGenerating: boolean;
  currentResponse: string;
  error: string | null;
}

interface SSERequest {
  action: "generate" | "edit" | "improve";
  content: string;
  context?: any;
}

export function useSSE(
  baseUrl: string = "http://localhost:8000"
): UseSSEReturn {
  const [isConnected, setIsConnected] = useState(true); // SSE is always "connected"
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentResponse, setCurrentResponse] = useState("");
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (action: string, content: string, context?: any) => {
      // Cancel any ongoing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      try {
        setError(null);
        setCurrentResponse("");
        setIsGenerating(true);

        // Create abort controller for this request
        const abortController = new AbortController();
        abortControllerRef.current = abortController;

        // Map action to endpoint
        const endpointMap = {
          generate: "/api/generate",
          edit: "/api/edit",
          improve: "/api/improve",
        };

        const endpoint = endpointMap[action as keyof typeof endpointMap];
        if (!endpoint) {
          throw new Error(`Unknown action: ${action}`);
        }

        // Prepare request body based on action
        let requestBody: any;
        if (action === "generate") {
          requestBody = { prompt: content, context };
        } else {
          requestBody = { content, context };
        }

        console.log(`Starting SSE request to ${baseUrl}${endpoint}`);

        // Make fetch request
        const response = await fetch(`${baseUrl}${endpoint}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
          },
          body: JSON.stringify(requestBody),
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Handle SSE stream
        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error("No response body reader");
        }

        const decoder = new TextDecoder();
        let buffer = "";

        try {
          while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Process complete SSE messages
            const lines = buffer.split("\n");
            buffer = lines.pop() || ""; // Keep incomplete line in buffer

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                try {
                  const data = JSON.parse(line.slice(6)); // Remove 'data: ' prefix

                  switch (data.type) {
                    case "generation_start":
                    case "edit_start":
                    case "improve_start":
                      console.log("Stream started:", data.message);
                      break;

                    case "generation_chunk":
                    case "edit_chunk":
                    case "improve_chunk":
                      if (data.content) {
                        setCurrentResponse((prev) => prev + data.content);
                      }
                      break;

                    case "generation_complete":
                    case "edit_complete":
                    case "improve_complete":
                      console.log("Stream completed:", data.message);
                      setIsGenerating(false);
                      break;

                    case "error":
                      setError(data.message || "Unknown error occurred");
                      setIsGenerating(false);
                      break;

                    default:
                      console.warn("Unknown SSE event type:", data.type);
                  }
                } catch (parseError) {
                  console.error("Failed to parse SSE data:", parseError);
                }
              }
            }
          }
        } finally {
          reader.releaseLock();
        }
      } catch (err: any) {
        if (err.name === "AbortError") {
          console.log("Request was aborted");
        } else {
          console.error("SSE request failed:", err);
          setError(err.message || "Request failed");
        }
        setIsGenerating(false);
      }
    },
    [baseUrl]
  );

  return {
    isConnected,
    sendMessage,
    isGenerating,
    currentResponse,
    error,
  };
}
