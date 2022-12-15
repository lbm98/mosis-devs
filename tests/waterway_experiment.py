from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass

from models.vessels import CrudeOilTanker, BulkCarrier
from models.waterway import Waterway

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


class SimpleGenerator1(AtomicDEVS):
    """
    Generates
        t=0:  CrudeOilTanker(uid=0)
        t=10: BulkCarrier(uid=1)
    from left to right

    The BulkCarrier should overtake the CrudeOilTanker (unlike Canal's)
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


class SimpleGenerator2(AtomicDEVS):
    """
    Generates
        t=5:  CrudeOilTanker(uid=2)
        t=15: BulkCarrier(uid=3)
    from right to left

    The BulkCarrier should overtake the CrudeOilTanker (unlike Canal's)
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
            return 5
        elif self.state.count == 1:
            return 10   # Note this is not 15, but correctly outputs an event at t=15
        else:
            return INFINITY

    def outputFnc(self):
        if self.state.count == 0:
            return {self.out_item: CrudeOilTanker(uid=2, creation_time=5)}
        elif self.state.count == 1:
            return {self.out_item: BulkCarrier(uid=3, creation_time=15)}
        else:
            assert False


class CoupledWaterway(CoupledDEVS):
    def __init__(self, name):
        CoupledDEVS.__init__(self, name)

        self.simple_generator_1 = self.addSubModel(SimpleGenerator1("simple_generator_1"))
        self.simple_generator_2 = self.addSubModel(SimpleGenerator2("simple_generator_2"))
        self.waterway = self.addSubModel(Waterway("waterway", distance_in_km=WATERWAY_DISTANCE))
        self.simple_collector_1 = self.addSubModel(SimpleCollector("simple_collector_1"))
        self.simple_collector_2 = self.addSubModel(SimpleCollector("simple_collector_2"))

        self.connectPorts(self.simple_generator_1.out_item, self.waterway.in1)
        self.connectPorts(self.simple_generator_2.out_item, self.waterway.in2)
        self.connectPorts(self.waterway.out1, self.simple_collector_1.in_item)
        self.connectPorts(self.waterway.out2, self.simple_collector_2.in_item)


def test():
    system = CoupledWaterway(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3605 + 0.01)  # Simulate just long enough
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels_1 = system.simple_collector_1.state.items
    vessels_2 = system.simple_collector_2.state.items

    assert [(v.uid, v.creation_time, v.time_in_system) for v in vessels_1] == [
        (1, 10, 3210),
        (0, 0, 3600)
    ]

    assert [(v.uid, v.creation_time, v.time_in_system) for v in vessels_2] == [
        (3, 15, 3210),
        (2, 5, 3600)
    ]


if __name__ == "__main__":
    test()
