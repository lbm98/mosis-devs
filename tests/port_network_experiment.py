from pypdevs.simulator import Simulator
from models.port_network import PortNetwork

import matplotlib.pyplot as plt
import numpy as np

from dataclasses import dataclass


def get_avg(lst):
    return sum(lst)/len(lst)


def test1():
    system = PortNetwork(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(1000000.0)
    # sim.setVerbose(None)
    sim.setClassicDEVS()

    # Make the random numbers reproducible
    np.random.seed(0)
    sim.simulate()

    vessels = system.sea_collector.state.vessels


    # Statistic #1
    time_in_system_data = [vessel.time_in_system for vessel in vessels]
    avg_travel_time = get_avg(time_in_system_data)

    # Statistic #2
    waiting_time_in_anchor_point_data = [vessel.waiting_time_in_anchor_point for vessel in vessels]
    avg_waiting_time_in_anchor_point = get_avg(waiting_time_in_anchor_point_data)

    # Statistic #3
    cum_vessels_gen = system.sea_collector.state.cum_vessels
    cum_vessels_col = system.generator.state.cum_vessels
    cum_gen = system.generator.state.num_vessels_generated
    avg_number_of_vessels = (cum_vessels_gen / cum_gen) - (cum_vessels_col / cum_gen)

    print(f"len_vessels: {len(vessels)}")
    print(f"avg_travel_time: {avg_travel_time}")
    print(f"avg_waiting_time_in_anchor_point: {avg_waiting_time_in_anchor_point}")
    print(f"avg_number_of_vessels: {avg_number_of_vessels}")



if __name__ == "__main__":
    test1()
