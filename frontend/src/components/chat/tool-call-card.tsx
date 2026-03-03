"use client";

import { useState } from "react";
import { Loader2, CheckCircle2, XCircle, Wrench, ChevronDown, ChevronRight } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { TOOL_ICONS, TOOL_DESCRIPTIONS } from "@/lib/constants";
import type { ToolCall } from "@/lib/types";

interface ToolCallCardProps {
  toolCall: ToolCall;
}

export function ToolCallCard({ toolCall }: ToolCallCardProps) {
  const [isOpen, setIsOpen] = useState(false);
  const ToolIcon = TOOL_ICONS[toolCall.tool_name] || Wrench;
  const description =
    TOOL_DESCRIPTIONS[toolCall.tool_name] ||
    toolCall.tool_name.replace(/_/g, " ");

  const isRunning = toolCall.status === "running";
  const isSuccess = toolCall.status === "ok";
  const isFailed = toolCall.status === "fail";

  const borderColor = isRunning
    ? "border-accent-blue/30"
    : isSuccess
      ? "border-accent-green/30"
      : isFailed
        ? "border-accent-red/30"
        : "border-border-subtle";

  const glowClass = isRunning
    ? "shadow-glow-blue"
    : isSuccess
      ? ""
      : isFailed
        ? "shadow-glow-red"
        : "";

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger
        className={`flex items-center justify-between w-full p-2.5 rounded-lg glass glass-border hover:bg-bg-hover/60 transition-all duration-200 text-left ${borderColor} ${glowClass}`}
      >
        <div className="flex items-center gap-2.5">
          <ToolIcon className="w-4 h-4 text-text-secondary" />
          <span className="text-sm text-text-primary">{description}</span>
        </div>
        <div className="flex items-center gap-2">
          {isRunning && <Loader2 className="w-4 h-4 text-accent-blue animate-spin" />}
          {isSuccess && <CheckCircle2 className="w-4 h-4 text-accent-green" />}
          {isFailed && <XCircle className="w-4 h-4 text-accent-red" />}
          {isOpen ? (
            <ChevronDown className="w-3.5 h-3.5 text-text-muted" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 text-text-muted" />
          )}
        </div>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="mt-1 p-3 rounded-lg bg-bg-primary/80 border border-border-subtle/50 space-y-2 animate-fade-in">
          <p className="text-xs text-text-muted font-mono">{toolCall.tool_name}</p>
          <div>
            <p className="text-xs text-text-muted mb-1">Input</p>
            <pre className="text-xs bg-bg-secondary/80 p-2.5 rounded-md overflow-x-auto text-text-secondary font-mono">
              {JSON.stringify(toolCall.tool_input, null, 2)}
            </pre>
          </div>
          {toolCall.result && (
            <div>
              <p className="text-xs text-text-muted mb-1">Result</p>
              <pre className="text-xs bg-bg-secondary/80 p-2.5 rounded-md overflow-x-auto text-text-secondary font-mono max-h-48 overflow-y-auto">
                {(() => {
                  try {
                    return JSON.stringify(JSON.parse(toolCall.result), null, 2);
                  } catch {
                    return toolCall.result;
                  }
                })()}
              </pre>
            </div>
          )}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
