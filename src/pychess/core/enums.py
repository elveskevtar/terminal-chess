from enum import Enum, auto

class Player(Enum):
    WHITE = auto()
    BLACK = auto()

    def opponent(self) -> 'Player':
        return Player.BLACK if self == Player.WHITE else Player.WHITE

class PieceType(Enum):
    PAWN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    QUEEN = auto()
    KING = auto()

class MoveResult(Enum):
    """Result of a move attempt."""
    INVALID = auto()  # Move was not valid
    SUCCESS = auto()  # Move was successful but no capture
    CAPTURE = auto()  # Move was successful and captured a piece

PIECE_VALUES = {
    PieceType.PAWN: 1,
    PieceType.KNIGHT: 3,
    PieceType.BISHOP: 3,
    PieceType.ROOK: 5,
    PieceType.QUEEN: 9,
    PieceType.KING: 0
}

PIECE_SYMBOLS = {
    PieceType.PAWN: "P",
    PieceType.KNIGHT: "N",
    PieceType.BISHOP: "B",
    PieceType.ROOK: "R",
    PieceType.QUEEN: "Q",
    PieceType.KING: "K"
}

PIECE_SYMBOLS_MAP = {v: k for k, v in PIECE_SYMBOLS.items()}
