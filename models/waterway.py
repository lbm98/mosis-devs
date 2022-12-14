from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass, field

from models.vessels import Vessel


@dataclass
class WaterwayInfo:
    in_out_vessel_port_1: (str, str)
    in_out_vessel_port_2: (str, str)
    distance_in_km: float


@dataclass
class VesselRecord:
    vessel: Vessel
    timer: float  # in seconds
    out_vessel_port: str


@dataclass
class ConfluenceState:
    # The remaining time until generation of a new event
    # Wait INDEFINITELY for the first input event
    remaining_time: float = INFINITY

    # The datastructure that stores [vessel,timer] pairs
    vessel_records: list[VesselRecord] = field(default_factory=list)

    # The index into vessel_records (for the vessel with the smallest timer)
    index_for_next_vessel: int | None = None


class Confluence(AtomicDEVS):
    def __init__(self, name, waterway_info: WaterwayInfo):
        super(Confluence, self).__init__(name)
        self.waterway_info = waterway_info

        in1, out1 = waterway_info.in_out_vessel_port_1
        in2, out2 = waterway_info.in_out_vessel_port_1

        # Receives Vessel's
        self.in_vessel_ports = {
            in1: self.addOutPort(in1),
            in2: self.addOutPort(in2)
        }

        # Sends Vessel's
        self.out_vessel_ports = {
            out1: self.addOutPort(out1),
            out2: self.addOutPort(out2)
        }

        # Set input to output port mapping
        self.in_out_port_mappings = {
            in1: out1,
            in2: out2
        }

        self.state = ConfluenceState()

    def extTransition(self, inputs):
        for in_vessel_port in self.in_vessel_ports.values():
            if in_vessel_port in inputs:
                # Get the vessel
                vessel = inputs[in_vessel_port]

                # Get the timer
                timer = vessel.get_time_in_seconds(self.waterway_info.distance_in_km)

                # Construct the vessel record
                vessel_record = VesselRecord(
                    vessel=vessel,
                    timer=timer,
                    out_vessel_port=self.in_out_port_mappings[in_vessel_port.getPortName()]
                )

                # Enqueue the vessel record
                self.state.vessel_records.append(vessel_record)

                # Apply the pattern: Ignore an Event (see MOSIS)
                for vessel_record in self.state.vessel_records:
                    vessel_record.timer -= self.elapsed

                # Schedule next event to run at smallest timer
                # Necessary, since it could be that the new input event has the smallest timer
                self.schedule_by_smallest_timer()

        return self.state

    def timeAdvance(self):
        return self.state.remaining_time

    def outputFnc(self):
        # Check precondition
        assert self.state.index_for_next_vessel is not None

        # Send the vessel (for which the timer expired)
        next_vessel = self.state.vessel_records[self.state.index_for_next_vessel]
        return {next_vessel.out_vessel_port: next_vessel}

    def intTransition(self):
        # Remove the (vessel,timer) pair we just sent
        self.state.vessel_records.pop(self.state.index_for_next_vessel)

        # If there are no more vessels in this confluence,
        #   wait INDEFINITELY for the next input event
        if len(self.state.vessel_records) == 0:
            self.state.remaining_time = INFINITY
            return

        # Lower the timers
        for vessel_record in self.state.vessel_records:
            vessel_record.timer -= self.state.remaining_time

        # Schedule next event to run at smallest timer
        self.schedule_by_smallest_timer()
        return self.state

    def schedule_by_smallest_timer(self):
        # Assume that at least one (vessel,timer) pair is in the queue
        assert len(self.state.vessel_records) != 0

        # Lookup the smallest time
        min_index, min_pair = self.state.remaining_time = min(
            enumerate(self.state.vessel_records),
            key=lambda pair: pair[1].timer
        )
        min_vessel, min_timer = min_pair

        # Schedule by smallest timer
        self.state.remaining_time = min_timer

        # Store the index of the pair (for the vessel with the smallest timer)
        self.state.index_for_next_vessel = min_index
