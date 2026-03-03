from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PipelineStage(str, Enum):
    RFQ_RECEIVED = "rfq_received"
    EMAIL_PARSED = "email_parsed"
    CUSTOMER_IDENTIFIED = "customer_identified"
    PARTS_EXTRACTED = "parts_extracted"
    PARTS_VALIDATED = "parts_validated"
    TRACKING_LOGGED = "tracking_logged"
    CAD_FILES_STORED = "cad_files_stored"
    VENDOR_SEARCH = "vendor_search"
    VENDOR_RFQS_SENT = "vendor_rfqs_sent"
    VENDOR_BIDS_RECEIVED = "vendor_bids_received"
    VENDOR_SELECTED = "vendor_selected"
    COST_CALCULATED = "cost_calculated"
    QUOTE_BUILT = "quote_built"
    QUOTE_REVIEW_GATE = "quote_review_gate"
    QB_PRODUCT_CREATED = "qb_product_created"
    QB_ESTIMATE_CREATED = "qb_estimate_created"
    QUOTE_SENT_TO_CUSTOMER = "quote_sent_to_customer"
    CUSTOMER_RESPONSE_RECEIVED = "customer_response_received"
    PO_CREATED = "po_created"
    WORK_ORDER_CREATED = "work_order_created"


STAGE_ORDER: list[PipelineStage] = [
    PipelineStage.RFQ_RECEIVED,
    PipelineStage.EMAIL_PARSED,
    PipelineStage.CUSTOMER_IDENTIFIED,
    PipelineStage.PARTS_EXTRACTED,
    PipelineStage.PARTS_VALIDATED,
    PipelineStage.TRACKING_LOGGED,
    PipelineStage.CAD_FILES_STORED,
    PipelineStage.VENDOR_SEARCH,
    PipelineStage.VENDOR_RFQS_SENT,
    PipelineStage.VENDOR_BIDS_RECEIVED,
    PipelineStage.VENDOR_SELECTED,
    PipelineStage.COST_CALCULATED,
    PipelineStage.QUOTE_BUILT,
    PipelineStage.QUOTE_REVIEW_GATE,
    PipelineStage.QB_PRODUCT_CREATED,
    PipelineStage.QB_ESTIMATE_CREATED,
    PipelineStage.QUOTE_SENT_TO_CUSTOMER,
    PipelineStage.CUSTOMER_RESPONSE_RECEIVED,
    PipelineStage.PO_CREATED,
    PipelineStage.WORK_ORDER_CREATED,
]


class PipelineState(BaseModel):
    current_stage: PipelineStage = PipelineStage.RFQ_RECEIVED
    completed_stages: list[PipelineStage] = []
    failed_stage: Optional[PipelineStage] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def advance_to(self, stage: PipelineStage) -> None:
        if self.current_stage not in self.completed_stages:
            self.completed_stages.append(self.current_stage)
        self.current_stage = stage

    def mark_failed(self, stage: PipelineStage, error_msg: str) -> None:
        self.failed_stage = stage
        self.error_message = error_msg

    def is_complete(self) -> bool:
        return (
            self.current_stage == PipelineStage.WORK_ORDER_CREATED
            and PipelineStage.WORK_ORDER_CREATED in self.completed_stages
        )

    def get_stage_status(self, stage: PipelineStage) -> str:
        if stage == self.failed_stage:
            return "failed"
        if stage in self.completed_stages:
            return "completed"
        if stage == self.current_stage:
            return "current"
        return "pending"
