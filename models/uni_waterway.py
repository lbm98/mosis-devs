from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass, field

from models.vessels import Vessel
from models.utils.math import get_time_in_seconds


@dataclass
class UniWaterwayState:
    # The remaining time until generation of a new output event
    # Initially, do not generate any output events
    # Instead, we first wait for an input event
    remaining_time: float = INFINITY

    # The list that stores the vessels in this waterway
    vessels: list[Vessel] = field(default_factory=list)

    # The list that stores the timers associated with the vessels in vessel_queue
    # The association is by index
    timers: list[float] = field(default_factory=list)

    # The index into vessels for the vessel with the smallest timer
    index_for_next_vessel: int | None = None


class UniWaterway(AtomicDEVS):
    def __init__(self, name: str, distance_in_km: float):
        AtomicDEVS.__init__(self, name)

        self.distance_in_km = distance_in_km

        # Receives Vessel's
        self.in_vessel = self.addInPort("in_vessel")

        # Sends Vessel's
        self.out_vessel = self.addOutPort("out_vessel")

        # Initialize the state
        self.state = UniWaterwayState()

    def extTransition(self, inputs):
        # Apply the pattern: Ignore an Event (see MOSIS)
        self.state.timers = [timer - self.elapsed for timer in self.state.timers]

        if self.in_vessel in inputs:
            # Get the vessel
            vessel = inputs[self.in_vessel]
            assert isinstance(vessel, Vessel)

            # Get the timer
            timer = get_time_in_seconds(
                distance_in_km=self.distance_in_km,
                velocity_in_knot=vessel.avg_velocity
            )

            # Enqueue the vessel and its timer
            self.state.vessels.append(vessel)
            self.state.timers.append(timer)

        # Generate the next output event at the smallest timer
        # Necessary, since it could be that the new vessel leaves the waterway first
        self.generate_at_smallest_timer()

        return self.state

    def timeAdvance(self):
        return self.state.remaining_time

    def outputFnc(self):
        # Check precondition
        assert self.state.index_for_next_vessel is not None

        # Send the vessel for which the timer expired
        return {self.out_vessel: self.state.vessels[self.state.index_for_next_vessel]}

    def intTransition(self):
        # Remove the vessel we just sent (and its timer)
        self.state.vessels.pop(self.state.index_for_next_vessel)
        self.state.timers.pop(self.state.index_for_next_vessel)

        # If there are no more vessels in this waterway,
        # wait INDEFINITELY for the next input event
        if len(self.state.vessels) == 0:
            self.state.remaining_time = INFINITY
        else:
            # Lower the timers
            self.state.timers = [timer - self.state.remaining_time for timer in self.state.timers]

            # Generate the next output event at the smallest timer
            self.generate_at_smallest_timer()

        return self.state

    def generate_at_smallest_timer(self):
        # Assume that the waterway contains at least one vessel
        assert len(self.state.vessels) != 0

        # Lookup the smallest timer
        min_index, min_timer = min(
            enumerate(self.state.timers),
            key=lambda p: p[1]
        )

        # Generate the next output event at the smallest timer
        self.state.remaining_time = min_timer

        # Store the index of the vessel with the smallest timer
        self.state.index_for_next_vessel = min_index
