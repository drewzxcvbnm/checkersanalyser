from moveanalyser import MoveAnalyser, Side
from pyrsistent import v, pvector

from movemaker import deduce_best_min_max_move

from checkersanalyser.movemaker import deduce_best_complete_move


def test():
    board = [
        [0, 0, 0, 0, 0, 0, 0, 0],  # 0
        [0, 0, 0, 0, 0, 0, 0, 0],  # 1
        [0, 0, 0, 0, 0, 0, 0, 0],  # 2
        [0, 3, 0, 0, 0, 0, 0, 0],  # 3
        [0, 0, 1, 0, 0, 0, 0, 0],  # 4
        [0, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    res2 = deduce_best_min_max_move(board, Side.BLACKES)
    print(repr(res2))
    assert repr(res2) == "{(3, 1) -> (4, 0)}"
