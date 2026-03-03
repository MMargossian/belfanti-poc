"""Demo RFQ loading endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from data.sample_rfqs import SAMPLE_RFQS

router = APIRouter(prefix="/api/demo", tags=["demo"])


class DemoRequest(BaseModel):
    index: int


@router.post("/load")
async def load_demo(body: DemoRequest):
    if body.index < 0 or body.index >= len(SAMPLE_RFQS):
        return {"error": f"Invalid demo index. Must be 0-{len(SAMPLE_RFQS) - 1}"}
    rfq = SAMPLE_RFQS[body.index]
    # Build the message text from the RFQ
    message = (
        f"From: {rfq['customer_name']} <{rfq['customer_email']}>\n"
        f"Company: {rfq['customer_company']}\n"
        f"Subject: {rfq['subject']}\n\n"
        f"{rfq['body']}\n\n"
        f"Attachments: {', '.join(rfq['attachments'])}"
    )
    return {"message": message, "rfq": rfq}
