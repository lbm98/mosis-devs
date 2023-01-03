from pypdevs.simulator import Simulator
from models.port_network import PortNetwork

import numpy as np


def test1():
    system = PortNetwork(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3600.0)
    # sim.setVerbose(None)
    sim.setClassicDEVS()

    # Make the random numbers reproducible
    np.random.seed(0)
    sim.simulate()



if __name__ == "__main__":
    test1()