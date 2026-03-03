"""
Email Intake module for the Belfanti CNC Manufacturing POC.
Parses incoming RFQ emails and identifies customers from a hardcoded database.
"""

from typing import Any

from models.customer import Contact, Customer
from modules.base import BaseModule


# Hardcoded customer database for the POC
_CUSTOMER_DB: list[Customer] = [
    Customer(
        id="CUST-001",
        company_name="Condor Aerospace",
        primary_contact=Contact(
            name="Tom Harrelson",
            email="tom.harrelson@condoraero.com",
            phone="(555) 234-8901",
            role="Procurement Manager",
        ),
        billing_address="4500 Skyline Blvd, Suite 300, Boulder, CO 80301",
        shipping_address="4500 Skyline Blvd, Dock B, Boulder, CO 80301",
        payment_terms="Net 30",
        quickbooks_id="QB-10451",
        notes="Long-standing customer. Primarily orders aerospace-grade aluminum and titanium parts.",
    ),
    Customer(
        id="CUST-002",
        company_name="Ridgeline Automation",
        primary_contact=Contact(
            name="Dana Kowalski",
            email="dana.k@ridgelineauto.com",
            phone="(555) 677-2340",
            role="Engineering Lead",
        ),
        billing_address="880 Industrial Pkwy, Greenville, SC 29607",
        shipping_address="880 Industrial Pkwy, Receiving, Greenville, SC 29607",
        payment_terms="Net 30",
        quickbooks_id="QB-10523",
        notes="Automation equipment manufacturer. Frequent repeat orders for steel and stainless components.",
    ),
    Customer(
        id="CUST-003",
        company_name="Apex Medical Devices",
        primary_contact=Contact(
            name="Ricardo Mendez",
            email="r.mendez@apexmedical.com",
            phone="(555) 819-4455",
            role="Director of Supply Chain",
        ),
        billing_address="1200 Medtech Dr, Minneapolis, MN 55413",
        shipping_address="1200 Medtech Dr, Clean Room Receiving, Minneapolis, MN 55413",
        payment_terms="Net 45",
        quickbooks_id="QB-10602",
        notes="Medical device company. Requires tight tolerances and passivated stainless steel parts.",
    ),
]

_URGENCY_KEYWORDS = {"rush", "urgent", "asap", "expedite", "critical", "emergency", "hurry"}


class EmailIntakeModule(BaseModule):
    """Parse incoming RFQ emails and identify customers."""

    @property
    def name(self) -> str:
        return "email_intake"

    @property
    def description(self) -> str:
        return "Parse incoming RFQ emails and identify customers"

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "parse_rfq_email",
                "description": (
                    "Parse an incoming RFQ email and return structured data including "
                    "customer info, mentioned parts/materials, urgency level, and attachments."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "email_text": {
                            "type": "string",
                            "description": "Full body text of the email.",
                        },
                        "sender_name": {
                            "type": "string",
                            "description": "Name of the person who sent the email.",
                        },
                        "sender_email": {
                            "type": "string",
                            "description": "Email address of the sender.",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line.",
                        },
                        "attachments": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of attachment filenames.",
                        },
                    },
                    "required": ["email_text", "sender_name", "sender_email", "subject"],
                },
            },
            {
                "name": "lookup_customer",
                "description": (
                    "Look up a customer in the database by email address and/or company name. "
                    "Returns the full customer record if found, or a suggestion to create a new one."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Customer email address to search for.",
                        },
                        "company_name": {
                            "type": "string",
                            "description": "Company name to search for (optional, improves matching).",
                        },
                    },
                    "required": ["email"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "parse_rfq_email":
            return self._parse_rfq_email(**tool_input)
        elif tool_name == "lookup_customer":
            return self._lookup_customer(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Internal tool implementations
    # ------------------------------------------------------------------

    def _parse_rfq_email(
        self,
        email_text: str,
        sender_name: str,
        sender_email: str,
        subject: str,
        attachments: list[str] | None = None,
    ) -> dict:
        """Parse an RFQ email and return structured data."""
        attachments = attachments or []

        # Detect urgency from subject and body combined
        combined_text = f"{subject} {email_text}".lower()
        detected_urgency = "standard"
        for keyword in _URGENCY_KEYWORDS:
            if keyword in combined_text:
                detected_urgency = "rush"
                break

        # Separate CAD files from other attachments
        cad_extensions = {".step", ".stp", ".iges", ".igs", ".dxf", ".dwg", ".stl", ".x_t", ".prt", ".sldprt"}
        drawing_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}

        cad_files = []
        drawing_files = []
        other_files = []
        for att in attachments:
            lower_att = att.lower()
            if any(lower_att.endswith(ext) for ext in cad_extensions):
                cad_files.append(att)
            elif any(lower_att.endswith(ext) for ext in drawing_extensions):
                drawing_files.append(att)
            else:
                other_files.append(att)

        return {
            "customer_name": sender_name,
            "customer_email": sender_email,
            "subject": subject,
            "body": email_text,
            "attachments": attachments,
            "cad_files": cad_files,
            "drawing_files": drawing_files,
            "other_files": other_files,
            "urgency": detected_urgency,
            "attachment_count": len(attachments),
        }

    def _lookup_customer(self, email: str, company_name: str | None = None) -> dict:
        """Look up a customer by email or company name."""
        email_lower = email.lower().strip()

        # Try email match first (strongest signal)
        for customer in _CUSTOMER_DB:
            if customer.primary_contact.email.lower() == email_lower:
                return {
                    "found": True,
                    "customer": customer.model_dump(),
                }

        # Try company name match if provided
        if company_name:
            company_lower = company_name.lower().strip()
            for customer in _CUSTOMER_DB:
                if company_lower in customer.company_name.lower():
                    return {
                        "found": True,
                        "customer": customer.model_dump(),
                        "match_type": "company_name",
                        "note": "Matched by company name. Email on file differs from sender.",
                    }

        # Try domain match as a fallback
        email_domain = email_lower.split("@")[-1] if "@" in email_lower else ""
        for customer in _CUSTOMER_DB:
            customer_domain = customer.primary_contact.email.lower().split("@")[-1]
            if email_domain and email_domain == customer_domain:
                return {
                    "found": True,
                    "customer": customer.model_dump(),
                    "match_type": "domain",
                    "note": (
                        f"Matched by email domain ({email_domain}). "
                        f"Contact on file is {customer.primary_contact.name} "
                        f"({customer.primary_contact.email}). "
                        "This may be a different contact at the same company."
                    ),
                }

        return {
            "found": False,
            "searched_email": email,
            "searched_company": company_name,
            "suggestion": "New customer - will need to create in QuickBooks",
        }
