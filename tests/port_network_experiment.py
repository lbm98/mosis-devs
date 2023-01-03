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

    print(f"avg_travel_time: {avg_travel_time}")

    # Statistic #2
    waiting_time_in_anchor_point_data = [vessel.waiting_time_in_anchor_point for vessel in vessels]
    avg_waiting_time_in_anchor_point = get_avg(waiting_time_in_anchor_point_data)

    print(f"avg_waiting_time_in_anchor_point: {avg_waiting_time_in_anchor_point}")

    # Statistic #3
    # NOT IMPLEMENTED

    # Statistic #4

    # Statistic #5
    lock_a___idle_time = system.lock_a.state.idle_time
    lock_b___idle_time = system.lock_b.state.idle_time
    lock_c___idle_time = system.lock_c.state.idle_time

    print(f"lock_a___idle_time: {lock_a___idle_time}")
    print(f"lock_b___idle_time: {lock_b___idle_time}")
    print(f"lock_c___idle_time: {lock_c___idle_time}")

    # Statistic #6
    lock_a___number_lock_state_changes_with_no_vessels = system.lock_a.state.number_lock_state_changes_with_no_vessels
    lock_b___number_lock_state_changes_with_no_vessels = system.lock_c.state.number_lock_state_changes_with_no_vessels
    lock_c___number_lock_state_changes_with_no_vessels = system.lock_c.state.number_lock_state_changes_with_no_vessels

    print(f"lock_a___number_lock_state_changes_with_no_vessels: {lock_a___number_lock_state_changes_with_no_vessels}")
    print(f"lock_b___number_lock_state_changes_with_no_vessels: {lock_b___number_lock_state_changes_with_no_vessels}")
    print(f"lock_c___number_lock_state_changes_with_no_vessels: {lock_c___number_lock_state_changes_with_no_vessels}")

    # Statistic #7
    rem_cap_lock_a = system.lock_a.state.sum_remaining_surface_area / system.lock_a.state.number_of_washings
    rem_cap_lock_b = system.lock_b.state.sum_remaining_surface_area / system.lock_b.state.number_of_washings
    rem_cap_lock_c = system.lock_c.state.sum_remaining_surface_area / system.lock_c.state.number_of_washings

    print(f"rem_cap_lock_a: {rem_cap_lock_a}")
    print(f"rem_cap_lock_b: {rem_cap_lock_b}")
    print(f"rem_cap_lock_c: {rem_cap_lock_c}")


if __name__ == "__main__":
    test1()
