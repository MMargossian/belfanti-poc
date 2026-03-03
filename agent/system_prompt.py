"""
Dynamic system prompt builder for the Belfanti CNC Manufacturing POC agent.
Constructs a context-aware prompt that includes CNC domain knowledge,
the current pipeline state, and only the steps for enabled modules.
"""

from state.pipeline import PipelineState, PipelineStage, STAGE_ORDER
from data.machine_rates import MACHINE_HOURLY_RATES, SETUP_COSTS, FINISHING_RATES
from models.rfq import MaterialType, MachineType, SurfaceFinish


# ── Mapping from pipeline stages to module names ─────────────────────────────

_STAGE_TO_MODULE: dict[PipelineStage, str] = {
    PipelineStage.RFQ_RECEIVED: "email_intake",
    PipelineStage.EMAIL_PARSED: "email_intake",
    PipelineStage.CUSTOMER_IDENTIFIED: "email_intake",
    PipelineStage.PARTS_EXTRACTED: "quote_extraction",
    PipelineStage.PARTS_VALIDATED: "quote_extraction",
    PipelineStage.TRACKING_LOGGED: "tracking",
    PipelineStage.CAD_FILES_STORED: "tracking",
    PipelineStage.VENDOR_SEARCH: "material_rfq",
    PipelineStage.VENDOR_RFQS_SENT: "material_rfq",
    PipelineStage.VENDOR_BIDS_RECEIVED: "material_rfq",
    PipelineStage.VENDOR_SELECTED: "material_rfq",
    PipelineStage.COST_CALCULATED: "quote_preparation",
    PipelineStage.QUOTE_BUILT: "quote_preparation",
    PipelineStage.QUOTE_REVIEW_GATE: "approval_gates",
    PipelineStage.QB_PRODUCT_CREATED: "quickbooks",
    PipelineStage.QB_ESTIMATE_CREATED: "quickbooks",
    PipelineStage.QUOTE_SENT_TO_CUSTOMER: "quickbooks",
    PipelineStage.CUSTOMER_RESPONSE_RECEIVED: "customer_response",
    PipelineStage.PO_CREATED: "purchase_order",
    PipelineStage.WORK_ORDER_CREATED: "work_order",
}


def _build_identity_section() -> str:
    """Return the identity and role block."""
    return (
        "You are Belfanti's AI manufacturing assistant. You orchestrate the entire "
        "CNC machining order pipeline from RFQ intake to work order creation. You "
        "have access to tools for each step of the process."
    )


def _build_domain_knowledge() -> str:
    """Return CNC domain knowledge as a concise reference block."""
    # Material list from the enum
    materials = ", ".join(m.value for m in MaterialType)

    # Machine rates as a readable table
    machine_rate_lines = []
    for mt in MachineType:
        rate = MACHINE_HOURLY_RATES.get(mt, 0)
        setup = SETUP_COSTS.get(mt, 0)
        machine_rate_lines.append(f"  - {mt.value}: ${rate:.2f}/hr, setup ${setup:.2f}")
    machine_rates_str = "\n".join(machine_rate_lines)

    # Finishing costs
    finish_lines = []
    for sf in SurfaceFinish:
        cost = FINISHING_RATES.get(sf, 0)
        finish_lines.append(f"  - {sf.value}: ${cost:.2f}/part")
    finish_str = "\n".join(finish_lines)

    return (
        "## CNC Domain Knowledge\n\n"
        f"**Materials available:** {materials}\n\n"
        "**Machine types and when to use each:**\n"
        "  - 3-axis mill: Simple prismatic parts, 2.5D features, standard pocketing and profiling\n"
        "  - 5-axis mill: Complex 3D geometry, undercuts, compound angles, aerospace contours\n"
        "  - Lathe: Round/cylindrical parts, shafts, bushings, turned features\n"
        "  - EDM: Hardened steel, fine features, tight internal corners, thin ribs\n"
        "  - Grinder: Precision finishing, tight flatness/parallelism, surface finish requirements\n\n"
        "**Typical tolerances:**\n"
        "  - Standard: +/- 0.005\"\n"
        "  - Precision: +/- 0.001\"\n"
        "  - Ultra-precision: +/- 0.0005\"\n\n"
        "**Machine rates (hourly + setup):**\n"
        f"{machine_rates_str}\n\n"
        "**Surface finishing costs (per part):**\n"
        f"{finish_str}"
    )


def _build_process_flow(enabled_modules: list[str]) -> str:
    """Build the process flow listing only steps whose module is enabled."""
    lines = ["## Process Flow\n"]
    lines.append("The pipeline proceeds through the following stages (only enabled stages are shown):\n")

    step_number = 1
    skipped_modules: set[str] = set()

    for stage in STAGE_ORDER:
        module_name = _STAGE_TO_MODULE.get(stage, "unknown")
        if module_name in enabled_modules:
            lines.append(f"  {step_number}. **{stage.value}** (module: {module_name})")
            step_number += 1
        else:
            skipped_modules.add(module_name)

    if skipped_modules:
        lines.append(
            f"\n*Disabled modules (skipped):* {', '.join(sorted(skipped_modules))}"
        )

    return "\n".join(lines)


def _build_current_state(pipeline_state: PipelineState) -> str:
    """Inject the current pipeline state so the agent knows where it is."""
    completed = [s.value for s in pipeline_state.completed_stages]
    completed_str = ", ".join(completed) if completed else "None"

    lines = [
        "## Current Pipeline State\n",
        f"**Current stage:** {pipeline_state.current_stage.value}",
        f"**Completed stages:** {completed_str}",
    ]

    if pipeline_state.failed_stage:
        lines.append(f"**Failed stage:** {pipeline_state.failed_stage.value}")
        lines.append(f"**Error:** {pipeline_state.error_message or 'Unknown error'}")

    if pipeline_state.is_complete():
        lines.append("\n**Pipeline status:** COMPLETE -- all stages finished.")
    elif pipeline_state.failed_stage:
        lines.append("\n**Pipeline status:** FAILED -- intervention required.")
    else:
        lines.append("\n**Pipeline status:** IN PROGRESS")

    return "\n".join(lines)


def _build_behavioral_instructions() -> str:
    """Return the behavioral guidelines for the agent."""
    return (
        "## Behavioral Instructions\n\n"
        "- Always explain what you are about to do before calling a tool.\n"
        "- Call tools one step at a time, confirming results before proceeding to the next step.\n"
        "- At approval gates, present a clear summary of the quote and wait for human input.\n"
        "- If a module is disabled, skip its steps and briefly explain why.\n"
        "- Be concise but informative.\n"
        "- Use professional manufacturing terminology.\n"
        "- When presenting numbers (costs, rates, tolerances), be precise.\n"
        "- If an error occurs during a tool call, report it clearly and suggest next steps."
    )


def build_system_prompt(
    enabled_modules: list[str],
    pipeline_state: PipelineState,
) -> str:
    """
    Construct the full dynamic system prompt for the orchestrator.

    Parameters
    ----------
    enabled_modules:
        List of module name strings that are currently active
        (e.g. ["email_intake", "quote_extraction", ...]).
    pipeline_state:
        The current PipelineState object reflecting progress through the pipeline.

    Returns
    -------
    A single string ready to be passed as the ``system`` parameter to the
    Anthropic messages API.
    """
    sections = [
        _build_identity_section(),
        "",
        _build_domain_knowledge(),
        "",
        _build_process_flow(enabled_modules),
        "",
        _build_current_state(pipeline_state),
        "",
        _build_behavioral_instructions(),
    ]
    return "\n\n".join(sections)
