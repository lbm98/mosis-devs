from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS

from models.messages import PortEntryRequest
from models.control_tower import ControlTower

from utils.simple_collector import SimpleCollector
from utils.simple_generator import SimpleGenerator


def generate_port_entry_requests(count):
    return PortEntryRequest(
        vessel_uid=count
    )


class CoupledControlTower(CoupledDEVS):
    def __init__(self, name):
        super(CoupledControlTower, self).__init__(name)

        self.simple_generator = self.addSubModel(
            SimpleGenerator("simple_generator", item_generator=generate_port_entry_requests))
        self.control_tower = self.addSubModel(ControlTower("control_tower"))
        self.simple_collector = self.addSubModel(SimpleCollector("simple_collector"))

        self.connectPorts(self.simple_generator.out_item, self.control_tower.in_port_entry_request)
        self.connectPorts(self.control_tower.out_port_entry_permission, self.simple_collector.in_item)


def test_control_tower():
    system = CoupledControlTower(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(10)
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    perm = system.simple_collector.items

    assert perm[0].vessel_uid == 0 and perm[0].avl_dock == '1'
    assert perm[1].vessel_uid == 1 and perm[1].avl_dock == '2'
    assert perm[2].vessel_uid == 2 and perm[2].avl_dock == '3'
    assert perm[3].vessel_uid == 3 and perm[3].avl_dock == '4'
    assert len(perm) == 8


if __name__ == "__main__":
    test_control_tower()
