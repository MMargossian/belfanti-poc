from pydantic import BaseModel
from typing import Optional
from enum import Enum


class MaterialType(str, Enum):
    ALUMINUM_6061 = "6061-T6 Aluminum"
    ALUMINUM_7075 = "7075-T6 Aluminum"
    STEEL_1018 = "1018 Steel"
    STEEL_4140 = "4140 Steel"
    STAINLESS_303 = "303 Stainless Steel"
    STAINLESS_304 = "304 Stainless Steel"
    STAINLESS_316 = "316 Stainless Steel"
    TITANIUM_GR5 = "Grade 5 Titanium (Ti-6Al-4V)"
    BRASS_360 = "360 Brass"
    DELRIN = "Delrin (Acetal)"
    NYLON = "Nylon 6/6"
    PEEK = "PEEK"


class MachineType(str, Enum):
    THREE_AXIS = "3-axis_mill"
    FIVE_AXIS = "5-axis_mill"
    LATHE = "lathe"
    EDM = "edm"
    GRINDER = "grinder"


class SurfaceFinish(str, Enum):
    AS_MACHINED = "as_machined"
    BEAD_BLAST = "bead_blast"
    ANODIZE = "anodize"
    HARD_ANODIZE = "hard_anodize"
    POWDER_COAT = "powder_coat"
    ELECTROPOLISH = "electropolish"
    PASSIVATE = "passivate"
    CHROME = "chrome_plate"
    NICKEL = "nickel_plate"


class MaterialSpec(BaseModel):
    material_type: MaterialType
    stock_size: Optional[str] = None  # e.g. "2x4x6 block"
    quantity_needed: float = 1.0
    unit: str = "each"


class PartSpec(BaseModel):
    part_number: str
    part_name: str
    description: Optional[str] = None
    material: MaterialSpec
    quantity: int = 1
    machine_type: MachineType = MachineType.THREE_AXIS
    estimated_machine_hours: Optional[float] = None
    surface_finish: SurfaceFinish = SurfaceFinish.AS_MACHINED
    tolerances: Optional[str] = None
    cad_file_name: Optional[str] = None
    drawing_file_name: Optional[str] = None
    is_existing_part: bool = False
    existing_part_id: Optional[str] = None


class RFQ(BaseModel):
    id: Optional[str] = None
    customer_name: str
    customer_email: str
    customer_company: Optional[str] = None
    subject: str
    body: str
    parts: list[PartSpec] = []
    raw_email_text: Optional[str] = None
    attachments: list[str] = []
    urgency: str = "standard"  # standard, rush, emergency
    notes: Optional[str] = None
