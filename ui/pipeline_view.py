"""Pipeline progress view for the Belfanti CNC Manufacturing POC.

Renders a compact, grouped stage indicator with dark-theme styling
placed at the top of the main content area.
"""

from __future__ import annotations

import streamlit as st

from state.pipeline import PipelineStage, PipelineState, STAGE_ORDER
from ui.theme import COLORS


# ---------------------------------------------------------------------------
# Human-readable labels for every pipeline stage
# ---------------------------------------------------------------------------

STAGE_LABELS: dict[PipelineStage, str] = {
    PipelineStage.RFQ_RECEIVED: "RFQ Received",
    PipelineStage.EMAIL_PARSED: "Email Parsed",
    PipelineStage.CUSTOMER_IDENTIFIED: "Customer Identified",
    PipelineStage.PARTS_EXTRACTED: "Parts Extracted",
    PipelineStage.PARTS_VALIDATED: "Parts Validated",
    PipelineStage.TRACKING_LOGGED: "Tracking Logged",
    PipelineStage.CAD_FILES_STORED: "CAD Files Stored",
    PipelineStage.VENDOR_SEARCH: "Vendor Search",
    PipelineStage.VENDOR_RFQS_SENT: "Vendor RFQs Sent",
    PipelineStage.VENDOR_BIDS_RECEIVED: "Vendor Bids Received",
    PipelineStage.VENDOR_SELECTED: "Vendor Selected",
    PipelineStage.COST_CALCULATED: "Cost Calculated",
    PipelineStage.QUOTE_BUILT: "Quote Built",
    PipelineStage.QUOTE_REVIEW_GATE: "Quote Review Gate",
    PipelineStage.QB_PRODUCT_CREATED: "QB Product Created",
    PipelineStage.QB_ESTIMATE_CREATED: "QB Estimate Created",
    PipelineStage.QUOTE_SENT_TO_CUSTOMER: "Quote Sent",
    PipelineStage.CUSTOMER_RESPONSE_RECEIVED: "Customer Response",
    PipelineStage.PO_CREATED: "PO Created",
    PipelineStage.WORK_ORDER_CREATED: "Work Order Created",
}

# ---------------------------------------------------------------------------
# Phase groupings  (label, list of PipelineStage members)
# ---------------------------------------------------------------------------

_PHASE_GROUPS: list[tuple[str, list[PipelineStage]]] = [
    (
        "Intake",
        [
            PipelineStage.RFQ_RECEIVED,
            PipelineStage.EMAIL_PARSED,
            PipelineStage.CUSTOMER_IDENTIFIED,
        ],
    ),
    (
        "Extraction",
        [
            PipelineStage.PARTS_EXTRACTED,
            PipelineStage.PARTS_VALIDATED,
        ],
    ),
    (
        "Tracking",
        [
            PipelineStage.TRACKING_LOGGED,
            PipelineStage.CAD_FILES_STORED,
        ],
    ),
    (
        "Sourcing",
        [
            PipelineStage.VENDOR_SEARCH,
            PipelineStage.VENDOR_RFQS_SENT,
            PipelineStage.VENDOR_BIDS_RECEIVED,
            PipelineStage.VENDOR_SELECTED,
        ],
    ),
    (
        "Quoting",
        [
            PipelineStage.COST_CALCULATED,
            PipelineStage.QUOTE_BUILT,
            PipelineStage.QUOTE_REVIEW_GATE,
        ],
    ),
    (
        "QuickBooks",
        [
            PipelineStage.QB_PRODUCT_CREATED,
            PipelineStage.QB_ESTIMATE_CREATED,
            PipelineStage.QUOTE_SENT_TO_CUSTOMER,
        ],
    ),
    (
        "Response",
        [
            PipelineStage.CUSTOMER_RESPONSE_RECEIVED,
        ],
    ),
    (
        "Orders",
        [
            PipelineStage.PO_CREATED,
            PipelineStage.WORK_ORDER_CREATED,
        ],
    ),
]

# ---------------------------------------------------------------------------
# Badge / chip styling (dark theme)
# ---------------------------------------------------------------------------

_STATUS_STYLES: dict[str, dict[str, str]] = {
    "completed": {
        "icon": "\u2713",
        "bg": f"{COLORS['green']}20",
        "fg": COLORS["green"],
        "border": f"{COLORS['green']}40",
    },
    "current": {
        "icon": "\u25B6",
        "bg": f"{COLORS['blue']}20",
        "fg": COLORS["blue"],
        "border": f"{COLORS['blue']}40",
    },
    "failed": {
        "icon": "\u2717",
        "bg": f"{COLORS['red']}20",
        "fg": COLORS["red"],
        "border": f"{COLORS['red']}40",
    },
    "pending": {
        "icon": "\u25CB",
        "bg": f"{COLORS['bg_elevated']}",
        "fg": COLORS["text_muted"],
        "border": COLORS["border"],
    },
}

_CSS = f"""
<style>
.pipeline-phase-label {{
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {COLORS['text_muted']};
    margin: 0.6rem 0 0.2rem 0;
    padding: 0;
}}
.pipeline-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    margin-bottom: 0.15rem;
}}
.pipeline-chip {{
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.65rem;
    font-weight: 500;
    padding: 0.2rem 0.5rem;
    border-radius: 1rem;
    border: 1px solid;
    white-space: nowrap;
    line-height: 1.4;
    transition: all 0.2s ease;
}}
.pipeline-progress-bar {{
    background: {COLORS['bg_elevated']};
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
    border: 1px solid {COLORS['border_subtle']};
}}
.pipeline-progress-fill {{
    background: linear-gradient(90deg, {COLORS['blue']}, {COLORS['green']});
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s ease;
}}
</style>
"""


def _chip_html(label: str, status: str) -> str:
    """Return HTML for a single pipeline stage chip."""
    style = _STATUS_STYLES.get(status, _STATUS_STYLES["pending"])
    return (
        f'<span class="pipeline-chip" '
        f'style="background:{style["bg"]};color:{style["fg"]};border-color:{style["border"]}">'
        f'{style["icon"]} {label}</span>'
    )


# ---------------------------------------------------------------------------
# Public renderer
# ---------------------------------------------------------------------------

def render_pipeline_view() -> None:
    """Render the pipeline progress indicator.

    Reads ``st.session_state["pipeline_state"]`` (a :class:`PipelineState`
    instance) and draws a compact grouped stage view using custom HTML/CSS.
    """
    pipeline: PipelineState = st.session_state.get("pipeline_state", PipelineState())

    # Count completion stats.
    total_stages = len(STAGE_ORDER)
    completed_count = len(pipeline.completed_stages)
    progress_pct = (completed_count / total_stages * 100) if total_stages else 0

    # Build HTML
    html_parts: list[str] = [_CSS]

    # Stats line: label left, count right
    html_parts.append(
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem">'
        f'<span style="font-size:0.75rem;font-weight:600;text-transform:uppercase;'
        f'letter-spacing:0.08em;color:{COLORS["text_secondary"]}">Pipeline Progress</span>'
        f'<span style="font-size:0.75rem;color:{COLORS["text_muted"]}">'
        f'{completed_count}/{total_stages} stages ({progress_pct:.0f}%)</span>'
        f'</div>'
    )

    # Progress bar
    html_parts.append(
        f'<div class="pipeline-progress-bar">'
        f'<div class="pipeline-progress-fill" style="width:{progress_pct:.0f}%"></div>'
        f'</div>'
    )

    # Phase groups with chips
    for phase_label, stages in _PHASE_GROUPS:
        html_parts.append(f'<div class="pipeline-phase-label">{phase_label}</div>')
        html_parts.append('<div class="pipeline-row">')
        for stage in stages:
            label = STAGE_LABELS.get(stage, stage.value)
            status = pipeline.get_stage_status(stage)
            html_parts.append(_chip_html(label, status))
        html_parts.append("</div>")

    st.markdown("".join(html_parts), unsafe_allow_html=True)
