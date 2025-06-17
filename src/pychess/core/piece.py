from .enums import Player, PieceType, PIECE_VALUES

class Piece:
    def __init__(self, player: Player, piece_type: PieceType):
        self.player = player
        self.piece_type = piece_type
        self.value = PIECE_VALUES[piece_type]
        self.moved = False

    def copy(self) -> 'Piece':
        """Create a copy of this piece."""
        piece = Piece(self.player, self.piece_type)
        piece.moved = self.moved
        return piece
