from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass, field

from models.messages import PortEntryRequest, PortEntryPermission


@dataclass
class ControlTowerState:
    # The datastructure that keeps track of the number of free spots in each dock
    docks_free_spots: dict[str, int] = field(default_factory=dict)

    # The remaining time until generation of a new event
    # We only react to external events
    # Wait INDEFINITELY for the first input
    remaining_time: float = INFINITY

    # If all docks are occupied, we enqueue the requests
    # As soon as a dock becomes available, we send a permission to the first-come request
    port_entry_requests: list[PortEntryRequest] = field(default_factory=list)

    # We need to send output, in response to input
    # This is not directly supported in DEVS
    # So, we use these variables
    stored_port_entry_permission: PortEntryPermission | None = None


class ControlTower(AtomicDEVS):
    """
    ControlTower is parameterized by docks_capacities
    This dictionary describes the names of the docks and their capacities.
    """
    def __init__(self, name, docks_capacities: dict[str, int]):
        super(ControlTower, self).__init__(name)
        self.control_tower_info = docks_capacities

        # Receives PortEntryRequest's
        self.in_port_entry_request = self.addInPort("in_port_entry_request")
        # Sends PortEntryPermission's
        self.out_port_entry_permission = self.addOutPort("out_port_entry_permission")

        # Initialize the state
        self.state = ControlTowerState(docks_free_spots=docks_capacities)

    def intTransition(self):
        # After responding to an input, wait INDEFINITELY for a new input
        self.state.remaining_time = INFINITY
        return self.state

    def extTransition(self, inputs):
        if self.in_port_entry_request in inputs:
            port_entry_request = inputs[self.in_port_entry_request]
            assert isinstance(port_entry_request, PortEntryRequest)

            # If all docks are occupied, we enqueue the requests
            # Else, use the first available dock
            if all(num_free_spots == 0 for num_free_spots in self.state.docks_free_spots.values()):
                self.state.port_entry_requests.append(port_entry_request)
            else:
                first_avl_dock = next(
                    (dock for dock in self.state.docks_free_spots if self.state.docks_free_spots[dock] != 0),
                    None
                )
                assert first_avl_dock is not None
                port_entry_permission = PortEntryPermission(
                    vessel_uid=port_entry_request.vessel_uid,
                    avl_dock=first_avl_dock
                )

                # Reserve the spot in the dock
                self.state.docks_free_spots[first_avl_dock] -= 1
                assert self.state.docks_free_spots[first_avl_dock] >= 0

                # Schedule to send a PortEntryPermission to out_port_entry_permission IMMEDIATELY
                self.state.remaining_time = 0
                self.state.stored_port_entry_permission = port_entry_permission

        # IF WE RECEIVE A RELEASE
        # CHECK IF ANY REQUESTS ARE IN THE QUEUE WAITING
        # IF SO, SERVE THE FIRST-COME REQUEST

        return self.state

    def timeAdvance(self):
        return self.state.remaining_time

    def outputFnc(self):
        assert self.state.stored_port_entry_permission is not None
        to_return = {self.out_port_entry_permission: self.state.stored_port_entry_permission}
        self.state.stored_port_entry_permission = None

        return to_return
