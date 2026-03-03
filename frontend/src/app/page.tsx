"use client";

import { useSession } from "@/hooks/use-session";
import { useChat } from "@/hooks/use-chat";
import { usePipeline } from "@/hooks/use-pipeline";
import { AppShell } from "@/components/layout/app-shell";
import { Header } from "@/components/layout/header";
import { PipelineView } from "@/components/pipeline/pipeline-view";
import { ChatContainer } from "@/components/chat/chat-container";
import { ChatInput } from "@/components/chat/chat-input";
import { ApprovalDialog } from "@/components/approval/approval-dialog";

export default function Home() {
  const { sessionId, apiKey, isReady, reset, setApiKey } = useSession();
  const { pipeline, updatePipeline, resetPipeline } = usePipeline();
  const {
    messages,
    isStreaming,
    approvalGate,
    sendMessage,
    submitApproval,
    clearMessages,
  } = useChat({ sessionId, onPipelineUpdate: updatePipeline });

  const handleReset = async () => {
    await reset();
    clearMessages();
    resetPipeline();
  };

  const handleDemoLoad = (message: string) => {
    if (apiKey) {
      sendMessage(message);
    }
  };

  if (!isReady) {
    return (
      <div className="flex items-center justify-center h-screen bg-bg-primary">
        <div className="text-text-muted">Loading...</div>
      </div>
    );
  }

  return (
    <AppShell
      sessionId={sessionId}
      apiKey={apiKey}
      onApiKeyChange={setApiKey}
      onDemoLoad={handleDemoLoad}
      onReset={handleReset}
    >
      <div className="flex flex-col h-full">
        <Header />
        <PipelineView pipeline={pipeline} />
        <ChatContainer messages={messages} />
        {approvalGate && (
          <ApprovalDialog gate={approvalGate} onSubmit={submitApproval} />
        )}
        <ChatInput
          onSend={sendMessage}
          disabled={isStreaming || !!approvalGate || !apiKey}
          placeholder={
            !apiKey
              ? "Enter your API key in the sidebar to get started..."
              : "Paste an RFQ email or describe what you need..."
          }
        />
      </div>
    </AppShell>
  );
}
