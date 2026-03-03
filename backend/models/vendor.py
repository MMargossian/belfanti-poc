from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class VendorSpecialty(str, Enum):
    ALUMINUM = "aluminum"
    STEEL = "steel"
    STAINLESS = "stainless_steel"
    TITANIUM = "titanium"
    PLASTICS = "plastics"
    BRASS = "brass"
    COPPER = "copper"


class Vendor(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    specialties: list[VendorSpecialty] = []
    lead_time_days: int = 5
    rating: float = 4.0  # 1-5
    min_order_value: float = 50.0
    notes: Optional[str] = None


class VendorQuote(BaseModel):
    id: str
    vendor_id: str
    vendor_name: str
    material_description: str
    quantity: float
    unit: str = "each"
    unit_price: float
    total_price: float
    lead_time_days: int
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None
    selected: bool = False
