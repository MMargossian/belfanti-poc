"""Agent run endpoint with SSE streaming."""

import json
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from state.store import get_state, set_state, set_session_id, init_session_state
from state.pipeline import PipelineStage
from agent.orchestrator import Orchestrator

router = APIRouter(prefix="/api/agent", tags=["agent"])

# Map tool names to the pipeline stage they complete
TOOL_STAGE_MAP: dict[str, PipelineStage] = {
    "parse_rfq_email": PipelineStage.EMAIL_PARSED,
    "lookup_customer": PipelineStage.CUSTOMER_IDENTIFIED,
    "extract_part_specs": PipelineStage.PARTS_EXTRACTED,
    "validate_part_specs": PipelineStage.PARTS_VALIDATED,
    "log_to_tracking_sheet": PipelineStage.TRACKING_LOGGED,
    "store_cad_files": PipelineStage.CAD_FILES_STORED,
    "search_material_vendors": PipelineStage.VENDOR_SEARCH,
    "send_vendor_rfqs": PipelineStage.VENDOR_RFQS_SENT,
    "evaluate_vendor_bids": PipelineStage.VENDOR_BIDS_RECEIVED,
    "select_vendor": PipelineStage.VENDOR_SELECTED,
    "calculate_part_cost": PipelineStage.COST_CALCULATED,
    "build_quote": PipelineStage.QUOTE_BUILT,
    "approval_gate_quote_review": PipelineStage.QUOTE_REVIEW_GATE,
    "qb_create_product": PipelineStage.QB_PRODUCT_CREATED,
    "qb_create_estimate": PipelineStage.QB_ESTIMATE_CREATED,
    "qb_email_estimate": PipelineStage.QUOTE_SENT_TO_CUSTOMER,
    "record_customer_response": PipelineStage.CUSTOMER_RESPONSE_RECEIVED,
    "create_purchase_order": PipelineStage.PO_CREATED,
    "create_work_order": PipelineStage.WORK_ORDER_CREATED,
}


class RunRequest(BaseModel):
    message: str


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


def _run_agent_generator(session_id: str, message: str):
    """Synchronous generator that runs the agent and yields SSE events."""
    # Re-establish context for this thread
    set_session_id(session_id)
    init_session_state()

    api_key = get_state("api_key", "")
    if not api_key:
        yield _sse_event("error", {"message": "No API key set. Use PUT /api/config/api-key first."})
        yield _sse_event("done", {})
        return

    orchestrator = Orchestrator(api_key)

    for event in orchestrator.run(message):
        event_type = event[0]

        if event_type == "text":
            yield _sse_event("text", {"content": event[1]})

        elif event_type == "tool_call":
            tool_name = event[1]
            tool_input = event[2]
            yield _sse_event("tool_call", {"tool_name": tool_name, "tool_input": tool_input})

        elif event_type == "tool_result":
            tool_name = event[1]
            result_str = event[2]
            yield _sse_event("tool_result", {"tool_name": tool_name, "result": result_str})
            # Advance pipeline if this tool maps to a stage
            pipeline = get_state("pipeline_state")
            if pipeline and tool_name in TOOL_STAGE_MAP:
                stage = TOOL_STAGE_MAP[tool_name]
                # Only advance if not already completed and result isn't an error
                if stage not in pipeline.completed_stages and '"error"' not in result_str:
                    pipeline.advance_to(stage)
                    # If this is the final stage, also mark it completed
                    if stage == PipelineStage.WORK_ORDER_CREATED:
                        pipeline.completed_stages.append(stage)
                    set_state("pipeline_state", pipeline)
            # Send pipeline update after each tool result
            if pipeline:
                yield _sse_event("pipeline_update", {
                    "current_stage": pipeline.current_stage.value,
                    "completed_stages": [s.value for s in pipeline.completed_stages],
                    "failed_stage": pipeline.failed_stage.value if pipeline.failed_stage else None,
                    "error_message": pipeline.error_message,
                })

        elif event_type == "approval_needed":
            gate_name = event[1]
            gate_data = event[2]
            set_state("approval_pending", gate_name)
            set_state("approval_gate_data", gate_data)
            yield _sse_event("approval_needed", {"gate_name": gate_name, "gate_data": gate_data})

        elif event_type == "error":
            yield _sse_event("error", {"message": event[1]})

        elif event_type == "done":
            pass

    yield _sse_event("done", {})


@router.post("/run")
async def run_agent(body: RunRequest, request: Request):
    session_id = request.headers.get("x-session-id", "")

    async def event_stream():
        loop = asyncio.get_event_loop()
        gen = _run_agent_generator(session_id, body.message)
        for chunk in gen:
            yield chunk

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
