from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass, field

from models.vessels import Vessel
from models.utils.math import get_time_in_seconds


@dataclass
class VesselRecord:
    vessel: Vessel
    timer: float  # in seconds

###
### MAYBE MAKE COUPLED DEVS WITH EACH DIRECTION AN ATOMIC DEVS
###

@dataclass
class CanalState:
    # The remaining time until generation of a new event
    # Wait INDEFINITELY for the first input event
    remaining_time: float = INFINITY

    # The datastructure that queues VesselRecord's
    # for movement left to right
    vessel_records_1: list[VesselRecord] = field(default_factory=list)

    # The datastructure that queues VesselRecord's
    # for movement right to left
    vessel_records_2: list[VesselRecord] = field(default_factory=list)

    # Is either
    #   "1" (if the next vessel that leaves comes from vessel_records_1)
    # Or
    #   "2" (if the next vessel that leaves comes from vessel_records_2)
    # queue_for_next_output: str | None = None

    queue_for_next_output: list[VesselRecord] | None = None


class Canal(AtomicDEVS):
    """
    in1   +----------------+  out1
          |      CANAL     |
    out2  +----------------+  in2
    """
    def __init__(self, name, distance_in_km: float):
        super(Canal, self).__init__(name)

        self.distance_in_km = distance_in_km

        # Receives Vessel's
        self.in1 = self.addInPort("in1")
        self.in2 = self.addInPort("in2")

        # Sends Vessel's
        self.out1 = self.addOutPort("out1")
        self.out2 = self.addOutPort("out2")

        self.state = CanalState()

    def extTransition(self, inputs):
        # Apply the pattern: Ignore an Event (see MOSIS)
        for vessel_record in self.state.vessel_records_1:
            vessel_record.timer -= self.elapsed
        for vessel_record in self.state.vessel_records_2:
            vessel_record.timer -= self.elapsed

        # Enqueue the vessel record in the right queue
        if self.in1 in inputs:
            self.enqueue_vessel_record(inputs[self.in1], self.state.vessel_records_1)
        if self.in2 in inputs:
            self.enqueue_vessel_record(inputs[self.in2], self.state.vessel_records_2)

        return self.state

    def enqueue_vessel_record(self, vessel, vessel_records):
        # Get the vessel
        assert isinstance(vessel, Vessel)

        if len(vessel_records) == 0:
            # The vessel is alone in its direction

            # Compute the timer
            timer = get_time_in_seconds(
                distance_in_km=self.distance_in_km,
                velocity_in_knot=vessel.avg_velocity
            )

            # schedule the departure of this vessel as the next output event,
            # but only if the vessels in the other direction do not leave sooner
            if self.state.remaining_time > timer:
                self.state.remaining_time = timer
                # Update queue_for_next_output as well
                self.state.queue_for_next_output = vessel_records
        else:
            # The vessel is NOT alone in its directions

            # Get the vessel that will be in front of this vessel
            vessel_in_front = vessel_records[-1].vessel

            # Get the minimum of the two velocities
            velocity = min(vessel.avg_velocity, vessel_in_front.avg_velocity)

            # Compute the timer with this velocity
            timer = get_time_in_seconds(
                distance_in_km=self.distance_in_km,
                velocity_in_knot=velocity
            )

        # Construct the vessel record
        vessel_record = VesselRecord(
            vessel=vessel,
            timer=timer,
        )

        # Enqueue the vessel record
        vessel_records.append(vessel_record)

    def timeAdvance(self):
        return self.state.remaining_time

    def outputFnc(self):
        if self.state.queue_for_next_output is self.state.vessel_records_1:
            return {self.out1: self.state.vessel_records_1[0].vessel}
        elif self.state.queue_for_next_output is self.state.vessel_records_2:
            return {self.out2: self.state.vessel_records_2[0].vessel}
        else:
            assert False

    def intTransition(self):
        # Remove the vessel_record pair we just sent
        self.state.queue_for_next_output.pop(0)

        # If there are no more vessels in the canal,
        # wait INDEFINITELY for the next input event
        if len(self.state.vessel_records_1) == 0 and len(self.state.vessel_records_2) == 0:
            self.state.remaining_time = INFINITY

        else:
            # Lower the timers
            for vessel_record in self.state.vessel_records_1:
                vessel_record.timer -= self.state.remaining_time
            for vessel_record in self.state.vessel_records_2:
                vessel_record.timer -= self.state.remaining_time

            # One direction still has vessels
            if len(self.state.vessel_records_1) == 0:
                self.state.remaining_time = self.state.vessel_records_2[0].timer
                # Update queue_for_next_output as well
                self.state.queue_for_next_output = self.state.vessel_records_2

            # The other directions still has vessels
            elif len(self.state.vessel_records_2) == 0:
                self.state.remaining_time = self.state.vessel_records_1[0].timer
                # Update queue_for_next_output as well
                self.state.queue_for_next_output = self.state.vessel_records_1

            # Both directions still have vessels
            else:
                # Schedule next event to run for the queue with the smallest timer
                if self.state.vessel_records_1[0].timer < self.state.vessel_records_2[0].timer:
                    self.state.remaining_time = self.state.vessel_records_1[0].timer
                    # Update queue_for_next_output as well
                    self.state.queue_for_next_output = self.state.vessel_records_1
                else:
                    self.state.remaining_time = self.state.vessel_records_2[0].timer
                    # Update queue_for_next_output as well
                    self.state.queue_for_next_output = self.state.vessel_records_2

        return self.state
