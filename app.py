"""
Belfanti CNC Manufacturing POC -- Streamlit entry point.

Run with:
    streamlit run app.py
"""

import json
import os

import streamlit as st
from dotenv import load_dotenv

from state.store import get_state, init_session_state, set_state

# ---------------------------------------------------------------------------
# Page configuration (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Belfanti CNC - AI Order Pipeline",
    page_icon="\U0001f3ed",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Environment & session bootstrap
# ---------------------------------------------------------------------------
load_dotenv()
init_session_state()

# Inject global dark-industrial theme
from ui.theme import inject_global_css, gradient_divider, COLORS  # noqa: E402
inject_global_css()

# Seed the API key from .env when available
env_key = os.getenv("ANTHROPIC_API_KEY", "")
if env_key and not get_state("api_key"):
    set_state("api_key", env_key)

# ---------------------------------------------------------------------------
# Late imports of UI components (they depend on session state being ready)
# ---------------------------------------------------------------------------
from ui.sidebar import render_sidebar  # noqa: E402
from ui.chat import add_message, render_chat_messages, _TOOL_DESCRIPTIONS  # noqa: E402
from ui.pipeline_view import render_pipeline_view  # noqa: E402
from ui.approval_dialog import render_approval_dialog  # noqa: E402

# Lazy import -- only instantiated when we actually need the agent
from agent.orchestrator import Orchestrator  # noqa: E402


# ===================================================================
# Agent event processing
# ===================================================================

def process_agent_events(event_generator) -> None:
    """Consume events from an :class:`Orchestrator` generator and render them.

    Event types handled:
        ("text", content)           -- streamed assistant text
        ("tool_call", name, input)  -- tool invocation header
        ("tool_result", name, data) -- tool return value
        ("approval_needed", gate, data) -- pause for human review
        ("error", message)          -- display an error
        ("done", None)              -- loop finished
    """
    full_text = ""
    text_placeholder = st.empty()
    tool_expanders: list = []

    for event in event_generator:
        event_type = event[0]

        # -- Streamed text --------------------------------------------------
        if event_type == "text":
            full_text += event[1]
            text_placeholder.markdown(full_text)

        # -- Tool call (show input in a collapsed expander) -----------------
        elif event_type == "tool_call":
            tool_name = event[1]
            tool_input = event[2]
            description = _TOOL_DESCRIPTIONS.get(tool_name, tool_name.replace("_", " ").title())
            emoji = _TOOL_EMOJIS_LOOKUP.get(tool_name, "\U0001f527")
            exp = st.expander(f"{emoji} {description}", expanded=False)
            exp.caption(f"`{tool_name}`")
            exp.json(tool_input)
            tool_expanders.append(exp)

        # -- Tool result (append output to the last expander) ---------------
        elif event_type == "tool_result":
            result = event[2]
            if tool_expanders:
                last_exp = tool_expanders[-1]
                try:
                    parsed = json.loads(result) if isinstance(result, str) else result
                    last_exp.json(parsed)
                except (json.JSONDecodeError, TypeError):
                    last_exp.code(str(result))

        # -- Approval gate --------------------------------------------------
        elif event_type == "approval_needed":
            gate_name = event[1]
            gate_data = event[2]
            set_state("approval_pending", gate_name)
            set_state("approval_gate_data", gate_data)

        # -- Error ----------------------------------------------------------
        elif event_type == "error":
            st.error(event[1])

        # -- Done (no-op) ---------------------------------------------------
        elif event_type == "done":
            pass

    # Persist the full assistant response in chat history
    if full_text:
        add_message("assistant", full_text)


# Quick lookup for streaming tool-call emojis (reuse from chat module)
from ui.chat import _TOOL_EMOJIS as _TOOL_EMOJIS_LOOKUP  # noqa: E402


# ===================================================================
# Layout
# ===================================================================

# ---- Sidebar (may return demo RFQ text when a sample button is clicked) ---
demo_rfq = render_sidebar()

# ---- Header --------------------------------------------------------------
st.markdown(
    f"""
    <div style="margin-bottom:0.25rem">
        <span style="font-size:1.75rem;font-weight:700;color:{COLORS['text_primary']}">
            AI-Powered Order Pipeline
        </span>
    </div>
    <div style="font-size:0.9rem;color:{COLORS['text_muted']};margin-bottom:0.75rem">
        From RFQ to Work Order
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Pipeline progress bar -----------------------------------------------
render_pipeline_view()

gradient_divider()

# ---- Chat history ---------------------------------------------------------
render_chat_messages()

# ---- Approval dialog (blocks chat input while waiting) --------------------
approval_pending = get_state("approval_pending")
if approval_pending:
    gate_data = get_state("approval_gate_data", {})
    result = render_approval_dialog(approval_pending, gate_data)
    if result:
        approval_result, feedback = result
        set_state("approval_pending", None)
        set_state("approval_result", approval_result)

        # Resume the agent with the human decision
        api_key = get_state("api_key")
        if api_key:
            orchestrator = Orchestrator(api_key)
            # Record the decision in the visible chat
            decision_text = (
                f"[{approval_result.upper()}] {feedback}"
                if feedback
                else f"[{approval_result.upper()}]"
            )
            add_message("user", decision_text)

            with st.chat_message("assistant"):
                process_agent_events(
                    orchestrator.resume_after_approval(approval_result, feedback)
                )
            st.rerun()

# ---- Chat input -----------------------------------------------------------
user_input = st.chat_input(
    "Paste an RFQ email or describe what you need\u2026",
    disabled=bool(get_state("agent_running")) or bool(approval_pending),
)

# Either the demo button or the chat box can provide a message to process
message_to_process = demo_rfq or user_input

if message_to_process and not approval_pending:
    api_key = get_state("api_key")
    if not api_key:
        st.warning(
            "\u26a0\ufe0f  Please enter your Anthropic API key in the sidebar to get started."
        )
    else:
        # Show the user message immediately
        add_message("user", message_to_process)
        with st.chat_message("user"):
            st.markdown(message_to_process)

        # Kick off the agentic loop
        orchestrator = Orchestrator(api_key)
        with st.chat_message("assistant"):
            process_agent_events(orchestrator.run(message_to_process))

        st.rerun()
