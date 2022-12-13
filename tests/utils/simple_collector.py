from pypdevs.DEVS import AtomicDEVS


class SimpleCollector(AtomicDEVS):
    """
    A simple collector the collects items
    """
    def __init__(self, name):
        super(SimpleCollector, self).__init__(name)

        self.in_item = self.addInPort("in_item")

        # The datastructure to store the collected items
        # Acts as the state
        self.collection = []

    def extTransition(self, inputs):
        if self.in_item in inputs:
            self.collection.append(inputs[self.in_item])
        return self.collection
