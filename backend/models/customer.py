from pydantic import BaseModel
from typing import Optional


class Contact(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    role: Optional[str] = None


class Customer(BaseModel):
    id: str
    company_name: str
    primary_contact: Contact
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    payment_terms: str = "Net 30"
    quickbooks_id: Optional[str] = None
    notes: Optional[str] = None
