import pytest

from pychess.core import (
    Chess, Board, Position, Piece, Player, PieceType, MoveResult,
    MoveParser
)

def test_initial_board_setup():
    """Test that the initial board is set up correctly."""
    game = Chess()
    board = game.board
    
    # Check that all pieces are in their correct starting positions
    # White pieces
    assert board.get_piece(Position(0, 0)).piece_type == PieceType.ROOK
    assert board.get_piece(Position(1, 0)).piece_type == PieceType.KNIGHT
    assert board.get_piece(Position(2, 0)).piece_type == PieceType.BISHOP
    assert board.get_piece(Position(3, 0)).piece_type == PieceType.QUEEN
    assert board.get_piece(Position(4, 0)).piece_type == PieceType.KING
    assert board.get_piece(Position(5, 0)).piece_type == PieceType.BISHOP
    assert board.get_piece(Position(6, 0)).piece_type == PieceType.KNIGHT
    assert board.get_piece(Position(7, 0)).piece_type == PieceType.ROOK
    
    # White pawns
    for x in range(8):
        assert board.get_piece(Position(x, 1)).piece_type == PieceType.PAWN
    
    # Black pieces
    assert board.get_piece(Position(0, 7)).piece_type == PieceType.ROOK
    assert board.get_piece(Position(1, 7)).piece_type == PieceType.KNIGHT
    assert board.get_piece(Position(2, 7)).piece_type == PieceType.BISHOP
    assert board.get_piece(Position(3, 7)).piece_type == PieceType.QUEEN
    assert board.get_piece(Position(4, 7)).piece_type == PieceType.KING
    assert board.get_piece(Position(5, 7)).piece_type == PieceType.BISHOP
    assert board.get_piece(Position(6, 7)).piece_type == PieceType.KNIGHT
    assert board.get_piece(Position(7, 7)).piece_type == PieceType.ROOK
    
    # Black pawns
    for x in range(8):
        assert board.get_piece(Position(x, 6)).piece_type == PieceType.PAWN

def test_basic_moves():
    """Test basic piece movements."""
    game = Chess()
    
    # Test pawn move
    result, _ = game.move(Position(4, 1), Position(4, 2))
    assert result == MoveResult.SUCCESS
    
    # Test knight move
    result, _ = game.move(Position(1, 7), Position(2, 5))
    assert result == MoveResult.SUCCESS
    
    # Test invalid move
    result, _ = game.move(Position(4, 0), Position(4, 2))  # King can't move like that
    assert result == MoveResult.INVALID

def test_captures():
    """Test piece captures."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up a capture situation
    game.board.add_piece(Piece(Player.WHITE, PieceType.PAWN), Position(4, 4))
    game.board.add_piece(Piece(Player.BLACK, PieceType.PAWN), Position(5, 5))
    
    # Test capture
    result, captured = game.move(Position(4, 4), Position(5, 5))
    assert result == MoveResult.CAPTURE
    assert captured.piece_type == PieceType.PAWN
    assert captured.player == Player.BLACK

def test_castling():
    """Test castling moves."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up pieces for castling
    game.board.add_piece(Piece(Player.WHITE, PieceType.KING), Position(4, 0))
    game.board.add_piece(Piece(Player.WHITE, PieceType.ROOK), Position(7, 0))
    
    # Test kingside castling
    result, _ = game.move(Position(4, 0), Position(6, 0))
    assert result == MoveResult.SUCCESS
    
    # Verify rook moved
    assert game.board.get_piece(Position(5, 0)).piece_type == PieceType.ROOK

def test_pawn_promotion():
    """Test pawn promotion."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up a pawn for promotion
    game.board.add_piece(Piece(Player.WHITE, PieceType.PAWN), Position(0, 6))
    game.current_player = Player.WHITE  # Ensure it's white's turn
    
    # Test promotion
    result, _ = game.move(Position(0, 6), Position(0, 7), PieceType.QUEEN)
    assert result == MoveResult.SUCCESS
    assert game.board.get_piece(Position(0, 7)).piece_type == PieceType.QUEEN

def test_check_and_checkmate():
    """Test check and checkmate detection."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up a proper checkmate position
    game.board.add_piece(Piece(Player.WHITE, PieceType.KING), Position(0, 0))
    game.board.add_piece(Piece(Player.BLACK, PieceType.KING), Position(2, 2))
    game.board.add_piece(Piece(Player.BLACK, PieceType.QUEEN), Position(1, 1))  # Queen controls diagonal
    game.board.add_piece(Piece(Player.BLACK, PieceType.ROOK), Position(0, 1))   # Rook controls vertical
    game.board.add_piece(Piece(Player.BLACK, PieceType.ROOK), Position(1, 0))   # Rook controls horizontal
    
    game.current_player = Player.WHITE
    
    # Verify checkmate
    assert game.board.is_in_check(Player.WHITE)
    assert not game.board.get_all_valid_moves(Player.WHITE)
    assert game.is_checkmate()
    assert game.is_game_over()

def test_stalemate():
    """Test stalemate detection."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up a stalemate position
    game.board.add_piece(Piece(Player.WHITE, PieceType.KING), Position(0, 0))
    game.board.add_piece(Piece(Player.BLACK, PieceType.KING), Position(2, 2))
    game.board.add_piece(Piece(Player.BLACK, PieceType.QUEEN), Position(1, 2))
    game.current_player = Player.WHITE
    
    assert game.is_stalemate()
    assert game.is_game_over()

def test_move_parser():
    """Test the move parser."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    parser = MoveParser()
    
    # Set up pieces for testing
    game.board.add_piece(Piece(Player.WHITE, PieceType.PAWN), Position(4, 1))
    game.board.add_piece(Piece(Player.WHITE, PieceType.KNIGHT), Position(1, 0))
    game.board.add_piece(Piece(Player.BLACK, PieceType.PAWN), Position(2, 2))
    game.board.add_piece(Piece(Player.WHITE, PieceType.KING), Position(4, 0))
    game.board.add_piece(Piece(Player.WHITE, PieceType.ROOK), Position(7, 0))
    
    # Test basic move parsing
    start, end, _ = parser.parse_move("e4", game.board, Player.WHITE)
    assert start == Position(4, 1)
    assert end == Position(4, 3)
    
    # Test capture parsing
    start, end, _ = parser.parse_move("Nxc3", game.board, Player.WHITE)
    assert start == Position(1, 0)
    assert end == Position(2, 2)
    
    # Test castling parsing
    start, end, _ = parser.parse_move("O-O", game.board, Player.WHITE)
    assert start == Position(4, 0)
    assert end == Position(6, 0)

def test_insufficient_material():
    """Test insufficient material detection."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Add just the kings
    game.board.add_piece(Piece(Player.WHITE, PieceType.KING), Position(0, 0))
    game.board.add_piece(Piece(Player.BLACK, PieceType.KING), Position(7, 7))
    
    assert game.is_draw()
    assert game.is_game_over()

def test_fifty_move_rule():
    """Test fifty-move rule."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up pieces for testing
    game.board.add_piece(Piece(Player.WHITE, PieceType.KNIGHT), Position(1, 0))
    game.board.add_piece(Piece(Player.BLACK, PieceType.KNIGHT), Position(6, 7))
    game.current_player = Player.WHITE
    
    # Make 50 moves without capture or pawn move
    for _ in range(25):  # 25 pairs of moves
        game.move(Position(1, 0), Position(2, 2))  # White knight
        game.move(Position(6, 7), Position(5, 5))  # Black knight
        game.move(Position(2, 2), Position(1, 0))  # White knight back
        game.move(Position(5, 5), Position(6, 7))  # Black knight back
    
    assert game.is_draw()
    assert game.is_game_over()

def test_threefold_repetition():
    """Test threefold repetition rule."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up pieces for testing
    game.board.add_piece(Piece(Player.WHITE, PieceType.KNIGHT), Position(1, 0))
    game.board.add_piece(Piece(Player.BLACK, PieceType.KNIGHT), Position(6, 7))
    game.current_player = Player.WHITE
    
    # Make moves that lead to the same position three times
    for _ in range(3):
        game.move(Position(1, 0), Position(2, 2))  # White knight
        game.move(Position(6, 7), Position(5, 5))  # Black knight
        game.move(Position(2, 2), Position(1, 0))  # White knight back
        game.move(Position(5, 5), Position(6, 7))  # Black knight back
    
    assert game.is_draw()
    assert game.is_game_over()

def test_en_passant():
    """Test en passant capture."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up pieces for en passant
    game.board.add_piece(Piece(Player.WHITE, PieceType.PAWN), Position(4, 4))
    game.board.add_piece(Piece(Player.BLACK, PieceType.PAWN), Position(3, 6))
    game.current_player = Player.BLACK
    
    # Black pawn moves two squares forward
    result, _ = game.move(Position(3, 6), Position(3, 4))
    assert result == MoveResult.SUCCESS
    
    # White pawn should be able to capture en passant
    result, captured = game.move(Position(4, 4), Position(3, 5))
    assert result == MoveResult.CAPTURE
    assert captured.piece_type == PieceType.PAWN
    assert captured.player == Player.BLACK

def test_en_passant_if_target_pawn_moved_before_last_move():
    """Test that en passant is only available immediately after the target pawn's double move."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up pieces
    game.board.add_piece(Piece(Player.WHITE, PieceType.PAWN), Position(4, 4))
    game.board.add_piece(Piece(Player.BLACK, PieceType.PAWN), Position(3, 6))
    game.board.add_piece(Piece(Player.WHITE, PieceType.KNIGHT), Position(0, 0))
    game.board.add_piece(Piece(Player.BLACK, PieceType.KNIGHT), Position(7, 7))
    game.current_player = Player.BLACK
    
    # Black pawn moves two squares forward
    game.move(Position(3, 6), Position(3, 4))
    
    # White makes another move
    game.move(Position(0, 0), Position(2, 1))
    
    # Black makes another move
    game.move(Position(7, 7), Position(5, 6))
    
    # White tries en passant (should fail)
    result, _ = game.move(Position(4, 4), Position(3, 3))
    assert result == MoveResult.INVALID

def test_pawn_cant_capture_forward():
    """Test that pawns cannot capture by moving forward."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up pieces
    game.board.add_piece(Piece(Player.WHITE, PieceType.PAWN), Position(4, 4))
    game.board.add_piece(Piece(Player.BLACK, PieceType.PAWN), Position(4, 5))
    game.current_player = Player.WHITE
    
    # Try to capture forward (should fail)
    result, _ = game.move(Position(4, 4), Position(4, 5))
    assert result == MoveResult.INVALID

def test_pawn_cant_skip_over_pieces():
    """Test that pawns cannot skip over pieces when making their initial two-square move."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up pieces
    game.board.add_piece(Piece(Player.WHITE, PieceType.PAWN), Position(4, 1))
    game.board.add_piece(Piece(Player.BLACK, PieceType.PAWN), Position(4, 2))
    game.current_player = Player.WHITE
    
    # Try to move two squares forward (should fail)
    result, _ = game.move(Position(4, 1), Position(4, 3))
    assert result == MoveResult.INVALID

def test_pawn_cant_move_backwards():
    """Test that pawns cannot move backwards."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up pieces
    game.board.add_piece(Piece(Player.WHITE, PieceType.PAWN), Position(4, 4))
    game.current_player = Player.WHITE
    
    # Try to move backwards (should fail)
    result, _ = game.move(Position(4, 4), Position(4, 3))
    assert result == MoveResult.INVALID

def test_pawn_on_final_rank_promotes_to_queen():
    """Test that pawns on the final rank promote to a queen."""
    game = Chess()
    game.board = Board(initialize=False)  # Create empty board
    
    # Set up pieces
    game.board.add_piece(Piece(Player.WHITE, PieceType.PAWN), Position(4, 6))
    game.current_player = Player.WHITE
    
    # Try to move to final rank without promotion (should fail)
    result, _ = game.move(Position(4, 6), Position(4, 7))
    assert result == MoveResult.SUCCESS
    assert game.board.get_piece(Position(4, 7)).piece_type == PieceType.QUEEN
