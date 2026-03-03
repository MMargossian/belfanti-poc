"""
Customer Response module for the Belfanti CNC Manufacturing POC.
Records and processes customer responses (accept/reject) to quotes,
and provides quote status lookups.
"""

from datetime import datetime
from typing import Any

from modules.base import BaseModule


# Module-level dict to track customer responses to quotes.
# Keyed by quote_id -> {"status": str, "customer_name": str, "notes": str, "response_date": str}
_quote_responses: dict[str, dict] = {}


class CustomerResponseModule(BaseModule):
    """Record and process customer responses to quotes."""

    @property
    def name(self) -> str:
        return "customer_response"

    @property
    def description(self) -> str:
        return "Record and process customer responses to quotes"

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "record_customer_response",
                "description": (
                    "Record a customer's response to a quote. If accepted, returns next steps "
                    "to create purchase order and sales order. If rejected, the quote is closed."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "quote_id": {
                            "type": "string",
                            "description": "The quote identifier the customer is responding to.",
                        },
                        "response": {
                            "type": "string",
                            "enum": ["accepted", "rejected"],
                            "description": "Customer response: 'accepted' or 'rejected'.",
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Name of the customer providing the response.",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Optional notes from the customer about their decision.",
                        },
                    },
                    "required": ["quote_id", "response", "customer_name"],
                },
            },
            {
                "name": "check_quote_status",
                "description": (
                    "Check the current status of a quote based on recorded customer responses. "
                    "Returns the quote ID, status, and the date the response was recorded."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "quote_id": {
                            "type": "string",
                            "description": "The quote identifier to check.",
                        },
                    },
                    "required": ["quote_id"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "record_customer_response":
            return self._record_customer_response(**tool_input)
        elif tool_name == "check_quote_status":
            return self._check_quote_status(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Internal tool implementations
    # ------------------------------------------------------------------

    def _record_customer_response(
        self,
        quote_id: str,
        response: str,
        customer_name: str,
        notes: str | None = None,
    ) -> dict:
        """Record a customer's acceptance or rejection of a quote."""
        response_date = datetime.now().isoformat()

        _quote_responses[quote_id] = {
            "status": response,
            "customer_name": customer_name,
            "notes": notes or "",
            "response_date": response_date,
        }

        print(f"[CustomerResponse] Quote {quote_id} -> {response} by {customer_name}")

        if response == "accepted":
            return {
                "quote_id": quote_id,
                "status": "accepted",
                "customer_name": customer_name,
                "response_date": response_date,
                "notes": notes or "",
                "next_steps": "Proceed to create purchase order and sales order",
            }
        else:
            return {
                "quote_id": quote_id,
                "status": "rejected",
                "customer_name": customer_name,
                "response_date": response_date,
                "notes": notes or "",
                "next_steps": "Quote closed. Log outcome to tracking sheet.",
            }

    def _check_quote_status(self, quote_id: str) -> dict:
        """Check the current status of a quote from recorded responses."""
        record = _quote_responses.get(quote_id)

        if record:
            return {
                "quote_id": quote_id,
                "status": record["status"],
                "response_date": record["response_date"],
                "customer_name": record["customer_name"],
                "notes": record["notes"],
            }

        return {
            "quote_id": quote_id,
            "status": "pending",
            "response_date": None,
            "note": "No customer response has been recorded for this quote.",
        }
