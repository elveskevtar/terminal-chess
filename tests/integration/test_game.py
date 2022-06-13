from tests.utils import assert_piece
from pychess.game import Chess, Color
import sys

FOOLS_MATE = "tests/resources/fools_mate"


def test_fools_mate():
    sys.stdin = open(FOOLS_MATE)
    game = Chess()
    game.start()
    assert game.done
    assert game.winner == Color.BLACK
    assert_piece(game.board[4, 7], "queen", Color.BLACK)
    assert_piece(game.board[4, 6], "pawn", Color.WHITE)
    assert_piece(game.board[5, 5], "pawn", Color.WHITE)
    assert (6, 5) not in game.board
    assert_piece(game.board[7, 4], "king", Color.WHITE)
