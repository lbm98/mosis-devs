from pypdevs.simulator import Simulator
from models.generator import Generator

import numpy as np


def test_generator():
    system = Generator(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3600.0)  # simulate 1 hour
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    # Make the random numbers reproducible
    np.random.seed(0)
    sim.simulate()

    result = system.state.vessel_count

    # should be around 100
    # that is, the first index of the bar chart
    assert result == 108


if __name__ == "__main__":
    test_generator()
