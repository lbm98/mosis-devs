from dataclasses import dataclass


@dataclass
class Base:
    x: int

    # Parameters set in derived classes
    a: int
    b: int


@dataclass
class Derived(Base):
    a: int = 1
    b: int = 1


def test():
    Derived(x=1)


if __name__ == "__main__":
    test()
