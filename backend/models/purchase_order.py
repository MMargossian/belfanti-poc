from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class POStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CLOSED = "closed"


class SalesOrderStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CLOSED = "closed"


class WorkOrderStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class PurchaseOrder(BaseModel):
    id: Optional[str] = None
    vendor_id: str
    vendor_name: str
    quote_id: str
    items: list[dict] = []  # material line items
    total: float = 0.0
    status: POStatus = POStatus.DRAFT
    created_at: Optional[datetime] = None
    expected_delivery: Optional[datetime] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None


class SalesOrder(BaseModel):
    id: Optional[str] = None
    quote_id: str
    customer_name: str
    customer_email: str
    line_items: list[dict] = []
    total: float = 0.0
    status: SalesOrderStatus = SalesOrderStatus.OPEN
    created_at: Optional[datetime] = None
    ship_date: Optional[datetime] = None
    notes: Optional[str] = None


class WorkOrder(BaseModel):
    id: Optional[str] = None
    sales_order_id: str
    quote_id: str
    parts: list[dict] = []
    packing_slip_url: Optional[str] = None
    print_pdf_url: Optional[str] = None
    fusion360_folder_url: Optional[str] = None
    status: WorkOrderStatus = WorkOrderStatus.CREATED
    created_at: Optional[datetime] = None
    notes: Optional[str] = None
