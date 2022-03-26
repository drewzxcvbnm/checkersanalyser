from moveanalyser import MoveAnalyser, Side
from pyrsistent import v, pvector


def test():
    fromm = [
        [1, 0, 1, 0, 1, 0, 1, 0],  # 0
        [0, 1, 0, 1, 0, 1, 0, 1],  # 1
        [1, 0, 1, 0, 1, 0, 1, 0],  # 2
        [0, 0, 0, 0, 0, 0, 0, 0],  # 3
        [0, 0, 0, 0, 0, 0, 0, 0],  # 4
        [0, 3, 0, 3, 0, 3, 0, 3],  # 5
        [3, 0, 3, 0, 3, 0, 3, 0],
        [0, 3, 0, 3, 0, 3, 0, 3]
    ]

    to = [
        [1, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 0, 0, 0, 0, 0],
        [0, 0, 0, 3, 0, 3, 0, 3],
        [3, 0, 3, 0, 3, 0, 3, 0],
        [0, 3, 0, 3, 0, 3, 0, 3]
    ]

    m = MoveAnalyser(fromm, to)

    res = m.calculate_move_for_side(Side.BLACKES)
    print(m.calculate_move_for_side(Side.BLACKES))
    assert repr(res) == "[{(5, 1) -> (4, 2)}]"
