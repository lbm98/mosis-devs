from pypdevs.simulator import Simulator
from pypdevs.infinity import INFINITY
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS

from models.messages import PortEntryRequest, PortEntryPermission
from models.control_tower import ControlTower


# Dock named "1" has a capacity of 3 vessels
# Dock named "2" has a capacity of 2 vessels
# ...
DOCKS_CAPACITIES = {
    "1": 3,
    "2": 2,
    "3": 1
}


class PermissionCollector(AtomicDEVS):
    """
    A simple collector the collects PortEntryPermission's
    """

    def __init__(self, name):
        super(PermissionCollector, self).__init__(name)
        self.in_port_entry_permission = self.addInPort("in_port_entry_permission")
        self.state = []

    def extTransition(self, inputs):
        assert self.in_port_entry_permission in inputs
        port_entry_permission = inputs[self.in_port_entry_permission]
        assert isinstance(port_entry_permission, PortEntryPermission)
        self.state.append(port_entry_permission)

        return self.state


class SimpleGenerator(AtomicDEVS):
    """
    Generates 8 vessels
        t=0: PortEntryRequest(vessel_uid=0)
        t=1: PortEntryRequest(vessel_uid=1)
        ...
        t=9: PortEntryRequest(vessel_uid=9)

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
        self.control_tower = self.addSubModel(ControlTower("control_tower", docks_capacities=DOCKS_CAPACITIES))
        self.permission_collector = self.addSubModel(PermissionCollector("vessel_collector"))

        self.connectPorts(self.simple_generator.out_item, self.control_tower.in_port_entry_request)
        self.connectPorts(self.control_tower.out_port_entry_permission, self.permission_collector.in_port_entry_permission)


def test():
    system = CoupledControlTower(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(10)  # Simulate more than long enough
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    permissions = system.permission_collector.state

    assert [(p.vessel_uid, p.avl_dock) for p in permissions] == [
        (0, '1'),
        (1, '1'),
        (2, '1'),

        (3, '2'),
        (4, '2'),

        (5, '3'),
    ]


if __name__ == "__main__":
    test()
