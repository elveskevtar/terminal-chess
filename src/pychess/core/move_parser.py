from typing import Optional, Tuple, List
from pychess.core.enums import PIECE_SYMBOLS_MAP, Player, PieceType, PIECE_SYMBOLS
from pychess.core.position import Position
from pychess.core.board import Board

class MoveParser:
    """Parser for chess algebraic notation (SAN) to moves."""
    
    @staticmethod
    def parse_square(square: str) -> Position:
        """Convert a square in algebraic notation (e.g., 'e4') to a Position.
        
        Args:
            square: A string representing a square in algebraic notation (e.g., 'e4').
            
        Returns:
            A Position object representing the square.
            
        Raises:
            ValueError: If the square is not in valid algebraic notation.
        """
        if len(square) != 2:
            raise ValueError(f"Invalid square: {square}")
        
        file = square[0].lower()
        rank = square[1]
        
        if not ('a' <= file <= 'h') or not ('1' <= rank <= '8'):
            raise ValueError(f"Invalid square: {square}")
        
        x = ord(file) - ord('a')
        y = int(rank) - 1
        return Position(x, y)

    @staticmethod
    def _filter_by_file(positions: List[Position], file: str) -> List[Position]:
        """Filter positions by file (a-h)."""
        file_x = ord(file.lower()) - ord('a')
        return [pos for pos in positions if pos.x == file_x]

    @staticmethod
    def _filter_by_rank(positions: List[Position], rank: str) -> List[Position]:
        """Filter positions by rank (1-8)."""
        rank_y = int(rank) - 1
        return [pos for pos in positions if pos.y == rank_y]

    @staticmethod
    def parse_move(move_str: str, board: Board, player: Player) -> Tuple[Position, Position, Optional[PieceType]]:
        """Parse a move in algebraic notation into start and end positions.
        
        Args:
            move_str: The move in algebraic notation (e.g., 'e4', 'Nf3', 'O-O').
            board: The current board state.
            player: The player making the move.

        Returns:
            A tuple containing:
            - The starting position
            - The ending position
            - The promotion piece type (if any)
            
        Raises:
            ValueError: If the move is not valid.
        """
        # Remove check and checkmate symbols
        move_str = move_str.strip().replace('+', '').replace('#', '')
        
        # Handle castling
        if move_str in ['O-O', '0-0']:
            # Kingside castling
            king_pos = Position(4, 0 if player == Player.WHITE else 7)
            return (king_pos, Position(6, king_pos.y), None)
        elif move_str in ['O-O-O', '0-0-0']:
            # Queenside castling
            king_pos = Position(4, 0 if player == Player.WHITE else 7)
            return (king_pos, Position(2, king_pos.y), None)

        # Handle pawn moves
        if len(move_str) >= 2 and move_str[0].islower():
            # Check for promotion
            promotion = None
            if '=' in move_str:
                move_str, promotion_str = move_str.split('=')
                promotion = PIECE_SYMBOLS_MAP[promotion_str.upper()]
            
            # Handle captures
            if 'x' in move_str:
                # Format: dxc4 or dxc4=Q
                file = ord(move_str[0]) - ord('a')
                end = MoveParser.parse_square(move_str[2:4])
                
                # Find the pawn that can make this capture
                possible_starts = []
                for pos, piece in board.board.items():
                    if (piece.player == player and 
                        piece.piece_type == PieceType.PAWN and 
                        pos.x == file):
                        # Check if this pawn can capture to the end square
                        if pos.is_pawn_move(end, player) and abs(end.x - pos.x) == 1:
                            possible_starts.append(pos)
                
                if not possible_starts:
                    raise ValueError(f"No pawn found that can make the capture {move_str}")
                if len(possible_starts) > 1:
                    raise ValueError(f"Ambiguous pawn capture {move_str}")
                
                return (possible_starts[0], end, promotion)
            
            # Regular pawn move
            end = MoveParser.parse_square(move_str)
            # Find the pawn that can move to this square
            possible_starts = []
            for pos, piece in board.board.items():
                if (piece.player == player and 
                    piece.piece_type == PieceType.PAWN and 
                    pos.x == end.x and  # Must be on same file for non-capture moves
                    pos.is_pawn_move(end, player) and
                    abs(end.x - pos.x) == 0):  # No horizontal movement for non-capture moves
                    possible_starts.append(pos)
            
            if not possible_starts:
                raise ValueError(f"No pawn found that can move to {move_str}")
            if len(possible_starts) > 1:
                raise ValueError(f"Ambiguous pawn move {move_str}")
            
            return (possible_starts[0], end, promotion)

        # Handle piece moves
        piece_type = PIECE_SYMBOLS_MAP[move_str[0].upper()]
        # Check for capture
        if 'x' in move_str:
            end = MoveParser.parse_square(move_str[move_str.index('x') + 1:])
            # Get the part before 'x' for disambiguation
            before_x = move_str[1:move_str.index('x')]
        else:
            end = MoveParser.parse_square(move_str[-2:])
            before_x = move_str[1:-2]

        # Find all pieces of this type that can move to the end square
        possible_starts = []
        for pos, piece in board.board.items():
            if (piece.player == player and 
                piece.piece_type == piece_type and 
                board.is_move_valid(pos, end, check_for_check=False)):
                possible_starts.append(pos)

        if not possible_starts:
            raise ValueError(f"No {piece_type.name.lower()} found that can move to {move_str}")
        
        # Handle disambiguation
        if len(possible_starts) > 1:
            if before_x:
                # Filter by file
                if before_x[0].islower():
                    file = ord(before_x[0]) - ord('a')
                    possible_starts = [pos for pos in possible_starts if pos.x == file]
                # Filter by rank
                if before_x[0].isdigit():
                    rank = int(before_x[0]) - 1
                    possible_starts = [pos for pos in possible_starts if pos.y == rank]
                # Filter by both file and rank
                if len(before_x) == 2:
                    file = ord(before_x[0]) - ord('a')
                    rank = int(before_x[1]) - 1
                    possible_starts = [pos for pos in possible_starts if pos.x == file and pos.y == rank]
            
            if len(possible_starts) != 1:
                raise ValueError(f"Ambiguous move {move_str}")

        return (possible_starts[0], end, None)

    @staticmethod
    def to_algebraic(start: Position, end: Position, board: Board, promotion: Optional[PieceType] = None) -> str:
        """Convert a move to algebraic notation.
        
        Args:
            start: The starting position.
            end: The ending position.
            board: The current board state.
            promotion: The promotion piece type (if any).
            
        Returns:
            The move in algebraic notation.
        """
        piece = board.get_piece(start)
        if not piece:
            raise ValueError("No piece at start position")
        
        # Handle castling
        if piece.piece_type == PieceType.KING and abs(end.x - start.x) == 2:
            return 'O-O' if end.x > start.x else 'O-O-O'
        
        # Get the piece symbol
        symbol = ''
        if piece.piece_type != PieceType.PAWN:
            symbol = PIECE_SYMBOLS[piece.piece_type]
        
        # Check if we need disambiguation
        if piece.piece_type != PieceType.PAWN:
            # Find all pieces of the same type that can move to the end position
            other_pieces = []
            for pos, p in board.board.items():
                if (p.player == piece.player and 
                    p.piece_type == piece.piece_type and 
                    pos != start and
                    end in board.get_piece_moves(pos)):
                    other_pieces.append(pos)
            
            if other_pieces:
                # Check if we need both file and rank disambiguation
                same_file = [p for p in other_pieces if p.x == start.x]
                same_rank = [p for p in other_pieces if p.y == start.y]
                
                if len(same_file) > 0 and len(same_rank) > 0:
                    # Need both file and rank
                    symbol += chr(start.x + ord('a')) + str(start.y + 1)
                elif len(same_file) > 0:
                    # Need rank only
                    symbol += str(start.y + 1)
                else:
                    # Need file only
                    symbol += chr(start.x + ord('a'))
        
        # Check if capture
        capture = board.get_piece(end) is not None
        if capture:
            if piece.piece_type == PieceType.PAWN:
                symbol = chr(start.x + ord('a'))
            symbol += 'x'
        
        # Add the destination square
        move = symbol + str(end)
        
        # Add promotion
        if promotion:
            move += f"={PIECE_SYMBOLS[promotion]}"
        
        # Create a copy of the board to simulate the move
        board_copy = board.copy()
        board_copy.move_piece(start, end)
        
        # Check if the move puts the opponent in check or checkmate
        opponent = piece.player.opponent()
        if board_copy.is_in_check(opponent):
            # Check if it's checkmate by seeing if the opponent has any valid moves
            if not board_copy.get_all_valid_moves(opponent):
                move += '#'
            else:
                move += '+'
        
        return move
