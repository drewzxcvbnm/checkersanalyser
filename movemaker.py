from copy import deepcopy
from typing import Optional

from pyrsistent import freeze, pvector

from checkersanalyser.common import Move, Side, get_move_chain, Piece, is_out_of_bounds, has_friend, has_enemy, \
    get_movement_vector, add, \
    is_free_for_occupation, flatlist, set_board
from moveanalyser import get_potential_moves

Board = list[list[int]]


def _get_pieces_for_side(board, side: Side) -> list[Piece]:
    pieces = []
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] in side.value:
                is_queen = board[i][j] == side.value[1]
                pieces.append(Piece(i, j, side, is_queen))
    return pieces


def _create_move(board: pvector(pvector([int])), fr: tuple[int, int], to: tuple[int, int], p: Piece) -> Optional[Move]:
    is_eat_move = False
    if is_out_of_bounds(to) or has_friend(board[to[0]][to[1]], p.side):
        return None
    cell = board[to[0]][to[1]]
    if not p.is_queen and p.side.is_back_move(fr, to) and not has_enemy(cell, p.side):
        return None
    if has_enemy(cell, p.side):
        move_vector = get_movement_vector(fr, to)
        to = add(move_vector, to)
        is_eat_move = True
    if not is_free_for_occupation(to, board):
        return None
    return Move(fr, to, is_eat_move, p)


def _get_moves_for_piece(board: Board, p: Piece) -> list[Move]:
    return [m for pm in get_potential_moves(p, board) if (m := _create_move(board, p.pos, pm, p)) is not None]


def execute_move(board: Board, move: list[tuple[int, int]], side: Side) -> Board:
    piece = board[move[0][0]][move[0][1]]
    pos = (move[0][0], move[0][1])
    for m in move[1:]:
        move_vector = get_movement_vector(pos, m)
        eaten_place = (m[0] - move_vector[0], m[1] - move_vector[1])
        if side.is_enemy(board[eaten_place[0]][eaten_place[1]]):
            board = set_board(board, eaten_place, 0)
        pos = m
    if any(map(lambda x: x[0] == side.last_enemy_line(), move)) and piece in (1, 3):
        piece += 1
    board = set_board(board, move[0], 0)
    return set_board(board, move[-1], piece)


def get_obligatory_moves(moves: list[Move]):
    return [i for i in moves if i.is_eat_move]


def _get_eat_moves_for_piece(p: Piece, b: Board):
    return [m for m in _get_moves_for_piece(b, p) if m.is_eat_move]


def get_non_obligatory_moves(moves: list[Move]):
    return [i for i in moves if not i.is_eat_move]


def complete_move(m: Move, b: Board) -> [Move]:
    s = m.piece.side
    v = b[m.fr[0]][m.fr[1]]
    if s.last_enemy_line() == m.to[0]:
        v = s.to_queen(v)
        m.piece.is_queen = True
    b = set_board(b, m.fr, 0)
    b = set_board(b, m.to, v)
    m.piece.pos = m.to
    if m.is_eat_move:
        move_vector = get_movement_vector(m.fr, m.to)
        eaten_piece = tuple(b1 - a1 for a1, b1 in zip(move_vector, m.to))
        b = b.set(eaten_piece[0], b[eaten_piece[0]].set(eaten_piece[1], 0))  # set eaten place to 0
    if not m.is_eat_move:
        return [m]
    new_piece = deepcopy(m.piece)
    if m.to[0] == m.piece.side.last_enemy_line():
        new_piece.is_queen = True
    new_piece.pos = m.to
    next_moves = _get_eat_moves_for_piece(new_piece, b)
    if len(next_moves) == 0:
        return [m]
    res = []
    for next_move in next_moves:
        next_move.prev_move = m
        [res.append(i) for i in complete_move(next_move, b)]
    return res


def _get_complete_player_moves(board: Board, moving_side: Side) -> list[Move]:
    start_moves = [m for p in _get_pieces_for_side(board, moving_side) for m in _get_moves_for_piece(board, p)]
    obl_moves = get_obligatory_moves(start_moves)
    if len(obl_moves) == 0:
        return start_moves
    return [cm for m in obl_moves for cm in complete_move(m, board)]


def _get_winning_side(b: Board) -> Optional[Side]:
    found_sides = set()
    for row in b:
        for cell in row:
            if cell == 0:
                continue
            if cell in Side.WHITES.value:
                found_sides.add(Side.WHITES)
            if cell in Side.BLACKES.value:
                found_sides.add(Side.BLACKES)
    if Side.WHITES in found_sides and Side.BLACKES in found_sides:
        return None
    if Side.WHITES in found_sides:
        return Side.WHITES
    else:
        return Side.BLACKES


def simulate_game(board: Board, moving_side: Side, prev_move: Move = None, depth: int = 0) -> list[tuple[Move, Board]]:
    if _get_winning_side(board) is not None:
        return [(prev_move, board)]
    if depth >= 5:
        return [(prev_move, board)]
    moves = _get_complete_player_moves(board, moving_side)
    res = []
    for m in moves:
        new_board = execute_move(board, m.to_list(), moving_side)
        if prev_move is not None:
            m.prev_move = prev_move
        [res.append(i) for i in simulate_game(new_board, moving_side.opposite_side(), m, depth + 1)]
    return res


def calculate_board_score(board: pvector(pvector([int])), side: Side) -> int:
    s1 = len(_get_pieces_for_side(board, side))
    s2 = len(_get_pieces_for_side(board, side.opposite_side()))
    return s1 - s2


def _get_tree_leaves(board: pvector(pvector([int])), side: Side) -> list[tuple[Move, int]]:
    res = [i for i in simulate_game(board, side)]
    leaves = [(i[0], calculate_board_score(i[1], side)) for i in res]
    return leaves


def deduce_best_move(board: list[list[int]], side: Side) -> Move:
    board = freeze(board)
    leaves = _get_tree_leaves(board, side)
    m = max(leaves, key=lambda x: x[1])[0]
    chain = get_move_chain(m)
    chain.reverse()
    return chain[0]
