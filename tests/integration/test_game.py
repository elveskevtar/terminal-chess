import pytest

from tests.utils import assert_piece
from pychess.game import Chess, Color
import sys

TEST_RESOURCES = "tests/resources"
FOOLS_MATE = f"{TEST_RESOURCES}/fools_mate"
BYRNE_FISCHER_NEW_YORK_1956 = f"{TEST_RESOURCES}/byrne_fischer_new_york_1956"
QUEENSIDE_CASTLING = f"{TEST_RESOURCES}/queenside_castling"
KINGSIDE_CASTLING = f"{TEST_RESOURCES}/kingside_castling"


@pytest.fixture
def chess_game(file_path):
    """Start game and yield object."""
    sys.stdin = open(file_path)
    game = Chess()
    try:
        game.start()
    except EOFError:
        # ignore EOFError since game is not always finished
        pass
    yield game


class TestChessLogic:
    """Testing the logic of the game."""

    @pytest.mark.parametrize("file_path", [FOOLS_MATE])
    def test_fools_mate(self, chess_game):
        assert chess_game.done
        assert chess_game.winner == Color.BLACK
        assert_piece(chess_game.board[4, 7], "queen", Color.BLACK)
        assert_piece(chess_game.board[4, 6], "pawn", Color.WHITE)
        assert_piece(chess_game.board[5, 5], "pawn", Color.WHITE)
        assert (6, 5) not in chess_game.board
        assert_piece(chess_game.board[7, 4], "king", Color.WHITE)

    @pytest.mark.parametrize("file_path", [BYRNE_FISCHER_NEW_YORK_1956])
    def test_byrne_fischer_new_york_1956(self, chess_game):
        assert chess_game.done
        assert chess_game.winner == Color.BLACK
        assert chess_game.turn == 83

    @pytest.mark.parametrize("file_path", [QUEENSIDE_CASTLING])
    def test_queenside_castling(self, chess_game):
        assert_piece(chess_game.board[7, 2], "king", Color.WHITE)
        assert_piece(chess_game.board[7, 3], "rook", Color.WHITE)

    @pytest.mark.parametrize("file_path", [KINGSIDE_CASTLING])
    def test_kingside_castling(self, chess_game):
        assert_piece(chess_game.board[7, 5], "rook", Color.WHITE)
        assert_piece(chess_game.board[7, 6], "king", Color.WHITE)
