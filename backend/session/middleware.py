"""FastAPI middleware that extracts X-Session-ID and sets context."""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from state.store import set_session_id, init_session_state


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        session_id = request.headers.get("x-session-id", "")
        if not session_id:
            session_id = str(uuid.uuid4())
        set_session_id(session_id)
        init_session_state()
        response = await call_next(request)
        response.headers["x-session-id"] = session_id
        return response
