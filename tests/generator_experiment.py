from pypdevs.simulator import Simulator
from models.generator import Generator

import numpy as np


def test1():
    system = Generator(name="system", num_vessels_to_generate=10000)  # Large enough
    sim = Simulator(system)
    sim.setTerminationTime(3600.0)
    # sim.setVerbose(None)
    sim.setClassicDEVS()

    # Make the random numbers reproducible
    np.random.seed(0)
    sim.simulate()
    vessel_count = system.state.num_vessels_generated
    # should be AROUND 100
    # that is, the first index of the bar chart
    assert vessel_count == 108


def test2():
    system = Generator(name="system", num_vessels_to_generate=100)
    sim = Simulator(system)
    sim.setTerminationTime(10000.0)  # Large enough
    # sim.setVerbose(None)
    sim.setClassicDEVS()

    # Make the random numbers reproducible
    np.random.seed(0)
    sim.simulate()
    vessel_count = system.state.num_vessels_generated
    # should be EXACTLY 100
    assert vessel_count == 100


if __name__ == "__main__":
    test1()
    test2()
