from pypdevs.simulator import Simulator
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS

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
    vessel = CrudeOilTanker(uid=count)
    if count == 0:  # leave immediately
        vessel.destination_dock = "4"  # takes 2 hours
        return vessel
    elif count == 3600:  # leave after 1 hour
        vessel.destination_dock = "1"  # takes 1 hour
        return vessel
    else:
        return None


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
    sim.setTerminationTime(7201)  # simulate for 2 hours (plus some leeway to account for FP errors)
    # sim.setVerbose(None)
    sim.setClassicDEVS()

    sim.simulate()

    result_1 = system.simple_collector_1.items
    result_2 = system.simple_collector_2.items
    print(result_1)
    print(result_2)


if __name__ == "__main__":
    test_confluence()
