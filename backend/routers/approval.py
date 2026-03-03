"""Approval submission endpoint with SSE streaming."""

import json
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from state.store import get_state, set_state, set_session_id, init_session_state
from state.pipeline import PipelineStage
from agent.orchestrator import Orchestrator
from routers.agent import TOOL_STAGE_MAP

router = APIRouter(prefix="/api/approval", tags=["approval"])


class ApprovalRequest(BaseModel):
    gate_name: str
    decision: str  # "approved", "rejected", "changes_requested"
    feedback: Optional[str] = ""


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


def _approval_generator(session_id: str, decision: str, feedback: str):
    set_session_id(session_id)
    init_session_state()

    api_key = get_state("api_key", "")
    if not api_key:
        yield _sse_event("error", {"message": "No API key set."})
        yield _sse_event("done", {})
        return

    orchestrator = Orchestrator(api_key)

    for event in orchestrator.resume_after_approval(decision, feedback):
        event_type = event[0]

        if event_type == "text":
            yield _sse_event("text", {"content": event[1]})
        elif event_type == "tool_call":
            yield _sse_event("tool_call", {"tool_name": event[1], "tool_input": event[2]})
        elif event_type == "tool_result":
            tool_name = event[1]
            result_str = event[2]
            yield _sse_event("tool_result", {"tool_name": tool_name, "result": result_str})
            # Advance pipeline if this tool maps to a stage
            pipeline = get_state("pipeline_state")
            if pipeline and tool_name in TOOL_STAGE_MAP:
                stage = TOOL_STAGE_MAP[tool_name]
                if stage not in pipeline.completed_stages and '"error"' not in result_str:
                    pipeline.advance_to(stage)
                    # If this is the final stage, also mark it completed
                    if stage == PipelineStage.WORK_ORDER_CREATED:
                        pipeline.completed_stages.append(stage)
                    set_state("pipeline_state", pipeline)
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


@router.post("/submit")
async def submit_approval(body: ApprovalRequest, request: Request):
    session_id = request.headers.get("x-session-id", "")

    async def event_stream():
        gen = _approval_generator(session_id, body.decision, body.feedback or "")
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
