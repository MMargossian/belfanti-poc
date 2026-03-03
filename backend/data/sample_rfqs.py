"""
Pre-built sample RFQ dictionaries for the Belfanti POC demo.
These are raw email representations (not parsed model instances) that can be
fed into the RFQ parsing pipeline to demonstrate the system end-to-end.
"""

SAMPLE_RFQS: list[dict] = [
    # -----------------------------------------------------------------------
    # Sample 1 — Simple: single aluminum bracket, 3-axis, qty 50
    # -----------------------------------------------------------------------
    {
        "customer_name": "Tom Harrelson",
        "customer_email": "t.harrelson@condoraerosystems.com",
        "customer_company": "Condor Aero Systems",
        "subject": "RFQ - Aluminum mounting bracket, qty 50",
        "body": (
            "Hi,\n\n"
            "We need a quote on a mounting bracket for one of our avionics enclosures. "
            "The part is pretty straightforward — it's a right-angle bracket machined "
            "from 6061-T6 aluminum, roughly 3.5 x 2.0 x 1.25 inches with four "
            "through-holes and a counterbored slot. General tolerances are +/-0.005 "
            "except the mounting holes which are +/-0.002. We need 50 pieces.\n\n"
            "Surface finish should be bead blast followed by clear anodize (Type II). "
            "Standard 3-axis mill work — nothing exotic. I've attached the STEP file "
            "and a PDF drawing with all the callouts.\n\n"
            "Lead time isn't critical but ideally within 3-4 weeks. Let me know "
            "pricing and delivery.\n\n"
            "Thanks,\n"
            "Tom Harrelson\n"
            "Purchasing — Condor Aero Systems\n"
            "(480) 555-0173"
        ),
        "attachments": [
            "BRK-4401_Rev_C.step",
            "BRK-4401_Rev_C_Drawing.pdf",
        ],
    },
    # -----------------------------------------------------------------------
    # Sample 2 — Medium: steel shaft + aluminum housing, lathe + 3-axis, qty 25
    # -----------------------------------------------------------------------
    {
        "customer_name": "Dana Kowalski",
        "customer_email": "dana.kowalski@ridgelineautomation.com",
        "customer_company": "Ridgeline Automation LLC",
        "subject": "Quote request — drive shaft and motor housing (25 sets)",
        "body": (
            "Hello,\n\n"
            "We're sourcing two mating parts for a custom linear actuator and need "
            "pricing on 25 sets.\n\n"
            "Part 1: Drive shaft, P/N RSA-2200-A. Turned from 1.5-inch 4140 pre-hard "
            "round bar. Finished OD is 1.000 +/-0.0005 over a 6-inch length with "
            "a keyway slot (3/16 x 3/32) and an M8 threaded end. We'll need the OD "
            "ground after turning to hit the tolerance — so lathe work first, then "
            "a grinding pass. Surface finish 32 Ra or better on the bearing journal, "
            "rest can be as-machined.\n\n"
            "Part 2: Motor housing, P/N RSA-2200-B. Machined from a 4 x 4 x 3 inch "
            "block of 6061-T6 aluminum. Has a central bore (1.001 +0.001/-0.000 "
            "press-fit for the shaft bearing), four bolt-circle holes on a 2.750 BC, "
            "and a cable relief pocket on one side. 3-axis mill work. Clear anodize "
            "the finished part.\n\n"
            "I've attached STEP models and drawings for both parts. We need these "
            "in about 4 weeks. Please quote material, machining, and finishing "
            "separately if possible.\n\n"
            "Best,\n"
            "Dana Kowalski\n"
            "Engineering Manager — Ridgeline Automation\n"
            "dana.kowalski@ridgelineautomation.com\n"
            "(616) 555-0294"
        ),
        "attachments": [
            "RSA-2200-A_DriveShaft.step",
            "RSA-2200-A_DriveShaft_Drawing.pdf",
            "RSA-2200-B_MotorHousing.step",
            "RSA-2200-B_MotorHousing_Drawing.pdf",
        ],
    },
    # -----------------------------------------------------------------------
    # Sample 3 — Complex: titanium implant + stainless fixture + PEEK insulator,
    #             5-axis + 3-axis + lathe, mixed quantities, rush order
    # -----------------------------------------------------------------------
    {
        "customer_name": "Dr. Rachel Mendez",
        "customer_email": "rmendez@apexmeddevices.com",
        "customer_company": "Apex Medical Devices",
        "subject": "URGENT — Multi-part RFQ for surgical instrument prototype",
        "body": (
            "Team,\n\n"
            "We have a tight timeline on a new surgical instrument prototype and need "
            "pricing ASAP — ideally by end of day tomorrow. We're targeting first "
            "articles in two weeks.\n\n"
            "There are three components:\n\n"
            "1) Articulating jaw tip, P/N AMD-7750-JAW. This is the critical part. "
            "Material is Ti-6Al-4V (Grade 5 titanium), machined from a 1 x 1 x 2 "
            "inch block. It has compound contoured surfaces on the gripping face and "
            "a pivot bore at 0.1875 +/-0.0002 — this will need 5-axis work. Surface "
            "finish must be electropolished per ASTM B912. Quantity: 10 pieces. We'll "
            "need full material certs and traceability since this is for a Class II "
            "medical device.\n\n"
            "2) Alignment fixture plate, P/N AMD-7750-FIX. 316 stainless steel, "
            "machined from 3 x 5 x 0.75 plate. Straightforward 3-axis mill work — "
            "array of precision dowel holes (12 holes at 0.2500 +/-0.0003) and "
            "perimeter bolt pattern. Passivate per ASTM A967. Quantity: 5 pieces.\n\n"
            "3) Insulator bushing, P/N AMD-7750-INS. PEEK rod, turned on a lathe. "
            "OD 0.500, ID 0.190, length 0.375. Tolerances are +/-0.001 on all "
            "dimensions. No finish required — as-machined is fine for PEEK. "
            "Quantity: 40 pieces.\n\n"
            "This is a rush job so please factor that into pricing. We can pay "
            "expedite fees if needed. All parts need to ship together.\n\n"
            "Please send a detailed quote broken out by part, and confirm you can "
            "meet the 2-week delivery. Call me directly if you have questions.\n\n"
            "Thank you,\n"
            "Dr. Rachel Mendez\n"
            "VP of Product Development — Apex Medical Devices\n"
            "rmendez@apexmeddevices.com\n"
            "(617) 555-0831"
        ),
        "attachments": [
            "AMD-7750-JAW_ArticulatingJaw.step",
            "AMD-7750-JAW_Drawing.pdf",
            "AMD-7750-FIX_AlignmentFixture.step",
            "AMD-7750-FIX_Drawing.pdf",
            "AMD-7750-INS_InsulatorBushing.step",
            "AMD-7750-INS_Drawing.pdf",
        ],
    },
]
