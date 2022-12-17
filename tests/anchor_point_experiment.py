from pypdevs.simulator import Simulator
from pypdevs.infinity import INFINITY
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS

from dataclasses import dataclass

from models.vessels import CrudeOilTanker
from models.anchor_point import AnchorPoint
from models.control_tower import ControlTower

from utils.vessel_collector import VesselCollector


# Dock named "1" has a capacity of 3 vessels
# Dock named "2" has a capacity of 2 vessels
# ...
DOCKS_CAPACITIES = {
    "1": 3,
    "2": 2,
    "3": 1
}


class SimpleGenerator(AtomicDEVS):
    """
    Generates 8 vessels
        t=0: CrudeOilTanker(uid=0)
        t=1: CrudeOilTanker(uid=1)
        ...
        t=7: CrudeOilTanker(uid=7)

    Note that it generates more ships than the port can handle (see DOCKS_CAPACITY)
    """

    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        self.out_item = self.addOutPort("out_item")
        self.state = 0

    def intTransition(self):
        self.state += 1
        return self.state

    def timeAdvance(self):
        if self.state == 0:
            return 0
        elif self.state <= 7:
            return 1
        else:
            return INFINITY

    def outputFnc(self):
        return {self.out_item: CrudeOilTanker(uid=self.state, creation_time=self.state)}


@dataclass
class SimpleControlTowerState:
    count: int = 0
    remaining_time: float = 0.0


class CoupledAnchorPoint(CoupledDEVS):
    def __init__(self, name):
        super(CoupledAnchorPoint, self).__init__(name)

        self.simple_generator = self.addSubModel(SimpleGenerator("simple_generator"))
        self.anchor_point = self.addSubModel(AnchorPoint("anchor_point"))
        self.control_tower = self.addSubModel(ControlTower("control_tower", docks_capacities=DOCKS_CAPACITIES))
        self.vessel_collector = self.addSubModel(VesselCollector("vessel_collector"))

        self.connectPorts(self.simple_generator.out_item, self.anchor_point.in_vessel)
        self.connectPorts(self.anchor_point.out_port_entry_request, self.control_tower.in_port_entry_request)
        self.connectPorts(self.control_tower.out_port_entry_permission,
                          self.anchor_point.in_port_entry_permission)
        self.connectPorts(self.anchor_point.out_vessel, self.vessel_collector.in_vessel)


def test():
    system = CoupledAnchorPoint(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(30)  # Simulate more than long enough
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels = system.vessel_collector.state.vessels

    assert [(v.uid, v.creation_time, v.time_in_system, v.destination_dock) for v in vessels] == [
        (0, 0, 0, '1'),
        (1, 1, 0, '1'),
        (2, 2, 0, '1'),

        (3, 3, 0, '2'),
        (4, 4, 0, '2'),

        (5, 5, 0, '3'),
    ]


if __name__ == "__main__":
    test()
