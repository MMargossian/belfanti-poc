"use client";

import { useState, useCallback, useRef } from "react";
import type { ChatMessage, ToolCall, ApprovalGate, PipelineState } from "@/lib/types";
import { streamSSE } from "@/lib/sse-client";

interface UseChatOptions {
  sessionId: string;
  onPipelineUpdate: (data: PipelineState) => void;
}

export function useChat({ sessionId, onPipelineUpdate }: UseChatOptions) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [approvalGate, setApprovalGate] = useState<ApprovalGate | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const currentAssistantRef = useRef<string>("");
  const currentToolCallsRef = useRef<ToolCall[]>([]);

  const addUserMessage = useCallback((content: string) => {
    const msg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, msg]);
  }, []);

  const sendMessage = useCallback(
    async (message: string) => {
      if (!sessionId || isStreaming) return;

      addUserMessage(message);
      setIsStreaming(true);
      currentAssistantRef.current = "";
      currentToolCallsRef.current = [];

      // Create a placeholder assistant message
      const assistantId = crypto.randomUUID();
      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          role: "assistant",
          content: "",
          toolCalls: [],
          timestamp: Date.now(),
        },
      ]);

      const controller = new AbortController();
      abortRef.current = controller;

      await streamSSE(
        "/api/agent/run",
        { message },
        sessionId,
        {
          onText: (content) => {
            currentAssistantRef.current += content;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: currentAssistantRef.current }
                  : m
              )
            );
          },
          onToolCall: (toolName, toolInput) => {
            const tc: ToolCall = {
              tool_name: toolName,
              tool_input: toolInput,
              status: "running",
            };
            currentToolCallsRef.current = [...currentToolCallsRef.current, tc];
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, toolCalls: [...currentToolCallsRef.current] }
                  : m
              )
            );
          },
          onToolResult: (toolName, result) => {
            currentToolCallsRef.current = currentToolCallsRef.current.map((tc) =>
              tc.tool_name === toolName && tc.status === "running"
                ? { ...tc, result, status: result.includes('"error"') ? "fail" : "ok" }
                : tc
            );
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, toolCalls: [...currentToolCallsRef.current] }
                  : m
              )
            );
          },
          onPipelineUpdate: (data) => {
            onPipelineUpdate(data);
          },
          onApprovalNeeded: (gateName, gateData) => {
            setApprovalGate({ gate_name: gateName, gate_data: gateData });
          },
          onError: (msg) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: m.content + `\n\n**Error:** ${msg}` }
                  : m
              )
            );
          },
          onDone: () => {
            setIsStreaming(false);
            abortRef.current = null;
          },
        },
        controller.signal
      );
    },
    [sessionId, isStreaming, addUserMessage, onPipelineUpdate]
  );

  const submitApproval = useCallback(
    async (decision: string, feedback: string = "") => {
      if (!sessionId || !approvalGate) return;

      const gateName = approvalGate.gate_name;
      setApprovalGate(null);
      setIsStreaming(true);

      // Add user decision message
      const decisionText = feedback
        ? `[${decision.toUpperCase()}] ${feedback}`
        : `[${decision.toUpperCase()}]`;
      addUserMessage(decisionText);

      currentAssistantRef.current = "";
      currentToolCallsRef.current = [];

      const assistantId = crypto.randomUUID();
      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          role: "assistant",
          content: "",
          toolCalls: [],
          timestamp: Date.now(),
        },
      ]);

      const controller = new AbortController();
      abortRef.current = controller;

      await streamSSE(
        "/api/approval/submit",
        { gate_name: gateName, decision, feedback },
        sessionId,
        {
          onText: (content) => {
            currentAssistantRef.current += content;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: currentAssistantRef.current }
                  : m
              )
            );
          },
          onToolCall: (toolName, toolInput) => {
            const tc: ToolCall = {
              tool_name: toolName,
              tool_input: toolInput,
              status: "running",
            };
            currentToolCallsRef.current = [...currentToolCallsRef.current, tc];
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, toolCalls: [...currentToolCallsRef.current] }
                  : m
              )
            );
          },
          onToolResult: (toolName, result) => {
            currentToolCallsRef.current = currentToolCallsRef.current.map((tc) =>
              tc.tool_name === toolName && tc.status === "running"
                ? { ...tc, result, status: result.includes('"error"') ? "fail" : "ok" }
                : tc
            );
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, toolCalls: [...currentToolCallsRef.current] }
                  : m
              )
            );
          },
          onPipelineUpdate: (data) => {
            onPipelineUpdate(data);
          },
          onApprovalNeeded: (gn, gd) => {
            setApprovalGate({ gate_name: gn, gate_data: gd });
          },
          onError: (msg) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: m.content + `\n\n**Error:** ${msg}` }
                  : m
              )
            );
          },
          onDone: () => {
            setIsStreaming(false);
            abortRef.current = null;
          },
        },
        controller.signal
      );
    },
    [sessionId, approvalGate, addUserMessage, onPipelineUpdate]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setApprovalGate(null);
    setIsStreaming(false);
    abortRef.current?.abort();
  }, []);

  return {
    messages,
    isStreaming,
    approvalGate,
    sendMessage,
    submitApproval,
    clearMessages,
  };
}
