"""
Machine shop rates, setup costs, and finishing costs for CNC operations.
Used by the cost estimation engine to calculate part pricing.
"""

from models.rfq import MachineType, SurfaceFinish


# Hourly machine rates (includes operator, overhead, tooling amortization)
MACHINE_HOURLY_RATES: dict[MachineType, float] = {
    MachineType.THREE_AXIS: 85.00,
    MachineType.FIVE_AXIS: 150.00,
    MachineType.LATHE: 75.00,
    MachineType.EDM: 125.00,
    MachineType.GRINDER: 65.00,
}

# One-time setup cost per job (fixturing, work-holding, program load, first-article)
SETUP_COSTS: dict[MachineType, float] = {
    MachineType.THREE_AXIS: 175.00,
    MachineType.FIVE_AXIS: 400.00,
    MachineType.LATHE: 150.00,
    MachineType.EDM: 350.00,
    MachineType.GRINDER: 200.00,
}

# Flat finishing cost per part (applied after machining)
FINISHING_RATES: dict[SurfaceFinish, float] = {
    SurfaceFinish.AS_MACHINED: 0.00,
    SurfaceFinish.BEAD_BLAST: 8.00,
    SurfaceFinish.ANODIZE: 15.00,
    SurfaceFinish.HARD_ANODIZE: 25.00,
    SurfaceFinish.POWDER_COAT: 18.00,
    SurfaceFinish.ELECTROPOLISH: 30.00,
    SurfaceFinish.PASSIVATE: 12.00,
    SurfaceFinish.CHROME: 45.00,
    SurfaceFinish.NICKEL: 40.00,
}
