"use client";

import { useEffect, useRef } from "react";
import { MessageSquare } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage } from "./chat-message";
import type { ChatMessage as ChatMessageType } from "@/lib/types";

interface ChatContainerProps {
  messages: ChatMessageType[];
}

export function ChatContainer({ messages }: ChatContainerProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <ScrollArea className="flex-1 relative">
      {/* Gradient fade at top */}
      <div className="sticky top-0 h-6 bg-gradient-to-b from-bg-primary to-transparent z-10 pointer-events-none" />
      <div className="px-6 pb-6">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-64 text-text-muted animate-fade-in">
            <div className="text-center">
              <div className="inline-flex p-4 rounded-2xl bg-bg-elevated/50 border border-border-subtle mb-4">
                <MessageSquare className="w-8 h-8 text-text-muted" />
              </div>
              <p className="text-base font-medium text-text-secondary mb-1">
                Ready to process
              </p>
              <p className="text-sm text-text-muted">
                Paste an RFQ email or select a sample to get started
              </p>
            </div>
          </div>
        )}
        {messages.map((msg) => (
          <div key={msg.id} className="animate-fade-in">
            <ChatMessage message={msg} />
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
