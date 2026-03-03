"""
Mock Vendor Database service for the Belfanti CNC Manufacturing POC.
Provides vendor search, quote requests, and quote comparison.
Uses data from data/vendors.py and data/materials_catalog.py.
"""

import random
import uuid
from datetime import datetime, timedelta

from data.vendors import VENDORS
from data.materials_catalog import MATERIALS_CATALOG
from models.rfq import MaterialType
from models.vendor import VendorSpecialty


# ------------------------------------------------------------------
# Material type -> vendor specialty mapping
# ------------------------------------------------------------------

_MATERIAL_TO_SPECIALTY: dict[str, list[VendorSpecialty]] = {
    MaterialType.ALUMINUM_6061: [VendorSpecialty.ALUMINUM],
    MaterialType.ALUMINUM_7075: [VendorSpecialty.ALUMINUM],
    MaterialType.STEEL_1018: [VendorSpecialty.STEEL],
    MaterialType.STEEL_4140: [VendorSpecialty.STEEL],
    MaterialType.STAINLESS_303: [VendorSpecialty.STAINLESS],
    MaterialType.STAINLESS_304: [VendorSpecialty.STAINLESS],
    MaterialType.STAINLESS_316: [VendorSpecialty.STAINLESS],
    MaterialType.TITANIUM_GR5: [VendorSpecialty.TITANIUM],
    MaterialType.BRASS_360: [VendorSpecialty.BRASS],
    MaterialType.DELRIN: [VendorSpecialty.PLASTICS],
    MaterialType.NYLON: [VendorSpecialty.PLASTICS],
    MaterialType.PEEK: [VendorSpecialty.PLASTICS],
}

# Also support searching by loose keyword strings
_KEYWORD_TO_SPECIALTY: dict[str, VendorSpecialty] = {
    "aluminum": VendorSpecialty.ALUMINUM,
    "steel": VendorSpecialty.STEEL,
    "stainless": VendorSpecialty.STAINLESS,
    "titanium": VendorSpecialty.TITANIUM,
    "brass": VendorSpecialty.BRASS,
    "copper": VendorSpecialty.COPPER,
    "plastic": VendorSpecialty.PLASTICS,
    "plastics": VendorSpecialty.PLASTICS,
    "delrin": VendorSpecialty.PLASTICS,
    "acetal": VendorSpecialty.PLASTICS,
    "nylon": VendorSpecialty.PLASTICS,
    "peek": VendorSpecialty.PLASTICS,
}


class MockVendorDBService:
    """Simulates a vendor database with search, quoting, and comparison."""

    # Cache of requested quotes so results stay consistent within a session
    _quote_cache: dict[str, dict] = {}

    @classmethod
    def search_vendors(cls, material_type: str) -> list[dict]:
        """Search for vendors that supply a given material type.

        Accepts either a MaterialType enum value (e.g. "6061-T6 Aluminum")
        or a keyword string (e.g. "aluminum", "steel", "plastics").

        Args:
            material_type: Material type enum value or keyword string.

        Returns:
            List of vendor dicts with id, name, email, specialties,
            lead_time_days, and rating.
        """
        # Resolve the required specialties
        required_specialties: set[VendorSpecialty] = set()

        # Check exact MaterialType match first
        for mt, specialties in _MATERIAL_TO_SPECIALTY.items():
            if material_type == mt or material_type == mt.value:
                required_specialties.update(specialties)
                break

        # Fallback to keyword matching
        if not required_specialties:
            search_lower = material_type.lower()
            for keyword, specialty in _KEYWORD_TO_SPECIALTY.items():
                if keyword in search_lower:
                    required_specialties.add(specialty)

        # If nothing matched, return all vendors as a fallback
        if not required_specialties:
            matching_vendors = VENDORS
        else:
            matching_vendors = [
                v for v in VENDORS
                if required_specialties.intersection(set(v.specialties))
            ]

        results = []
        for v in matching_vendors:
            results.append({
                "id": v.id,
                "name": v.name,
                "email": v.email,
                "specialties": [s.value for s in v.specialties],
                "lead_time_days": v.lead_time_days,
                "rating": v.rating,
            })

        print(f"[MockVendorDB] Search for '{material_type}' -> {len(results)} vendor(s) found")
        return results

    @classmethod
    def request_quote(
        cls,
        vendor_id: str,
        material_description: str,
        quantity: float,
        unit: str = "each",
    ) -> dict:
        """Request a price quote from a vendor for a material.

        Generates a realistic price based on the materials catalog with
        vendor-specific markup and lead time variation. Results are
        deterministic per vendor+material combination within a session.

        Args:
            vendor_id: Vendor identifier (e.g. "VND-001").
            material_description: Description of the material needed.
            quantity: Number of units required.
            unit: Unit of measure (default "each").

        Returns:
            VendorQuote-compatible dict with pricing and lead time.
        """
        # Check cache for consistency
        cache_key = f"{vendor_id}:{material_description}:{quantity}:{unit}"
        if cache_key in cls._quote_cache:
            return cls._quote_cache[cache_key]

        # Look up the vendor
        vendor = None
        for v in VENDORS:
            if v.id == vendor_id:
                vendor = v
                break

        if vendor is None:
            return {
                "error": f"Vendor '{vendor_id}' not found",
                "status": "failed",
            }

        # Find base price from materials catalog
        base_price_per_kg = _find_base_price(material_description)

        # Seed random for consistent results within a session
        seed_string = f"{vendor_id}-{material_description}"
        rng = random.Random(hash(seed_string))

        # Vendor-specific markup: 5-25%
        markup_factor = 1.0 + rng.uniform(0.05, 0.25)
        unit_price = round(base_price_per_kg * markup_factor, 2)

        # Lead time variation: vendor base +/- 2 days (minimum 1)
        lead_time = max(1, vendor.lead_time_days + rng.randint(-2, 2))

        total_price = round(unit_price * quantity, 2)
        quote_id = f"vq-{uuid.uuid4().hex[:8]}"
        valid_until = datetime.now() + timedelta(days=30)

        quote = {
            "id": quote_id,
            "vendor_id": vendor.id,
            "vendor_name": vendor.name,
            "material_description": material_description,
            "quantity": quantity,
            "unit": unit,
            "unit_price": unit_price,
            "total_price": total_price,
            "lead_time_days": lead_time,
            "valid_until": valid_until.isoformat(),
            "notes": f"Quote from {vendor.name} for {quantity} {unit} of {material_description}",
        }

        cls._quote_cache[cache_key] = quote

        print(
            f"[MockVendorDB] Quote from {vendor.name}: "
            f"${unit_price:.2f}/unit x {quantity} = ${total_price:.2f} "
            f"({lead_time} days)"
        )
        return quote

    @classmethod
    def compare_quotes(cls, quotes: list[dict]) -> dict:
        """Compare vendor quotes and recommend the best option.

        Uses a weighted scoring model:
            60% price (lower is better)
            30% lead time (shorter is better)
            10% vendor rating (higher is better)

        Args:
            quotes: List of vendor quote dicts (from request_quote).

        Returns:
            Dict with cheapest, fastest, recommended, and comparison_table.
        """
        if not quotes:
            return {
                "cheapest": None,
                "fastest": None,
                "recommended": None,
                "comparison_table": [],
            }

        # Find cheapest and fastest
        cheapest = min(quotes, key=lambda q: q.get("total_price", float("inf")))
        fastest = min(quotes, key=lambda q: q.get("lead_time_days", float("inf")))

        # Build comparison table with scores
        max_price = max(q.get("total_price", 1) for q in quotes) or 1
        max_lead = max(q.get("lead_time_days", 1) for q in quotes) or 1

        comparison_table = []
        for q in quotes:
            # Normalize: lower price and lead time are better (score 0-1)
            price_score = 1.0 - (q.get("total_price", 0) / max_price)
            lead_score = 1.0 - (q.get("lead_time_days", 0) / max_lead)

            # Rating: look up from vendor data (0-1 scale)
            vendor_rating = _get_vendor_rating(q.get("vendor_id", ""))
            rating_score = vendor_rating / 5.0

            # Weighted composite
            composite = (0.60 * price_score) + (0.30 * lead_score) + (0.10 * rating_score)

            comparison_table.append({
                "vendor_id": q.get("vendor_id"),
                "vendor_name": q.get("vendor_name"),
                "unit_price": q.get("unit_price"),
                "total_price": q.get("total_price"),
                "lead_time_days": q.get("lead_time_days"),
                "rating": vendor_rating,
                "price_score": round(price_score, 3),
                "lead_score": round(lead_score, 3),
                "rating_score": round(rating_score, 3),
                "composite_score": round(composite, 3),
            })

        # Sort by composite score descending (highest = best)
        comparison_table.sort(key=lambda r: r["composite_score"], reverse=True)
        recommended = comparison_table[0] if comparison_table else None

        # Find the full quote dict that matches the recommended vendor
        recommended_quote = None
        if recommended:
            for q in quotes:
                if q.get("vendor_id") == recommended["vendor_id"]:
                    recommended_quote = q
                    break

        print(
            f"[MockVendorDB] Quote comparison: "
            f"cheapest={cheapest.get('vendor_name')}, "
            f"fastest={fastest.get('vendor_name')}, "
            f"recommended={recommended['vendor_name'] if recommended else 'N/A'}"
        )

        return {
            "cheapest": cheapest,
            "fastest": fastest,
            "recommended": recommended_quote or recommended,
            "comparison_table": comparison_table,
        }

    @classmethod
    def reset(cls) -> None:
        """Clear the quote cache. Useful for testing."""
        cls._quote_cache.clear()


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------

def _find_base_price(material_description: str) -> float:
    """Look up the base price_per_kg from the materials catalog.

    Falls back to a reasonable default if no exact match is found.
    """
    desc_lower = material_description.lower()

    # Try exact enum match first
    for material_type, catalog_entry in MATERIALS_CATALOG.items():
        if (
            material_description == material_type
            or material_description == material_type.value
            or material_description == catalog_entry["name"]
        ):
            return catalog_entry["price_per_kg"]

    # Fuzzy keyword match
    for material_type, catalog_entry in MATERIALS_CATALOG.items():
        name_lower = catalog_entry["name"].lower()
        # Check if key terms from the catalog name appear in the description
        if any(word in desc_lower for word in name_lower.split() if len(word) > 3):
            return catalog_entry["price_per_kg"]

    # Default fallback price
    return 15.00


def _get_vendor_rating(vendor_id: str) -> float:
    """Look up a vendor's rating from the vendor list."""
    for v in VENDORS:
        if v.id == vendor_id:
            return v.rating
    return 3.0  # Default if vendor not found
