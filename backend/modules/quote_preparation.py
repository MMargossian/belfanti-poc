"""
Quote Preparation module for Phase D of the Belfanti CNC Manufacturing POC.
Calculates part costs and assembles customer quotes with material, machine time,
and finishing costs.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Any

from modules.base import BaseModule
from data.machine_rates import MACHINE_HOURLY_RATES, SETUP_COSTS, FINISHING_RATES
from models.rfq import MachineType, SurfaceFinish
from models.quote import Quote, QuoteLineItem, QuoteStatus


def _resolve_machine_type(machine_type_str: str) -> MachineType:
    """Resolve a string to a MachineType enum, trying value and name match."""
    for mt in MachineType:
        if machine_type_str == mt.value or machine_type_str == mt.name or machine_type_str == mt:
            return mt
    raise ValueError(f"Unknown machine_type: '{machine_type_str}'. Valid values: {[m.value for m in MachineType]}")


def _resolve_surface_finish(surface_finish_str: str) -> SurfaceFinish:
    """Resolve a string to a SurfaceFinish enum, trying value and name match."""
    for sf in SurfaceFinish:
        if surface_finish_str == sf.value or surface_finish_str == sf.name or surface_finish_str == sf:
            return sf
    raise ValueError(
        f"Unknown surface_finish: '{surface_finish_str}'. Valid values: {[s.value for s in SurfaceFinish]}"
    )


def _generate_quote_id() -> str:
    """Generate a quote ID like 'Q-' followed by 6 random alphanumeric characters."""
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=6))
    return f"Q-{suffix}"


class QuotePreparationModule(BaseModule):
    """Calculate costs and build customer quote with material, machine time, and finishing costs."""

    # In-memory storage for the current session's quote and line items
    _current_line_items: list[dict] = []
    _current_quote: dict | None = None

    @property
    def name(self) -> str:
        return "quote_preparation"

    @property
    def description(self) -> str:
        return "Calculate costs and build customer quote with material, machine time, and finishing costs"

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "calculate_part_cost",
                "description": (
                    "Calculate the full cost breakdown for a single part, including "
                    "material, machining, setup, and finishing costs. Applies a margin "
                    "to determine the selling price. Returns a QuoteLineItem-compatible dict."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "part_number": {
                            "type": "string",
                            "description": "Part number identifier.",
                        },
                        "part_name": {
                            "type": "string",
                            "description": "Human-readable part name.",
                        },
                        "material_type": {
                            "type": "string",
                            "description": "Material type (for reference in the line item).",
                        },
                        "material_cost": {
                            "type": "number",
                            "description": "Per-unit material cost from the vendor quote.",
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of parts to produce.",
                        },
                        "machine_type": {
                            "type": "string",
                            "description": "Machine type enum value (e.g. '3-axis_mill', 'lathe').",
                        },
                        "estimated_hours": {
                            "type": "number",
                            "description": "Estimated machine hours per part.",
                        },
                        "surface_finish": {
                            "type": "string",
                            "description": "Surface finish enum value (e.g. 'anodize', 'as_machined').",
                        },
                        "margin_percent": {
                            "type": "number",
                            "description": "Profit margin percentage (default 30).",
                        },
                    },
                    "required": [
                        "part_number",
                        "part_name",
                        "material_type",
                        "material_cost",
                        "quantity",
                        "machine_type",
                        "estimated_hours",
                        "surface_finish",
                    ],
                },
            },
            {
                "name": "build_quote",
                "description": (
                    "Assemble a complete customer quote from a list of calculated "
                    "line items. Generates a quote ID, calculates subtotal, tax, "
                    "and total. Returns the full Quote as a dict."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Customer's full name.",
                        },
                        "customer_email": {
                            "type": "string",
                            "description": "Customer's email address.",
                        },
                        "customer_company": {
                            "type": "string",
                            "description": "Customer's company name (optional).",
                        },
                        "line_items": {
                            "type": "array",
                            "description": "List of line item dicts from calculate_part_cost.",
                            "items": {"type": "object"},
                        },
                        "tax_rate": {
                            "type": "number",
                            "description": "Tax rate as a percentage (default 0).",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Optional notes for the quote.",
                        },
                    },
                    "required": ["customer_name", "customer_email", "line_items"],
                },
            },
            {
                "name": "adjust_margin",
                "description": (
                    "Recalculate a specific line item with a new margin percentage. "
                    "Returns the updated line item dict with revised pricing."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "line_item_index": {
                            "type": "integer",
                            "description": "Zero-based index of the line item to adjust.",
                        },
                        "new_margin_percent": {
                            "type": "number",
                            "description": "New profit margin percentage.",
                        },
                    },
                    "required": ["line_item_index", "new_margin_percent"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "calculate_part_cost":
            return self._calculate_part_cost(tool_input)
        elif tool_name == "build_quote":
            return self._build_quote(tool_input)
        elif tool_name == "adjust_margin":
            return self._adjust_margin(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Tool implementations
    # ------------------------------------------------------------------

    def _calculate_part_cost(self, tool_input: dict) -> dict:
        part_number = tool_input["part_number"]
        part_name = tool_input["part_name"]
        material_type = tool_input["material_type"]
        material_cost = tool_input["material_cost"]
        quantity = tool_input["quantity"]
        machine_type_str = tool_input["machine_type"]
        estimated_hours = tool_input["estimated_hours"]
        surface_finish_str = tool_input["surface_finish"]
        margin_percent = tool_input.get("margin_percent", 30.0)

        # Resolve enums
        machine_type = _resolve_machine_type(machine_type_str)
        surface_finish = _resolve_surface_finish(surface_finish_str)

        # Look up rates
        hourly_rate = MACHINE_HOURLY_RATES[machine_type]
        setup_cost = SETUP_COSTS[machine_type]
        finishing_cost = FINISHING_RATES[surface_finish]

        # Calculate costs
        machine_cost = round(hourly_rate * estimated_hours, 2)
        setup_cost_per_unit = round(setup_cost / quantity, 2)
        unit_cost = round(material_cost + machine_cost + setup_cost_per_unit + finishing_cost, 2)
        unit_price = round(unit_cost / (1 - margin_percent / 100), 2)
        line_total = round(unit_price * quantity, 2)

        line_item = {
            "part_number": part_number,
            "part_name": part_name,
            "description": f"{part_name} - {material_type} - {surface_finish_str}",
            "quantity": quantity,
            "material_cost": round(material_cost, 2),
            "machine_cost": machine_cost,
            "finishing_cost": round(finishing_cost, 2),
            "setup_cost": round(setup_cost, 2),
            "unit_cost": unit_cost,
            "margin_percent": margin_percent,
            "unit_price": unit_price,
            "line_total": line_total,
            "line_price": line_total,
        }

        # Store for potential margin adjustment
        self._current_line_items.append(line_item)

        print(
            f"[QuotePrep] Part {part_number}: "
            f"material=${material_cost:.2f} + machine=${machine_cost:.2f} + "
            f"setup=${setup_cost_per_unit:.2f}/unit + finish=${finishing_cost:.2f} = "
            f"cost=${unit_cost:.2f} -> price=${unit_price:.2f} @ {margin_percent}% margin "
            f"-> line total=${line_total:.2f} (qty {quantity})"
        )

        return line_item

    def _build_quote(self, tool_input: dict) -> dict:
        customer_name = tool_input["customer_name"]
        customer_email = tool_input["customer_email"]
        customer_company = tool_input.get("customer_company")
        line_items = tool_input["line_items"]
        tax_rate = tool_input.get("tax_rate", 0.0)
        notes = tool_input.get("notes")

        quote_id = _generate_quote_id()
        subtotal = round(sum(item.get("line_total", item.get("line_price", 0)) for item in line_items), 2)
        tax_amount = round(subtotal * (tax_rate / 100), 2)
        total = round(subtotal + tax_amount, 2)

        now = datetime.now()
        valid_until = now + timedelta(days=30)

        quote = {
            "id": quote_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_company": customer_company,
            "line_items": line_items,
            "subtotal": subtotal,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "total": total,
            "status": QuoteStatus.DRAFT.value,
            "created_at": now.isoformat(),
            "valid_until": valid_until.isoformat(),
            "notes": notes,
            "revision": 1,
        }

        self._current_quote = quote

        print(
            f"[QuotePrep] Quote {quote_id} built for {customer_name}: "
            f"subtotal=${subtotal:.2f}, tax=${tax_amount:.2f}, total=${total:.2f}"
        )

        return quote

    def _adjust_margin(self, tool_input: dict) -> dict:
        line_item_index = tool_input["line_item_index"]
        new_margin_percent = tool_input["new_margin_percent"]

        if line_item_index < 0 or line_item_index >= len(self._current_line_items):
            return {
                "error": (
                    f"Invalid line_item_index {line_item_index}. "
                    f"Valid range: 0-{len(self._current_line_items) - 1}"
                ),
            }

        item = self._current_line_items[line_item_index]
        old_margin = item["margin_percent"]
        unit_cost = item["unit_cost"]
        quantity = item["quantity"]

        # Recalculate with new margin
        new_unit_price = round(unit_cost / (1 - new_margin_percent / 100), 2)
        new_line_total = round(new_unit_price * quantity, 2)

        item["margin_percent"] = new_margin_percent
        item["unit_price"] = new_unit_price
        item["line_total"] = new_line_total
        item["line_price"] = new_line_total

        print(
            f"[QuotePrep] Margin adjusted for item {line_item_index} "
            f"({item['part_number']}): {old_margin}% -> {new_margin_percent}% "
            f"(price ${item['unit_price']:.2f} -> ${new_unit_price:.2f})"
        )

        return item
