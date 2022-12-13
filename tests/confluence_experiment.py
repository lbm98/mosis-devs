from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS

from models.vessels import CrudeOilTanker
from models.confluence import Confluence, ConfluenceInfoRecord

from utils.simple_collector import SimpleCollector
from utils.simple_generator import SimpleGenerator

# The average velocity of a CrudeOilTanker is 10.7 knots or 19.8164 km/h
# set first distance to
#   1 x 19.8164 = 19.8164 --- takes 1 hour
# set second distance to
#   2 x 19.8164 = 39.6328 --- takes 2 hours
CP_CONFLUENCE_INFO = [
    ConfluenceInfoRecord(
        distance_in_km=19.8164,
        docks=["1", "2"],
        port_name="out_vessel_1"
    ),
    ConfluenceInfoRecord(
        distance_in_km=39.6328,
        docks=["3", "4"],
        port_name="out_vessel_2"
    )
]


def generate_vessels(count):
    # leaves immediately
    # takes 2 hours
    # arrives in 2 hours
    if count == 0:
        vessel = CrudeOilTanker(uid=0)
        vessel.destination_dock = "4"
        return vessel

    # leaves after 0.5 hour
    # takes 2 hours
    # arrives in 2.5 hours
    elif count == 1800:  # leave
        vessel = CrudeOilTanker(uid=1)
        vessel.destination_dock = "4"
        return vessel

    # leaves after 1 hour
    # takes 1 hour
    # arrives in 2 hours
    elif count == 3600:
        vessel = CrudeOilTanker(uid=2)
        vessel.destination_dock = "1"
        return vessel

    # leaves after 1.5 hour
    # takes 2 hours
    # arrives in 3.5 hours
    elif count == 5400:
        vessel = CrudeOilTanker(uid=3)
        vessel.destination_dock = "4"
        return vessel


class CoupledConfluence(CoupledDEVS):
    def __init__(self, name):
        super(CoupledConfluence, self).__init__(name)

        self.simple_generator = self.addSubModel(SimpleGenerator("simple_generator", item_generator=generate_vessels))
        self.confluence = self.addSubModel(Confluence("anchor_point", confluence_info=CP_CONFLUENCE_INFO))
        self.simple_collector_1 = self.addSubModel(SimpleCollector("simple_collector_1"))
        self.simple_collector_2 = self.addSubModel(SimpleCollector("simple_collector_2"))

        self.connectPorts(self.simple_generator.out_item, self.confluence.in_vessel)
        self.connectPorts(self.confluence.out_vessel_ports["out_vessel_1"], self.simple_collector_1.in_item)
        self.connectPorts(self.confluence.out_vessel_ports["out_vessel_2"], self.simple_collector_2.in_item)


def test_confluence():
    system = CoupledConfluence(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3.5 * 3600 + 1)  # simulate for 3.5 hours (plus some leeway)
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels_1 = system.simple_collector_1.items
    vessels_2 = system.simple_collector_2.items

    assert [v.uid for v in vessels_1] == [2]
    assert [v.uid for v in vessels_2] == [0, 1, 3]


if __name__ == "__main__":
    test_confluence()
