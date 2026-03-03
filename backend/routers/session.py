"""Session management endpoints."""

import os
import uuid
from fastapi import APIRouter, Request
from pydantic import BaseModel

from session.manager import session_manager
from state.store import set_session_id, init_session_state, get_state, set_state, SESSION_DEFAULTS
from state.pipeline import PipelineState

router = APIRouter(prefix="/api/session", tags=["session"])


class SessionResponse(BaseModel):
    session_id: str
    has_api_key: bool = False


@router.post("", response_model=SessionResponse)
async def create_session():
    session_id = str(uuid.uuid4())
    set_session_id(session_id)
    init_session_state()
    # Auto-seed API key from env if available
    env_key = os.getenv("ANTHROPIC_API_KEY", "")
    if env_key:
        set_state("api_key", env_key)
    return SessionResponse(session_id=session_id, has_api_key=bool(env_key))


@router.delete("")
async def reset_session(request: Request):
    session_id = request.headers.get("x-session-id", "")
    if session_id:
        session_manager.delete(session_id)
    # Create fresh
    set_session_id(session_id)
    defaults = {k: v for k, v in SESSION_DEFAULTS.items()}
    defaults["pipeline_state"] = PipelineState()
    session_manager.create(session_id, defaults)
    return {"status": "reset"}


@router.get("/state")
async def get_session_state(request: Request):
    session_id = request.headers.get("x-session-id", "")
    data = session_manager.get_all(session_id)
    if data is None:
        return {"error": "session not found"}
    # Convert non-serializable objects
    state = {}
    for k, v in data.items():
        if isinstance(v, PipelineState):
            state[k] = v.model_dump(mode="json")
        else:
            try:
                import json
                json.dumps(v, default=str)
                state[k] = v
            except (TypeError, ValueError):
                state[k] = str(v)
    return state
