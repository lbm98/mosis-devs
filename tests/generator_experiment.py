from pypdevs.simulator import Simulator
from models.generator import Generator

import numpy as np


def test():
    system = Generator(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3600.0)  # simulate 1 hour
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    # Make the random numbers reproducible
    np.random.seed(0)
    sim.simulate()

    vessel_count = system.state.vessel_count

    # should be around 100
    # that is, the first index of the bar chart
    assert vessel_count == 108


if __name__ == "__main__":
    test()
