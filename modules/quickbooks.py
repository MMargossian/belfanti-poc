"""
QuickBooks module for Phase D of the Belfanti CNC Manufacturing POC.
Creates products, estimates, generates PDFs, emails estimates, and manages
the accept/reject workflow through MockQuickBooksService.
"""

from typing import Any

from modules.base import BaseModule
from services.mock_quickbooks import MockQuickBooksService


# Module-level singleton
_qb = MockQuickBooksService()


class QuickBooksModule(BaseModule):
    """Create products, estimates, and manage QuickBooks workflow."""

    @property
    def name(self) -> str:
        return "quickbooks"

    @property
    def description(self) -> str:
        return "Create products, estimates, and manage QuickBooks workflow"

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "qb_create_product",
                "description": (
                    "Create a product/service item in QuickBooks. "
                    "Returns the product ID, name, SKU, and unit price."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Product name.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Product description.",
                        },
                        "unit_price": {
                            "type": "number",
                            "description": "Unit price for the product.",
                        },
                        "sku": {
                            "type": "string",
                            "description": "Optional stock-keeping unit code.",
                        },
                    },
                    "required": ["name", "description", "unit_price"],
                },
            },
            {
                "name": "qb_create_estimate",
                "description": (
                    "Create a QuickBooks estimate (quote) for a customer with "
                    "line items. Returns the estimate ID, number, subtotal, and total."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Name of the customer.",
                        },
                        "line_items": {
                            "type": "array",
                            "description": (
                                "List of line item dicts, each with description, "
                                "quantity, unit_price, and amount."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "unit_price": {"type": "number"},
                                    "amount": {"type": "number"},
                                },
                                "required": ["description", "quantity", "unit_price", "amount"],
                            },
                        },
                        "notes": {
                            "type": "string",
                            "description": "Optional notes for the estimate.",
                        },
                    },
                    "required": ["customer_name", "line_items"],
                },
            },
            {
                "name": "qb_generate_pdf",
                "description": (
                    "Generate a PDF document for a QuickBooks estimate. "
                    "Returns the PDF URL and filename."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "estimate_id": {
                            "type": "string",
                            "description": "The QuickBooks estimate ID.",
                        },
                    },
                    "required": ["estimate_id"],
                },
            },
            {
                "name": "qb_email_estimate",
                "description": (
                    "Email a QuickBooks estimate to the customer. "
                    "Optionally include a custom message."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "estimate_id": {
                            "type": "string",
                            "description": "The QuickBooks estimate ID to send.",
                        },
                        "to_email": {
                            "type": "string",
                            "description": "Recipient email address.",
                        },
                        "message": {
                            "type": "string",
                            "description": "Optional custom message body for the email.",
                        },
                    },
                    "required": ["estimate_id", "to_email"],
                },
            },
            {
                "name": "qb_close_quote",
                "description": (
                    "Close a quote by accepting or rejecting it. If accepted, "
                    "the estimate is converted to an invoice in QuickBooks."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "estimate_id": {
                            "type": "string",
                            "description": "The QuickBooks estimate ID to close.",
                        },
                        "action": {
                            "type": "string",
                            "enum": ["accept", "reject"],
                            "description": "Whether to accept or reject the quote.",
                        },
                    },
                    "required": ["estimate_id", "action"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "qb_create_product":
            return self._create_product(tool_input)
        elif tool_name == "qb_create_estimate":
            return self._create_estimate(tool_input)
        elif tool_name == "qb_generate_pdf":
            return self._generate_pdf(tool_input)
        elif tool_name == "qb_email_estimate":
            return self._email_estimate(tool_input)
        elif tool_name == "qb_close_quote":
            return self._close_quote(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Tool implementations
    # ------------------------------------------------------------------

    def _create_product(self, tool_input: dict) -> dict:
        return _qb.create_product(
            name=tool_input["name"],
            description=tool_input["description"],
            unit_price=tool_input["unit_price"],
            sku=tool_input.get("sku"),
        )

    def _create_estimate(self, tool_input: dict) -> dict:
        return _qb.create_estimate(
            customer_name=tool_input["customer_name"],
            line_items=tool_input["line_items"],
            notes=tool_input.get("notes"),
        )

    def _generate_pdf(self, tool_input: dict) -> dict:
        return _qb.generate_estimate_pdf(
            estimate_id=tool_input["estimate_id"],
        )

    def _email_estimate(self, tool_input: dict) -> dict:
        return _qb.send_estimate_email(
            estimate_id=tool_input["estimate_id"],
            to_email=tool_input["to_email"],
            message=tool_input.get("message"),
        )

    def _close_quote(self, tool_input: dict) -> dict:
        estimate_id = tool_input["estimate_id"]
        action = tool_input["action"]

        if action == "accept":
            result = _qb.convert_estimate_to_invoice(estimate_id)
            result["action"] = "accepted"
            print(f"[QB] Quote {estimate_id} accepted and converted to invoice")
            return result
        elif action == "reject":
            print(f"[QB] Quote {estimate_id} rejected")
            return {
                "estimate_id": estimate_id,
                "action": "rejected",
                "status": "rejected",
            }
        else:
            return {"error": f"Invalid action: '{action}'. Must be 'accept' or 'reject'."}
