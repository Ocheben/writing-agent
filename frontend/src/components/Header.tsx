import React, { useState } from "react";
import { PenTool, Menu, Wifi, WifiOff } from "lucide-react";

interface HeaderProps {
  title: string;
  onTitleChange: (title: string) => void;
  isConnected: boolean;
  onToggleSidebar: () => void;
}

export function Header({
  title,
  onTitleChange,
  isConnected,
  onToggleSidebar,
}: HeaderProps) {
  const [isEditingTitle, setIsEditingTitle] = useState(false);

  return (
    <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="p-2 hover:bg-accent rounded-md transition-colors"
          >
            <Menu className="h-4 w-4" />
          </button>

          <div className="flex items-center gap-2">
            <PenTool className="h-5 w-5 text-primary" />
            <span className="font-semibold text-lg">Writing Agent</span>
          </div>
        </div>

        <div className="flex-1 max-w-md mx-4">
          {isEditingTitle ? (
            <input
              type="text"
              value={title}
              onChange={(e) => onTitleChange(e.target.value)}
              onBlur={() => setIsEditingTitle(false)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  setIsEditingTitle(false);
                }
              }}
              className="w-full text-center text-lg font-medium bg-transparent border-none outline-none focus:ring-2 focus:ring-ring rounded px-2 py-1"
              autoFocus
            />
          ) : (
            <button
              onClick={() => setIsEditingTitle(true)}
              className="w-full text-center text-lg font-medium hover:bg-accent rounded px-2 py-1 transition-colors"
            >
              {title}
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-sm">
            {isConnected ? (
              <>
                <Wifi className="h-4 w-4 text-green-500" />
                <span className="text-green-600">Connected</span>
              </>
            ) : (
              <>
                <WifiOff className="h-4 w-4 text-red-500" />
                <span className="text-red-600">Disconnected</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
