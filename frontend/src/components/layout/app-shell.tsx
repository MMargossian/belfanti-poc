"use client";

import { Sidebar } from "./sidebar";

interface AppShellProps {
  sessionId: string;
  apiKey: string;
  onApiKeyChange: (key: string) => void;
  onDemoLoad: (message: string) => void;
  onReset: () => void;
  children: React.ReactNode;
}

export function AppShell({
  sessionId,
  apiKey,
  onApiKeyChange,
  onDemoLoad,
  onReset,
  children,
}: AppShellProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-bg-primary">
      <Sidebar
        sessionId={sessionId}
        apiKey={apiKey}
        onApiKeyChange={onApiKeyChange}
        onDemoLoad={onDemoLoad}
        onReset={onReset}
      />
      <main className="flex-1 flex flex-col overflow-hidden transition-all duration-300">
        {children}
      </main>
    </div>
  );
}
