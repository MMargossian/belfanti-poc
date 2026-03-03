"""
Mock vendor database for the Belfanti CNC Manufacturing POC.
Five vendors with varied specialties, lead times, and ratings.
"""

from models.vendor import Vendor, VendorSpecialty


VENDORS: list[Vendor] = [
    Vendor(
        id="VND-001",
        name="Pacific Metal Supply",
        email="orders@pacificmetalsupply.com",
        phone="(503) 555-0142",
        specialties=[VendorSpecialty.ALUMINUM, VendorSpecialty.BRASS],
        lead_time_days=3,
        rating=4.7,
        min_order_value=75.00,
        notes="West coast distributor. Excellent stock of 6061 and 7075 plate and bar. "
              "Same-day shipping on orders placed before noon PST. "
              "Quantity discounts available on orders over $500.",
    ),
    Vendor(
        id="VND-002",
        name="Midwest Steel Corp",
        email="sales@midweststeel.com",
        phone="(312) 555-0287",
        specialties=[VendorSpecialty.STEEL, VendorSpecialty.STAINLESS],
        lead_time_days=5,
        rating=4.3,
        min_order_value=100.00,
        notes="Full-service steel distributor based in Chicago. Offers precision "
              "saw-cutting to length at no extra charge. Carries both cold-rolled "
              "and hot-rolled stock. Pre-hard 4140 usually in stock.",
    ),
    Vendor(
        id="VND-003",
        name="TitanSource Inc",
        email="quotes@titansource.com",
        phone="(860) 555-0193",
        specialties=[VendorSpecialty.TITANIUM, VendorSpecialty.STAINLESS],
        lead_time_days=7,
        rating=4.8,
        min_order_value=250.00,
        notes="Specialty supplier for aerospace and medical-grade materials. "
              "All titanium comes with full mill certs and traceability. "
              "Can source odd sizes on request — allow extra lead time for specials.",
    ),
    Vendor(
        id="VND-004",
        name="PolyParts Direct",
        email="info@polypartsdirect.com",
        phone="(949) 555-0361",
        specialties=[VendorSpecialty.PLASTICS],
        lead_time_days=4,
        rating=4.1,
        min_order_value=50.00,
        notes="Engineering plastics specialist. Stocks Delrin, Nylon, UHMW, PEEK, "
              "and Ultem in rod, bar, and sheet. PEEK orders may require 2-week lead "
              "on non-standard sizes. Free material data sheets on request.",
    ),
    Vendor(
        id="VND-005",
        name="AllMetals Warehouse",
        email="orders@allmetalswarehouse.com",
        phone="(214) 555-0518",
        specialties=[
            VendorSpecialty.ALUMINUM,
            VendorSpecialty.STEEL,
            VendorSpecialty.STAINLESS,
            VendorSpecialty.TITANIUM,
            VendorSpecialty.BRASS,
            VendorSpecialty.COPPER,
        ],
        lead_time_days=6,
        rating=3.9,
        min_order_value=50.00,
        notes="General-purpose metals warehouse with broad inventory. "
              "Competitive pricing on common alloys but limited specialty stock. "
              "Good fallback option when primary vendors are backordered. "
              "No minimum cut fees.",
    ),
]
