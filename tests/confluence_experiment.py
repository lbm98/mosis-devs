from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS

from models.vessels import CrudeOilTanker
from models.confluence import Confluence

from utils.simple_collector import SimpleCollector
from utils.simple_generator import SimpleGenerator


CP_CONFLUENCE_INFO = {
    "port1": ["1", "2"],
    "port2": ["3", "4"],
    "port3": ["4", "5"],
}


# Goes from port 1 to 2
def generate_vessels_1(count):
    if count == 0:
        vessel = CrudeOilTanker(uid=0)
        vessel.destination_dock = "3"
        return vessel


# Goes from port 2 to 3
def generate_vessels_2(count):
    if count == 0:
        vessel = CrudeOilTanker(uid=1)
        vessel.destination_dock = "5"
        return vessel


# Goes from port 3 to 1
def generate_vessels_3(count):
    if count == 0:
        vessel = CrudeOilTanker(uid=2)
        vessel.destination_dock = "1"
        return vessel


class CoupledConfluence(CoupledDEVS):
    def __init__(self, name):
        super(CoupledConfluence, self).__init__(name)

        self.simple_generator_1 = self.addSubModel(
            SimpleGenerator("simple_generator", item_generator=generate_vessels_1))
        self.simple_generator_2 = self.addSubModel(
            SimpleGenerator("simple_generator", item_generator=generate_vessels_2))
        self.simple_generator_3 = self.addSubModel(
            SimpleGenerator("simple_generator", item_generator=generate_vessels_3))

        self.confluence = self.addSubModel(Confluence("anchor_point", confluence_info=CP_CONFLUENCE_INFO))

        self.simple_collector_1 = self.addSubModel(SimpleCollector("simple_collector_1"))
        self.simple_collector_2 = self.addSubModel(SimpleCollector("simple_collector_2"))
        self.simple_collector_3 = self.addSubModel(SimpleCollector("simple_collector_3"))

        self.connectPorts(self.simple_generator_1.out_item, self.confluence.in_vessel_ports["port1"])
        self.connectPorts(self.simple_generator_2.out_item, self.confluence.in_vessel_ports["port2"])
        self.connectPorts(self.simple_generator_3.out_item, self.confluence.in_vessel_ports["port3"])

        self.connectPorts(self.confluence.out_vessel_ports["port1"], self.simple_collector_1.in_item)
        self.connectPorts(self.confluence.out_vessel_ports["port2"], self.simple_collector_2.in_item)
        self.connectPorts(self.confluence.out_vessel_ports["port3"], self.simple_collector_3.in_item)


def test_confluence():
    system = CoupledConfluence(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(1)
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels_1 = system.simple_collector_1.items
    vessels_2 = system.simple_collector_2.items
    vessels_3 = system.simple_collector_3.items

    # print([v.uid for v in vessels_1])
    # print([v.uid for v in vessels_2])
    # print([v.uid for v in vessels_3])

    assert [v.uid for v in vessels_1] == [2]
    assert [v.uid for v in vessels_2] == [0]
    assert [v.uid for v in vessels_3] == [1]


if __name__ == "__main__":
    test_confluence()
