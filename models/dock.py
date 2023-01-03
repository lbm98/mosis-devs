from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass, field
import numpy as np

from models.vessels import Vessel
from models.messages import PortDepartureRequest
from models.utils.constants import SECONDS_PER_HOUR


@dataclass
class DockState:
    # The remaining time until generation of a new output event
    # Initially, do not generate any output events
    # Instead, we first wait for an input event
    remaining_time: float = INFINITY

    # The list that stores the vessels in this dock
    vessels: list[Vessel] = field(default_factory=list)

    # The list that stores the timers associated with the vessels in vessels
    # The association is by index
    timers: list[float] = field(default_factory=list)

    # The index into vessels for the vessel with the smallest timer
    index_for_next_vessel: int | None = None


class Dock(AtomicDEVS):
    """
    Dock is parameterized by a name

    Note that:
    1. The name must be present in the docks_capacities parameter to ControlTower
    2. There are no checks on the capacity of the docks
    This is because the ControlTower ensures proper blocking of vessels if the capacity is reached
    """
    def __init__(self, name: str, vessels: list=None):
        AtomicDEVS.__init__(self, name)

        # Note this name has a special purpose (see ControlTower and PortDepartureRequest)
        if vessels is None:
            vessels = []
        self.name = name

        # Receives Vessel's
        self.in_vessel = self.addInPort("in_vessel")

        # Sends Vessel's
        self.out_vessel = self.addOutPort("out_vessel")

        # Sends PortDepartureRequest's
        self.out_port_departure_request = self.addOutPort("out_port_departure_request")

        # Initialize the state
        self.state = DockState()

        if vessels:
            for vessel in vessels:
                assert isinstance(vessel, Vessel)
                # Get the timer
                # Convert to correct unit = seconds
                mu = 36 * SECONDS_PER_HOUR
                sigma = 12 * SECONDS_PER_HOUR
                # Sample from normal distribution
                timer = np.random.normal(mu, sigma)
                # Apply a lower bound of 6 hours
                timer = max(timer, 6 * SECONDS_PER_HOUR)

                # Enqueue the vessel and its timer
                self.state.vessels.append(vessel)
                self.state.timers.append(timer)

    def extTransition(self, inputs):
        # Apply the pattern: Ignore an Event (see MOSIS)
        self.state.timers = [timer - self.elapsed for timer in self.state.timers]

        if self.in_vessel in inputs:
            # Get the vessel
            vessel = inputs[self.in_vessel]
            assert isinstance(vessel, Vessel)

            # Get the timer
            # Convert to correct unit = seconds
            mu = 36 * SECONDS_PER_HOUR
            sigma = 12 * SECONDS_PER_HOUR
            # Sample from normal distribution
            timer = np.random.normal(mu, sigma)
            # Apply a lower bound of 6 hours
            timer = max(timer, 6 * SECONDS_PER_HOUR)

            # Enqueue the vessel and its timer
            self.state.vessels.append(vessel)
            self.state.timers.append(timer)
        else:
            assert False

        # Generate the next output event at the smallest timer
        # Necessary, since it could be that the new vessel leaves the dock first
        self.generate_at_smallest_timer()

        return self.state

    def timeAdvance(self):
        return self.state.remaining_time

    def outputFnc(self):
        # Check precondition
        assert self.state.index_for_next_vessel is not None

        # Send the vessel for which the timer expired,
        # route this vessel to the Sea (by setting destination_dock) and
        # send a PortDepartureRequest
        vessel = self.state.vessels[self.state.index_for_next_vessel]
        vessel.destination_dock = "9"
        return {
            self.out_vessel: vessel,
            self.out_port_departure_request: PortDepartureRequest(dock=self.name)
        }

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
        # Assume that the dock contains at least one vessel
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
