from collections import deque
from typing import Optional, Tuple
from .enums import Player, PieceType, MoveResult
from .board import Board
from .position import Position
from .piece import Piece

class Chess:
    def __init__(self):
        self.board = Board()
        self.current_player = Player.WHITE
        self.move_history = deque()
        self.position_history = []  # For threefold repetition
        self.moves_since_capture_or_pawn = 0  # For fifty-move rule
        self._add_position_to_history()

    def _add_position_to_history(self):
        """Add the current board position to the history."""
        # Create a string representation of the board state
        position_str = str(self.board)
        self.position_history.append(position_str)

    def _is_threefold_repetition(self) -> bool:
        """Check if the current position has occurred three times."""
        current_position = str(self.board)
        return self.position_history.count(current_position) >= 3

    def _is_fifty_move_rule(self) -> bool:
        """Check if fifty moves have been made without a capture or pawn move."""
        return self.moves_since_capture_or_pawn >= 50

    def _is_insufficient_material(self) -> bool:
        """Check if there is insufficient material to checkmate."""
        pieces = list(self.board.board.values())
        if len(pieces) <= 2:  # Only kings
            return True
        
        # Count pieces by type and player
        piece_counts = {player: {piece_type: 0 for piece_type in PieceType} 
                       for player in Player}
        for piece in pieces:
            piece_counts[piece.player][piece.piece_type] += 1

        # Check for known insufficient material combinations
        for player in Player:
            opponent = player.opponent()
            # King and Knight vs King
            if (piece_counts[player][PieceType.KING] == 1 and 
                piece_counts[player][PieceType.KNIGHT] == 1 and
                all(piece_counts[player][pt] == 0 for pt in PieceType if pt not in [PieceType.KING, PieceType.KNIGHT]) and
                piece_counts[opponent][PieceType.KING] == 1 and 
                all(piece_counts[opponent][pt] == 0 for pt in PieceType if pt != PieceType.KING)):
                return True
            
            # King and Bishop vs King
            if (piece_counts[player][PieceType.KING] == 1 and 
                piece_counts[player][PieceType.BISHOP] == 1 and
                all(piece_counts[player][pt] == 0 for pt in PieceType if pt not in [PieceType.KING, PieceType.BISHOP]) and
                piece_counts[opponent][PieceType.KING] == 1 and 
                all(piece_counts[opponent][pt] == 0 for pt in PieceType if pt != PieceType.KING)):
                return True

        return False

    def is_checkmate(self) -> bool:
        """Check if the current player is in checkmate.
        
        Returns:
            True if the current player is in checkmate, False otherwise.
        """
        if not self.board.is_in_check(self.current_player):
            return False
        
        # If there are no valid moves and the king is in check, it's checkmate
        return len(self.board.get_all_valid_moves(self.current_player)) == 0

    def is_stalemate(self) -> bool:
        """Check if the current player is in stalemate.
        
        Returns:
            True if the current player is in stalemate, False otherwise.
        """
        if self.board.is_in_check(self.current_player):
            return False
        
        # If there are no valid moves and the king is not in check, it's stalemate
        return len(self.board.get_all_valid_moves(self.current_player)) == 0

    def move(self, start: Position, end: Position, promotion_piece: Optional[PieceType] = None) -> tuple[MoveResult, Optional[Piece]]:
        """Move a piece from one position to another.
        
        Args:
            start: The position of the piece to move.
            end: The new position of the piece.
            promotion_piece: The piece type to promote to if a pawn reaches the end.

        Returns:
            A tuple containing:
            - MoveResult: The result of the move attempt
            - Optional[Piece]: The captured piece if any, None otherwise
        """
        result, captured = self.board.move_piece(start, end)
        if result != MoveResult.INVALID:
            # Handle pawn promotion
            piece = self.board.get_piece(end)
            if piece and piece.piece_type == PieceType.PAWN:
                if (piece.player == Player.WHITE and end.y == 7) or (piece.player == Player.BLACK and end.y == 0):
                    if promotion_piece is None:
                        promotion_piece = PieceType.QUEEN  # Default to queen
                    self.board.remove_piece(end)
                    self.board.add_piece(Piece(piece.player, promotion_piece), end)

            # Update move history and position history
            self.move_history.append((start, end, result, captured))
            self._add_position_to_history()

            # Update moves since capture or pawn move
            if result == MoveResult.CAPTURE or piece.piece_type == PieceType.PAWN:
                self.moves_since_capture_or_pawn = 0
            else:
                self.moves_since_capture_or_pawn += 1

            self.current_player = self.current_player.opponent()
        return (result, captured)

    def is_draw(self) -> bool:
        """Check if the game is a draw.
        
        Returns:
            True if the game is a draw, False otherwise.
        """
        return (self._is_threefold_repetition() or 
                self._is_fifty_move_rule() or 
                self._is_insufficient_material() or 
                self.is_stalemate())

    def is_game_over(self) -> bool:
        """Check if the game is over.
        
        Returns:
            True if the game is over (checkmate or draw), False otherwise.
        """
        return self.is_checkmate() or self.is_draw() 