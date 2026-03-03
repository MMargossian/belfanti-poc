"""
Material RFQ module for Phase D of the Belfanti CNC Manufacturing POC.
Handles vendor search, RFQ distribution, bid evaluation, and vendor selection.
"""

from typing import Any

from modules.base import BaseModule
from services.mock_vendor_db import MockVendorDBService


# Module-level singleton
_vendor_db = MockVendorDBService()


class MaterialRFQModule(BaseModule):
    """Search vendors, send material RFQs, evaluate bids, and select winners."""

    @property
    def name(self) -> str:
        return "material_rfq"

    @property
    def description(self) -> str:
        return "Search vendors, send material RFQs, evaluate bids, and select winners"

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "search_material_vendors",
                "description": (
                    "Search for vendors that supply a given material type. "
                    "Accepts a MaterialType enum value (e.g. '6061-T6 Aluminum') "
                    "or a keyword string (e.g. 'aluminum', 'steel', 'plastics')."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "material_type": {
                            "type": "string",
                            "description": "Material type enum value or keyword to search for.",
                        },
                    },
                    "required": ["material_type"],
                },
            },
            {
                "name": "send_vendor_rfqs",
                "description": (
                    "Send material RFQ requests to a list of vendors and collect "
                    "their price quotes. Returns a list of vendor quotes with "
                    "pricing and lead time information."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "vendors": {
                            "type": "array",
                            "description": "List of vendor dicts, each with at least vendor_id and vendor_name.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "vendor_id": {"type": "string"},
                                    "vendor_name": {"type": "string"},
                                },
                                "required": ["vendor_id", "vendor_name"],
                            },
                        },
                        "material_description": {
                            "type": "string",
                            "description": "Description of the material being requested.",
                        },
                        "quantity": {
                            "type": "number",
                            "description": "Quantity of material needed.",
                        },
                        "unit": {
                            "type": "string",
                            "description": "Unit of measure (e.g. 'each', 'kg', 'lbs').",
                        },
                    },
                    "required": ["vendors", "material_description", "quantity", "unit"],
                },
            },
            {
                "name": "evaluate_vendor_bids",
                "description": (
                    "Evaluate and compare vendor quotes using a weighted scoring "
                    "model (price, lead time, rating). Returns the cheapest, "
                    "fastest, and recommended vendor."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "quotes": {
                            "type": "array",
                            "description": "List of vendor quote dicts to compare.",
                            "items": {"type": "object"},
                        },
                    },
                    "required": ["quotes"],
                },
            },
            {
                "name": "select_vendor",
                "description": (
                    "Record the selection of a vendor for a material quote. "
                    "Returns a confirmation of the selection."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "quote_id": {
                            "type": "string",
                            "description": "The ID of the selected vendor quote.",
                        },
                        "vendor_name": {
                            "type": "string",
                            "description": "Name of the selected vendor.",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for selecting this vendor.",
                        },
                    },
                    "required": ["quote_id", "vendor_name", "reason"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "search_material_vendors":
            return self._search_material_vendors(tool_input)
        elif tool_name == "send_vendor_rfqs":
            return self._send_vendor_rfqs(tool_input)
        elif tool_name == "evaluate_vendor_bids":
            return self._evaluate_vendor_bids(tool_input)
        elif tool_name == "select_vendor":
            return self._select_vendor(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Tool implementations
    # ------------------------------------------------------------------

    def _search_material_vendors(self, tool_input: dict) -> list[dict]:
        material_type = tool_input["material_type"]
        vendors = _vendor_db.search_vendors(material_type)
        return vendors

    def _send_vendor_rfqs(self, tool_input: dict) -> list[dict]:
        vendors = tool_input["vendors"]
        material_description = tool_input["material_description"]
        quantity = tool_input["quantity"]
        unit = tool_input["unit"]

        quotes = []
        for vendor in vendors:
            quote = _vendor_db.request_quote(
                vendor_id=vendor["vendor_id"],
                material_description=material_description,
                quantity=quantity,
                unit=unit,
            )
            quotes.append(quote)

        return quotes

    def _evaluate_vendor_bids(self, tool_input: dict) -> dict:
        quotes = tool_input["quotes"]
        comparison = _vendor_db.compare_quotes(quotes)
        return comparison

    def _select_vendor(self, tool_input: dict) -> dict:
        quote_id = tool_input["quote_id"]
        vendor_name = tool_input["vendor_name"]
        reason = tool_input["reason"]

        return {
            "status": "selected",
            "quote_id": quote_id,
            "vendor_name": vendor_name,
            "reason": reason,
            "message": f"Vendor '{vendor_name}' selected for quote {quote_id}. Reason: {reason}",
        }
