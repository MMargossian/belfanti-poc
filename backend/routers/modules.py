"""Module toggle endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from state.store import get_state, set_state

router = APIRouter(prefix="/api/modules", tags=["modules"])


class ModulesUpdate(BaseModel):
    enabled_modules: list[str]


ALL_MODULES = [
    {"name": "email_intake", "label": "Email Intake", "group": "intake"},
    {"name": "quote_extraction", "label": "Quote Extraction", "group": "intake"},
    {"name": "tracking", "label": "Tracking & Files", "group": "tracking"},
    {"name": "material_rfq", "label": "Material RFQ", "group": "quoting"},
    {"name": "quote_preparation", "label": "Quote Preparation", "group": "quoting"},
    {"name": "quickbooks", "label": "QuickBooks", "group": "quoting"},
    {"name": "approval_gates", "label": "Approval Gates", "group": "approval"},
    {"name": "customer_response", "label": "Customer Response", "group": "fulfillment"},
    {"name": "purchase_order", "label": "Purchase Orders", "group": "fulfillment"},
    {"name": "work_order", "label": "Work Orders", "group": "fulfillment"},
]


@router.get("")
async def get_modules():
    enabled = get_state("enabled_modules", [])
    return [
        {**m, "enabled": m["name"] in enabled}
        for m in ALL_MODULES
    ]


@router.put("")
async def update_modules(body: ModulesUpdate):
    set_state("enabled_modules", body.enabled_modules)
    return {"status": "updated", "enabled_modules": body.enabled_modules}
