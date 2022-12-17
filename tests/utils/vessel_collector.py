from pypdevs.DEVS import AtomicDEVS

from dataclasses import dataclass, field

from models.vessels import Vessel


@dataclass
class CollectorState:
    vessels: list[Vessel] = field(default_factory=list)
    current_time: float = 0.0


class VesselCollector(AtomicDEVS):
    """
    A simple collector the collects Vessel's
    """

    def __init__(self, name):
        super(VesselCollector, self).__init__(name)
        self.in_vessel = self.addInPort("in_vessel")
        self.state = CollectorState()

    def extTransition(self, inputs):
        self.state.current_time += self.elapsed

        assert self.in_vessel in inputs
        vessel = inputs[self.in_vessel]

        assert isinstance(vessel, Vessel)
        vessel.time_in_system = self.state.current_time - vessel.creation_time

        self.state.vessels.append(vessel)

        return self.state
