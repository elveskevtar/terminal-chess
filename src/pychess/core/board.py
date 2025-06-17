from typing import Dict, Optional
from pychess.core.enums import Player, PieceType, MoveResult
from pychess.core.position import Position
from pychess.core.piece import Piece

class Board:
    """Represents a chess board."""
    
    def __init__(self, initialize: bool = True):
        """Initialize a new chess board.
        
        Args:
            initialize: Whether to initialize the board with the standard chess setup.
        """
        self.board: Dict[Position, Piece] = {}
        self.king_positions: Dict[Player, Position] = {}
        self.last_move: Optional[tuple[Position, Position]] = None
        if initialize:
            self._initialize_board()

    def _initialize_board(self):
        # Define starting positions for each piece type
        starting_positions = {
            PieceType.PAWN: {
                Player.WHITE: [(x, 1) for x in range(8)],
                Player.BLACK: [(x, 6) for x in range(8)]
            },
            PieceType.ROOK: {
                Player.WHITE: [(0, 0), (7, 0)],
                Player.BLACK: [(0, 7), (7, 7)]
            },
            PieceType.KNIGHT: {
                Player.WHITE: [(1, 0), (6, 0)],
                Player.BLACK: [(1, 7), (6, 7)]
            },
            PieceType.BISHOP: {
                Player.WHITE: [(2, 0), (5, 0)],
                Player.BLACK: [(2, 7), (5, 7)]
            },
            PieceType.QUEEN: {
                Player.WHITE: [(3, 0)],
                Player.BLACK: [(3, 7)]
            },
            PieceType.KING: {
                Player.WHITE: [(4, 0)],
                Player.BLACK: [(4, 7)]
            }
        }

        # Place all pieces on the board
        for piece_type, player_positions in starting_positions.items():
            for player, positions in player_positions.items():
                for x, y in positions:
                    self.add_piece(Piece(player, piece_type), Position(x, y))

    def add_piece(self, piece: Piece, pos: Position) -> Optional[Piece]:
        """Add a piece to the board at a given position.
        
        Args:
            piece: The piece to add.
            pos: The position to add the piece to.

        Returns:
            The piece that was captured, or None if the position is not occupied.
        """
        captured = self.remove_piece(pos)
        self.board[pos] = piece
        if piece.piece_type == PieceType.KING:
            self.king_positions[piece.player] = pos
        return captured

    def remove_piece(self, pos: Position) -> Optional[Piece]:
        """Remove a piece from the board at a given position.
        
        Args:
            pos: The position of the piece to remove.

        Returns:
            The piece that was removed, or None if the position is not occupied.
        """
        return self.board.pop(pos, None)

    def get_piece(self, pos: Position) -> Optional[Piece]:
        """Get the piece at a given position."""
        return self.board.get(pos)

    def is_path_clear(self, start: Position, end: Position) -> bool:
        """Check if the path between two positions is clear of pieces.
        
        This only checks the squares between start and end, not including
        the end position (which may contain a piece to capture).
        """
        if start == end:
            return True

        dx, dy = start.get_direction(end)
        current = Position(start.x + dx, start.y + dy)

        while current != end:
            if self.get_piece(current) is not None:
                return False
            current = Position(current.x + dx, current.y + dy)

        return True

    def get_king_position(self, player: Player) -> Optional[Position]:
        """Get the position of the king for a given player."""
        return self.king_positions.get(player)

    def copy(self) -> 'Board':
        """Create a copy of this board."""
        new_board = Board()
        new_board.board = {pos: piece.copy() for pos, piece in self.board.items()}
        new_board.king_positions = self.king_positions.copy()
        new_board.last_move = self.last_move
        return new_board

    def would_move_expose_king(self, start: Position, end: Position) -> bool:
        """Check if a move would expose the king to check.
        
        This is done by simulating the move and checking if the player ends up in check.
        """
        piece = self.remove_piece(start)
        if not piece:
            return False

        # Simulate the move
        captured_piece = self.get_piece(end)
        if captured_piece:
            self.remove_piece(end)
        self.add_piece(piece, end)

        # Check if the player is in check
        is_exposed = self.is_in_check(piece.player)

        # Restore the board state
        self.remove_piece(end)
        if captured_piece:
            self.add_piece(captured_piece, end)
        self.add_piece(piece, start)

        return is_exposed

    def is_move_valid(self, start: Position, end: Position, check_for_check: bool = True) -> bool:
        """Check if a move is valid based on basic chess rules.
        
        Args:
            start: The position of the piece to move.
            end: The new position of the piece.
            check_for_check: Whether to check if the move leaves the king in check.
        """
        piece = self.get_piece(start)
        if not piece:
            return False

        # Get the piece at the end position (if any)
        target_piece = self.get_piece(end)
        
        # Can't capture your own pieces
        if target_piece and target_piece.player == piece.player:
            return False

        # Check piece-specific movement rules
        if piece.piece_type == PieceType.PAWN:
            # For pawns, check if it's a capture move
            is_capture = target_piece is not None
            dx = abs(end.x - start.x)
            
            # Normal move (forward)
            if dx == 0:
                if not start.is_pawn_move(end, piece.player):
                    return False
                # Can't capture when moving straight
                if is_capture:
                    return False
                # Check if path is clear
                if not self.is_path_clear(start, end):
                    return False
            
            # Capture move (diagonal)
            elif dx == 1:
                if not start.is_pawn_move(end, piece.player):
                    return False
                # Must capture when moving diagonally
                if not is_capture:
                    # Check for en passant
                    if not self.last_move:
                        return False
                    last_start, last_end = self.last_move
                    last_piece = self.get_piece(last_end)
                    if not (last_piece and 
                           last_piece.piece_type == PieceType.PAWN and 
                           abs(last_end.y - last_start.y) == 2 and
                           last_end.x == end.x and
                           last_end.y == start.y):
                        return False
            else:
                return False

        elif piece.piece_type == PieceType.KNIGHT:
            if not start.is_knight_move(end):
                return False

        elif piece.piece_type == PieceType.BISHOP:
            if not start.is_diagonal(end) or not self.is_path_clear(start, end):
                return False

        elif piece.piece_type == PieceType.ROOK:
            if not start.is_straight(end) or not self.is_path_clear(start, end):
                return False

        elif piece.piece_type == PieceType.QUEEN:
            if not (start.is_straight(end) or start.is_diagonal(end)) or not self.is_path_clear(start, end):
                return False

        elif piece.piece_type == PieceType.KING:
            # Normal king move
            if start.get_distance(end) == 1:
                pass  # Valid normal move
            
            # Castling
            elif not piece.moved and abs(start.x - end.x) == 2 and start.y == end.y:
                # Determine if it's kingside or queenside castling
                rook_x = 7 if end.x > start.x else 0
                rook_pos = Position(rook_x, start.y)
                rook = self.get_piece(rook_pos)
                
                if not rook or rook.moved or rook.piece_type != PieceType.ROOK:
                    return False
                
                # Check if path is clear
                direction = 1 if end.x > start.x else -1
                current = Position(start.x + direction, start.y)
                while current != rook_pos:
                    if self.get_piece(current) is not None:
                        return False
                    current = Position(current.x + direction, current.y)
            else:
                return False

        # If we're not checking for check, we're done
        if not check_for_check:
            return True

        # Check if the move would leave the king in check
        return not self.would_move_expose_king(start, end)

    def is_in_check(self, player: Player) -> bool:
        """Check if the king for a given player is in check."""
        king_pos = self.get_king_position(player)
        if not king_pos:
            return False
        
        opponent = player.opponent()
        return self.is_position_attacked(king_pos, opponent)

    def is_position_attacked(self, pos: Position, by_player: Player) -> bool:
        """Check if a position is under attack by any of the opponent's pieces."""
        for attacker_pos, piece in self.board.items():
            if piece.player == by_player:
                # Check if the piece can attack the position (without check validation)
                if self.is_move_valid(attacker_pos, pos, check_for_check=False):
                    return True
        return False

    def move_piece(self, start: Position, end: Position) -> tuple[MoveResult, Optional[Piece]]:
        """Move a piece from one position to another.
        
        Args:
            start: The position of the piece to move.
            end: The new position of the piece.

        Returns:
            A tuple containing:
            - MoveResult: The result of the move attempt
            - Optional[Piece]: The captured piece if any, None otherwise
        """
        if not self.is_move_valid(start, end):
            return (MoveResult.INVALID, None)

        piece = self.remove_piece(start)
        if not piece:
            return (MoveResult.INVALID, None)

        captured = None
        # Handle en passant capture
        if (piece.piece_type == PieceType.PAWN and 
            abs(end.x - start.x) == 1 and 
            self.get_piece(end) is None):
            # Remove the captured pawn
            captured_pos = Position(end.x, start.y)
            captured = self.remove_piece(captured_pos)

        # Handle castling
        if (piece.piece_type == PieceType.KING and 
            abs(end.x - start.x) == 2):
            # Move the rook
            rook_x = 7 if end.x > start.x else 0
            new_rook_x = end.x - 1 if end.x > start.x else end.x + 1
            rook_pos = Position(rook_x, start.y)
            new_rook_pos = Position(new_rook_x, start.y)
            rook = self.remove_piece(rook_pos)
            self.add_piece(rook, new_rook_pos)

        # Get any piece at the destination before moving
        if captured is None:  # Only check if we haven't already captured via en passant
            captured = self.get_piece(end)
        
        # Move the piece to its new position
        self.add_piece(piece, end)
        piece.moved = True
        self.last_move = (start, end)

        if captured:
            return (MoveResult.CAPTURE, captured)
        return (MoveResult.SUCCESS, None)

    def get_knight_moves(self, pos: Position) -> list[Position]:
        """Get all possible positions a knight can move to from a given position."""
        moves = []
        for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            new_pos = Position(pos.x + dx, pos.y + dy)
            if new_pos.is_on_board():
                moves.append(new_pos)
        return moves

    def get_bishop_moves(self, pos: Position) -> list[Position]:
        """Get all possible positions a bishop can move to from a given position."""
        moves = []
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            current = Position(pos.x + dx, pos.y + dy)
            while current.is_on_board():
                moves.append(current)
                if self.get_piece(current):
                    break
                current = Position(current.x + dx, current.y + dy)
        return moves

    def get_rook_moves(self, pos: Position) -> list[Position]:
        """Get all possible positions a rook can move to from a given position."""
        moves = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            current = Position(pos.x + dx, pos.y + dy)
            while current.is_on_board():
                moves.append(current)
                if self.get_piece(current):
                    break
                current = Position(current.x + dx, current.y + dy)
        return moves

    def get_queen_moves(self, pos: Position) -> list[Position]:
        """Get all possible positions a queen can move to from a given position."""
        return self.get_bishop_moves(pos) + self.get_rook_moves(pos)

    def get_king_moves(self, pos: Position) -> list[Position]:
        """Get all possible positions a king can move to from a given position."""
        moves = []
        piece = self.get_piece(pos)
        if not piece:
            return moves

        # Normal moves
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_pos = Position(pos.x + dx, pos.y + dy)
                if new_pos.is_on_board():
                    moves.append(new_pos)
        
        # Castling
        if not piece.moved:
            # Kingside castling
            kingside_rook_pos = Position(7, pos.y)
            kingside_rook = self.get_piece(kingside_rook_pos)
            if kingside_rook and not kingside_rook.moved and self.is_path_clear(pos, kingside_rook_pos):
                # Check if squares are under attack
                if not self.is_position_attacked(Position(5, pos.y), piece.player.opponent()) and \
                   not self.is_position_attacked(Position(6, pos.y), piece.player.opponent()):
                    moves.append(Position(6, pos.y))
            
            # Queenside castling
            queenside_rook_pos = Position(0, pos.y)
            queenside_rook = self.get_piece(queenside_rook_pos)
            if queenside_rook and not queenside_rook.moved and self.is_path_clear(pos, queenside_rook_pos):
                # Check if squares are under attack
                if not self.is_position_attacked(Position(3, pos.y), piece.player.opponent()) and \
                   not self.is_position_attacked(Position(2, pos.y), piece.player.opponent()):
                    moves.append(Position(2, pos.y))
        
        return moves

    def get_pawn_moves(self, pos: Position) -> list[Position]:
        """Get all possible positions a pawn can move to from a given position."""
        moves = []
        piece = self.get_piece(pos)
        if not piece:
            return moves

        # Determine direction based on player
        dy = 1 if piece.player == Player.WHITE else -1
        
        # Forward moves
        new_pos = Position(pos.x, pos.y + dy)
        if new_pos.is_on_board() and not self.get_piece(new_pos):
            moves.append(new_pos)
            # Initial two-square move
            if (piece.player == Player.WHITE and pos.y == 1) or (piece.player == Player.BLACK and pos.y == 6):
                new_pos = Position(pos.x, pos.y + 2 * dy)
                if not self.get_piece(new_pos):
                    moves.append(new_pos)
        
        # Capture moves
        for dx in [-1, 1]:
            new_pos = Position(pos.x + dx, pos.y + dy)
            if new_pos.is_on_board():
                target = self.get_piece(new_pos)
                if target and target.player != piece.player:
                    moves.append(new_pos)
        
        # En passant
        if self.last_move:
            last_start, last_end = self.last_move
            last_piece = self.get_piece(last_end)
            if (last_piece and 
                last_piece.piece_type == PieceType.PAWN and 
                abs(last_end.y - last_start.y) == 2 and
                last_end.y == pos.y and
                abs(last_end.x - pos.x) == 1):
                moves.append(Position(last_end.x, pos.y + dy))
        
        return moves

    def get_piece_moves(self, pos: Position) -> list[Position]:
        """Get all possible positions a piece can move to from a given position."""
        piece = self.get_piece(pos)
        if not piece:
            return []

        if piece.piece_type == PieceType.PAWN:
            return self.get_pawn_moves(pos)
        elif piece.piece_type == PieceType.KNIGHT:
            return self.get_knight_moves(pos)
        elif piece.piece_type == PieceType.BISHOP:
            return self.get_bishop_moves(pos)
        elif piece.piece_type == PieceType.ROOK:
            return self.get_rook_moves(pos)
        elif piece.piece_type == PieceType.QUEEN:
            return self.get_queen_moves(pos)
        elif piece.piece_type == PieceType.KING:
            return self.get_king_moves(pos)
        return []

    def get_all_valid_moves(self, player: Player) -> list[tuple[Position, Position]]:
        """Get all valid moves for a given player."""
        valid_moves = []
        # Create a list of positions to check to avoid modifying during iteration
        positions = [pos for pos, piece in self.board.items() if piece.player == player]
        
        # Check all pieces belonging to the player
        for pos in positions:
            # Get all possible moves for this piece
            for target in self.get_piece_moves(pos):
                # Only check for check if the move is otherwise valid
                if self.is_move_valid(pos, target, check_for_check=True):
                    valid_moves.append((pos, target))
        return valid_moves
