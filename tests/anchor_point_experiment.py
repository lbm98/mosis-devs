from pypdevs.simulator import Simulator
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS

from models.vessels import CrudeOilTanker
from models.anchor_point import AnchorPoint
from models.control_tower import ControlTower


# A simple generator that sends Vessel's every second
class SimpleGenerator(AtomicDEVS):
    def __init__(self, name):
        super(SimpleGenerator, self).__init__(name)

        # Sends PortEntryRequest's
        self.out_vessel = self.addOutPort("out_vessel")

        # Define the state
        self.count = 0

    def intTransition(self):
        self.count += 1
        return self.count

    def timeAdvance(self):
        return 1.0

    def outputFnc(self):
        vessel = CrudeOilTanker(
            uid=self.count
        )
        return {self.out_vessel: vessel}


# A simple collector that receives Vessel's from AnchorPoint
class SimpleCollector(AtomicDEVS):
    def __init__(self, name):
        super(SimpleCollector, self).__init__(name)

        # Receives Vessel's
        self.in_vessel = self.addInPort("in_vessel")

        # Collects Vessel's
        # Acts as the state
        self.vessels = []

    def extTransition(self, inputs):
        if self.in_vessel in inputs:
            vessel = inputs[self.in_vessel]
            self.vessels.append(vessel)
        return self.vessels


class CoupledAnchorPoint(CoupledDEVS):
    def __init__(self, name):
        super(CoupledAnchorPoint, self).__init__(name)

        self.simple_generator = self.addSubModel(SimpleGenerator("simple_generator"))
        self.anchor_point = self.addSubModel(AnchorPoint("anchor_point"))
        self.control_tower = self.addSubModel(ControlTower("control_tower"))
        self.simple_collector = self.addSubModel(SimpleCollector("simple_collector"))

        self.connectPorts(self.simple_generator.out_vessel, self.anchor_point.in_vessel)
        self.connectPorts(self.anchor_point.out_port_entry_request, self.control_tower.in_port_entry_request)
        self.connectPorts(self.control_tower.out_port_entry_permission, self.anchor_point.in_port_entry_permission)
        self.connectPorts(self.anchor_point.out_vessel, self.simple_collector.in_vessel)


def test_anchor_point():
    system = CoupledAnchorPoint(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(10)
    sim.setVerbose(None)
    sim.setClassicDEVS()

    sim.simulate()

    result = system.simple_collector.vessels
    print(result)

    assert result[0].uid == 0 and result[0].destination_dock == '1'
    assert result[1].uid == 1 and result[1].destination_dock == '2'
    assert result[2].uid == 2 and result[2].destination_dock == '3'
    assert result[3].uid == 3 and result[3].destination_dock == '4'
    assert len(result) == 8


if __name__ == "__main__":
    test_anchor_point()
