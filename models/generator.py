from pypdevs.DEVS import AtomicDEVS

from dataclasses import dataclass
import random
import numpy as np

from models.vessels import *
from models.utils.constants import HOURS_PER_DAY, SECONDS_PER_HOUR

# Average amount of vessels arriving at the port on an hourly basis
NUM_VESSELS_ARRIVING_PER_HOUR = [100, 120, 150, 175, 125, 50, 42, 68, 200, 220, 250, 245, 253, 236, 227, 246, 203, 43,
                                 51, 33, 143, 187, 164, 123]


@dataclass
class GeneratorState:
    # The remaining time until generation of new event
    remaining: float = 0.0
    # The current simulation time
    current_time: float = 0.0
    # The number of vessels generated
    vessel_count: int = 0


class Generator(AtomicDEVS):
    def __init__(self, name):
        super(Generator, self).__init__(name)
        self.out = self.addOutPort("out")
        self.state = GeneratorState()

    def intTransition(self):
        # Update simulation time
        self.state.current_time += self.timeAdvance()

        # Find the index of the bar chart
        hour = int(self.state.current_time) // SECONDS_PER_HOUR

        # Index the bar chart
        num_vessels_per_hour_mean = NUM_VESSELS_ARRIVING_PER_HOUR[hour % HOURS_PER_DAY]

        # Compute the Inter-Arrival-Time
        iat = np.random.exponential(SECONDS_PER_HOUR/num_vessels_per_hour_mean)
        self.state.remaining = iat

        return self.state

    def timeAdvance(self):
        # Return remaining time
        return self.state.remaining

    def outputFnc(self):
        self.state.vessel_count += 1
        # Sample vessel type
        chosen_vessel_obj = random.choices(ALL_VESSELS, VESSEL_WEIGHTS)[0]
        return {self.out: chosen_vessel_obj(uid=self.state.vessel_count)}
