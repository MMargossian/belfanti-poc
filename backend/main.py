"""FastAPI application entry point for Belfanti CNC Manufacturing POC."""

import os
import logging

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from session.middleware import SessionMiddleware
from routers import session, agent, approval, pipeline, modules, demo
from state.store import get_state, set_state, set_session_id, init_session_state

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Belfanti CNC Manufacturing POC", version="1.0.0")

# CORS — allow localhost for dev + production frontend URL from env
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:3005",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3005",
]
frontend_url = os.getenv("FRONTEND_URL", "")
if frontend_url:
    cors_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-session-id"],
)

# Session middleware
app.add_middleware(SessionMiddleware)

# Routers
app.include_router(session.router)
app.include_router(agent.router)
app.include_router(approval.router)
app.include_router(pipeline.router)
app.include_router(modules.router)
app.include_router(demo.router)


# API key config endpoint
class ApiKeyRequest(BaseModel):
    api_key: str


@app.put("/api/config/api-key")
async def set_api_key(body: ApiKeyRequest, request: Request):
    session_id = request.headers.get("x-session-id", "")
    set_session_id(session_id)
    init_session_state()
    set_state("api_key", body.api_key)
    return {"status": "ok"}


# Seed API key from env if available
@app.on_event("startup")
async def startup():
    env_key = os.getenv("ANTHROPIC_API_KEY", "")
    if env_key:
        logging.info("ANTHROPIC_API_KEY found in environment")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
