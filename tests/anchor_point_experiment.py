from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS

from models.vessels import CrudeOilTanker
from models.anchor_point import AnchorPoint
from models.control_tower import ControlTower

from utils.simple_generator import SimpleGenerator
from utils.simple_collector import SimpleCollector


def generate_vessels(count):
    return CrudeOilTanker(uid=count)


class CoupledAnchorPoint(CoupledDEVS):
    def __init__(self, name):
        super(CoupledAnchorPoint, self).__init__(name)

        self.simple_generator = self.addSubModel(SimpleGenerator("simple_generator", item_generator=generate_vessels))
        self.anchor_point = self.addSubModel(AnchorPoint("anchor_point"))
        self.control_tower = self.addSubModel(ControlTower("control_tower"))
        self.simple_collector = self.addSubModel(SimpleCollector("simple_collector"))

        self.connectPorts(self.simple_generator.out_item, self.anchor_point.in_vessel)
        self.connectPorts(self.anchor_point.out_port_entry_request, self.control_tower.in_port_entry_request)
        self.connectPorts(self.control_tower.out_port_entry_permission, self.anchor_point.in_port_entry_permission)
        self.connectPorts(self.anchor_point.out_vessel, self.simple_collector.in_item)


def test_anchor_point():
    system = CoupledAnchorPoint(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(10)
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels = system.simple_collector.items

    assert vessels[0].uid == 0 and vessels[0].destination_dock == '1'
    assert vessels[1].uid == 1 and vessels[1].destination_dock == '2'
    assert vessels[2].uid == 2 and vessels[2].destination_dock == '3'
    assert vessels[3].uid == 3 and vessels[3].destination_dock == '4'
    assert len(vessels) == 8


if __name__ == "__main__":
    test_anchor_point()
