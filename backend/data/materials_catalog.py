"""
Materials catalog with realistic CNC material properties and pricing.
Key = MaterialType enum value. Used for cost estimation and vendor matching.
"""

from models.rfq import MaterialType


MATERIALS_CATALOG: dict[str, dict] = {
    MaterialType.ALUMINUM_6061: {
        "name": "6061-T6 Aluminum",
        "density": 2.70,  # g/cm3
        "price_per_kg": 8.50,
        "machinability_rating": 9,
        "typical_stock_sizes": [
            "1x2x6 block",
            "2x4x6 block",
            "2x6x12 block",
            "3x3x12 block",
            "1.0 dia x 12 round bar",
            "2.0 dia x 12 round bar",
            "0.5x4x48 flat bar",
        ],
        "notes": "General-purpose alloy. Excellent machinability, good weldability. "
                 "Most common choice for prototypes and fixtures.",
    },
    MaterialType.ALUMINUM_7075: {
        "name": "7075-T6 Aluminum",
        "density": 2.81,
        "price_per_kg": 14.00,
        "machinability_rating": 8,
        "typical_stock_sizes": [
            "1x2x6 block",
            "2x4x6 block",
            "2x6x12 block",
            "1.5 dia x 12 round bar",
            "2.0 dia x 12 round bar",
        ],
        "notes": "High-strength aerospace alloy. Harder than 6061, chips well but "
                 "more tool wear. Not recommended for welding.",
    },
    MaterialType.STEEL_1018: {
        "name": "1018 Cold-Rolled Steel",
        "density": 7.87,
        "price_per_kg": 3.25,
        "machinability_rating": 7,
        "typical_stock_sizes": [
            "1x2x12 block",
            "2x4x12 block",
            "1.0 dia x 12 round bar",
            "2.0 dia x 12 round bar",
            "3.0 dia x 12 round bar",
            "0.5x4x48 flat bar",
        ],
        "notes": "Low-carbon general-purpose steel. Easy to machine and weld. "
                 "Case-hardenable. Good for shafts, pins, and structural parts.",
    },
    MaterialType.STEEL_4140: {
        "name": "4140 Alloy Steel (Pre-Hard)",
        "density": 7.85,
        "price_per_kg": 5.50,
        "machinability_rating": 5,
        "typical_stock_sizes": [
            "1x2x12 block",
            "2x4x12 block",
            "2x6x12 block",
            "1.0 dia x 12 round bar",
            "2.5 dia x 12 round bar",
        ],
        "notes": "Chrome-moly alloy, often supplied pre-hardened to 28-32 HRC. "
                 "Good strength and fatigue resistance. Use carbide tooling.",
    },
    MaterialType.STAINLESS_303: {
        "name": "303 Stainless Steel",
        "density": 8.03,
        "price_per_kg": 10.50,
        "machinability_rating": 7,
        "typical_stock_sizes": [
            "1x2x12 block",
            "2x4x12 block",
            "0.75 dia x 12 round bar",
            "1.5 dia x 12 round bar",
            "2.0 dia x 12 round bar",
        ],
        "notes": "Free-machining stainless with added sulfur. Best stainless for "
                 "screw machine work. Not suitable for welding or marine use.",
    },
    MaterialType.STAINLESS_304: {
        "name": "304 Stainless Steel",
        "density": 8.00,
        "price_per_kg": 12.00,
        "machinability_rating": 4,
        "typical_stock_sizes": [
            "1x2x12 block",
            "2x4x12 block",
            "2x6x12 block",
            "1.0 dia x 12 round bar",
            "2.0 dia x 12 round bar",
        ],
        "notes": "Most common austenitic stainless. Work-hardens quickly, use sharp "
                 "tools and positive rake. Weldable and corrosion-resistant.",
    },
    MaterialType.STAINLESS_316: {
        "name": "316 Stainless Steel",
        "density": 8.00,
        "price_per_kg": 15.00,
        "machinability_rating": 3,
        "typical_stock_sizes": [
            "1x2x12 block",
            "2x4x6 block",
            "2x6x12 block",
            "1.0 dia x 12 round bar",
            "2.0 dia x 12 round bar",
        ],
        "notes": "Marine-grade stainless with molybdenum for superior corrosion "
                 "resistance. Gummy to machine — reduce speed, increase feed. "
                 "Common in medical and food-processing applications.",
    },
    MaterialType.TITANIUM_GR5: {
        "name": "Grade 5 Titanium (Ti-6Al-4V)",
        "density": 4.43,
        "price_per_kg": 75.00,
        "machinability_rating": 2,
        "typical_stock_sizes": [
            "1x2x6 block",
            "2x4x6 block",
            "1.0 dia x 6 round bar",
            "1.5 dia x 6 round bar",
            "2.0 dia x 6 round bar",
        ],
        "notes": "Aerospace and medical-grade titanium. Very low thermal conductivity "
                 "— use high-pressure coolant, low surface speed, aggressive chip load. "
                 "Expensive tooling wear. Plan for 3-4x cycle time vs aluminum.",
    },
    MaterialType.BRASS_360: {
        "name": "360 Free-Cutting Brass",
        "density": 8.50,
        "price_per_kg": 17.50,
        "machinability_rating": 10,
        "typical_stock_sizes": [
            "1x2x12 block",
            "2x4x12 block",
            "0.5 dia x 12 round bar",
            "1.0 dia x 12 round bar",
            "2.0 dia x 12 round bar",
        ],
        "notes": "Best machinability of any common metal. Produces small chips, "
                 "excellent surface finish off the tool. Ideal for fittings, "
                 "connectors, and decorative parts.",
    },
    MaterialType.DELRIN: {
        "name": "Delrin (Acetal Homopolymer)",
        "density": 1.41,
        "price_per_kg": 25.00,
        "machinability_rating": 9,
        "typical_stock_sizes": [
            "1x2x12 block",
            "2x4x12 block",
            "1.0 dia x 12 round bar",
            "2.0 dia x 12 round bar",
            "3.0 dia x 12 round bar",
            "0.5x6x48 sheet",
        ],
        "notes": "Stiff engineering plastic with low friction. Machines like butter — "
                 "use sharp uncoated tools, high spindle speed. Prone to melting if "
                 "tool is dull. Good dimensional stability.",
    },
    MaterialType.NYLON: {
        "name": "Nylon 6/6",
        "density": 1.14,
        "price_per_kg": 22.00,
        "machinability_rating": 8,
        "typical_stock_sizes": [
            "1x2x12 block",
            "2x4x12 block",
            "1.0 dia x 12 round bar",
            "2.0 dia x 12 round bar",
            "3.0 dia x 12 round bar",
            "0.5x6x48 sheet",
        ],
        "notes": "Tough and wear-resistant engineering plastic. Absorbs moisture — "
                 "hold tolerances to +/-0.005 at best. Use air blast for chip clearing. "
                 "Good for gears, bushings, and wear pads.",
    },
    MaterialType.PEEK: {
        "name": "PEEK (Polyether Ether Ketone)",
        "density": 1.31,
        "price_per_kg": 175.00,
        "machinability_rating": 6,
        "typical_stock_sizes": [
            "1x2x6 block",
            "2x4x6 block",
            "1.0 dia x 6 round bar",
            "1.5 dia x 6 round bar",
            "0.5x4x12 sheet",
        ],
        "notes": "High-performance polymer for extreme environments. Expensive — "
                 "minimize material waste. Can replace metals in weight-critical "
                 "applications. Autoclavable for medical use. Stock sizes limited.",
    },
}
