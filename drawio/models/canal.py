from pypdevs.DEVS import CoupledDEVS

from models.uni_canal import UniCanal


class Canal(CoupledDEVS):
    """
    in1   +----------------+  out1
          |     CANAL      |
    out2  +----------------+  in2
    """
    def __init__(self, name: str, distance_in_km: float):
        CoupledDEVS.__init__(self, name)

        # Receives Vessel's
        self.in1 = self.addInPort("in1")
        self.in2 = self.addInPort("in2")

        # Sends Vessel's
        self.out1 = self.addOutPort("out1")
        self.out2 = self.addOutPort("out2")

        self.uni_canal_1 = self.addSubModel(UniCanal("uni_canal_1", distance_in_km=distance_in_km))
        self.uni_canal_2 = self.addSubModel(UniCanal("uni_canal_2", distance_in_km=distance_in_km))

        # Connect the first direction
        self.connectPorts(self.in1, self.uni_canal_1.in_vessel)
        self.connectPorts(self.uni_canal_1.out_vessel, self.out1)

        # Connect the other direction
        self.connectPorts(self.in2, self.uni_canal_2.in_vessel)
        self.connectPorts(self.uni_canal_2.out_vessel, self.out2)
