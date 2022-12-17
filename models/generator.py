from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

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
    remaining_time: float = 0.0
    # The current simulation time
    current_time: float = 0.0
    # The number of vessels generated
    num_vessels_generated: int = 0


class Generator(AtomicDEVS):
    def __init__(self, name, num_vessels_to_generate):
        super(Generator, self).__init__(name)
        self.num_vessels_to_generate = num_vessels_to_generate
        self.out = self.addOutPort("out")
        self.state = GeneratorState()

    def intTransition(self):
        # Update simulation time
        self.state.current_time += self.timeAdvance()

        # Register that we generated a vessel
        self.state.num_vessels_generated += 1

        # Find the index of the bar chart
        hour = int(self.state.current_time) // SECONDS_PER_HOUR

        # Index the bar chart
        num_vessels_per_hour_mean = NUM_VESSELS_ARRIVING_PER_HOUR[hour % HOURS_PER_DAY]

        # If more vessels should be generated
        #   Schedule next event at some Inter-Arrival-Time
        # Else
        #   Do nothing anymore
        if self.state.num_vessels_generated < self.num_vessels_to_generate:
            iat = np.random.exponential(SECONDS_PER_HOUR/num_vessels_per_hour_mean)
            self.state.remaining_time = iat
        else:
            self.state.remaining_time = INFINITY

        return self.state

    def timeAdvance(self):
        # Return remaining time
        return self.state.remaining_time

    def outputFnc(self):

        # Sample vessel type
        vessel_ctor = random.choices(ALL_VESSELS, VESSEL_WEIGHTS)[0]
        vessel = vessel_ctor(
            uid=self.state.num_vessels_generated,
            # Important addition
            creation_time=self.state.current_time + self.state.remaining_time
        )
        return {self.out: vessel}
