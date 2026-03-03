"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Send } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Paste an RFQ email or describe what you need...",
}: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    }
  }, [value]);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setValue("");
    }
  }, [value, disabled, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <div className="p-4 border-t border-border/50 glass">
      <div className="flex gap-2 items-end">
        <div className="flex-1 relative">
          <Textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={2}
            className={`resize-none pr-20 transition-opacity duration-200 ${
              disabled ? "opacity-50" : ""
            }`}
          />
          <span className="absolute bottom-2 right-3 text-[10px] text-text-muted select-none pointer-events-none">
            Enter to send
          </span>
        </div>
        <Button
          size="icon"
          onClick={handleSend}
          disabled={!canSend}
          className={`h-10 w-10 rounded-lg transition-all duration-200 ${
            canSend
              ? "bg-accent-blue hover:bg-accent-blue/90 hover:shadow-glow-blue"
              : "bg-bg-elevated text-text-muted"
          }`}
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
