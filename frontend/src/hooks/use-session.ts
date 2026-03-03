"use client";

import { useState, useEffect, useCallback } from "react";
import { createSession, resetSession, setApiKey as apiSetKey } from "@/lib/api";

const SESSION_KEY = "belfanti-session-id";
const ENV_KEY_FLAG = "belfanti-has-env-key";

export function useSession() {
  const [sessionId, setSessionId] = useState<string>("");
  const [apiKey, setApiKeyState] = useState<string>("");
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(SESSION_KEY);
    if (stored) {
      setSessionId(stored);
      // If the backend had an env key last time, restore that flag
      if (localStorage.getItem(ENV_KEY_FLAG) === "true") {
        setApiKeyState("env");
      }
      setIsReady(true);
    } else {
      createSession().then((res) => {
        localStorage.setItem(SESSION_KEY, res.session_id);
        setSessionId(res.session_id);
        if (res.has_api_key) {
          localStorage.setItem(ENV_KEY_FLAG, "true");
          setApiKeyState("env");
        }
        setIsReady(true);
      });
    }
  }, []);

  const reset = useCallback(async () => {
    if (sessionId) {
      await resetSession(sessionId);
    }
    const res = await createSession();
    localStorage.setItem(SESSION_KEY, res.session_id);
    setSessionId(res.session_id);
    if (res.has_api_key) {
      localStorage.setItem(ENV_KEY_FLAG, "true");
      setApiKeyState("env");
    } else {
      localStorage.removeItem(ENV_KEY_FLAG);
      setApiKeyState("");
    }
  }, [sessionId]);

  const setApiKey = useCallback(
    async (key: string) => {
      if (sessionId) {
        await apiSetKey(sessionId, key);
        setApiKeyState(key);
      }
    },
    [sessionId]
  );

  return { sessionId, apiKey, isReady, reset, setApiKey };
}
