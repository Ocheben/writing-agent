import { useState } from "react";
import { WritingEditor } from "./components/WritingEditor";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { useSSE } from "./hooks/useSSE";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [document, setDocument] = useState({
    title: "Untitled Document",
    content: "",
  });

  const { isConnected, sendMessage, isGenerating, currentResponse, error } =
    useSSE();

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <Header
        title={document.title}
        onTitleChange={(title) => setDocument((prev) => ({ ...prev, title }))}
        isConnected={isConnected}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          document={document}
          onDocumentChange={setDocument}
        />

        {/* Main Editor Area */}
        <div className="flex-1 flex flex-col">
          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 mx-6 mt-4 rounded">
              <strong className="font-bold">Error: </strong>
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          <div className="flex-1 overflow-auto">
            <div className="max-w-4xl mx-auto p-6">
              <WritingEditor
                content={document.content}
                onContentChange={(content) =>
                  setDocument((prev) => ({ ...prev, content }))
                }
                onAIRequest={sendMessage}
                isGenerating={isGenerating}
                aiResponse={currentResponse}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
