from copy import deepcopy
from enum import Enum, auto
from itertools import chain
from time import sleep
from types import LambdaType
from typing import Any, Dict, Generator, Iterable, Tuple


class Color(Enum):
    BLACK = auto(), '\x1b[6;30;{}m', "black"
    WHITE = auto(), '\x1b[6;37;{}m', "white"
    ENDC = auto(), '\x1b[0m', ""

    @property
    def name(self) -> str:
        return self.value[2]

    @property
    def escape_code(self) -> str:
        return self.value[1]

    def __str__(self):
        return self.escape_code

    def __deepcopy__(self, memo):
        return self


class Piece:
    def __init__(self, color: Color, pos: Tuple[int, int]):
        self.color = color
        self.pos = pos
        self.name = "piece"
        self.short_name = "na"
        self.moved = False

    def describe(self) -> str:
        return self.color.name + " " + self.name + " " + coord_to_square(self.pos)

    def __str__(self):
        return str(self.color) + self.short_name


class Pawn(Piece):
    def __init__(self, color: Color, pos: Tuple[int, int]):
        super().__init__(color, pos)
        self.name = "pawn"
        self.short_name = "P"
        self.just_moved_two_squares = 0


class King(Piece):
    def __init__(self, color: Color, pos: Tuple[int, int]):
        super().__init__(color, pos)
        self.name = "king"
        self.short_name = "K"


class Queen(Piece):
    def __init__(self, color: Color, pos: Tuple[int, int]):
        super().__init__(color, pos)
        self.name = "queen"
        self.short_name = "Q"


class Rook(Piece):
    def __init__(self, color: Color, pos: Tuple[int, int]):
        super().__init__(color, pos)
        self.name = "rook"
        self.short_name = "R"


class Bishop(Piece):
    def __init__(self, color: Color, pos: Tuple[int, int]):
        super().__init__(color, pos)
        self.name = "bishop"
        self.short_name = "B"


class Knight(Piece):
    def __init__(self, color: Color, pos: Tuple[int, int]):
        super().__init__(color, pos)
        self.name = "knight"
        self.short_name = "N"


def create_board() -> Dict[Tuple[int, int], Piece]:
    board = {
        **dict(zip([(0, 4), (7, 4)], [(King, color) for color in [Color.BLACK, Color.WHITE]])),
        **dict(zip([(0, 3), (7, 3)], [(Queen, color) for color in [Color.BLACK, Color.WHITE]])),
        **dict(zip([(0, 0), (7, 0)], [(Rook, color) for color in [Color.BLACK, Color.WHITE]])),
        **dict(zip([(0, 7), (7, 7)], [(Rook, color) for color in [Color.BLACK, Color.WHITE]])),
        **dict(zip([(0, 1), (7, 1)], [(Knight, color) for color in [Color.BLACK, Color.WHITE]])),
        **dict(zip([(0, 6), (7, 6)], [(Knight, color) for color in [Color.BLACK, Color.WHITE]])),
        **dict(zip([(0, 2), (7, 2)], [(Bishop, color) for color in [Color.BLACK, Color.WHITE]])),
        **dict(zip([(0, 5), (7, 5)], [(Bishop, color) for color in [Color.BLACK, Color.WHITE]])),
        **dict(zip([(1, x) for x in range(8)], [(Pawn, Color.BLACK) for _ in range(8)])),
        **dict(zip([(6, x) for x in range(8)], [(Pawn, Color.WHITE) for _ in range(8)])),
    }
    for pos in board.keys():
        board[pos] = board[pos][0](board[pos][1], pos)
    return board


def clear_console():
    print("\033c")


def square_to_coord(square: str) -> tuple:
    return 8 - int(square[1]), ord(square[0]) - ord("a")


def coord_to_square(coord: Tuple) -> str:
    return chr(coord[1] + ord("a")) + str(-coord[0] + 8)


def add_coords(coord1: Tuple, coord2: Tuple) -> Tuple:
    return coord1[0] + coord2[0], coord1[1] + coord2[1]


def mult_coord(coord: Tuple, mult: int) -> Tuple:
    return coord[0] * mult, coord[1] * mult


def parse_fail(move: str) -> Tuple:
    return False, "invalid move: " + move


def parse_success(msg: str, start_coord: Tuple, dest_coord: Tuple,
                  promote_func=None, check=False, checkmate=False) -> Tuple:
    return True, msg, start_coord, dest_coord, promote_func, check, checkmate


def success_message(moving_piece: Piece, dest: str, capture: Piece = None) -> str:
    if capture is not None and capture.pos != square_to_coord(dest):
        return moving_piece.describe() + " captures " + capture.describe() + " en passant"
    elif capture is not None:
        return moving_piece.describe() + " captures " + capture.describe()
    return moving_piece.describe() + " moves to " + dest


def valid_coord(coord: tuple) -> bool:
    return 0 <= coord[0] and coord[0] <= 7 and 0 <= coord[1] and coord[1] <= 7


def valid_square(square: str) -> bool:
    return not (len(square) != 2 or square[0] not in "abcdefgh"
                or not square[1].isnumeric() or int(square[1]) == 0 or int(square[1]) > 8)


def valid_piece(piece: str) -> bool:
    return not (len(piece) != 1 or piece not in "KQBRN")


def valid_promoting_piece(piece: str) -> bool:
    return not (len(piece) != 1 or piece not in "QBRN")


def opposite_color(color: Color) -> Color:
    return Color.BLACK if color == Color.WHITE else Color.WHITE


def filter_chain(iterable: Iterable, *filters: LambdaType) -> Iterable:
    for filter_func in filters:
        iterable = filter(filter_func, iterable)
    return iterable


piece_map = {
    "K": {
        "create_func": King,
        "scan_args": {
            "piece_class": "king",
            "deltas": [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
            "extended": False,
        },
    },
    "Q": {
        "create_func": Queen,
        "scan_args": {
            "piece_class": "queen",
            "deltas": [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1)],
            "extended": True,
        },
    },
    "B": {
        "create_func": Bishop,
        "scan_args": {
            "piece_class": "bishop",
            "deltas": [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            "extended": True,
        },
    },
    "R": {
        "create_func": Rook,
        "scan_args": {
            "piece_class": "rook",
            "deltas": [(-1, 0), (0, -1), (1, 0), (0, 1)],
            "extended": True,
        },
    },
    "N": {
        "create_func": Knight,
        "scan_args": {
            "piece_class": "knight",
            "deltas": [(-1, -2), (1, -2), (-1, 2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1)],
            "extended": False,
        },
    }
}


class Chess:
    def __init__(self):
        self.captures = {color: [] for color in [Color.WHITE, Color.BLACK]}
        self.kings = {color: None for color in [Color.WHITE, Color.BLACK]}
        self.move_generator = PotentialMoveGenerator(self)
        self.board = create_board()
        self.populate_kings()
        self.winner = None
        self.done = False
        self.turn = 1

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def populate_kings(self):
        for piece in self.board.values():
            if piece.name == "king":
                self.kings[piece.color] = piece

    def player_turn(self) -> int:
        return self.turn % 2

    def get_player_dir(self) -> int:
        return int((self.player_turn() - 0.5) * -2)

    def player_color(self) -> Color:
        return Color.WHITE if self.player_turn() else Color.BLACK

    def opponent_color(self) -> Color:
        return Color.BLACK if self.player_turn() else Color.WHITE

    def piece_exists(self, coord: tuple, piece_class=None,
                     piece_color=None, specific_rank=None, specific_file=None) -> bool:
        return coord in self.board \
            and (specific_rank is None or coord[0] == specific_rank) \
            and (specific_file is None or coord[1] == specific_file) \
            and (piece_class is None or self.board[coord].name == piece_class) \
            and (piece_color is None or self.board[coord].color == piece_color)

    def is_check(self, king_color: Color) -> bool:
        move_generator = self.move_generator.get_moves(opposite_color(king_color), skip_check=True)
        for move in move_generator:
            if move[1] != self.kings[king_color].pos:
                continue
            return True
        return False

    def is_checkmate(self, king_color: Color) -> bool:
        if not self.is_check(king_color):
            return False
        try:
            next(self.move_generator.get_moves(king_color))
        except StopIteration:
            return True
        return False

    def start(self, sleep_time: float = 0):
        msg = ""
        while not self.done:
            print_game(self, msg)
            move = input(" {} move: ".format("White" if self.player_turn() else "Black"))
            result = self.parse_move(move)
            msg = result[1]
            if result[0]:
                if result[6]:
                    msg = "(checkmate) " + msg
                    self.done, self.winner = True, self.player_color()
                elif result[5]:
                    msg = "(check) " + msg
                self.move(*result[2:5])
            sleep(sleep_time)
        print_game(self, msg)

    def move(self, start_coord: Tuple, end_coord: Tuple, promote_func=None):
        if end_coord in self.board:
            self.captures[self.player_color()].append(self.board[end_coord])
        elif self.board[start_coord].name == "pawn" and start_coord[1] != end_coord[1]:
            delta = (self.player_turn() - 0.5) * 2
            capture_coord = add_coords(end_coord, (delta, 0))
            self.captures[self.player_color()].append(self.board.pop(capture_coord))
        self.board[end_coord] = self.board[start_coord]
        self.board[end_coord].pos = end_coord
        self.board[end_coord].moved = True
        self.board.pop(start_coord)

        if promote_func is not None:
            self.board[end_coord] = promote_func(self.player_color(), end_coord)
        if self.board[end_coord].name == "pawn" and abs(end_coord[0] - start_coord[0]) == 2:
            self.board[end_coord].just_moved_two_squares = self.turn
        if self.board[end_coord].name == "king" and abs(end_coord[1] - start_coord[1]) == 2:
            if end_coord[1] - start_coord[1] < 0:
                rook_pos = add_coords(end_coord, (0, -2))
                self.board[add_coords(end_coord, (0, 1))] = self.board[rook_pos]
                self.board.pop(rook_pos)
            else:
                rook_pos = add_coords(end_coord, (0, 1))
                self.board[add_coords(end_coord, (0, -1))] = self.board[rook_pos]
                self.board.pop(rook_pos)
        self.turn += 1

    def parse_move(self, move: str) -> Tuple:
        if len(move) < 2:
            return parse_fail(move)
        original_move = move
        move = move.strip()

        move_generator = self.move_generator.get_moves(self.player_color())
        color_filter = lambda move: self.board[move[0]].color == self.player_color()
        piece_filter = lambda move: self.board[move[0]].name == "king"
        dest_filter = lambda move: move[0][0] == move[1][0] and abs(move[0][1] - move[1][1]) == 2
        if move == "O-O-O":
            dir_filter = lambda move: move[0][1] > move[1][1]
            potential_moves = list(filter_chain(
                move_generator, dest_filter, piece_filter, color_filter, dir_filter))
            if len(potential_moves) == 1:
                return parse_success("queenside castle", *potential_moves[0])
            return False, "invalid queenside castle"
        if move == "O-O":
            dir_filter = lambda move: move[0][1] < move[1][1]
            potential_moves = list(filter_chain(
                move_generator, dest_filter, piece_filter, color_filter, dir_filter))
            if len(potential_moves) == 1:
                return parse_success("kingside castle", *potential_moves[0])
            return False, "invalid kingside castle"

        success_args = {"promote_func": None, "check": False, "checkmate": False}
        if move[-1:] == "+":
            success_args["check"], move = True, move[:-1]
        elif move[-1:] == "#":
            success_args["checkmate"], move = True, move[:-1]

        if move[-2:-1] == "=":
            if not valid_promoting_piece(move[-1:]):
                return False, "invalid promoting piece: " + move[-1:]
            success_args["promote_func"] = piece_map[move[-1:]]["create_func"]
            move = move[:-2]

        dest = move[-2:]
        move = move[:-2]
        if not valid_square(dest):
            return False, "invalid destination: " + dest
        dest_coord = square_to_coord(dest)

        moving_piece, capture = None, None
        if len(move) > 0 and move[0].isupper() and not valid_piece(move[0]):
            return False, "invalid piece: " + move[0]
        elif len(move) > 0 and valid_piece(move[0]):
            moving_piece = move[0]
            move = move[1:]

        if moving_piece is not None and success_args["promote_func"] is not None:
            return False, "trying to promote not a pawn? that's not allowed!"
        if moving_piece is None:
            promoting_rank = 0 if self.player_color() == Color.WHITE else 7
            if success_args["promote_func"] is None and dest_coord[0] == promoting_rank:
                return False, "use pawn promotion notation"
            if success_args["promote_func"] is not None and dest_coord[0] != promoting_rank:
                return False, "pawn must reach other side to promote"

        if self.piece_exists(dest_coord, piece_color=self.opponent_color()):
            capture = self.board[dest_coord]
        if moving_piece is None and not self.piece_exists(dest_coord):
            delta = (self.player_turn() - 0.5) * 2
            capture_look = add_coords(dest_coord, (delta, 0))
            if self.piece_exists(
                    capture_look, piece_class="pawn", piece_color=self.opponent_color()) \
                    and self.board[capture_look].just_moved_two_squares == self.turn - 1:
                capture = self.board[capture_look]
        if move[-1:] == "x":
            move = move[:-1]
            if capture is None:
                return parse_fail(original_move)
        elif capture is not None:
            return False, "use capture notation"

        specific_rank, specific_file = None, None
        if len(move) > 2:
            return parse_fail(original_move)
        if len(move) == 1 and valid_square(move[0] + "1"):
            specific_file = square_to_coord(move[0] + "1")[1]
        elif len(move) == 1 and valid_square("a" + move[0]):
            specific_rank = square_to_coord("a" + move[0])[0]
        elif len(move) == 1:
            return parse_fail(original_move)
        if len(move) == 2 and valid_square(move):
            start_coord = square_to_coord(move)
            specific_rank, specific_file = start_coord
        elif len(move) == 2:
            return parse_fail(original_move)

        rank_filter = lambda move: specific_rank is None or specific_rank == move[0][0]
        file_filter = lambda move: specific_file is None or specific_file == move[0][1]
        color_filter = lambda move: self.board[move[0]].color == self.player_color()
        piece_filter = lambda move: self.board[move[0]].name == "pawn"
        dest_filter = lambda move: move[1] == dest_coord
        if moving_piece is not None:
            piece_class: str = piece_map[moving_piece]["scan_args"]["piece_class"]
            piece_filter = lambda move: self.board[move[0]].name == piece_class
        potential_moves = list(filter_chain(
            move_generator, dest_filter, piece_filter, color_filter, rank_filter, file_filter))
        if len(potential_moves) > 1:
            return False, "ambiguous move, must specify distinguishing rank and/or file"
        if len(potential_moves) == 1:
            square = potential_moves[0][0]
            success = parse_success(success_message(self.board[square], dest, capture),
                                    square, dest_coord, **success_args)
            copy = deepcopy(self)
            copy.move(*success[2:5])
            is_checkmate = copy.is_checkmate(self.opponent_color())
            is_check = copy.is_check(self.opponent_color())
            if not success[6] and is_checkmate:
                return False, "use checkmate notation"
            if not success[5] and is_check and not is_checkmate:
                return False, "use check notation"
            if success[5] and not is_check:
                return False, "not check"
            if success[6] and not is_checkmate:
                return False, "not checkmate"
            return success
        return parse_fail(original_move)


def print_game(game: Chess, msg: str):
    clear_console()
    print_board(game)
    print(" " + msg)


def print_captures(game: Chess, color: Color, rank: int):
    columns = 2
    rank_str = " "
    for col in range(columns):
        tile_color = (rank + col) % 2 * (44 - 42) + 42
        if len(game.captures[color]) > rank + (8 * col):
            rank_str += str(game.captures[color][rank + (8 * col)]).format(tile_color)
        else:
            rank_str += str(Color.BLACK).format(tile_color) + " "
        rank_str += " " + str(Color.ENDC)
    print(rank_str, end="")


def print_board(game: Chess):
    print(" caps\t  a b c d e f g h \t caps")
    for rank in range(8):
        print_captures(game, Color.WHITE, rank)
        rank_str = "\t  "
        for file in range(8):
            tile_color = (rank + file) % 2 * (44 - 42) + 42
            if (rank, file) in game.board:
                rank_str += str(game.board[rank, file]).format(tile_color)
            else:
                rank_str += str(Color.BLACK).format(tile_color) + " "
            rank_str += " " + str(Color.ENDC)
        rank_str += " {}\t".format(str(8 - rank))
        print(rank_str, end="")
        print_captures(game, Color.BLACK, rank)
        print()
    print()


class PotentialMoveGenerator:
    def __init__(self, game: Chess):
        self.game = game

    def _scan_deltas(self, coord: Tuple[int, int], scan_args: Dict[str, Any],
                     piece_exists_args: Dict[str, Any] = {}, find_empty: bool = True) -> Generator:
        for delta in scan_args["deltas"]:
            mult = 1
            while True:
                current_look = add_coords(coord, mult_coord(delta, mult))
                if valid_coord(current_look) and \
                        (find_empty and not self.game.piece_exists(current_look)
                         or self.game.piece_exists(current_look, **piece_exists_args)):
                    yield coord, current_look
                if not scan_args["extended"] \
                        or not valid_coord(current_look) or self.game.piece_exists(current_look):
                    break
                mult += 1

    def _get_castling_moves(self, coord: Tuple[int, int], player_color: Color) -> Generator:
        if not self.game.board[coord].moved:
            kingside, queenside = True, True
            rook_pos = add_coords(coord, (0, -4))
            if self.game.piece_exists(rook_pos, piece_class="rook", piece_color=player_color) \
                    and not self.game.board[rook_pos].moved:
                for file_delta in range(-1, -4, -1):
                    if self.game.piece_exists(add_coords(coord, (0, file_delta))):
                        queenside = False
                        break
                if queenside and not self._is_self_check(player_color, coord, add_coords(coord, (0, -1))):
                    yield coord, add_coords(coord, (0, -2))
            rook_pos = add_coords(coord, (0, 3))
            if self.game.piece_exists(rook_pos, piece_class="rook", piece_color=player_color) \
                    and not self.game.board[rook_pos].moved:
                for file_delta in range(1, 3):
                    if self.game.piece_exists(add_coords(coord, (0, file_delta))):
                        kingside = False
                        break
                if kingside and not self._is_self_check(player_color, coord, add_coords(coord, (0, 1))):
                    yield coord, add_coords(coord, (0, 2))

    def _get_moves_pawn(self, coord: Tuple[int, int], opponent_color: Color) -> Generator:
        delta = self.game.get_player_dir()
        first_look = add_coords(coord, (delta, 0))
        second_look = add_coords(coord, (delta * 2, 0))
        if not self.game.piece_exists(first_look):
            yield coord, first_look
            if not self.game.board[coord].moved and not self.game.piece_exists(second_look):
                yield coord, second_look
        capture_looks = [add_coords(coord, (delta, file_delta)) for file_delta in [-1, 1]]
        for capture_look in capture_looks:
            if self.game.piece_exists(capture_look):
                yield coord, capture_look
            elif not self.game.piece_exists(capture_look):
                en_passant_look = add_coords(capture_look, (-delta, 0))
                if self.game.piece_exists(en_passant_look, piece_class="pawn", piece_color=opponent_color) \
                        and self.game.board[en_passant_look].just_moved_two_squares == self.game.turn - 1:
                    yield coord, capture_look

    def _get_moves(self, coord: Tuple[int, int], player_color: Color, find_empty: bool = True) -> Generator:
        opponent_color = opposite_color(player_color)
        if self.game.board[coord].short_name in piece_map:
            scan_args = piece_map[self.game.board[coord].short_name]["scan_args"]
            move_generator = self._scan_deltas(coord, scan_args, {"piece_color": opponent_color}, find_empty)
            if self.game.board[coord].name == "king":
                move_generator = chain(move_generator, self._get_castling_moves(coord, player_color))
        else:
            move_generator = self._get_moves_pawn(coord, opponent_color)
        for move in move_generator:
            yield move

    def _is_self_check(self, player_color: Color,
                       start_coord: Tuple[int, int], end_coord: Tuple[int, int]) -> bool:
        game_copy = deepcopy(self.game)
        game_copy.move(start_coord, end_coord)
        return game_copy.is_check(player_color)

    def get_moves(self, player_color: Color, skip_check: bool = False,
                  start_coord: Tuple[int, int] = None) -> Generator[Tuple[int, int], None, None]:
        match_color = lambda coord: self.game.board[coord].color == player_color
        match_pos = lambda coord: True if start_coord is None else coord == start_coord
        for coord in filter_chain(self.game.board.keys(), match_pos, match_color):
            for move in self._get_moves(coord, player_color):
                if skip_check or not self._is_self_check(player_color, *move):
                    yield move
