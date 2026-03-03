"""Thread-safe in-memory session manager."""

import threading
import copy
from typing import Any


class SessionManager:
    """Stores per-session state in a thread-safe dict."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, dict[str, Any]] = {}

    def exists(self, session_id: str) -> bool:
        with self._lock:
            return session_id in self._sessions

    def create(self, session_id: str, defaults: dict[str, Any]) -> None:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = copy.deepcopy(defaults)

    def get(self, session_id: str, key: str, default: Any = None) -> Any:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return default
            return session.get(key, default)

    def set(self, session_id: str, key: str, value: Any) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is not None:
                session[key] = value

    def get_all(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            return copy.deepcopy(session)

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)


# Module-level singleton
session_manager = SessionManager()
