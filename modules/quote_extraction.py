"""
Quote Extraction module for the Belfanti CNC Manufacturing POC.
Extracts and validates part specifications from RFQ details.
"""

from typing import Any

from models.rfq import MachineType, MaterialSpec, MaterialType, PartSpec, SurfaceFinish
from modules.base import BaseModule


# Hardcoded database of parts the shop has manufactured before
_EXISTING_PARTS: dict[str, dict] = {
    "BRK-4401": {
        "part_number": "BRK-4401",
        "part_name": "Mounting Bracket - Type A",
        "material": "6061-T6 Aluminum",
        "machine_type": "3-axis_mill",
        "surface_finish": "anodize",
        "tolerances": "+/- 0.005\"",
        "last_manufactured": "2024-03",
        "machine_hours": 0.8,
        "notes": "Last manufactured 2024-03, used 6061-T6, 0.8 hrs machine time. Standard repeat order.",
    },
    "SFT-2200": {
        "part_number": "SFT-2200",
        "part_name": "Drive Shaft Coupler",
        "material": "4140 Steel",
        "machine_type": "lathe",
        "surface_finish": "as_machined",
        "tolerances": "+/- 0.001\"",
        "last_manufactured": "2024-07",
        "machine_hours": 1.5,
        "notes": "Last manufactured 2024-07, used 4140 Steel, 1.5 hrs machine time. Requires center drilling.",
    },
    "HSG-1050": {
        "part_number": "HSG-1050",
        "part_name": "Sensor Housing",
        "material": "303 Stainless Steel",
        "machine_type": "5-axis_mill",
        "surface_finish": "passivate",
        "tolerances": "+/- 0.002\"",
        "last_manufactured": "2025-01",
        "machine_hours": 2.2,
        "notes": "Last manufactured 2025-01, used 303 SS, 2.2 hrs machine time. Complex geometry, 5-axis required.",
    },
    "PIN-0078": {
        "part_number": "PIN-0078",
        "part_name": "Dowel Pin - Custom",
        "material": "304 Stainless Steel",
        "machine_type": "lathe",
        "surface_finish": "electropolish",
        "tolerances": "+/- 0.0005\"",
        "last_manufactured": "2024-11",
        "machine_hours": 0.3,
        "notes": "Last manufactured 2024-11, used 304 SS, 0.3 hrs machine time. High-precision medical grade.",
    },
}

# Materials that cannot be used with EDM (non-conductive)
_NON_CONDUCTIVE_MATERIALS = {
    MaterialType.DELRIN,
    MaterialType.NYLON,
    MaterialType.PEEK,
}

# Map of material enum values by lowercase name fragments for fuzzy matching
_MATERIAL_LOOKUP: dict[str, MaterialType] = {}
for mt in MaterialType:
    _MATERIAL_LOOKUP[mt.value.lower()] = mt
    # Also index by enum name (e.g., "aluminum_6061")
    _MATERIAL_LOOKUP[mt.name.lower()] = mt


def _resolve_material(raw: str) -> MaterialType | None:
    """Attempt to resolve a raw material string to a MaterialType enum value."""
    raw_lower = raw.strip().lower()

    # Exact match against enum value or name
    for key, mt in _MATERIAL_LOOKUP.items():
        if raw_lower == key:
            return mt

    # Substring match (e.g., "6061" should match "6061-T6 Aluminum")
    for mt in MaterialType:
        if raw_lower in mt.value.lower() or raw_lower in mt.name.lower():
            return mt

    return None


def _resolve_machine_type(raw: str) -> MachineType | None:
    """Attempt to resolve a raw machine type string to a MachineType enum."""
    raw_lower = raw.strip().lower().replace(" ", "_").replace("-", "_")
    for mt in MachineType:
        if raw_lower == mt.value.lower() or raw_lower == mt.name.lower():
            return mt
    # Flexible matching
    if "5" in raw_lower and ("axis" in raw_lower or "ax" in raw_lower):
        return MachineType.FIVE_AXIS
    if "3" in raw_lower and ("axis" in raw_lower or "ax" in raw_lower):
        return MachineType.THREE_AXIS
    if "lathe" in raw_lower or "turn" in raw_lower:
        return MachineType.LATHE
    if "edm" in raw_lower:
        return MachineType.EDM
    if "grind" in raw_lower:
        return MachineType.GRINDER
    return None


def _resolve_surface_finish(raw: str) -> SurfaceFinish | None:
    """Attempt to resolve a raw surface finish string to a SurfaceFinish enum."""
    raw_lower = raw.strip().lower().replace(" ", "_").replace("-", "_")
    for sf in SurfaceFinish:
        if raw_lower == sf.value.lower() or raw_lower == sf.name.lower():
            return sf
    # Flexible matching
    if "bead" in raw_lower and "blast" in raw_lower:
        return SurfaceFinish.BEAD_BLAST
    if "hard" in raw_lower and "anod" in raw_lower:
        return SurfaceFinish.HARD_ANODIZE
    if "anod" in raw_lower:
        return SurfaceFinish.ANODIZE
    if "powder" in raw_lower:
        return SurfaceFinish.POWDER_COAT
    if "electro" in raw_lower and "polish" in raw_lower:
        return SurfaceFinish.ELECTROPOLISH
    if "passiv" in raw_lower:
        return SurfaceFinish.PASSIVATE
    if "chrome" in raw_lower:
        return SurfaceFinish.CHROME
    if "nickel" in raw_lower:
        return SurfaceFinish.NICKEL
    if "as" in raw_lower and "machine" in raw_lower:
        return SurfaceFinish.AS_MACHINED
    return None


class QuoteExtractionModule(BaseModule):
    """Extract part specifications from RFQ details and validate them."""

    @property
    def name(self) -> str:
        return "quote_extraction"

    @property
    def description(self) -> str:
        return "Extract part specifications from RFQ details and validate"

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "extract_part_specs",
                "description": (
                    "Register and validate a list of extracted part specifications. "
                    "The agent (Claude) extracts part info from the email text using its intelligence, "
                    "then calls this tool to validate and store the parts. Each part dict should include "
                    "fields like part_number, part_name, material_type, quantity, machine_type, "
                    "surface_finish, tolerances, stock_size, estimated_machine_hours, and cad_file_name."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "part_number": {
                                        "type": "string",
                                        "description": "Part number / identifier.",
                                    },
                                    "part_name": {
                                        "type": "string",
                                        "description": "Human-readable part name.",
                                    },
                                    "material_type": {
                                        "type": "string",
                                        "description": "Material specification (e.g., '6061-T6 Aluminum').",
                                    },
                                    "quantity": {
                                        "type": "integer",
                                        "description": "Number of parts requested.",
                                        "default": 1,
                                    },
                                    "machine_type": {
                                        "type": "string",
                                        "description": "Machine type (e.g., '3-axis_mill', 'lathe', 'edm').",
                                    },
                                    "surface_finish": {
                                        "type": "string",
                                        "description": "Required surface finish (e.g., 'anodize', 'as_machined').",
                                    },
                                    "tolerances": {
                                        "type": "string",
                                        "description": "Tolerance specification (e.g., '+/- 0.005\"').",
                                    },
                                    "stock_size": {
                                        "type": "string",
                                        "description": "Raw material stock size (e.g., '2x4x6 block').",
                                    },
                                    "estimated_machine_hours": {
                                        "type": "number",
                                        "description": "Estimated CNC machine hours per part.",
                                    },
                                    "cad_file_name": {
                                        "type": "string",
                                        "description": "Associated CAD file name.",
                                    },
                                },
                                "required": ["part_number", "part_name", "material_type"],
                            },
                            "description": "List of part specification dicts to validate and register.",
                        },
                    },
                    "required": ["parts"],
                },
            },
            {
                "name": "check_existing_part",
                "description": (
                    "Check if a part number exists in the shop's database of previously manufactured parts. "
                    "Returns historical details if found (material used, machine time, last manufacture date)."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "part_number": {
                            "type": "string",
                            "description": "Part number to look up.",
                        },
                    },
                    "required": ["part_number"],
                },
            },
            {
                "name": "validate_part_specs",
                "description": (
                    "Run validation checks on a list of part specifications. "
                    "Checks material/machine compatibility (e.g., cannot EDM plastic), "
                    "reasonable quantities, and valid enum values."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "part_number": {"type": "string"},
                                    "part_name": {"type": "string"},
                                    "material_type": {"type": "string"},
                                    "quantity": {"type": "integer"},
                                    "machine_type": {"type": "string"},
                                    "surface_finish": {"type": "string"},
                                    "tolerances": {"type": "string"},
                                    "estimated_machine_hours": {"type": "number"},
                                },
                                "required": ["part_number", "part_name", "material_type"],
                            },
                            "description": "List of part specification dicts to validate.",
                        },
                    },
                    "required": ["parts"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "extract_part_specs":
            return self._extract_part_specs(tool_input["parts"])
        elif tool_name == "check_existing_part":
            return self._check_existing_part(tool_input["part_number"])
        elif tool_name == "validate_part_specs":
            return self._validate_part_specs(tool_input["parts"])
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Internal tool implementations
    # ------------------------------------------------------------------

    def _extract_part_specs(self, parts: list[dict]) -> dict:
        """Validate and convert raw part dicts into PartSpec objects."""
        validated_parts: list[dict] = []
        warnings: list[str] = []

        for i, raw_part in enumerate(parts, start=1):
            part_number = raw_part.get("part_number", f"UNKNOWN-{i}")
            part_name = raw_part.get("part_name", "Unnamed Part")

            # Resolve material type
            material_str = raw_part.get("material_type", "")
            material_type = _resolve_material(material_str)
            if material_type is None:
                warnings.append(
                    f"Part {part_number}: Unrecognized material '{material_str}'. "
                    f"Defaulting to 6061-T6 Aluminum. Valid options: "
                    f"{', '.join(mt.value for mt in MaterialType)}"
                )
                material_type = MaterialType.ALUMINUM_6061

            # Resolve machine type
            machine_str = raw_part.get("machine_type", "3-axis_mill")
            machine_type = _resolve_machine_type(machine_str)
            if machine_type is None:
                warnings.append(
                    f"Part {part_number}: Unrecognized machine type '{machine_str}'. "
                    f"Defaulting to 3-axis mill."
                )
                machine_type = MachineType.THREE_AXIS

            # Resolve surface finish
            finish_str = raw_part.get("surface_finish", "as_machined")
            surface_finish = _resolve_surface_finish(finish_str)
            if surface_finish is None:
                warnings.append(
                    f"Part {part_number}: Unrecognized surface finish '{finish_str}'. "
                    f"Defaulting to as-machined."
                )
                surface_finish = SurfaceFinish.AS_MACHINED

            quantity = raw_part.get("quantity", 1)
            if not isinstance(quantity, int) or quantity < 1:
                warnings.append(f"Part {part_number}: Invalid quantity '{quantity}'. Defaulting to 1.")
                quantity = 1

            # Build the PartSpec
            material_spec = MaterialSpec(
                material_type=material_type,
                stock_size=raw_part.get("stock_size"),
                quantity_needed=float(quantity),
            )

            part_spec = PartSpec(
                part_number=part_number,
                part_name=part_name,
                material=material_spec,
                quantity=quantity,
                machine_type=machine_type,
                estimated_machine_hours=raw_part.get("estimated_machine_hours"),
                surface_finish=surface_finish,
                tolerances=raw_part.get("tolerances"),
                cad_file_name=raw_part.get("cad_file_name"),
            )

            validated_parts.append(part_spec.model_dump())

        return {
            "parts": validated_parts,
            "parts_count": len(validated_parts),
            "warnings": warnings,
        }

    def _check_existing_part(self, part_number: str) -> dict:
        """Check if a part number exists in the historical database."""
        part_upper = part_number.strip().upper()
        existing = _EXISTING_PARTS.get(part_upper)

        if existing:
            return {
                "found": True,
                **existing,
            }

        return {
            "found": False,
            "part_number": part_number,
        }

    def _validate_part_specs(self, parts: list[dict]) -> dict:
        """Run validation checks on a set of part specs."""
        issues: list[str] = []
        warnings: list[str] = []

        for raw_part in parts:
            pn = raw_part.get("part_number", "UNKNOWN")

            # --- Resolve enums for validation ---
            material_type = _resolve_material(raw_part.get("material_type", ""))
            machine_type = _resolve_machine_type(raw_part.get("machine_type", "3-axis_mill"))
            surface_finish = _resolve_surface_finish(raw_part.get("surface_finish", "as_machined"))

            # Check: valid material
            if material_type is None:
                issues.append(
                    f"Part {pn}: Unknown material '{raw_part.get('material_type')}'. "
                    f"Must be one of: {', '.join(mt.value for mt in MaterialType)}"
                )

            # Check: valid machine type
            if machine_type is None:
                issues.append(
                    f"Part {pn}: Unknown machine type '{raw_part.get('machine_type')}'. "
                    f"Must be one of: {', '.join(mt.value for mt in MachineType)}"
                )

            # Check: valid surface finish
            if surface_finish is None and raw_part.get("surface_finish"):
                issues.append(
                    f"Part {pn}: Unknown surface finish '{raw_part.get('surface_finish')}'. "
                    f"Must be one of: {', '.join(sf.value for sf in SurfaceFinish)}"
                )

            # Check: cannot EDM non-conductive materials (plastics)
            if (
                material_type in _NON_CONDUCTIVE_MATERIALS
                and machine_type == MachineType.EDM
            ):
                issues.append(
                    f"Part {pn}: Cannot use EDM with {material_type.value}. "
                    "EDM requires electrically conductive materials."
                )

            # Check: anodize only applies to aluminum
            aluminum_types = {MaterialType.ALUMINUM_6061, MaterialType.ALUMINUM_7075}
            if surface_finish in (SurfaceFinish.ANODIZE, SurfaceFinish.HARD_ANODIZE):
                if material_type and material_type not in aluminum_types:
                    warnings.append(
                        f"Part {pn}: Anodize finish is typically for aluminum, "
                        f"but material is {material_type.value}. Please confirm."
                    )

            # Check: passivate typically for stainless steel
            stainless_types = {
                MaterialType.STAINLESS_303,
                MaterialType.STAINLESS_304,
                MaterialType.STAINLESS_316,
            }
            if surface_finish == SurfaceFinish.PASSIVATE:
                if material_type and material_type not in stainless_types:
                    warnings.append(
                        f"Part {pn}: Passivation is typically for stainless steel, "
                        f"but material is {material_type.value}. Please confirm."
                    )

            # Check: reasonable quantity
            quantity = raw_part.get("quantity", 1)
            if isinstance(quantity, (int, float)):
                if quantity > 10000:
                    warnings.append(
                        f"Part {pn}: Very high quantity ({quantity}). "
                        "Please confirm this is not a typo."
                    )
                if quantity <= 0:
                    issues.append(f"Part {pn}: Quantity must be greater than zero (got {quantity}).")

            # Check: reasonable machine hours
            hours = raw_part.get("estimated_machine_hours")
            if hours is not None:
                if hours <= 0:
                    warnings.append(f"Part {pn}: Machine hours should be positive (got {hours}).")
                elif hours > 100:
                    warnings.append(
                        f"Part {pn}: Estimated machine hours ({hours}) seems very high. "
                        "Please verify."
                    )

        valid = len(issues) == 0
        return {
            "valid": valid,
            "issues": issues,
            "warnings": warnings,
        }
