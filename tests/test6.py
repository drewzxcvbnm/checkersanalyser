from moveanalyser import MoveAnalyser, Side
from pyrsistent import v, pvector


def test():
    fromm = [
        [1, 0, 0, 0, 1, 0, 1, 0],  # 0
        [0, 1, 0, 1, 0, 1, 0, 1],  # 1
        [0, 0, 0, 0, 0, 0, 1, 0],  # 2
        [0, 0, 0, 1, 0, 0, 0, 0],  # 3
        [0, 0, 0, 0, 0, 0, 0, 0],  # 4
        [0, 4, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    to = [
        [1, 0, 0, 0, 1, 0, 1, 0],  # 0
        [0, 0, 0, 0, 0, 1, 0, 1],  # 1
        [4, 0, 0, 0, 0, 0, 1, 0],  # 2
        [0, 0, 0, 0, 0, 0, 0, 0],  # 3
        [0, 0, 0, 0, 0, 0, 0, 0],  # 4
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    m = MoveAnalyser(fromm, to)
    res = m.calculate_move_for_side(Side.BLACKES)
    print(res)
    expected = "[{(5, 1) -> (2, 4) -> (0, 2) -> (2, 0)}]"
    assert repr(res) == expected
