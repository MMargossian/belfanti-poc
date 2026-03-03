import streamlit as st

from state.pipeline import PipelineState


def init_session_state() -> None:
    """Initialize all session state keys with their defaults if not already set."""
    defaults = {
        "messages": [],
        "pipeline_state": PipelineState(),
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
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_state(key: str, default=None):
    """Retrieve a value from session state, returning *default* if the key is missing."""
    return st.session_state.get(key, default)


def set_state(key: str, value) -> None:
    """Set a value in session state."""
    st.session_state[key] = value
