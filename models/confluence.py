from pypdevs.DEVS import AtomicDEVS, Port
from pypdevs.infinity import INFINITY

from dataclasses import dataclass, field

from models.vessels import Vessel


@dataclass
class ConfluenceState:
    # The remaining time until generation of a new event
    # Wait INDEFINITELY for the first input event
    remaining_time: float = INFINITY

    # Stores the vessels
    vessels: list[Vessel] = field(default_factory=list)

    # Stores the output port for the next vessel (FCFS)
    output_port_for_next_vessel: Port | None = None


class Confluence(AtomicDEVS):
    """
    The parameter confluence_info maps:
        port_name -> list of docks
    if the next-hop of the vessel is through port_name
    """
    def __init__(self, name: str, confluence_info: dict[str, list[str]]):
        super(Confluence, self).__init__(name)
        self.confluence_info = confluence_info

        # num IN ports = num OUT ports

        # Receives Vessel's on input ports
        self.in_vessel_ports = {}
        for port_name in self.confluence_info:
            self.in_vessel_ports[port_name] = self.addInPort(port_name)

        # Sends Vessel's on output ports
        self.out_vessel_ports = {}
        for port_name in self.confluence_info:
            self.out_vessel_ports[port_name] = self.addOutPort(port_name)

        self.state = ConfluenceState()

    def extTransition(self, inputs):
        for in_vessel_port in self.in_vessel_ports.values():
            if in_vessel_port in inputs:
                # Get the vessel
                vessel = inputs[in_vessel_port]

                # Enqueue the vessel
                self.state.vessels.append(vessel)

                # Schedule next event to run IMMEDIATELY
                self.state.remaining_time = 0

                # Figure out the output port for the next vessel
                self.set_output_port_for_next_vessel()

        return self.state

    def timeAdvance(self):
        return self.state.remaining_time

    def outputFnc(self):
        # Check precondition
        assert self.state.output_port_for_next_vessel is not None

        # Send the next vessel (FCFS)
        return {self.state.output_port_for_next_vessel: self.state.vessels[0]}

    def intTransition(self):
        # Remove the vessel we just sent
        self.state.vessels.pop(0)

        # If there are no more vessels in this confluence,
        #   wait INDEFINITELY for the next input event
        # else
        #   schedule next event to run IMMEDIATELY, and
        #   figure out the output port for the next vessel
        if len(self.state.vessels) == 0:
            self.state.remaining_time = INFINITY
        else:
            self.state.remaining_time = 0
            self.set_output_port_for_next_vessel()

        return self.state

    def set_output_port_for_next_vessel(self):
        # Assume the next vessel is the first one in the queue (due to FCFS)
        vessel = self.state.vessels[0]

        # Lookup the output port for the next-hop on the route to the vessels destination
        for port_name, docks in self.confluence_info.items():
            if vessel.destination_dock in docks:
                self.state.output_port_for_next_vessel = self.out_vessel_ports[port_name]
                break
