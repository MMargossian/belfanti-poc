"""Centralized theme and CSS injection for the Belfanti CNC Manufacturing POC.

Call ``inject_global_css()`` once at the top of ``app.py`` to apply the dark
industrial theme across all pages and components.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Design-system colour palette
# ---------------------------------------------------------------------------

COLORS = {
    # Backgrounds
    "bg_primary": "#0f1117",
    "bg_secondary": "#1a1d28",
    "bg_surface": "#1e2130",
    "bg_elevated": "#252838",
    # Borders
    "border": "#2d3148",
    "border_subtle": "#232639",
    # Text
    "text_primary": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    # Accents
    "blue": "#3b82f6",
    "green": "#22c55e",
    "amber": "#f59e0b",
    "red": "#ef4444",
    # Chat bubbles
    "chat_user_bg": "#1a2332",
    "chat_assistant_bg": "#252838",
}


def gradient_divider() -> None:
    """Render a thin gradient line instead of a solid ``st.divider()``."""
    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,'
        f'{COLORS["blue"]}40 0%,{COLORS["border"]}60 50%,transparent 100%);'
        'margin:1rem 0"></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Global CSS injection
# ---------------------------------------------------------------------------

_GLOBAL_CSS = """
<style>
/* ---------- Google Fonts: Inter ---------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ---------- Base typography ---------- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ---------- Hide hamburger menu & footer ---------- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

/* ---------- Reduce block-container padding ---------- */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
    max-width: 1200px;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background-color: %(bg_secondary)s !important;
    border-right: 1px solid %(border)s !important;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
}

/* ---------- Chat messages ---------- */
div[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.75rem !important;
    border: 1px solid %(border_subtle)s !important;
}
/* User messages — blue tint */
div[data-testid="stChatMessage"]:has(img[alt="user"]),
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: %(chat_user_bg)s !important;
}
/* Assistant messages — elevated surface */
div[data-testid="stChatMessage"]:has(img[alt="assistant"]),
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: %(chat_assistant_bg)s !important;
}

/* ---------- Chat input ---------- */
div[data-testid="stChatInput"] {
    background-color: %(bg_surface)s !important;
    border-color: %(border)s !important;
}
div[data-testid="stChatInput"] textarea {
    color: %(text_primary)s !important;
}

/* ---------- Expanders (tool calls) ---------- */
details[data-testid="stExpander"] {
    background-color: %(bg_surface)s !important;
    border: 1px solid %(border)s !important;
    border-radius: 8px !important;
    margin-bottom: 0.5rem !important;
}
details[data-testid="stExpander"] summary {
    color: %(text_secondary)s !important;
    font-size: 0.85rem !important;
}
details[data-testid="stExpander"] summary:hover {
    color: %(text_primary)s !important;
}
/* Code blocks inside expanders */
details[data-testid="stExpander"] pre {
    background-color: %(bg_primary)s !important;
    border: 1px solid %(border_subtle)s !important;
    border-radius: 6px !important;
}

/* ---------- Text inputs & text areas ---------- */
input[type="text"], input[type="password"], textarea {
    background-color: %(bg_surface)s !important;
    border-color: %(border)s !important;
    color: %(text_primary)s !important;
    border-radius: 6px !important;
}
input[type="text"]:focus, input[type="password"]:focus, textarea:focus {
    border-color: %(blue)s !important;
    box-shadow: 0 0 0 1px %(blue)s40 !important;
}

/* ---------- Buttons ---------- */
button[data-testid="stBaseButton-secondary"] {
    background-color: %(bg_surface)s !important;
    border: 1px solid %(border)s !important;
    color: %(text_primary)s !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
}
button[data-testid="stBaseButton-secondary"]:hover {
    background-color: %(bg_elevated)s !important;
    border-color: %(blue)s !important;
}
button[data-testid="stBaseButton-primary"] {
    background-color: %(blue)s !important;
    border-radius: 6px !important;
}

/* ---------- Toggle switches ---------- */
div[data-testid="stToggle"] label span {
    font-size: 0.85rem !important;
    color: %(text_secondary)s !important;
}

/* ---------- Containers with border ---------- */
div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
    border-color: %(border)s !important;
    border-radius: 8px !important;
    background-color: %(bg_surface)s !important;
}

/* ---------- Dataframes ---------- */
.stDataFrame {
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ---------- Metric overrides ---------- */
div[data-testid="stMetric"] {
    background-color: %(bg_elevated)s !important;
    padding: 0.75rem 1rem !important;
    border-radius: 8px !important;
    border: 1px solid %(border)s !important;
}
div[data-testid="stMetric"] label {
    color: %(text_muted)s !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ---------- Section label utility ---------- */
.section-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: %(text_secondary)s;
    margin-bottom: 0.5rem;
}

/* ---------- Status pills ---------- */
.status-pill {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 1rem;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.status-pill.ok {
    background-color: %(green)s20;
    color: %(green)s;
    border: 1px solid %(green)s40;
}
.status-pill.fail {
    background-color: %(red)s20;
    color: %(red)s;
    border: 1px solid %(red)s40;
}

/* ---------- Approval action buttons ---------- */
.approve-btn button {
    background-color: %(green)s !important;
    color: white !important;
    border: none !important;
}
.approve-btn button:hover {
    background-color: #16a34a !important;
}
.changes-btn button {
    background-color: transparent !important;
    color: %(amber)s !important;
    border: 1px solid %(amber)s !important;
}
.changes-btn button:hover {
    background-color: %(amber)s15 !important;
}
.reject-btn button {
    background-color: %(red)s !important;
    color: white !important;
    border: none !important;
}
.reject-btn button:hover {
    background-color: #dc2626 !important;
}

/* ---------- Scrollbar ---------- */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: %(bg_primary)s;
}
::-webkit-scrollbar-thumb {
    background: %(border)s;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: %(text_muted)s;
}
</style>
""" % COLORS


def inject_global_css() -> None:
    """Inject the global dark-industrial CSS into the current Streamlit page.

    Call this **once** near the top of ``app.py``, right after
    ``init_session_state()``.
    """
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
