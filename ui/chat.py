"""Chat message rendering and management for the Belfanti CNC Manufacturing POC."""

import json

import streamlit as st

from ui.theme import COLORS


# ---------------------------------------------------------------------------
# Emoji mapping for known tool names
# ---------------------------------------------------------------------------

_TOOL_EMOJIS: dict[str, str] = {
    "parse_email": "\U0001F4E7",       # envelope
    "identify_customer": "\U0001F464",  # bust in silhouette
    "extract_parts": "\U0001F529",      # nut and bolt
    "validate_parts": "\u2705",         # check mark
    "log_tracking": "\U0001F4CB",       # clipboard
    "store_cad_files": "\U0001F4C1",    # file folder
    "search_vendors": "\U0001F50D",     # magnifying glass
    "send_vendor_rfqs": "\U0001F4E4",   # outbox tray
    "receive_vendor_bids": "\U0001F4E5",  # inbox tray
    "select_vendor": "\U0001F3AF",      # bullseye
    "calculate_cost": "\U0001F4B0",     # money bag
    "build_quote": "\U0001F4DD",        # memo
    "review_quote": "\U0001F9D0",       # monocle
    "create_qb_product": "\U0001F4E6",  # package
    "create_qb_estimate": "\U0001F4CA",  # bar chart
    "send_quote": "\U0001F4E8",         # incoming envelope
    "receive_response": "\U0001F4EC",   # mailbox with mail
    "create_po": "\U0001F4C4",          # page facing up
    "create_work_order": "\U0001F3ED",  # factory
}

_DEFAULT_TOOL_EMOJI = "\U0001F527"  # wrench

# ---------------------------------------------------------------------------
# Human-readable present-participle descriptions for tool calls
# ---------------------------------------------------------------------------

_TOOL_DESCRIPTIONS: dict[str, str] = {
    "parse_email": "Parsing incoming email",
    "identify_customer": "Identifying customer",
    "extract_parts": "Extracting part specifications",
    "validate_parts": "Validating part requirements",
    "log_tracking": "Logging to tracking sheet",
    "store_cad_files": "Storing CAD files to Drive",
    "search_vendors": "Searching vendor database",
    "send_vendor_rfqs": "Sending RFQs to vendors",
    "receive_vendor_bids": "Receiving vendor bids",
    "select_vendor": "Selecting best vendor",
    "calculate_cost": "Calculating cost breakdown",
    "build_quote": "Building customer quote",
    "review_quote": "Reviewing quote for approval",
    "create_qb_product": "Creating QuickBooks product",
    "create_qb_estimate": "Creating QuickBooks estimate",
    "send_quote": "Sending quote to customer",
    "receive_response": "Processing customer response",
    "create_po": "Creating purchase order",
    "create_work_order": "Generating work order",
}


def _tool_emoji(tool_name: str) -> str:
    """Return an emoji for the given tool name."""
    return _TOOL_EMOJIS.get(tool_name, _DEFAULT_TOOL_EMOJI)


def _render_tool_call(item: dict) -> None:
    """Render a single tool-call block inside an st.expander."""
    tool_name = item.get("tool_name", "unknown_tool")
    tool_input = item.get("tool_input", {})
    tool_result = item.get("tool_result", "")

    # Determine whether the result looks like an error.
    is_error = False
    if isinstance(tool_result, str):
        lower = tool_result.lower()
        is_error = lower.startswith("error") or lower.startswith("failed")
    elif isinstance(tool_result, dict):
        is_error = tool_result.get("error") is not None or tool_result.get("status") == "error"

    emoji = _tool_emoji(tool_name)
    description = _TOOL_DESCRIPTIONS.get(tool_name, tool_name.replace("_", " ").title())
    label = f"{emoji} {description}"

    with st.expander(label, expanded=False):
        # Status pill + raw tool name
        pill_class = "fail" if is_error else "ok"
        pill_text = "FAIL" if is_error else "OK"
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">'
            f'<span style="font-size:0.75rem;color:{COLORS["text_muted"]}">`{tool_name}`</span>'
            f'<span class="status-pill {pill_class}">{pill_text}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Input section
        st.markdown(
            f'<div class="section-label">Input</div>',
            unsafe_allow_html=True,
        )
        try:
            formatted_input = json.dumps(tool_input, indent=2, default=str)
        except (TypeError, ValueError):
            formatted_input = str(tool_input)
        st.code(formatted_input, language="json")

        # Result section
        st.markdown(
            f'<div class="section-label">Result</div>',
            unsafe_allow_html=True,
        )
        if is_error:
            st.error(str(tool_result))
        else:
            try:
                if isinstance(tool_result, str):
                    parsed = json.loads(tool_result)
                    formatted_result = json.dumps(parsed, indent=2, default=str)
                elif isinstance(tool_result, dict):
                    formatted_result = json.dumps(tool_result, indent=2, default=str)
                else:
                    formatted_result = str(tool_result)
            except (json.JSONDecodeError, TypeError, ValueError):
                formatted_result = str(tool_result)
            st.code(formatted_result, language="json")


def render_chat_messages() -> None:
    """Render all messages stored in ``st.session_state["messages"]``."""
    messages: list[dict] = st.session_state.get("messages", [])

    for msg in messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")

        with st.chat_message(role):
            if isinstance(content, str):
                st.markdown(content)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, str):
                        st.markdown(item)
                    elif isinstance(item, dict):
                        item_type = item.get("type", "")
                        if item_type == "text":
                            st.markdown(item.get("text", ""))
                        elif item_type == "tool_call":
                            _render_tool_call(item)
                        else:
                            # Fallback: render as JSON
                            st.json(item)


def add_message(role: str, content: str) -> None:
    """Append a plain-text message to session state."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    st.session_state["messages"].append({"role": role, "content": content})


def add_tool_message(tool_name: str, tool_input: dict, tool_result: str) -> None:
    """Append a tool-call record as an assistant message.

    The message is stored with a list-based content block so that the chat
    renderer can display it inside an expander with formatted JSON.
    """
    entry = {
        "type": "tool_call",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_result": tool_result,
    }

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    st.session_state["messages"].append({
        "role": "assistant",
        "content": [entry],
    })


def render_agent_event(event_type: str, data) -> None:
    """Process a single event yielded by the orchestrator generator.

    Supported *event_type* values:

    * ``"text"`` -- streaming text delta; appended to the current assistant
      message and rendered inline.
    * ``"tool_call"`` -- a tool invocation about to execute.  *data* should be
      a dict with ``tool_name`` and ``tool_input`` keys.
    * ``"tool_result"`` -- result of the most recent tool call.  *data* should
      be a dict with ``tool_name``, ``tool_input``, and ``tool_result`` keys.
    * ``"error"`` -- an error string to display prominently.
    """
    if event_type == "text":
        # Append text to the last assistant message (create one if needed).
        messages: list[dict] = st.session_state.get("messages", [])
        if messages and messages[-1].get("role") == "assistant" and isinstance(messages[-1].get("content"), str):
            messages[-1]["content"] += str(data)
        else:
            add_message("assistant", str(data))
        st.markdown(str(data))

    elif event_type == "tool_call":
        if isinstance(data, dict):
            tool_name = data.get("tool_name", "unknown_tool")
            tool_input = data.get("tool_input", {})
            emoji = _tool_emoji(tool_name)
            description = _TOOL_DESCRIPTIONS.get(tool_name, tool_name.replace("_", " ").title())
            with st.expander(f"{emoji} {description}", expanded=True):
                st.caption(f"`{tool_name}`")
                st.markdown(
                    f'<div class="section-label">Input</div>',
                    unsafe_allow_html=True,
                )
                try:
                    st.code(json.dumps(tool_input, indent=2, default=str), language="json")
                except (TypeError, ValueError):
                    st.code(str(tool_input), language="json")

    elif event_type == "tool_result":
        if isinstance(data, dict):
            add_tool_message(
                tool_name=data.get("tool_name", "unknown_tool"),
                tool_input=data.get("tool_input", {}),
                tool_result=data.get("tool_result", ""),
            )

    elif event_type == "error":
        st.error(str(data))
