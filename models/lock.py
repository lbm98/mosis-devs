from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass, field

from models.vessels import Vessel

from enum import Enum


class IntervalState(Enum):
    GATE_CLOSING = 1,
    WASHING = 2,
    GATE_OPENING = 3,
    GATE_IS_OPEN = 4


class WaterLevel(Enum):
    LOW = 0,
    HIGH = 1


@dataclass
class LockState:
    remaining_lock_shift_interval: int

    current_surface_area: int

    # The remaining time until generation of a new output event
    # Initially, do not generate any output events
    # Instead, we first wait for an input event
    remaining_time: float = INFINITY

    # The list that stores the vessels in this lock
    vessels_in_lock: list[Vessel] = field(default_factory=list)

    vessels_waiting_low: list[Vessel] = field(default_factory=list)

    vessels_waiting_high: list[Vessel] = field(default_factory=list)

    interval_state: IntervalState = IntervalState.GATE_IS_OPEN

    # Water level (1 = HIGH, 0 = LOW)
    current_water_level: WaterLevel = WaterLevel.HIGH


class Lock(AtomicDEVS):
    """
    Input durations are in minutes

    We assume that the amount of time it takes for all the vessels to leave the lock is never longer than the
    shift_interval_time - (2*gate_duration + washing_duration)
    """
    def __init__(self, name: str, washing_duration: int, lock_shift_interval: int, gate_duration: int, surface_area: int,
                 time_between_departures: int=30):
        AtomicDEVS.__init__(self, name)

        # Lock attributes
        self.name = name
        self.washing_duration = washing_duration * 60
        self.lock_shift_interval = lock_shift_interval * 60
        self.gate_duration = gate_duration * 60
        self.surface_area = surface_area
        self.time_between_departures = time_between_departures

        # Receive vessels on low and high level
        self.in_low = self.addInPort('in_vessel_low')
        self.in_high = self.addInPort('in_vessel_high')

        # Send vessels on low and high level
        self.out_low = self.addOutPort('out_vessel_low')
        self.out_high = self.addOutPort('out_vessel_high')

        # Initialize state
        self.state = LockState(current_surface_area=self.surface_area, remaining_lock_shift_interval=self.lock_shift_interval)

    def extTransition(self, inputs):
        if self.in_low in inputs:
            vessel = inputs[self.in_low]
            assert isinstance(vessel, Vessel)
            if self.state.interval_state == IntervalState.GATE_IS_OPEN and not self.state.current_water_level and self.state.current_surface_area >= vessel.surface_area:
                self.state.vessels_in_lock.append(vessel)
                self.state.current_surface_area -= vessel.surface_area
            else:
                self.state.vessels_waiting_low.append(vessel)
        elif self.in_high in inputs:
            vessel = inputs[self.in_high]
            assert isinstance(vessel, Vessel)
            if self.state.interval_state == IntervalState.GATE_IS_OPEN and self.state.current_water_level and self.state.current_surface_area >= vessel.surface_area:
                self.state.vessels_in_lock.append(vessel)
                self.state.current_surface_area -= vessel.surface_area
            else:
                self.state.vessels_waiting_high.append(vessel)
        return self.state

    def timeAdvance(self):
        if self.state.interval_state == IntervalState.GATE_CLOSING:
            return self.gate_duration
        elif self.state.interval_state == IntervalState.WASHING:
            return self.washing_duration
        elif self.state.interval_state == IntervalState.GATE_OPENING:
            return self.gate_duration
        elif self.state.interval_state == IntervalState.GATE_IS_OPEN:
            if len(self.state.vessels_in_lock) == 0:
                return self.state.remaining_lock_shift_interval - (2*self.gate_duration + self.washing_duration)
            else:
                self.state.remaining_lock_shift_interval -= self.time_between_departures
                # See assumption above
                assert self.state.remaining_lock_shift_interval >= 0
                return self.time_between_departures
        else:
            assert False

    def intTransition(self):
        if self.state.interval_state == IntervalState.GATE_CLOSING:
            # This reset can be done anywhere after outputting and inputting the vessels
            self.state.current_surface_area = self.surface_area
            self.state.remaining_lock_shift_interval = self.lock_shift_interval
            self.state.interval_state = IntervalState.WASHING
            return self.state
        elif self.state.interval_state == IntervalState.WASHING:
            if self.state.current_water_level == WaterLevel.HIGH:
                self.state.current_water_level = WaterLevel.LOW
            elif self.state.current_water_level == WaterLevel.LOW:
                self.state.current_water_level = WaterLevel.HIGH
            else:
                assert False
            self.state.interval_state = IntervalState.GATE_OPENING
            return self.state
        elif self.state.interval_state == IntervalState.GATE_OPENING:
            self.state.interval_state = IntervalState.GATE_IS_OPEN
            return self.state
        elif self.state.interval_state == IntervalState.GATE_IS_OPEN:

            if self.state.current_water_level == WaterLevel.HIGH:
                for idx, vessel in enumerate(self.state.vessels_waiting_high):
                    if self.state.current_surface_area - vessel.surface_area >= 0:
                        self.state.vessels_in_lock.append(vessel)
                        self.state.current_surface_area -= vessel.surface_area
                        self.state.vessels_waiting_high.pop(idx)

            elif self.state.current_water_level == WaterLevel.LOW:
                for idx, vessel in enumerate(self.state.vessels_waiting_low):
                    if self.state.current_surface_area - vessel.surface_area >= 0:
                        self.state.vessels_in_lock.append(vessel)
                        self.state.current_surface_area -= vessel.surface_area
                        self.state.vessels_waiting_low.pop(idx)

            if len(self.state.vessels_in_lock) != 0:
                self.state.vessels_in_lock.pop(0)
                self.state.interval_state = IntervalState.GATE_IS_OPEN
                return self.state
            self.state.interval_state = IntervalState.GATE_CLOSING
            return self.state
        else:
            assert False

    def outputFnc(self):
        if self.state.interval_state == IntervalState.GATE_IS_OPEN:
            if len(self.state.vessels_in_lock) != 0:
                vessel = self.state.vessels_in_lock[0]
                if self.state.current_water_level == WaterLevel.LOW:
                    return {self.out_low: vessel}
                elif self.state.current_water_level == WaterLevel.HIGH:
                    return {self.out_high: vessel}
        return {}
