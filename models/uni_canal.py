from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass, field

from models.vessels import Vessel
from models.utils.math import get_time_in_seconds


@dataclass
class UniCanalState:
    # The remaining time until generation of a new output event
    # Initially, do not generate any output events
    # Instead, we first wait for an input event
    remaining_time: float = INFINITY

    # The list that stores the vessels in this canal
    vessels: list[Vessel] = field(default_factory=list)

    # The list that stores the timers associated with the vessels in vessel_queue
    # The association is by index
    timers: list[float] = field(default_factory=list)

    # Note that there is no need for index_for_next_vessel as in UniWaterwayState
    # In this case, the next-index is always 0


class UniCanal(AtomicDEVS):
    def __init__(self, name: str, distance_in_km: float):
        AtomicDEVS.__init__(self, name)

        self.distance_in_km = distance_in_km

        # Receives Vessel's
        self.in_vessel = self.addInPort("in_vessel")

        # Sends Vessel's
        self.out_vessel = self.addOutPort("out_vessel")

        # Initialize the state
        self.state = UniCanalState()

    def extTransition(self, inputs):
        # Apply the pattern: Ignore an Event (see MOSIS)
        self.state.timers = [timer - self.elapsed for timer in self.state.timers]

        if self.in_vessel in inputs:
            # Get the vessel
            vessel = inputs[self.in_vessel]
            assert isinstance(vessel, Vessel)

            # Get the timer
            timer = self.get_timer(vessel)

            # Enqueue the vessel and its timer
            self.state.vessels.append(vessel)
            self.state.timers.append(timer)
        else:
            assert False

        # The next vessel to leave, is ALWAYS the vessel at the head of the queue
        # Use the timer of this vessel to schedule the next output event
        self.state.remaining_time = self.state.timers[0]

        return self.state

    def get_timer(self, vessel: Vessel):
        if len(self.state.vessels) == 0:
            # The vessel is alone in its direction

            # The vessel does not need to consider other vessels
            timer = get_time_in_seconds(
                distance_in_km=self.distance_in_km,
                velocity_in_knot=vessel.avg_velocity
            )
        else:
            # The vessel is NOT alone in its directions

            # Get the vessel that will be in front of this vessel
            vessel_in_front = self.state.vessels[-1]

            # Get the minimum of the two velocities
            velocity = min(vessel.avg_velocity, vessel_in_front.avg_velocity)

            # Compute the timer with this velocity
            timer = get_time_in_seconds(
                distance_in_km=self.distance_in_km,
                velocity_in_knot=velocity
            )
        return timer

    def timeAdvance(self):
        if self.state.remaining_time < 0:
            pass
        return self.state.remaining_time

    def outputFnc(self):
        # Send the vessel at the head of the queue
        return {self.out_vessel: self.state.vessels[0]}

    def intTransition(self):
        # Remove the vessel we just sent (and its timer)
        # This is ALWAYS the vessel at the head of the queue
        self.state.vessels.pop(0)
        self.state.timers.pop(0)

        # If there are no more vessels in this waterway,
        # wait INDEFINITELY for the next input event
        if len(self.state.vessels) == 0:
            self.state.remaining_time = INFINITY
        else:
            # Lower the timers
            self.state.timers = [timer - self.state.remaining_time for timer in self.state.timers]

            # The next vessel to leave, is ALWAYS the vessel at the head of the queue
            # Use the timer of this vessel to schedule the next output event
            self.state.remaining_time = self.state.timers[0]

        return self.state
