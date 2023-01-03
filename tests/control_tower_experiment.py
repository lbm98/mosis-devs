from pypdevs.simulator import Simulator
from pypdevs.infinity import INFINITY
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS

from models.messages import PortEntryRequest, PortEntryPermission, PortDepartureRequest
from models.control_tower import ControlTower

from dataclasses import dataclass, field


# Dock named "1" has a capacity of 3 vessels
# Dock named "2" has a capacity of 2 vessels
# ...
DOCKS_CAPACITIES = {
    "1": 3,
    "2": 2,
    "3": 1
}


@dataclass
class CollectorState:
    permissions: list[PortEntryPermission] = field(default_factory=list)
    current_time: float = 0.0

class PermissionCollector(AtomicDEVS):
    """
    A simple collector the collects PortEntryPermission's
    """

    def __init__(self, name):
        super(PermissionCollector, self).__init__(name)
        self.in_port_entry_permission = self.addInPort("in_port_entry_permission")
        self.state = CollectorState()

    def extTransition(self, inputs):
        self.state.current_time += self.elapsed

        assert self.in_port_entry_permission in inputs
        port_entry_permission = inputs[self.in_port_entry_permission]
        assert isinstance(port_entry_permission, PortEntryPermission)

        # Decorate with arrival-time
        port_entry_permission.arrival_time = self.state.current_time

        self.state.permissions.append(port_entry_permission)

        return self.state


class EntryRequestGenerator(AtomicDEVS):
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


class DepartRequestGeneratorDock1(AtomicDEVS):
    """
    Generates DepartRequest's for Dock named "1"
        t=10: PortDepartureRequest(dock="1")
        t=12: PortDepartureRequest(dock="1")
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
            return 10
        elif self.state == 1:
            return 2
        else:
            return INFINITY

    def outputFnc(self):
        if self.state == 0:
            return {self.out_item: PortDepartureRequest(dock="1")}
        elif self.state == 1:
            return {self.out_item: PortDepartureRequest(dock="1")}
        else:
            assert False


class DepartRequestGeneratorDock2(AtomicDEVS):
    """
    Generates DepartRequest's for Dock named "2"
        t=11: PortDepartureRequest(dock="2")
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
            return 11
        else:
            return INFINITY

    def outputFnc(self):
        if self.state == 0:
            return {self.out_item: PortDepartureRequest(dock="2")}
        else:
            assert False


class CoupledControlTower(CoupledDEVS):
    def __init__(self, name):
        super(CoupledControlTower, self).__init__(name)

        self.entry_request_generator = self.addSubModel(EntryRequestGenerator("entry_request_generator"))
        self.depart_request_generator_1 = self.addSubModel(DepartRequestGeneratorDock1("depart_request_generator_1"))
        self.depart_request_generator_2 = self.addSubModel(DepartRequestGeneratorDock2("depart_request_generator_2"))
        self.control_tower = self.addSubModel(ControlTower("control_tower", docks_capacities=DOCKS_CAPACITIES))
        self.permission_collector = self.addSubModel(PermissionCollector("permission_collector"))

        self.connectPorts(self.entry_request_generator.out_item, self.control_tower.in_port_entry_request)
        self.connectPorts(self.depart_request_generator_1.out_item, self.control_tower.in_port_depart_request)
        self.connectPorts(self.depart_request_generator_2.out_item, self.control_tower.in_port_depart_request)
        self.connectPorts(self.control_tower.out_port_entry_permission, self.permission_collector.in_port_entry_permission)


def test():
    system = CoupledControlTower(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(20)  # Simulate more than long enough
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    permissions = system.permission_collector.state.permissions

    # print([(p.vessel_uid, p.avl_dock, p.arrival_time) for p in permissions])

    assert [(p.vessel_uid, p.avl_dock, p.arrival_time) for p in permissions] == [
        (0, '1', 0),
        (1, '1', 1),
        (2, '1', 2),
        (3, '2', 3),
        (4, '2', 4),
        (5, '3', 5),

        (6, '1', 10),
        (7, '2', 11),
        (8, '1', 12)
    ]


if __name__ == "__main__":
    test()
