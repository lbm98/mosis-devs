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
    # Wait INDEFINITELY for the first input event
    remaining_time = INFINITY

    # The datastructure that stores [vessel,timer] pairs
    vessel_timer_pairs = []

    # The output port (for the vessel with the smallest timer)
    output_port_for_next_vessel: Port | None = None

    # The index into vessel_timer_pairs (for the vessel with the smallest timer)
    timer_pair_index_for_next_vessel: int | None = None


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
            # Necessary, since it could be that the new input event has the smallest timer
            self.schedule_by_smallest_timer()

        return self.state

    def timeAdvance(self):
        return self.state.remaining_time

    def outputFnc(self):
        # Check preconditions
        assert self.state.output_port_for_next_vessel is not None
        assert self.state.timer_pair_index_for_next_vessel is not None

        # Send the vessel (for which the timer expired)
        next_vessel, _ = self.state.vessel_timer_pairs[self.state.timer_pair_index_for_next_vessel]
        to_return = {self.state.output_port_for_next_vessel: next_vessel}

        return to_return

    def intTransition(self):
        # If there are no more vessels in this confluence,
        # do nothing
        if len(self.state.vessel_timer_pairs) == 0:
            return

        # Remove the (vessel,timer) pair from the queue
        self.state.vessel_timer_pairs.pop(self.state.timer_pair_index_for_next_vessel)

        # Update the timers
        for vessel_timer_pair in self.state.vessel_timer_pairs:
            vessel_timer_pair[1] -= self.state.remaining_time

        # Schedule next event to run at smallest timer
        self.schedule_by_smallest_timer()
        return self.state

    def schedule_by_smallest_timer(self):
        # If there are no more vessels in this confluence,
        # wait INDEFINITELY for the next input event
        if len(self.state.vessel_timer_pairs) == 0:
            self.state.remaining_time = INFINITY
            return

        # Lookup the smallest time
        min_index, min_pair = self.state.remaining_time = min(
            enumerate(self.state.vessel_timer_pairs),
            key=lambda pair: pair[1][1]  # pair[1] for enumerate, pair[1][1] for timer
        )
        vessel, smallest_timer = min_pair

        # Schedule by smallest timer
        self.state.remaining_time = smallest_timer

        # Store the output port (for the vessel with the smallest timer)
        port_name = next(
            record.port_name for record in self.confluence_info
            if vessel.destination_dock in record.docks
        )
        self.state.output_port_for_next_vessel = self.out_vessel_ports[port_name]

        # Store the index of the pair (for the vessel with the smallest timer)
        self.state.timer_pair_index_for_next_vessel = min_index
