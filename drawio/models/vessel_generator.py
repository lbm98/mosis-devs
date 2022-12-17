from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from models.vessels import CrudeOilTanker, BulkCarrier


class VesselGenerator(AtomicDEVS):
    """
    Generates
        t=0:  CrudeOilTanker(uid=0)
        t=10: BulkCarrier(uid=1)
    from left to right

    The BulkCarrier should NOT overtake the CrudeOilTanker (unlike Waterway's)
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
            return 0
        elif self.state == 1:
            return 10
        else:
            return INFINITY

    def outputFnc(self):
        if self.state == 0:
            return {self.out_item: CrudeOilTanker(uid=0, creation_time=0)}
        elif self.state == 1:
            return {self.out_item: BulkCarrier(uid=1, creation_time=10)}
        else:
            assert False
