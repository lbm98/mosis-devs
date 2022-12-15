from pypdevs.simulator import Simulator
from pypdevs.infinity import INFINITY
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS

from models.messages import PortEntryRequest
from models.control_tower import ControlTower

from utils.simple_collector import SimpleCollector


class SimpleGenerator(AtomicDEVS):
    """
    Generates
        t=0: PortEntryRequest(vessel_uid=0)
        t=1: PortEntryRequest(vessel_uid=1)
        ...
        t=9: PortEntryRequest(vessel_uid=9)
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
        elif self.state <= 9:
            return 1
        else:
            return INFINITY

    def outputFnc(self):
        return {self.out_item: PortEntryRequest(vessel_uid=self.state)}


class CoupledControlTower(CoupledDEVS):
    def __init__(self, name):
        super(CoupledControlTower, self).__init__(name)

        self.simple_generator = self.addSubModel(SimpleGenerator("simple_generator"))
        self.control_tower = self.addSubModel(ControlTower("control_tower"))
        self.simple_collector = self.addSubModel(SimpleCollector("simple_collector"))

        self.connectPorts(self.simple_generator.out_item, self.control_tower.in_port_entry_request)
        self.connectPorts(self.control_tower.out_port_entry_permission, self.simple_collector.in_item)


def test():
    system = CoupledControlTower(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(10)  # Simulate more than long enough
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    permissions = system.simple_collector.state.items

    assert [(p.vessel_uid, p.avl_dock) for p in permissions] == [
        (0, '1'),
        (1, '2'),
        (2, '3'),
        (3, '4'),
        (4, '5'),
        (5, '6'),
        (6, '7'),
        (7, '8'),
    ]


if __name__ == "__main__":
    test()
