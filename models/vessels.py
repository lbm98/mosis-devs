from dataclasses import dataclass

from models.utils.constants import SECONDS_PER_HOUR, KMH_PER_KNOT


@dataclass
class Vessel:
    # The unique identifier for a vessel
    # Set by Generator's
    uid: int

    creation_time: float

    vessel_type: str
    surface_area: int  # in meter squared
    avg_velocity: float  # in knots
    max_velocity: float  # in knots

    # The destination of the vessel
    # Set at AnchorPoint and used at Confluence's
    destination_dock: str | None = None

    def get_time_in_seconds(self, distance_in_km):
        # Should we use average velocity or max velocity?
        # We choose to use average velocity
        time_in_hours = distance_in_km / (KMH_PER_KNOT * self.avg_velocity)
        return time_in_hours * SECONDS_PER_HOUR


class CrudeOilTanker(Vessel):
    def __init__(self, uid, creation_time):
        super().__init__(
            vessel_type="Crude Oil Tanker",
            surface_area=11007,
            avg_velocity=10.7,
            max_velocity=15.4,
            uid=uid,
            creation_time=creation_time
        )


class BulkCarrier(Vessel):
    def __init__(self, uid, creation_time):
        super().__init__(
            vessel_type="Bulk Carrier",
            surface_area=5399,
            avg_velocity=12,
            max_velocity=15.6,
            uid=uid,
            creation_time=creation_time
        )


class TugBoat(Vessel):
    def __init__(self, uid, creation_time):
        super().__init__(
            vessel_type="Tug Boat",
            surface_area=348,
            avg_velocity=7.8,
            max_velocity=10.6,
            uid=uid,
            creation_time=creation_time
        )


class SmallCargoFreighter(Vessel):
    def __init__(self, uid, creation_time):
        super().__init__(
            vessel_type="Small Cargo Freighter",
            surface_area=1265,
            avg_velocity=6.4,
            max_velocity=9.8,
            uid=uid,
            creation_time=creation_time
        )


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