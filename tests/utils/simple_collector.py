from pypdevs.DEVS import AtomicDEVS

from dataclasses import dataclass, field
from models.utils.my_log import my_log


@dataclass
class CollectorState:
    items: list[any] = field(default_factory=list)
    current_time: float = 0.0


class SimpleCollector(AtomicDEVS):
    """
    A simple collector the collects items
    """

    def __init__(self, name):
        super(SimpleCollector, self).__init__(name)
        self.in_item = self.addInPort("in_item")
        self.state = CollectorState()

    def extTransition(self, inputs):
        self.state.current_time += self.elapsed

        assert self.in_item in inputs
        item = inputs[self.in_item]
        item.time_in_system = self.state.current_time - item.creation_time

        # my_log(f"{item.uid},{self.state.current_time},{item.creation_time}")

        self.state.items.append(item)

        return self.state
