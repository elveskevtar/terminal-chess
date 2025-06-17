import pytest

from pychess.core import (
    Chess, Board, Position, Piece, Player, PieceType, MoveResult,
    MoveParser
)

def test_fischer_byrne_game():
    """Test the famous Fischer-Byrne game from 1956."""
    game = Chess()
    parser = MoveParser()
    
    # Read moves from the file
    with open('tests/resources/byrne_fischer_new_york_1956', 'r') as f:
        moves = [line.strip() for line in f if line.strip()]
    
    # Apply each move
    for move in moves:
        start, end, promotion = parser.parse_move(move, game.board, game.current_player)
        result, _ = game.move(start, end, promotion)
        assert result != MoveResult.INVALID, f"Invalid move: {move}"
    
    # Verify final state
    assert game.is_checkmate()
    assert game.current_player == Player.WHITE  # Black (Fischer) won
    assert game.is_game_over()
    
    # Verify the final position
    # Black king is on g7
    assert game.board.get_piece(Position(6, 6)).piece_type == PieceType.KING
    assert game.board.get_piece(Position(6, 6)).player == Player.BLACK
    
    # White king is on c1
    assert game.board.get_piece(Position(2, 0)).piece_type == PieceType.KING
    assert game.board.get_piece(Position(2, 0)).player == Player.WHITE
    
    # Black rook is on c2 (delivering checkmate)
    assert game.board.get_piece(Position(2, 1)).piece_type == PieceType.ROOK
    assert game.board.get_piece(Position(2, 1)).player == Player.BLACK
    
    # White is in check
    assert game.board.is_in_check(Player.WHITE)
    
    # White has no valid moves
    assert not game.board.get_all_valid_moves(Player.WHITE) 