from pypdevs.simulator import Simulator
from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
from pypdevs.infinity import INFINITY

from models.vessels import CrudeOilTanker, TugBoat
from models.lock import Lock

from utils.vessel_collector import VesselCollector

"""
    state   | GATE_IS_OPEN | CLOSING | WASHING | OPENING
    seconds |     5        |    4    |    7    |    4

    1 cycle = 5 + 4 + 7 + 4 = 20 seconds

    HIGH ====> LOW

    generate_high + in_vessel_high  +----------------+  in_vessel_low + generate_low
                                    |     Lock       |
    collect_high + out_vessel_high  +----------------+  out_vessel_low + collect_low

    uid | t | direction | comment
    ------------------------------
    0   | 0 |     =>    | enter lock
    1   | 1 |     =>    | enter lock
    2   | 2 |     =>    | wait, lock capacity reached (11000 + 11000 + 11000 > 30000)
    3   | 3 |     <=    | wait
    4   | 4 |     <=    | wait
    5   | 5 |     <=    | wait, but capacity will be reached later for <=
    6   | 6 |     =>    | wait
    7   | 7 |     =>    | wait, but capacity will be reached later for =>
    8   | 8 |     =>    | small vessel, does not have to wait

    with no depart delays:
        at t=20  collect 0,1   at collect_high
        at t=40  collect 3,4   at collect_low
        at t=60  collect 2,6,8 at collect_high
        at t=80  collect 5     at collect_low
        at t=100 collect 7     at collect_high

    with depart delays of 10 seconds:
        at t=20  collect 0 at collect_high
        at t=30  collect 1 at collect_high
        ...
        at t=50  collect 3 at collect_low
        at t=60  collect 4 at collect_low
        ...
        at t=80  collect 2 at collect_high
        at t=90  collect 6 at collect_high
        at t=100 collect 8 at collect_high
        ...
        at t=120 collect 5 at collect_low
        ...
        at t=140 collect 7 at collect_high
"""


class GenerateHigh(AtomicDEVS):
    """
    Generate at 0,1,2,6,7,8
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
            return 0  # at 0
        elif self.state == 1:
            return 1  # at 1
        elif self.state == 2:
            return 1  # at 2
        elif self.state == 3:
            return 4  # at 6
        elif self.state == 4:
            return 1  # at 7
        elif self.state == 5:
            return 1  # at 8
        else:
            return INFINITY

    def outputFnc(self):
        if self.state == 0:
            return {self.out_item: CrudeOilTanker(uid=0, creation_time=0)}
        elif self.state == 1:
            return {self.out_item: CrudeOilTanker(uid=1, creation_time=1)}
        elif self.state == 2:
            return {self.out_item: CrudeOilTanker(uid=2, creation_time=2)}
        elif self.state == 3:
            return {self.out_item: CrudeOilTanker(uid=6, creation_time=6)}
        elif self.state == 4:
            return {self.out_item: CrudeOilTanker(uid=7, creation_time=7)}
        elif self.state == 5:
            return {self.out_item: TugBoat(uid=8, creation_time=8)}
        else:
            assert False


class GenerateLow(AtomicDEVS):
    """
    Generate at 3,4,5
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
            return 3  # at 3
        elif self.state == 1:
            return 1  # at 4
        elif self.state == 2:
            return 1  # at 5
        else:
            return INFINITY

    def outputFnc(self):
        if self.state == 0:
            return {self.out_item: CrudeOilTanker(uid=3, creation_time=3)}
        elif self.state == 1:
            return {self.out_item: CrudeOilTanker(uid=4, creation_time=4)}
        elif self.state == 2:
            return {self.out_item: CrudeOilTanker(uid=5, creation_time=5)}
        else:
            assert False


class CoupledLock(CoupledDEVS):
    def __init__(self, name):
        CoupledDEVS.__init__(self, name)

        self.generate_high = self.addSubModel(GenerateHigh("generate_high"))
        self.generate_low = self.addSubModel(GenerateLow("generate_low"))

        self.lock = self.addSubModel(
            Lock("lock",
                 washing_duration=7,
                 lock_shift_interval=20,
                 gate_duration=4,
                 surface_area=30000,
                 time_between_departures=10
                 )
        )

        self.collect_high = self.addSubModel(VesselCollector("collect_high"))
        self.collect_low = self.addSubModel(VesselCollector("collect_low"))

        self.connectPorts(self.generate_high.out_item, self.lock.in_high)
        self.connectPorts(self.generate_low.out_item, self.lock.in_low)
        self.connectPorts(self.lock.out_high, self.collect_high.in_vessel)
        self.connectPorts(self.lock.out_low, self.collect_low.in_vessel)


def test():
    system = CoupledLock(name="system")
    sim = Simulator(system)
    sim.setTerminationTime(150)  # Simulate long enough
    # sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.simulate()

    vessels_low = system.collect_low.state.vessels
    vessels_high = system.collect_high.state.vessels

    # print([(v.uid, v.creation_time, v.time_in_system) for v in vessels_low])
    # print([(v.uid, v.creation_time, v.time_in_system) for v in vessels_high])

    assert [(v.uid, v.creation_time, v.time_in_system) for v in vessels_low] == [
        (0, 0, 20.0),
        (1, 1, 29.0),
        (2, 2, 78.0),
        (6, 6, 84.0),
        (8, 8, 92.0),
        (7, 7, 133.0)
    ]

    assert [(v.uid, v.creation_time, v.time_in_system) for v in vessels_high] == [
        (3, 3, 47.0),
        (4, 4, 56.0),
        (5, 5, 115.0)
    ]


if __name__ == "__main__":
    test()
