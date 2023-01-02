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


class SimpleGenerator(AtomicDEVS):
    """
    Generates
        t=0:  CrudeOilTanker(uid=0)
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
        else:
            return INFINITY

    def outputFnc(self):
        if self.state.count == 0:
            return {self.out_item: CrudeOilTanker(uid=0, creation_time=0)}
        else:
            assert False

class CoupledLock(CoupledDEVS):
    def __init__(self, name):
        super(CoupledLock, self).__init__(name)

        self.lock = self.addSubModel(Lock('A', 1, 4, 1, 25000))
        self.simple_generator = self.addSubModel(SimpleGenerator('Generator'))
        self.simple_collector = self.addSubModel(VesselCollector('Collector'))

        self.connectPorts(self.simple_generator.out_item, self.lock.in_high)
        self.connectPorts(self.lock.out_low, self.simple_collector.in_vessel)


def test():
    system = CoupledLock(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3610 + 0.01)  # Simulate just long enough
    sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels = system.simple_collector.state.vessels

    assert [(v.uid, v.creation_time, v.time_in_system) for v in vessels] == [
        (0, 0, 270),
    ]

if __name__ == "__main__":
    test()
