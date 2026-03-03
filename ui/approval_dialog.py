"""Approval gate dialog for the Belfanti CNC Manufacturing POC.

When the agent pipeline reaches a human-approval gate (e.g. quote review or
email review), this module renders an interactive approval dialog and returns
the user's decision so the orchestrator can continue.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from ui.theme import COLORS


def _render_quote_review(gate_data: dict) -> None:
    """Display a quote review summary with line items."""
    customer = gate_data.get("customer_name", "Unknown Customer")
    total = gate_data.get("total_amount")
    summary = gate_data.get("summary", "")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div style="background:{COLORS["bg_elevated"]};padding:0.75rem 1rem;'
            f'border-radius:8px;border:1px solid {COLORS["border"]}">'
            f'<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;'
            f'color:{COLORS["text_muted"]};margin-bottom:0.25rem">Customer</div>'
            f'<div style="font-size:1.1rem;font-weight:600;color:{COLORS["text_primary"]}">'
            f'{customer}</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        if total is not None:
            st.markdown(
                f'<div style="background:{COLORS["bg_elevated"]};padding:0.75rem 1rem;'
                f'border-radius:8px;border:1px solid {COLORS["border"]}">'
                f'<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;'
                f'color:{COLORS["text_muted"]};margin-bottom:0.25rem">Quote Total</div>'
                f'<div style="font-size:1.1rem;font-weight:600;color:{COLORS["green"]}">'
                f'${total:,.2f}</div></div>',
                unsafe_allow_html=True,
            )

    if summary:
        st.markdown(summary)

    # Line items table
    line_items = gate_data.get("line_items", [])
    if line_items:
        st.markdown(
            f'<div class="section-label" style="margin-top:0.75rem">Line Items</div>',
            unsafe_allow_html=True,
        )
        df = pd.DataFrame(line_items)
        st.dataframe(df, use_container_width=True, hide_index=True)


def _render_email_review(gate_data: dict) -> None:
    """Display an email preview for review."""
    to_addr = gate_data.get("to", "")
    subject = gate_data.get("subject", "")
    body = gate_data.get("body", "")
    attachments = gate_data.get("attachments", [])

    st.markdown(f"**To:** {to_addr}")
    st.markdown(f"**Subject:** {subject}")

    st.markdown(
        f'<div class="section-label" style="margin-top:0.5rem">Body</div>',
        unsafe_allow_html=True,
    )
    st.text(body)

    if attachments:
        st.markdown(
            f'<div class="section-label" style="margin-top:0.5rem">Attachments</div>',
            unsafe_allow_html=True,
        )
        # Render attachments as inline badges
        badges_html = " ".join(
            f'<span style="display:inline-block;padding:0.2rem 0.6rem;'
            f'border-radius:1rem;font-size:0.75rem;font-weight:500;'
            f'background:{COLORS["bg_elevated"]};color:{COLORS["text_secondary"]};'
            f'border:1px solid {COLORS["border"]};margin-right:0.25rem">{att}</span>'
            for att in attachments
        )
        st.markdown(badges_html, unsafe_allow_html=True)


def render_approval_dialog(
    gate_name: str,
    gate_data: dict,
) -> Optional[tuple[str, str]]:
    """Render an approval dialog and return the user's decision.

    Parameters
    ----------
    gate_name:
        The identifier for the approval gate (e.g. ``"quote_review"`` or
        ``"email_review"``).
    gate_data:
        A dict containing the data to display for review.

    Returns
    -------
    tuple[str, str] or None
        A ``(decision, feedback)`` pair where *decision* is one of
        ``"approved"``, ``"rejected"``, or ``"changes_requested"``.
        *feedback* is the text from the feedback area (empty string when
        approving).  Returns ``None`` if no button has been pressed yet.
    """
    # Use a unique key prefix so multiple gates can coexist in one session.
    key_prefix = f"approval_{gate_name}"

    # Track whether a decision has been made in this gate interaction.
    decision_key = f"{key_prefix}_decision"
    feedback_key = f"{key_prefix}_feedback"

    # If a previous decision was recorded, return it immediately.
    if st.session_state.get(decision_key):
        decision = st.session_state[decision_key]
        feedback = st.session_state.get(feedback_key, "")
        # Clear for next time
        del st.session_state[decision_key]
        if feedback_key in st.session_state:
            del st.session_state[feedback_key]
        return (decision, feedback)

    # ---- Dialog container ---------------------------------------------------
    with st.container(border=True):
        # Amber gradient header
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #fbbf24 0%, {COLORS['amber']} 100%);
                color: #1a1a1a;
                padding: 0.6rem 1rem;
                border-radius: 8px;
                font-weight: 700;
                font-size: 1.05rem;
                margin-bottom: 0.75rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                box-shadow: 0 2px 8px {COLORS['amber']}30;
            ">
                \u26A0\uFE0F Approval Required &mdash; {gate_name.replace('_', ' ').title()}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Gate-specific content
        if gate_name == "quote_review":
            _render_quote_review(gate_data)
        elif gate_name == "email_review":
            _render_email_review(gate_data)
        else:
            # Generic fallback: render all keys
            for k, v in gate_data.items():
                st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")

        # Gradient divider before feedback
        st.markdown(
            f'<div style="height:1px;background:linear-gradient(90deg,'
            f'{COLORS["amber"]}40 0%,{COLORS["border"]}60 50%,transparent 100%);'
            f'margin:0.75rem 0"></div>',
            unsafe_allow_html=True,
        )

        # Feedback text area
        feedback_text = st.text_area(
            "Feedback / Comments",
            key=f"{key_prefix}_text_area",
            height=80,
            placeholder="Add feedback for changes or rejection\u2026",
            label_visibility="collapsed",
        )

        # Action buttons with styled wrappers
        btn_col1, btn_col2, btn_col3 = st.columns(3)

        with btn_col1:
            st.markdown('<div class="approve-btn">', unsafe_allow_html=True)
            if st.button(
                "\u2705 Approve",
                key=f"{key_prefix}_approve",
                type="primary",
                use_container_width=True,
            ):
                st.session_state[decision_key] = "approved"
                st.session_state[feedback_key] = ""
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with btn_col2:
            st.markdown('<div class="changes-btn">', unsafe_allow_html=True)
            if st.button(
                "\U0001F504 Request Changes",
                key=f"{key_prefix}_changes",
                use_container_width=True,
            ):
                st.session_state[decision_key] = "changes_requested"
                st.session_state[feedback_key] = feedback_text
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with btn_col3:
            st.markdown('<div class="reject-btn">', unsafe_allow_html=True)
            if st.button(
                "\u274C Reject",
                key=f"{key_prefix}_reject",
                use_container_width=True,
            ):
                st.session_state[decision_key] = "rejected"
                st.session_state[feedback_key] = feedback_text
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    return None
