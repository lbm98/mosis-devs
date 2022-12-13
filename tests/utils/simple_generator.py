from pypdevs.DEVS import AtomicDEVS


class SimpleGenerator(AtomicDEVS):
    """
    A simple generator that sends item's every n seconds
    By default every second
    Users must provide an item generator function
    """
    def __init__(self, name, item_generator, n: float = 1):
        super(SimpleGenerator, self).__init__(name)
        self.item_generator = item_generator
        self.n = n

        self.out_item = self.addOutPort("out_item")

        # Define the state
        self.count = 0

    def intTransition(self):
        self.count += 1
        return self.count

    def timeAdvance(self):
        return self.n

    def outputFnc(self):
        item = self.item_generator(self.count)
        if item is not None:
            return {self.out_item: item}
        return {}
