from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
from pypdevs.infinity import INFINITY

from models.vessels import CrudeOilTanker, BulkCarrier
from models.canal import Canal

from utils.simple_collector import SimpleCollector

# The average velocity of a CrudeOilTanker is 10.7 knots or 19.8164 km/h
# Set the distance to 19.8164
# This takes 1 hour or 3600 seconds
#
# The average velocity of a BulkCarrier is 12 knots or 22.224 km/h
# This takes 0.89166666666 hours or 3210 seconds (a little less)
# However, the BulkCarrier will have to slow-down to match the CrudeOilTanker's speed.
# So, it will take 3600 seconds
CANAL_DISTANCE = 19.8164


class SimpleGenerator1(AtomicDEVS):
    """
    Generate a CrudeOilTanker at t=0 and a BulkCarrier at t=5
    This will test the slowing-down feature
    """

    def __init__(self, name):
        super(SimpleGenerator1, self).__init__(name)
        self.out_item = self.addOutPort("out_item")
        self.state = 0

    def intTransition(self):
        self.state += 1
        return self.state

    def timeAdvance(self):
        if self.state == 0:
            return 0
        elif self.state == 1:
            return 5
        else:
            return INFINITY

    def outputFnc(self):
        if self.state == 0:
            return {self.out_item: CrudeOilTanker(uid=0)}
        elif self.state == 1:
            return {self.out_item: BulkCarrier(uid=1)}


class CoupledCanal(CoupledDEVS):
    def __init__(self, name):
        super(CoupledCanal, self).__init__(name)

        self.simple_generator_1 = self.addSubModel(SimpleGenerator1("simple_generator_1"))

        self.canal = self.addSubModel(Canal("canal", distance_in_km=CANAL_DISTANCE))

        self.simple_collector_1 = self.addSubModel(SimpleCollector("simple_collector_1"))

        self.connectPorts(self.simple_generator_1.out_item, self.canal.in1)
        self.connectPorts(self.canal.out1, self.simple_collector_1.in_item)


def test_canal():
    system = CoupledCanal(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3605 + 1)  # simulate till last arrival
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels_1 = system.simple_collector_1.items

    assert [v.uid for v in vessels_1] == [0, 1]


if __name__ == "__main__":
    test_canal()
