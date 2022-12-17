class Data1:
    lst = []


class Data2:
    def __init__(self):
        self.lst = []


def test1():
    x = Data1()
    y = Data1()
    x.lst.append(1)
    # UNEXPECTED!
    assert y.lst == [1]


def test2():
    x = Data2()
    y = Data2()
    x.lst.append(1)
    # EXPECTED!
    assert y.lst == []


if __name__ == "__main__":
    test1()
    test2()
