"""Sidebar rendering for the Belfanti CNC Manufacturing POC."""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st

from data.sample_rfqs import SAMPLE_RFQS
from ui.theme import COLORS, gradient_divider


# ---------------------------------------------------------------------------
# Module group definitions
# ---------------------------------------------------------------------------

_MODULE_GROUPS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "RFQ Intake",
        [
            ("email_intake", "Email Intake"),
            ("quote_extraction", "Quote Extraction"),
            ("tracking", "Tracking"),
        ],
    ),
    (
        "Quoting",
        [
            ("material_rfq", "Material RFQ"),
            ("quote_preparation", "Quote Preparation"),
            ("quickbooks", "QuickBooks"),
            ("approval_gates", "Approval Gates"),
        ],
    ),
    (
        "Order Processing",
        [
            ("customer_response", "Customer Response"),
            ("purchase_order", "Purchase Order"),
            ("work_order", "Work Order"),
        ],
    ),
]

# Demo button definitions: (label, description, variant style)
_DEMO_BUTTONS = [
    ("Simple: Aluminum Bracket", "Basic single-part RFQ, standard lead time", "outline"),
    ("Medium: Steel Shaft + Housing", "Multi-part RFQ with material sourcing", "outline"),
    ("Complex: Medical Device (Rush)", "Multi-part rush order with tight tolerances", "default"),
]


def _load_env_api_key() -> str:
    """Attempt to read an Anthropic API key from a .env file."""
    try:
        from dotenv import dotenv_values
        values = dotenv_values()
        return values.get("ANTHROPIC_API_KEY", "")
    except ImportError:
        pass

    # Fallback: read manually from the environment / .env file next to cwd.
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.isfile(env_path):
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("\"'")
    return os.environ.get("ANTHROPIC_API_KEY", "")


def _format_rfq_as_email(rfq: dict) -> str:
    """Convert a sample RFQ dict into a human-readable email string."""
    parts = [
        f"From: {rfq['customer_name']} <{rfq['customer_email']}>",
        f"Company: {rfq['customer_company']}",
        f"Subject: {rfq['subject']}",
        "",
        rfq["body"],
    ]
    if rfq.get("attachments"):
        parts.append("")
        parts.append("Attachments:")
        for att in rfq["attachments"]:
            parts.append(f"  - {att}")
    return "\n".join(parts)


def _sidebar_gradient_divider() -> None:
    """Sidebar-specific thinner gradient divider."""
    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,'
        f'{COLORS["blue"]}30 0%,{COLORS["border_subtle"]}50 50%,transparent 100%);'
        'margin:0.75rem 0"></div>',
        unsafe_allow_html=True,
    )


def _connection_indicator(connected: bool) -> str:
    """Return a small coloured dot + label HTML for API connection status."""
    if connected:
        return (
            f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:0.75rem;color:{COLORS["green"]}">'
            f'<span style="width:6px;height:6px;border-radius:50%;background:{COLORS["green"]};display:inline-block"></span>'
            'Connected</span>'
        )
    return (
        f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:0.75rem;color:{COLORS["amber"]}">'
        f'<span style="width:6px;height:6px;border-radius:50%;background:{COLORS["amber"]};display:inline-block"></span>'
        'Not connected</span>'
    )


# ---------------------------------------------------------------------------
# Main sidebar renderer
# ---------------------------------------------------------------------------

def render_sidebar() -> Optional[str]:
    """Render the application sidebar and return any demo message to inject.

    Returns
    -------
    str or None
        The formatted RFQ email text if a demo button was clicked, otherwise
        ``None``.
    """
    demo_message: Optional[str] = None

    with st.sidebar:
        # ---- Branding block ------------------------------------------------
        st.markdown(
            f"""
            <div style="text-align:center;padding:0.5rem 0 0.25rem 0">
                <div style="font-size:1.3rem;font-weight:700;color:{COLORS['text_primary']};
                            letter-spacing:0.02em">
                    Belfanti CNC
                </div>
                <div style="font-size:0.8rem;color:{COLORS['text_muted']};margin-top:0.15rem">
                    Manufacturing Pipeline Assistant
                </div>
                <div style="height:2px;width:60px;margin:0.6rem auto 0 auto;
                            background:linear-gradient(90deg,{COLORS['blue']},{COLORS['blue']}80);
                            border-radius:1px"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _sidebar_gradient_divider()

        # ---- API Key -------------------------------------------------------
        st.markdown(
            f'<div class="section-label">API Configuration</div>',
            unsafe_allow_html=True,
        )

        # Seed from .env / environment if the user has not yet entered one.
        if not st.session_state.get("api_key"):
            env_key = _load_env_api_key()
            if env_key:
                st.session_state["api_key"] = env_key

        api_key = st.text_input(
            "Anthropic API Key",
            value=st.session_state.get("api_key", ""),
            type="password",
            key="sidebar_api_key_input",
            placeholder="sk-ant-...",
            label_visibility="collapsed",
        )
        st.session_state["api_key"] = api_key

        # Connection status indicator
        st.markdown(
            _connection_indicator(bool(api_key)),
            unsafe_allow_html=True,
        )

        _sidebar_gradient_divider()

        # ---- Module Toggles ------------------------------------------------
        st.markdown(
            f'<div class="section-label">Modules</div>',
            unsafe_allow_html=True,
        )

        enabled: list[str] = list(st.session_state.get("enabled_modules", []))

        for group_label, modules in _MODULE_GROUPS:
            st.markdown(
                f'<div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;'
                f'letter-spacing:0.06em;color:{COLORS["text_muted"]};margin:0.6rem 0 0.25rem 0">'
                f'{group_label}</div>',
                unsafe_allow_html=True,
            )
            for module_key, display_name in modules:
                is_on = st.toggle(
                    display_name,
                    value=(module_key in enabled),
                    key=f"toggle_{module_key}",
                )
                if is_on and module_key not in enabled:
                    enabled.append(module_key)
                elif not is_on and module_key in enabled:
                    enabled.remove(module_key)

        st.session_state["enabled_modules"] = enabled

        _sidebar_gradient_divider()

        # ---- Demo Quick Start ----------------------------------------------
        st.markdown(
            f'<div class="section-label">Demo Quick Start</div>',
            unsafe_allow_html=True,
        )

        for idx, (label, description, variant) in enumerate(_DEMO_BUTTONS):
            # Use primary style for the complex/rush demo, secondary for others
            btn_type = "primary" if variant == "default" else "secondary"
            if st.button(label, key=f"demo_btn_{idx}", use_container_width=True, type=btn_type):
                demo_message = _format_rfq_as_email(SAMPLE_RFQS[idx])
            st.markdown(
                f'<div style="font-size:0.7rem;color:{COLORS["text_muted"]};'
                f'margin:-0.5rem 0 0.5rem 0;padding-left:0.25rem">{description}</div>',
                unsafe_allow_html=True,
            )

        _sidebar_gradient_divider()

        # ---- Reset ----------------------------------------------------------
        if st.button(
            "\U0001f5d1  Reset Session",
            key="reset_btn",
            type="secondary",
            use_container_width=True,
        ):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    return demo_message
