from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from dataclasses import dataclass

from models.vessels import Vessel
from models.messages import PortEntryRequest, PortEntryPermission


@dataclass
class AnchorPointState:
    # The remaining time until generation of a new event
    # We only react to external events
    # Wait INDEFINITELY for the first input
    remaining_time = INFINITY

    # The datastructure to queue the waiting Vessel's
    vessels = []

    # We need to send output, in response to input
    # This is not directly supported in DEVS
    # So, we use these variables
    what_to_do = ""
    stored_port_entry_request: PortEntryRequest = None
    stored_vessel: Vessel = None


class AnchorPoint(AtomicDEVS):
    def __init__(self, name):
        super(AnchorPoint, self).__init__(name)

        # Receives Vessel's
        self.in_vessel = self.addInPort("in_vessel")
        # Receives PortEntryPermission's
        self.in_port_entry_permission = self.addInPort("in_port_entry_permission")
        # Sends PortEntryRequest's
        self.out_port_entry_request = self.addOutPort("out_port_entry_request")
        # Sends Vessel's
        self.out_vessel = self.addOutPort("out_vessel")

        self.state = AnchorPointState()

    def intTransition(self):
        # After responding to an input, wait INDEFINITELY for a new input
        self.state.remaining_time = INFINITY
        return self.state

    def extTransition(self, inputs):
        if self.in_vessel in inputs:
            vessel = inputs[self.in_vessel]
            assert isinstance(vessel, Vessel)

            # Enqueue the vessel
            self.state.vessels.append(inputs[self.in_vessel])

            # Schedule to send a PortEntryRequest to out_port_entry_request IMMEDIATELY
            self.state.remaining_time = 0
            self.state.what_to_do = "send_port_entry_request"
            self.state.stored_port_entry_request = PortEntryRequest(vessel_uid=vessel.uid)

        elif self.in_port_entry_permission in inputs:
            port_entry_permission = inputs[self.in_port_entry_permission]
            assert isinstance(port_entry_permission, PortEntryPermission)

            # Schedule to send a Vessel to out_vessel IMMEDIATELY
            self.state.remaining_time = 0
            self.state.what_to_do = "send_vessel"

            # Lookup Vessel in the queue (by vessel_uid in the PortEntryPermission)
            vessel = next(
                vessel for vessel in self.state.vessels if vessel.uid == port_entry_permission.vessel_uid
            )

            # Set the destination dock
            vessel.destination_dock = port_entry_permission.avl_dock
            self.state.stored_vessel = vessel

        return self.state

    def timeAdvance(self):
        return self.state.remaining_time

    def outputFnc(self):
        if self.state.what_to_do == "send_port_entry_request":
            assert self.state.stored_port_entry_request is not None
            to_return = {self.out_port_entry_request: self.state.stored_port_entry_request}
            self.state.stored_port_entry_request = None

        elif self.state.what_to_do == "send_vessel":
            assert self.state.stored_vessel is not None
            to_return = {self.out_vessel: self.state.stored_vessel}
            self.state.stored_vessel = None
        else:
            assert False

        self.state.what_to_do = ""
        return to_return
