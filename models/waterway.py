from pypdevs.DEVS import CoupledDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass, field

from models.uni_waterway import UniWaterway
from models.vessels import Vessel


@dataclass
class WaterwayState:
    # The remaining time until generation of a new event
    # Wait INDEFINITELY for the first input event
    remaining_time: float = INFINITY

    # The list that stores the vessels in this waterway (moving from left to right)
    vessels_1: list[Vessel] = field(default_factory=list)

    # The list that stores the vessels in this waterway (moving from right to left)
    vessels_2: list[Vessel] = field(default_factory=list)

    # Is either vessels_1 or vessels_2
    next_vessel_queue: list[Vessel] = field(default_factory=list)


class Waterway(CoupledDEVS):
    """
    in1   +----------------+  out1
          |    WATERWAY    |
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

        self.uni_waterway_1 = self.addSubModel(UniWaterway("uni_waterway_1", distance_in_km=distance_in_km))
        self.uni_waterway_2 = self.addSubModel(UniWaterway("uni_waterway_2", distance_in_km=distance_in_km))

        # Connect the first direction
        self.connectPorts(self.in1, self.uni_waterway_1.in_vessel)
        self.connectPorts(self.uni_waterway_1.out_vessel, self.out1)

        # Connect the other direction
        self.connectPorts(self.in2, self.uni_waterway_2.in_vessel)
        self.connectPorts(self.uni_waterway_2.out_vessel, self.out2)

        # Initialize the state
        self.state = WaterwayState()
