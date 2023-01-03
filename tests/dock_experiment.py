from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
from pypdevs.infinity import INFINITY

import numpy as np

from models.vessels import CrudeOilTanker
from models.dock import Dock
from models.messages import PortDepartureRequest
from models.utils.constants import SECONDS_PER_HOUR

from utils.vessel_collector import VesselCollector


class RequestCollector(AtomicDEVS):
    """
    A simple collector the collects PortDepartureRequest's
    """

    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        self.in_port_departure_request = self.addInPort("in_port_departure_request")
        self.state = []

    def extTransition(self, inputs):
        assert self.in_port_departure_request in inputs
        port_departure_request = inputs[self.in_port_departure_request]
        assert isinstance(port_departure_request, PortDepartureRequest)
        self.state.append(port_departure_request)

        return self.state


class SimpleGenerator(AtomicDEVS):
    """
    Generates 100 vessels at t=0
    """

    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        self.out_item = self.addOutPort("out_item")
        self.state = 0

    def intTransition(self):
        self.state += 1
        return self.state

    def timeAdvance(self):
        if self.state < 100:
            return 0
        else:
            return INFINITY

    def outputFnc(self):
        return {self.out_item: CrudeOilTanker(uid=self.state, creation_time=self.state)}


class CoupledDock(CoupledDEVS):
    def __init__(self, name):
        CoupledDEVS.__init__(self, name)

        self.simple_generator = self.addSubModel(SimpleGenerator("simple_generator"))
        self.dock = self.addSubModel(Dock("dock"))
        self.vessel_collector = self.addSubModel(VesselCollector("vessel_collector"))
        self.request_collector = self.addSubModel(RequestCollector("request_collector"))

        self.connectPorts(self.simple_generator.out_item, self.dock.in_vessel)
        self.connectPorts(self.dock.out_vessel, self.vessel_collector.in_vessel)
        self.connectPorts(self.dock.out_port_departure_request, self.request_collector.in_port_departure_request)


def test():
    # Simulate for the mean time of the distribution (36 hours)
    # Expect that half of the vessels depart (50 vessels)
    system = CoupledDock(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(36 * SECONDS_PER_HOUR)
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    # Make the random numbers reproducible
    np.random.seed(0)

    sim.simulate()

    vessels = system.vessel_collector.state.vessels
    requests = system.request_collector.state

    # should be AROUND 50
    assert len(vessels) == 45
    assert len(requests) == 45

    assert vessels[0].destination_dock == '9'
    assert requests[0].dock == 'dock'


if __name__ == "__main__":
    test()
