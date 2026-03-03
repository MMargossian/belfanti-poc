"""
Purchase Order module for the Belfanti CNC Manufacturing POC.
Creates purchase orders and sales orders in QuickBooks, sends PO notifications
to vendors, sends order confirmations to customers, and confirms deliveries.
"""

from datetime import datetime
from typing import Any

from modules.base import BaseModule
from services.mock_quickbooks import MockQuickBooksService
from services.mock_gmail import MockGmailService


# Module-level service singletons
_qb = MockQuickBooksService
_gmail = MockGmailService

# Track delivery confirmations by PO ID
_delivery_records: dict[str, dict] = {}


class PurchaseOrderModule(BaseModule):
    """Create purchase orders, sales orders, send confirmations, and track delivery."""

    @property
    def name(self) -> str:
        return "purchase_order"

    @property
    def description(self) -> str:
        return "Create purchase orders, sales orders, send confirmations, and track delivery"

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "create_purchase_order",
                "description": (
                    "Create a purchase order for materials from a vendor. "
                    "Uses QuickBooks to generate the PO with line items and totals."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "vendor_id": {
                            "type": "string",
                            "description": "Unique identifier for the vendor.",
                        },
                        "vendor_name": {
                            "type": "string",
                            "description": "Name of the vendor.",
                        },
                        "quote_id": {
                            "type": "string",
                            "description": "The quote this purchase order relates to.",
                        },
                        "materials": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "unit_price": {"type": "number"},
                                    "total": {"type": "number"},
                                },
                            },
                            "description": "List of material line items with description, quantity, unit_price, and total.",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Optional notes for the purchase order.",
                        },
                    },
                    "required": ["vendor_id", "vendor_name", "quote_id", "materials"],
                },
            },
            {
                "name": "create_sales_order",
                "description": (
                    "Create a sales order for a customer from an accepted quote/estimate. "
                    "Uses QuickBooks to generate the SO with line items."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Name of the customer.",
                        },
                        "quote_id": {
                            "type": "string",
                            "description": "The originating quote identifier.",
                        },
                        "estimate_id": {
                            "type": "string",
                            "description": "The QuickBooks estimate identifier.",
                        },
                        "line_items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "unit_price": {"type": "number"},
                                    "amount": {"type": "number"},
                                },
                            },
                            "description": "List of line items with description, quantity, unit_price, and amount.",
                        },
                    },
                    "required": ["customer_name", "quote_id", "estimate_id", "line_items"],
                },
            },
            {
                "name": "send_po_to_vendor",
                "description": (
                    "Send a purchase order notification email to a vendor. "
                    "Uses Gmail to deliver the PO details."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "po_id": {
                            "type": "string",
                            "description": "The purchase order identifier to send.",
                        },
                        "vendor_email": {
                            "type": "string",
                            "description": "Vendor's email address.",
                        },
                        "vendor_name": {
                            "type": "string",
                            "description": "Vendor's name for the email greeting.",
                        },
                    },
                    "required": ["po_id", "vendor_email", "vendor_name"],
                },
            },
            {
                "name": "send_order_confirmation",
                "description": (
                    "Send an order confirmation email to the customer with sales order "
                    "details and expected delivery date."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_email": {
                            "type": "string",
                            "description": "Customer's email address.",
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Customer's name for the email greeting.",
                        },
                        "sales_order_number": {
                            "type": "string",
                            "description": "The sales order number to reference in the confirmation.",
                        },
                        "expected_delivery": {
                            "type": "string",
                            "description": "Expected delivery date string (e.g. '2026-03-15').",
                        },
                    },
                    "required": ["customer_email", "customer_name", "sales_order_number", "expected_delivery"],
                },
            },
            {
                "name": "confirm_delivery",
                "description": (
                    "Confirm that materials from a purchase order have been received. "
                    "Marks the PO as received and optionally records a tracking number."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "po_id": {
                            "type": "string",
                            "description": "The purchase order identifier to mark as received.",
                        },
                        "tracking_number": {
                            "type": "string",
                            "description": "Optional shipment tracking number.",
                        },
                    },
                    "required": ["po_id"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "create_purchase_order":
            return self._create_purchase_order(**tool_input)
        elif tool_name == "create_sales_order":
            return self._create_sales_order(**tool_input)
        elif tool_name == "send_po_to_vendor":
            return self._send_po_to_vendor(**tool_input)
        elif tool_name == "send_order_confirmation":
            return self._send_order_confirmation(**tool_input)
        elif tool_name == "confirm_delivery":
            return self._confirm_delivery(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Internal tool implementations
    # ------------------------------------------------------------------

    def _create_purchase_order(
        self,
        vendor_id: str,
        vendor_name: str,
        quote_id: str,
        materials: list[dict],
        notes: str | None = None,
    ) -> dict:
        """Create a purchase order via QuickBooks."""
        # Convert materials to the line_items format QuickBooks expects
        line_items = []
        for mat in materials:
            line_items.append({
                "description": mat.get("description", ""),
                "quantity": mat.get("quantity", 1),
                "unit_price": mat.get("unit_price", 0.0),
                "amount": mat.get("total", mat.get("quantity", 1) * mat.get("unit_price", 0.0)),
            })

        po_result = _qb.create_purchase_order(
            vendor_name=vendor_name,
            line_items=line_items,
            notes=notes,
        )

        return {
            "po_id": po_result["po_id"],
            "po_number": po_result["po_number"],
            "vendor_id": vendor_id,
            "vendor_name": vendor_name,
            "quote_id": quote_id,
            "total": po_result["total"],
            "status": po_result["status"],
        }

    def _create_sales_order(
        self,
        customer_name: str,
        quote_id: str,
        estimate_id: str,
        line_items: list[dict],
    ) -> dict:
        """Create a sales order via QuickBooks."""
        so_result = _qb.create_sales_order(
            customer_name=customer_name,
            estimate_id=estimate_id,
            line_items=line_items,
        )

        return {
            "so_id": so_result["so_id"],
            "so_number": so_result["so_number"],
            "customer_name": customer_name,
            "quote_id": quote_id,
            "estimate_id": estimate_id,
            "total": so_result["total"],
            "status": so_result["status"],
        }

    def _send_po_to_vendor(
        self,
        po_id: str,
        vendor_email: str,
        vendor_name: str,
    ) -> dict:
        """Send a PO notification email to the vendor via Gmail."""
        # Look up PO details from QuickBooks for the email body
        po_data = _qb.get_purchase_order(po_id)
        po_number = po_data["po_number"] if po_data else po_id
        total = po_data["total"] if po_data else "N/A"

        subject = f"Purchase Order {po_number} from Belfanti CNC Manufacturing"
        body = (
            f"Dear {vendor_name},\n\n"
            f"Please find attached Purchase Order {po_number}.\n\n"
            f"Order Total: ${total}\n\n"
            f"Please confirm receipt and expected delivery timeline.\n\n"
            f"Thank you,\n"
            f"Belfanti CNC Manufacturing"
        )

        email_result = _gmail.send_email(
            to=vendor_email,
            subject=subject,
            body=body,
            attachments=[f"{po_number}.pdf"],
        )

        # Update PO status to sent
        if po_data:
            po_data["status"] = "sent"

        return {
            "po_id": po_id,
            "po_number": po_number,
            "vendor_email": vendor_email,
            "email_message_id": email_result["message_id"],
            "status": "sent",
        }

    def _send_order_confirmation(
        self,
        customer_email: str,
        customer_name: str,
        sales_order_number: str,
        expected_delivery: str,
    ) -> dict:
        """Send an order confirmation email to the customer via Gmail."""
        subject = f"Order Confirmation - {sales_order_number} | Belfanti CNC Manufacturing"
        body = (
            f"Dear {customer_name},\n\n"
            f"Thank you for your order. This email confirms that your order "
            f"({sales_order_number}) has been received and is being processed.\n\n"
            f"Expected Delivery: {expected_delivery}\n\n"
            f"We will notify you when your order ships. If you have any questions, "
            f"please don't hesitate to reach out.\n\n"
            f"Best regards,\n"
            f"Belfanti CNC Manufacturing"
        )

        email_result = _gmail.send_email(
            to=customer_email,
            subject=subject,
            body=body,
        )

        return {
            "customer_email": customer_email,
            "customer_name": customer_name,
            "sales_order_number": sales_order_number,
            "expected_delivery": expected_delivery,
            "email_message_id": email_result["message_id"],
            "status": "sent",
        }

    def _confirm_delivery(
        self,
        po_id: str,
        tracking_number: str | None = None,
    ) -> dict:
        """Confirm that a PO delivery has been received."""
        received_at = datetime.now().isoformat()

        # Update PO status in QuickBooks
        po_data = _qb.get_purchase_order(po_id)
        po_number = po_id
        if po_data:
            po_data["status"] = "received"
            po_number = po_data.get("po_number", po_id)

        # Store delivery record
        _delivery_records[po_id] = {
            "po_id": po_id,
            "po_number": po_number,
            "tracking_number": tracking_number,
            "received_at": received_at,
            "status": "received",
        }

        print(f"[PurchaseOrder] PO {po_number} marked as received")

        return {
            "po_id": po_id,
            "po_number": po_number,
            "tracking_number": tracking_number,
            "received_at": received_at,
            "status": "received",
        }
