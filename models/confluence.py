from pypdevs.DEVS import AtomicDEVS, Port
from pypdevs.infinity import INFINITY

from dataclasses import dataclass


@dataclass
class ConfluenceInfoRecord:
    distance_in_km: float
    docks: list[str]
    port_name: str


@dataclass
class ConfluenceState:
    # The remaining time until generation of a new event
    # Wait INDEFINITELY for the first input
    remaining_time = INFINITY

    # The datastructure that stores [vessel,timer] pairs
    vessel_timer_pairs = []

    # The output port for the vessel with the smallest timer
    output_port_for_next_vessel: Port | None = None


class Confluence(AtomicDEVS):
    def __init__(self, name, confluence_info):
        super(Confluence, self).__init__(name)
        self.confluence_info = confluence_info

        # Receives Vessel's
        self.in_vessel = self.addInPort("in_vessel")

        # Store all the output ports by a name (so we can look up a port by its name)
        self.out_vessel_ports = {}
        for record in self.confluence_info:
            self.out_vessel_ports[record.port_name] = self.addOutPort(record.port_name)

        self.state = ConfluenceState()

    def extTransition(self, inputs):
        if self.in_vessel in inputs:
            # Get the vessel
            vessel = inputs[self.in_vessel]

            # Get the timer
            # This is the time needed for the vessel to travel to the next "place"
            # So, we need to consider the vessel's destination
            distance_in_km = next(
                record.distance_in_km for record in self.confluence_info
                if vessel.destination_dock in record.docks
            )
            timer = vessel.get_time_in_seconds(distance_in_km)

            # Enqueue the (vessel,timer) pair
            self.state.vessel_timer_pairs.append([vessel, timer])

            # Apply the pattern: Ignore an Event (see MOSIS)
            for vessel_timer_pair in self.state.vessel_timer_pairs:
                vessel_timer_pair[1] -= self.elapsed

            # Schedule next event to run at smallest timer
            self.schedule_by_smallest_timer()

            # Store the output port for when the next event runs
            port_name = next(
                record.port_name for record in self.confluence_info
                if vessel.destination_dock in record.docks
            )
            self.state.output_port_for_next_vessel = self.out_vessel_ports[port_name]

        return self.state

    def timeAdvance(self):
        return self.state.remaining_time

    def outputFnc(self):
        assert self.state.output_port_for_next_vessel is not None

        # Send the vessel (for which the timer expired)
        next_vessel, _ = self.state.vessel_timer_pairs[0]
        to_return = {self.state.output_port_for_next_vessel: next_vessel}

        # Remove the (vessel,timer) pair from the queue
        self.state.vessel_timer_pairs.pop(0)

        self.state.output_port_for_next_vessel = None
        return to_return

    def intTransition(self):
        self.schedule_by_smallest_timer()
        return self.state

    def schedule_by_smallest_timer(self):
        # Sort by timer (the smallest timer first)
        self.state.vessel_timer_pairs = sorted(
            self.state.vessel_timer_pairs, key=lambda x: x[1]
        )

        # Given the (vessel,timer) pair with the smallest timer
        # Schedule to send vessel on its route when timer expires
        _, smallest_timer = self.state.vessel_timer_pairs[0]
        self.state.remaining_time = smallest_timer
