"""
State store backed by contextvars + SessionManager.
Replaces the Streamlit session_state layer while keeping identical
get_state / set_state / init_session_state signatures.
"""

import contextvars
from typing import Any

from state.pipeline import PipelineState

# ContextVar holds the current session ID (set by middleware on each request)
_current_session_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_session_id"
)

# Lazy import to avoid circular deps — filled on first use
_manager = None


def _get_manager():
    global _manager
    if _manager is None:
        from session.manager import session_manager
        _manager = session_manager
    return _manager


SESSION_DEFAULTS: dict[str, Any] = {
    "messages": [],
    "pipeline_state": None,  # Will be PipelineState() when created
    "rfq": None,
    "parts": [],
    "customer": None,
    "vendor_quotes": [],
    "selected_vendor_quote": None,
    "quote": None,
    "purchase_order": None,
    "sales_order": None,
    "work_order": None,
    "tracking_sheet_rows": [],
    "drive_files": [],
    "api_key": "",
    "enabled_modules": [
        "email_intake",
        "quote_extraction",
        "tracking",
        "material_rfq",
        "quote_preparation",
        "quickbooks",
        "approval_gates",
        "customer_response",
        "purchase_order",
        "work_order",
    ],
    "approval_pending": None,
    "approval_gate_data": {},
    "approval_result": None,
    "agent_messages": [],
    "agent_running": False,
}


def get_session_id() -> str:
    """Return the session ID for the current request context."""
    return _current_session_id.get()


def set_session_id(session_id: str) -> None:
    """Set the session ID in the current context (called by middleware)."""
    _current_session_id.set(session_id)


def init_session_state() -> None:
    """Ensure current session exists in the manager with all default keys."""
    sid = get_session_id()
    mgr = _get_manager()
    if not mgr.exists(sid):
        defaults = {k: v for k, v in SESSION_DEFAULTS.items()}
        defaults["pipeline_state"] = PipelineState()
        mgr.create(sid, defaults)


def get_state(key: str, default=None) -> Any:
    """Retrieve a value from the current session."""
    sid = get_session_id()
    return _get_manager().get(sid, key, default)


def set_state(key: str, value: Any) -> None:
    """Set a value in the current session."""
    sid = get_session_id()
    _get_manager().set(sid, key, value)
