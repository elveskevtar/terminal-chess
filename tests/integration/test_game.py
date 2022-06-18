from tests.utils import assert_piece
from pychess.game import Chess, Color
import sys

TEST_RESOURCES = "tests/resources/"
FOOLS_MATE = TEST_RESOURCES + "fools_mate"
BYRNE_FISCHER_NEW_YORK_1956 = TEST_RESOURCES + "byrne_fischer_new_york_1956"


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


def test_byrne_fischer_new_york_1956():
    sys.stdin = open(BYRNE_FISCHER_NEW_YORK_1956)
    game = Chess()
    game.start()
    assert game.done
    assert game.winner == Color.BLACK
    assert game.turn == 83
