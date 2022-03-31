import enum
from copy import deepcopy

from pyrsistent import v, pvector, freeze

VALID_PLACES = [(x, y) for y in range(8) for x in range(8)]


def logged(func):
    def logged_func(*args, **kwargs):
        self = args[0]
        print(f"INPUT:from: {self._meta['from']}")
        print(f"INPUT:to: {self._meta['to']}")
        print(f"INPUT:args: {args[1:]} {kwargs}")
        res = func(*args, **kwargs)
        print(f"OUTPUT: {res}")
        return res

    return logged_func


def is_out_of_bounds(pos: tuple[int, int]) -> bool:
    return pos not in VALID_PLACES


def is_free_for_occupation(pos: tuple[int, int], board: pvector(pvector([int]))) -> bool:
    if is_out_of_bounds(pos):
        return False
    return board[pos[0]][pos[1]] == 0


def norm(el: int) -> int:
    if el == 0:
        return 0
    if el > 0:
        return 1
    return -1


class Side(enum.Enum):
    WHITES = (1, 2)
    BLACKES = (3, 4)

    @staticmethod
    def deduce_side(v: int):
        return Side.BLACKES if v in Side.BLACKES.value else Side.WHITES

    def to_pawn(self, v: int) -> int:
        return Side.WHITES.value[0] if self == Side.WHITES else Side.BLACKES.value[0]

    def opposite_side(self):
        return Side.WHITES if self == Side.BLACKES else Side.BLACKES

    def last_enemy_line(self):
        if self == Side.BLACKES:
            return 7
        else:
            return 0

    def is_back_move(self, fr: tuple[int, int], to: tuple[int, int]):
        distance_to_enemy_line_before = abs(self.last_enemy_line() - fr[0])
        distance_to_enemy_line_after = abs(self.last_enemy_line() - to[0])
        return distance_to_enemy_line_after > distance_to_enemy_line_before


def has_enemy(board_value: int, side: Side) -> bool:
    return board_value in side.opposite_side().value


def has_friend(board_value: int, side: Side) -> bool:
    return board_value in side.value


def add(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]


class Piece:

    def __init__(self, i, j, side: Side, is_queen):
        self.pos = (i, j)
        self.side = side
        self.is_queen = is_queen


def get_potential_moves(p: Piece, board: pvector(pvector([int]))) -> list[tuple[int, int]]:
    i = p.pos[0]
    j = p.pos[1]
    directions = [(i - 1, j - 1), (i - 1, j + 1), (i + 1, j - 1), (i + 1, j + 1)]
    if not p.is_queen:
        return directions
    queen_moves = []
    for direction in directions:
        movement_vector = get_movement_vector(p.pos, direction)
        move = add(p.pos, movement_vector)
        while not is_out_of_bounds(move) and board[move[0]][move[1]] == 0:
            queen_moves.append(move)
            move = add(move, movement_vector)
        queen_moves.append(move)
    return queen_moves


class Move:

    def __init__(self, fr: tuple[int, int], to: tuple[int, int], is_eat_move: bool, piece: Piece):
        self.fr = fr
        self.to = to
        self.is_eat_move = is_eat_move
        self.piece = piece
        self.prev_move = None

    def __str__(self):
        return f"{self.fr} -> {self.to}"

    def __repr__(self):
        moves = get_move_chain(self)
        moves.reverse()
        res = str(moves[0].fr)
        for m in moves:
            res += " -> " + str(m.to)
        return "{" + res + "}"

    def to_list(self) -> list[tuple[int, int]]:
        moves = get_move_chain(self)
        moves.reverse()
        res = [moves[0].fr]
        for m in moves:
            res.append(m.to)
        return res


def get_move_chain(m: Move, chain=None) -> list[Move]:
    if chain is None:
        chain = []
    chain.append(m)
    if m.prev_move is None:
        return chain
    return get_move_chain(m.prev_move, chain)


def get_movement_vector(pos1: tuple[int, int], pos2: tuple[int, int]) -> tuple[int, int]:
    return norm(pos2[0] - pos1[0]), norm(pos2[1] - pos1[1])


def simplify_cell(v: int):
    if v == 0:
        return v
    return Side.deduce_side(v).to_pawn(v)


def simplified_board(board: pvector(pvector([int]))):
    sboard = []
    for row in board:
        sboard.append([simplify_cell(i) for i in row.tolist()])
    return freeze(sboard)


class MoveAnalyser:
    def __init__(self, fromm: list[list[int]], to: list[list[int]]):
        self._meta = {"from": fromm, "to": to}
        self.fromm = freeze(fromm)
        self.to = simplified_board(freeze(to))

    def _get_pieces_for_side(self, side: Side) -> list[Piece]:
        pieces = []
        for i in range(len(self.fromm)):
            for j in range(len(self.fromm)):
                if self.fromm[i][j] in side.value:
                    is_queen = self.fromm[i][j] == side.value[1]
                    pieces.append(Piece(i, j, side, is_queen))
        return pieces

    def _make_move(self, board: pvector(pvector([int])), valid_player_moves: list[Move], move: Move):
        p = board[move.fr[0]][move.fr[1]]
        board = board.set(move.fr[0], board[move.fr[0]].set(move.fr[1], 0))  # set initial place to 0
        board = board.set(move.to[0], board[move.to[0]].set(move.to[1], p))  # set target place
        if move.is_eat_move:
            move_vector = get_movement_vector(move.fr, move.to)
            eaten_piece = tuple(b - a for a, b in zip(move_vector, move.to))
            board = board.set(eaten_piece[0], board[eaten_piece[0]].set(eaten_piece[1], 0))  # set eaten place to 0

        if simplified_board(board) == self.to:
            # if board == self.to:
            valid_player_moves.append(move)
        if not move.is_eat_move:
            return
        new_piece = deepcopy(move.piece)
        if move.to[0] == move.piece.side.last_enemy_line():
            new_piece.is_queen = True
        new_piece.pos = move.to
        for next_move in filter(lambda m: m.is_eat_move, self._get_moves_for_piece(board, new_piece)):
            next_move.prev_move = move
            self._make_move(board, valid_player_moves, next_move)

    @staticmethod
    def _create_move(board: pvector(pvector([int])), fr: tuple[int, int], to: tuple[int, int], p: Piece) -> Move | None:
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

    def _get_moves_for_piece(self, board: pvector(pvector([int])), p: Piece) -> list[Move]:
        return [m for pm in get_potential_moves(p, board) if (m := self._create_move(board, p.pos, pm, p)) is not None]

    @logged
    def calculate_move_for_side(self, side: Side) -> list[Move]:
        moves: list[Move] = [m for p in self._get_pieces_for_side(side) for m in
                             self._get_moves_for_piece(self.fromm, p)]
        valid_player_moves: list[Move] = []
        for move in filter(lambda m: m.is_eat_move, moves):
            self._make_move(self.fromm, valid_player_moves, move)
        if len(valid_player_moves) != 0:
            return valid_player_moves
        for move in filter(lambda m: not m.is_eat_move, moves):
            self._make_move(self.fromm, valid_player_moves, move)
        return valid_player_moves
