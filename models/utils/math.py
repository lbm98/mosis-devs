from models.utils.constants import SECONDS_PER_HOUR, KMH_PER_KNOT


def get_time_in_seconds(distance_in_km, velocity_in_knot):
    time_in_hours = distance_in_km / (KMH_PER_KNOT * velocity_in_knot)
    return time_in_hours * SECONDS_PER_HOUR
