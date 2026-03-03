import { User, Bot } from "lucide-react";
import { StreamingText } from "./streaming-text";
import { ToolCallCard } from "./tool-call-card";
import type { ChatMessage as ChatMessageType } from "@/lib/types";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  const time = new Date(message.timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""} mb-4 animate-slide-up`}>
      {/* Avatar */}
      <div className="flex-shrink-0 mt-1">
        {isUser ? (
          <div className="w-8 h-8 rounded-full bg-accent-blue/20 border border-accent-blue/30 flex items-center justify-center">
            <User className="w-4 h-4 text-accent-blue" />
          </div>
        ) : (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent-blue/30 to-accent-green/30 border border-accent-blue/20 flex items-center justify-center">
            <Bot className="w-4 h-4 text-accent-blue" />
          </div>
        )}
      </div>

      {/* Message bubble */}
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 glass glass-border ${
          isUser
            ? "bg-accent-blue/10 border-accent-blue/20"
            : "bg-bg-elevated/60 border-border-subtle/50"
        }`}
      >
        <StreamingText content={message.content} />
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.toolCalls.map((tc, i) => (
              <ToolCallCard key={`${tc.tool_name}-${i}`} toolCall={tc} />
            ))}
          </div>
        )}
        <p className="text-[10px] text-text-muted mt-2 select-none">{time}</p>
      </div>
    </div>
  );
}
