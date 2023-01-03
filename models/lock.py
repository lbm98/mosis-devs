from pypdevs.DEVS import AtomicDEVS

from models.vessels import Vessel

from dataclasses import dataclass, field
from enum import Enum


class IntervalState(Enum):
    GATE_CLOSING = 1,
    WASHING = 2,
    GATE_OPENING = 3,
    GATE_IS_OPEN = 4,


class WaterLevel(Enum):
    LOW = 0,
    HIGH = 1


@dataclass
class LockState:
    current_surface_area: int

    current_water_level: WaterLevel = WaterLevel.HIGH

    interval_state: IntervalState = IntervalState.GATE_IS_OPEN

    # Start the state machine immediately
    remaining_time: float = 0

    vessels_in_lock: list[Vessel] = field(default_factory=list)

    vessels_waiting_low: list[Vessel] = field(default_factory=list)

    vessels_waiting_high: list[Vessel] = field(default_factory=list)

    sum_remaining_surface_area: float = 0.0
    number_of_washings: int = 0
    number_lock_state_changes_with_no_vessels: int = 0
    idle_time: int = 0


class Lock(AtomicDEVS):
    def __init__(self, name: str, washing_duration: int, lock_shift_interval: int, gate_duration: int,
                 surface_area: int,
                 time_between_departures: int = 30):
        AtomicDEVS.__init__(self, name)

        # Lock attributes
        self.name = name
        self.washing_duration = washing_duration
        self.lock_shift_interval = lock_shift_interval
        self.gate_duration = gate_duration
        self.surface_area = surface_area
        self.time_between_departures = time_between_departures

        # Receive vessels on low and high level
        self.in_low = self.addInPort('in_vessel_low')
        self.in_high = self.addInPort('in_vessel_high')

        # Send vessels on low and high level
        self.out_low = self.addOutPort('out_vessel_low')
        self.out_high = self.addOutPort('out_vessel_high')

        # Initialize state
        self.state = LockState(current_surface_area=self.surface_area)

    def extTransition(self, inputs):
        # Pattern: Ignore an Event
        self.state.remaining_time -= self.elapsed

        if self.in_high in inputs:
            vessel = inputs[self.in_high]
            assert isinstance(vessel, Vessel)

            # If the gate is open, it can be that some vessels are in the process of leaving the lock
            # Just always push the incoming vessels in the vessels_waiting queue and transfer them at the end
            self.state.vessels_waiting_high.append(vessel)
        elif self.in_low in inputs:
            vessel = inputs[self.in_low]
            assert isinstance(vessel, Vessel)

            # If the gate is open, it can be that some vessels are in the process of leaving the lock
            # Just always push the incoming vessels in the vessels_waiting queue and transfer them at the end
            self.state.vessels_waiting_low.append(vessel)

        else:
            assert False

        return self.state

    def normal_transition_time(self):
        if self.state.interval_state == IntervalState.GATE_CLOSING:
            return self.gate_duration
        elif self.state.interval_state == IntervalState.WASHING:
            return self.washing_duration
        elif self.state.interval_state == IntervalState.GATE_OPENING:
            return self.gate_duration
        elif self.state.interval_state == IntervalState.GATE_IS_OPEN:
            return self.lock_shift_interval - (2 * self.gate_duration + self.washing_duration)
        else:
            assert False

    def timeAdvance(self):
        return self.state.remaining_time

    def intTransition(self):
        # ASSUMPTION: we do not care about the number of time_between_departures before
        self.state.remaining_time = self.normal_transition_time()

        if self.state.interval_state == IntervalState.GATE_CLOSING:
            # Transfer all the waiting vessels
            if self.state.current_water_level == WaterLevel.HIGH:
                self.state.vessels_waiting_high = self.transfer_vessels_waiting_to_lock(self.state.vessels_waiting_high)
            else:
                self.state.vessels_waiting_low = self.transfer_vessels_waiting_to_lock(self.state.vessels_waiting_low)
            self.state.interval_state = IntervalState.WASHING

        elif self.state.interval_state == IntervalState.WASHING:
            self.swap_water_levels()
            self.state.sum_remaining_surface_area += self.surface_area - self.state.current_surface_area
            self.state.number_of_washings += 1
            if len(self.state.vessels_in_lock) == 0:
                self.state.number_lock_state_changes_with_no_vessels += 1
                self.state.idle_time += self.lock_shift_interval
            self.state.interval_state = IntervalState.GATE_OPENING


        elif self.state.interval_state == IntervalState.GATE_OPENING:
            self.state.interval_state = IntervalState.GATE_IS_OPEN

        elif self.state.interval_state == IntervalState.GATE_IS_OPEN:
            # Can be used for both HIGH and LOW
            self.handle_gate_is_open()

        else:
            assert False

        return self.state

    def handle_gate_is_open(self):
        if len(self.state.vessels_in_lock) == 0:
            # Base case
            # Transition to the next state
            self.state.interval_state = IntervalState.GATE_CLOSING

        else:
            # We have outputted a vessel in outputFnc, so remove it here
            self.state.vessels_in_lock.pop(0)

            if len(self.state.vessels_in_lock) == 0:
                # No more vessels in the lock
                # Transition to the next state
                self.state.interval_state = IntervalState.GATE_CLOSING

            else:
                # Still vessels in the lock, schedule the next removal
                self.state.remaining_time = self.time_between_departures
                # Stay in the same state
                self.state.interval_state = IntervalState.GATE_IS_OPEN

    def outputFnc(self):
        if self.state.interval_state == IntervalState.GATE_IS_OPEN:
            if len(self.state.vessels_in_lock) != 0:
                vessel = self.state.vessels_in_lock[0]
                if self.state.current_water_level == WaterLevel.HIGH:
                    return {self.out_high: vessel}
                else:
                    return {self.out_low: vessel}
        return {}

    def transfer_vessels_waiting_to_lock(self, vessels_waiting):
        assert len(self.state.vessels_in_lock) == 0

        still_vessels_waiting = []
        for idx, vessel in enumerate(vessels_waiting):
            if self.can_fit_capacity(vessel):
                self.state.vessels_in_lock.append(vessel)
                # Update the current surface area
                self.state.current_surface_area -= vessel.surface_area
            else:
                still_vessels_waiting.append(vessel)

        # Reset the surface area
        self.state.current_surface_area = self.surface_area
        return still_vessels_waiting

    def can_fit_capacity(self, vessel):
        return self.state.current_surface_area - vessel.surface_area >= 0

    def swap_water_levels(self):
        if self.state.current_water_level == WaterLevel.HIGH:
            self.state.current_water_level = WaterLevel.LOW
        elif self.state.current_water_level == WaterLevel.LOW:
            self.state.current_water_level = WaterLevel.HIGH
        else:
            assert False
