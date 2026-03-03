"use client";

import { useRef, useCallback } from "react";
import { streamSSE, type SSECallbacks } from "@/lib/sse-client";

export function useSSE() {
  const abortRef = useRef<AbortController | null>(null);

  const start = useCallback(
    (
      path: string,
      body: Record<string, unknown>,
      sessionId: string,
      callbacks: SSECallbacks
    ) => {
      // Abort any existing stream
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      streamSSE(path, body, sessionId, callbacks, controller.signal);
    },
    []
  );

  const stop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  return { start, stop };
}
