from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
from pypdevs.infinity import INFINITY

from models.vessels import CrudeOilTanker, BulkCarrier
from models.waterway import Waterway, WaterwayInfo

from utils.simple_collector import SimpleCollector
from utils.simple_generator import SimpleGenerator

# The average velocity of a CrudeOilTanker is 10.7 knots or 19.8164 km/h
# Set the distance to 19.8164
# This takes 1 hour or 3600 seconds
#
# The average velocity of a BulkCarrier is 12 knots or 22.224 km/h
# This takes 0.89166666666 hours or 3210 seconds (a little less)
WATERWAY_INFO = WaterwayInfo(
    in_out_vessel_port_1=("in1", "out1"),
    in_out_vessel_port_2=("in2", "out2"),
    distance_in_km=19.8164
)


class SimpleGenerator1(AtomicDEVS):
    """
    Generate a CrudeOilTanker at t=0 and t=10
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
            return 10
        else:
            return INFINITY

    def outputFnc(self):
        if self.state == 0:
            return {self.out_item: CrudeOilTanker(uid=0)}
        elif self.state == 1:
            return {self.out_item: CrudeOilTanker(uid=2)}


class SimpleGenerator2(AtomicDEVS):
    """
    Generate a BulkCarrier at t=5
    """

    def __init__(self, name):
        super(SimpleGenerator2, self).__init__(name)
        self.out_item = self.addOutPort("out_item")
        self.state = 0

    def intTransition(self):
        self.state += 1
        return self.state

    def timeAdvance(self):
        if self.state == 0:
            return 5
        else:
            return INFINITY

    def outputFnc(self):
        if self.state == 0:
            return {self.out_item: BulkCarrier(uid=1)}


class CoupledWaterway(CoupledDEVS):
    def __init__(self, name):
        super(CoupledWaterway, self).__init__(name)

        self.simple_generator_1 = self.addSubModel(SimpleGenerator1("simple_generator_1"))
        self.simple_generator_2 = self.addSubModel(SimpleGenerator2("simple_generator_2"))

        self.waterway = self.addSubModel(Waterway("waterway", waterway_info=WATERWAY_INFO))

        self.simple_collector_1 = self.addSubModel(SimpleCollector("simple_collector_1"))
        self.simple_collector_2 = self.addSubModel(SimpleCollector("simple_collector_2"))

        self.connectPorts(self.simple_generator_1.out_item, self.waterway.in_vessel_ports["in1"])
        self.connectPorts(self.simple_generator_2.out_item, self.waterway.in_vessel_ports["in2"])

        self.connectPorts(self.waterway.out_vessel_ports["out1"], self.simple_collector_1.in_item)
        self.connectPorts(self.waterway.out_vessel_ports["out2"], self.simple_collector_2.in_item)


def test_confluence():
    system = CoupledWaterway(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3610)  # simulate till last arrival
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels_1 = system.simple_collector_1.items
    vessels_2 = system.simple_collector_2.items

    assert [v.uid for v in vessels_1] == [0, 2]
    assert [v.uid for v in vessels_2] == [1]


if __name__ == "__main__":
    test_confluence()
