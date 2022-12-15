from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass

from models.vessels import CrudeOilTanker, BulkCarrier
from models.uni_waterway import UniWaterway

from utils.simple_collector import SimpleCollector

# The average velocity of a CrudeOilTanker is 10.7 knots or 19.8164 km/h
# Set the distance to 19.8164
# This takes 1 hour or 3600 seconds
#
# The average velocity of a BulkCarrier is 12 knots or 22.224 km/h
# This takes 0.89166666666 hours or (a little less than) 3210 seconds
WATERWAY_DISTANCE = 19.8164


@dataclass
class GeneratorState:
    count: int = 0


class SimpleGenerator(AtomicDEVS):
    """
    Generates
        t=0:  CrudeOilTanker(uid=0)
        t=10: BulkCarrier(uid=1)
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
        else:
            return INFINITY

    def outputFnc(self):
        if self.state.count == 0:
            return {self.out_item: CrudeOilTanker(uid=0, creation_time=0)}
        elif self.state.count == 1:
            return {self.out_item: BulkCarrier(uid=1, creation_time=10)}
        else:
            assert False


class CoupledUniWaterway(CoupledDEVS):
    def __init__(self, name):
        super(CoupledUniWaterway, self).__init__(name)

        self.simple_generator = self.addSubModel(SimpleGenerator("simple_generator"))
        self.uni_waterway = self.addSubModel(UniWaterway("uni_waterway", distance_in_km=WATERWAY_DISTANCE))
        self.simple_collector = self.addSubModel(SimpleCollector("simple_collector"))

        self.connectPorts(self.simple_generator.out_item, self.uni_waterway.in_vessel)
        self.connectPorts(self.uni_waterway.out_vessel, self.simple_collector.in_item)


def test():
    system = CoupledUniWaterway(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3600 + 0.01)  # simulate till last arrival
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels = system.simple_collector.state.items

    assert [(v.uid, v.time_in_system) for v in vessels] == [
        (1, 3210),
        (0, 3600)
    ]


if __name__ == "__main__":
    test()
