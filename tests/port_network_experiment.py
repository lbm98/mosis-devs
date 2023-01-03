from pypdevs.simulator import Simulator
from models.port_network import PortNetwork

import matplotlib.pyplot as plt
import numpy as np


def test1():
    system = PortNetwork(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(8000000.0)
    # sim.setVerbose(None)
    sim.setClassicDEVS()

    # Make the random numbers reproducible
    np.random.seed(2)
    sim.simulate()

    vessels = system.sea_collector.state.vessels
    stats = [vessel.time_in_system for vessel in vessels]

    plt.plot(stats)
    plt.show()

if __name__ == "__main__":
    test1()
