from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class QuoteStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SENT_TO_CUSTOMER = "sent_to_customer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVISION_REQUESTED = "revision_requested"


class QuoteLineItem(BaseModel):
    part_number: str
    part_name: str
    description: Optional[str] = None
    quantity: int = 1
    material_cost: float = 0.0
    machine_cost: float = 0.0
    finishing_cost: float = 0.0
    setup_cost: float = 0.0
    unit_cost: float = 0.0
    line_total: float = 0.0
    margin_percent: float = 30.0
    unit_price: float = 0.0
    line_price: float = 0.0


class Quote(BaseModel):
    id: Optional[str] = None
    rfq_id: Optional[str] = None
    customer_name: str
    customer_email: str
    customer_company: Optional[str] = None
    line_items: list[QuoteLineItem] = []
    subtotal: float = 0.0
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0
    status: QuoteStatus = QuoteStatus.DRAFT
    quickbooks_estimate_id: Optional[str] = None
    quickbooks_pdf_url: Optional[str] = None
    created_at: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None
    revision: int = 1
