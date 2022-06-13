from pychess.game import Color, Piece


def assert_piece(piece: Piece, name: str, color: Color):
    assert piece.name == name
    assert piece.color == color
