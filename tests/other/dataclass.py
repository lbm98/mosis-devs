from dataclasses import dataclass, field


# https://stackoverflow.com/questions/53632152/why-cant-dataclasses-have-mutable-defaults-in-their-class-attributes-declaratio


# Wrong dataclass
@dataclass
class Data1:
    lst = []

    def add(self, item):
        self.lst.append(item)


# Correct dataclass
@dataclass
class Data2:
    lst: list[int] = field(default_factory=list)

    def add(self, item):
        self.lst.append(item)


def test1():
    x1 = Data1()
    y1 = Data1()
    x1.add(1)
    y1.add(2)

    # UNEXPECTED!
    assert x1.lst == [1, 2]
    assert y1.lst == [1, 2]

    x2 = Data2()
    y2 = Data2()
    x2.add(1)
    y2.add(2)

    # EXPECTED!
    assert x2.lst == [1]
    assert y2.lst == [2]


if __name__ == "__main__":
    test1()