from models.constants import SECONDS_PER_HOUR

KMH_PER_KNOT = 1.852


class Vessel:
    def __init__(self,
                 vessel_type,
                 surface_area,
                 avg_velocity,
                 max_velocity,
                 uid):
        # The unique identifier for a vessel
        # Set by Generator
        self.uid: int = uid

        # The destination of the vessel
        # Set at AnchorPoint and used at confluences
        self.destination_dock: str | None = None

        # self.creation_time = creation_time

        self.vessel_type = vessel_type
        self.surface_area = surface_area
        self.avg_velocity = avg_velocity
        self.max_velocity = max_velocity

    def get_time_in_seconds(self, distance_in_km):
        # Should we use average velocity or max velocity?
        # We choose to use average velocity
        time_in_hours = distance_in_km / (KMH_PER_KNOT * self.avg_velocity)
        return time_in_hours * SECONDS_PER_HOUR


class CrudeOilTanker(Vessel):
    def __init__(self, uid):
        super().__init__(
            vessel_type="Crude Oil Tanker",
            surface_area=11007,
            avg_velocity=10.7,
            max_velocity=15.4,
            uid=uid
        )


class BulkCarrier(Vessel):
    def __init__(self, uid):
        super().__init__(
            vessel_type="Bulk Carrier",
            surface_area=5399,
            avg_velocity=12,
            max_velocity=15.6,
            uid=uid
        )


class TugBoat(Vessel):
    def __init__(self, uid):
        super().__init__(
            vessel_type="Tug Boat",
            surface_area=348,
            avg_velocity=7.8,
            max_velocity=10.6,
            uid=uid
        )


class SmallCargoFreighter(Vessel):
    def __init__(self, uid):
        super().__init__(
            vessel_type="Small Cargo Freighter",
            surface_area=1265,
            avg_velocity=6.4,
            max_velocity=9.8,
            uid=uid
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