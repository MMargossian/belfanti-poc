"""Pipeline state endpoint."""

from fastapi import APIRouter

from state.store import get_state

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.get("")
async def get_pipeline():
    pipeline = get_state("pipeline_state")
    if pipeline is None:
        return {"current_stage": "rfq_received", "completed_stages": []}
    return {
        "current_stage": pipeline.current_stage.value,
        "completed_stages": [s.value for s in pipeline.completed_stages],
        "failed_stage": pipeline.failed_stage.value if pipeline.failed_stage else None,
        "error_message": pipeline.error_message,
    }
