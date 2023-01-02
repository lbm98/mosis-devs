from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS

from drawio.models.vessel_collector import VesselCollector
from drawio.models.canal import Canal
from drawio.models.vessel_generator import VesselGenerator


class CoupledSystem(CoupledDEVS):
    def __init__(self, name):
        CoupledDEVS.__init__(self, name)

        self.canal = self.addSubModel(Canal("canal", distance_in_km=19.8164))
        self.gen1 = self.addSubModel(VesselGenerator("gen1"))
        self.col2 = self.addSubModel(VesselCollector("col2"))
        self.col1 = self.addSubModel(VesselCollector("col1"))
        self.gen2 = self.addSubModel(VesselGenerator("gen2"))

        self.connectPorts(self.gen1.out_vessel, self.canal.in1)
        self.connectPorts(self.canal.out1, self.col2.in_vessel)
        self.connectPorts(self.canal.out2, self.col1.in_vessel)
        self.connectPorts(self.gen2.out_vessel, self.canal.in2)


def simulate():
    system = CoupledSystem(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(3615 + 0.01)  # Simulate just long enough
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()


if __name__ == "__main__":
    simulate()