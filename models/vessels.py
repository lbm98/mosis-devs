from dataclasses import dataclass


@dataclass
class Vessel:
    # The unique identifier for a vessel
    # Set by Generator's
    uid: int
    creation_time: float

    # The destination of the vessel
    # Set at AnchorPoint and used at Confluence's
    destination_dock: str | None

    vessel_type: str
    surface_area: int  # in square metre
    avg_velocity: float  # in knots
    max_velocity: float  # in knots


@dataclass
class CrudeOilTanker(Vessel):
    destination_dock: str | None = None
    vessel_type: str = "Crude Oil Tanker"
    surface_area: int = 11007
    avg_velocity: float = 10.7
    max_velocity: float = 15.4


@dataclass
class BulkCarrier(Vessel):
    destination_dock: str | None = None
    vessel_type: str = "Bulk Carrier"
    surface_area: int = 5399
    avg_velocity: float = 12
    max_velocity: float = 15.6


@dataclass
class TugBoat(Vessel):
    destination_dock: str | None = None
    vessel_type: str = "Tug Boat"
    surface_area: int = 348
    avg_velocity: float = 7.8
    max_velocity: float = 10.6


@dataclass
class SmallCargoFreighter(Vessel):
    destination_dock: str | None = None
    vessel_type: str = "Small Cargo Freighter"
    surface_area: int = 1265
    avg_velocity: float = 6.4
    max_velocity: float = 9.8


ALL_VESSELS = [
    CrudeOilTanker,
    BulkCarrier,
    TugBoat,
    SmallCargoFreighter
]

VESSEL_WEIGHTS = [
    0.28,
    0.22,
    0.33,
    0.17
]
