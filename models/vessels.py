from dataclasses import dataclass, field


@dataclass
class Vessel:
    # The unique identifier for a vessel
    # Set by Generator's
    uid: int

    creation_time: float
    time_in_system: float | None

    # time_of_arrival = time_in_system + creation_time

    # The destination of the vessel
    # Set at AnchorPoint and used at Confluence's
    destination_dock: str | None

    vessel_type: str
    surface_area: int  # in square metre
    avg_velocity: float  # in knots
    max_velocity: float  # in knots
    waiting_time_in_anchor_point: float | None


@dataclass
class CrudeOilTanker(Vessel):
    time_in_system: float | None = None
    destination_dock: str | None = None
    vessel_type: str = "Crude Oil Tanker"
    surface_area: int = 11007
    avg_velocity: float = 10.7
    max_velocity: float = 15.4
    waiting_time_in_anchor_point: float | None = None


@dataclass
class BulkCarrier(Vessel):
    time_in_system: float | None = None
    destination_dock: str | None = None
    vessel_type: str = "Bulk Carrier"
    surface_area: int = 5399
    avg_velocity: float = 12
    max_velocity: float = 15.6
    waiting_time_in_anchor_point: float | None = None


@dataclass
class TugBoat(Vessel):
    time_in_system: float | None = None
    destination_dock: str | None = None
    vessel_type: str = "Tug Boat"
    surface_area: int = 348
    avg_velocity: float = 7.8
    max_velocity: float = 10.6
    waiting_time_in_anchor_point: float | None = None


@dataclass
class SmallCargoFreighter(Vessel):
    time_in_system: float | None = None
    destination_dock: str | None = None
    vessel_type: str = "Small Cargo Freighter"
    surface_area: int = 1265
    avg_velocity: float = 6.4
    max_velocity: float = 9.8
    waiting_time_in_anchor_point: float | None = None


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
