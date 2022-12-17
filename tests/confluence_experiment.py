from pypdevs.simulator import Simulator
from pypdevs.infinity import INFINITY
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS

from models.vessels import CrudeOilTanker
from models.confluence import Confluence

from utils.vessel_collector import VesselCollector

# This information means:
#   to reach docks named "1" and "2", go out the port named "port1"
#   to reach docks named "3" and "4", go out the port named "port2"
#   ...
#
# A port-name identifies an (input,output) port pair
CONFLUENCE_INFO = {
    "port1": ["1", "2"],
    "port2": ["3", "4"],
    "port3": ["4", "5"],
}

# Goes from port 1 to 2
VESSEL_1 = CrudeOilTanker(uid=0, creation_time=0, destination_dock="3")

# Goes from port 2 to 3
VESSEL_2 = CrudeOilTanker(uid=1, creation_time=0, destination_dock="5")

# Goes from port 3 to 1
VESSEL_3 = CrudeOilTanker(uid=2, creation_time=0, destination_dock="1")


class SimpleGenerator(AtomicDEVS):
    """
    Generates at t=0 the given vessel
    """

    def __init__(self, name, vessel):
        AtomicDEVS.__init__(self, name)
        self.out_item = self.addOutPort("out_item")
        self.vessel = vessel
        self.state = 0

    def intTransition(self):
        self.state += 1
        return self.state

    def timeAdvance(self):
        if self.state == 0:
            return 0
        else:
            return INFINITY

    def outputFnc(self):
        return {self.out_item: self.vessel}


class CoupledConfluence(CoupledDEVS):
    def __init__(self, name):
        super(CoupledConfluence, self).__init__(name)

        self.simple_generator_1 = self.addSubModel(SimpleGenerator("simple_generator_1", vessel=VESSEL_1))
        self.simple_generator_2 = self.addSubModel(SimpleGenerator("simple_generator_2", vessel=VESSEL_2))
        self.simple_generator_3 = self.addSubModel(SimpleGenerator("simple_generator_3", vessel=VESSEL_3))

        self.confluence = self.addSubModel(Confluence("confluence", confluence_info=CONFLUENCE_INFO))

        self.vessel_collector_1 = self.addSubModel(VesselCollector("vessel_collector_1"))
        self.vessel_collector_2 = self.addSubModel(VesselCollector("vessel_collector_2"))
        self.vessel_collector_3 = self.addSubModel(VesselCollector("vessel_collector_3"))

        self.connectPorts(self.simple_generator_1.out_item, self.confluence.in_vessel_ports["port1"])
        self.connectPorts(self.simple_generator_2.out_item, self.confluence.in_vessel_ports["port2"])
        self.connectPorts(self.simple_generator_3.out_item, self.confluence.in_vessel_ports["port3"])

        self.connectPorts(self.confluence.out_vessel_ports["port1"], self.vessel_collector_1.in_vessel)
        self.connectPorts(self.confluence.out_vessel_ports["port2"], self.vessel_collector_2.in_vessel)
        self.connectPorts(self.confluence.out_vessel_ports["port3"], self.vessel_collector_3.in_vessel)


def test():
    system = CoupledConfluence(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(0.01)  # Simulate just long enough
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels_1 = system.vessel_collector_1.state.vessels
    vessels_2 = system.vessel_collector_2.state.vessels
    vessels_3 = system.vessel_collector_3.state.vessels

    assert [(v.uid, v.creation_time, v.time_in_system) for v in vessels_1] == [
        (2, 0, 0)
    ]

    assert [(v.uid, v.creation_time, v.time_in_system) for v in vessels_2] == [
        (0, 0, 0)
    ]

    assert [(v.uid, v.creation_time, v.time_in_system) for v in vessels_3] == [
        (1, 0, 0)
    ]


if __name__ == "__main__":
    test()
