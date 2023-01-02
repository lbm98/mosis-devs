from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
from pypdevs.infinity import INFINITY

from models.lock import Lock

from dataclasses import dataclass

from models.vessels import CrudeOilTanker, BulkCarrier
from utils.vessel_collector import VesselCollector


@dataclass
class GeneratorState:
    count: int = 0


class SimpleGeneratorHigh(AtomicDEVS):
    """
    Generates
        t=0:  CrudeOilTanker(uid=0)
        t=10: BulkCarrier(uid=1)

    The BulkCarrier should NOT overtake the CrudeOilTanker (unlike Waterway's)
    """

    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        self.out_item = self.addOutPort("out_item")
        self.state = GeneratorState()

    def intTransition(self):
        self.state.count += 1
        return self.state

    def timeAdvance(self):
        if self.state.count == 0:
            return 0
        elif self.state.count == 1:
            return 10
        elif self.state.count == 2:
            return 10
        else:
            return INFINITY

    def outputFnc(self):
        if self.state.count == 0:
            return {self.out_item: CrudeOilTanker(uid=0, creation_time=0)}
        elif self.state.count == 1:
            return {self.out_item: BulkCarrier(uid=1, creation_time=10)}
        elif self.state.count == 2:
            return {self.out_item: BulkCarrier(uid=2, creation_time=20)}
        else:
            assert False


class SimpleGeneratorLow(AtomicDEVS):
    """
    Generates
        t=0:  CrudeOilTanker(uid=0)
        t=10: BulkCarrier(uid=1)

    The BulkCarrier should NOT overtake the CrudeOilTanker (unlike Waterway's)
    """

    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        self.out_item = self.addOutPort("out_item")
        self.state = GeneratorState()

    def intTransition(self):
        self.state.count += 1
        return self.state

    def timeAdvance(self):
        if self.state.count == 0:
            return 0
        elif self.state.count == 1:
            return 10
        elif self.state.count == 2:
            return 10
        else:
            return INFINITY

    def outputFnc(self):
        if self.state.count == 0:
            return {self.out_item: CrudeOilTanker(uid=3, creation_time=0)}
        elif self.state.count == 1:
            return {self.out_item: BulkCarrier(uid=4, creation_time=10)}
        elif self.state.count == 2:
            return {self.out_item: BulkCarrier(uid=5, creation_time=20)}
        else:
            assert False


class CoupledLock(CoupledDEVS):
    def __init__(self, name):
        super(CoupledLock, self).__init__(name)

        self.lock = self.addSubModel(Lock('A', 1, 4, 1, 20000))
        self.simple_generator_high = self.addSubModel(SimpleGeneratorHigh('Generator_high'))
        self.simple_generator_low = self.addSubModel(SimpleGeneratorLow('Generator_low'))

        self.simple_collector_low = self.addSubModel(VesselCollector('Collector_low'))
        self.simple_collector_high = self.addSubModel(VesselCollector('Collector_high'))

        self.connectPorts(self.simple_generator_high.out_item, self.lock.in_high)
        self.connectPorts(self.simple_generator_low.out_item, self.lock.in_low)
        self.connectPorts(self.lock.out_high, self.simple_collector_high.in_vessel)
        self.connectPorts(self.lock.out_low, self.simple_collector_low.in_vessel)


def test():
    system = CoupledLock(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3610 + 0.01)  # Simulate just long enough
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels_low = system.simple_collector_low.state.vessels
    vessels_high = system.simple_collector_high.state.vessels

    assert [(v.uid, v.creation_time, v.time_in_system) for v in vessels_low] == [(0, 0, 270.0), (1, 10, 290.0), (2, 20, 730.0)]
    assert [(v.uid, v.creation_time, v.time_in_system) for v in vessels_high] == [(3, 0, 510.0), (5, 20, 520.0), (4, 10, 980.0)]


if __name__ == "__main__":
    test()
