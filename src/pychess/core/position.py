from pychess.core.enums import Player

class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def is_on_board(self) -> bool:
        """Check if the position is on the board."""
        return 0 <= self.x < 8 and 0 <= self.y < 8

    def __str__(self):
        return f"({chr(self.x + 97)}{self.y + 1})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

    def get_direction(self, other: 'Position') -> tuple[int, int]:
        """Get the direction vector from this position to another.
        
        Returns:
            A tuple (dx, dy) where each component is -1, 0, or 1.
        """
        dx = other.x - self.x
        dy = other.y - self.y
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
        return (dx, dy)

    def get_distance(self, other: 'Position') -> int:
        """Get the maximum distance between this position and another."""
        return max(abs(other.x - self.x), abs(other.y - self.y))

    def is_diagonal(self, other: 'Position') -> bool:
        """Check if the movement is diagonal."""
        return abs(other.x - self.x) == abs(other.y - self.y)

    def is_straight(self, other: 'Position') -> bool:
        """Check if the movement is straight (horizontal or vertical)."""
        return other.x == self.x or other.y == self.y

    def is_knight_move(self, other: 'Position') -> bool:
        """Check if the movement is a knight's L-shape."""
        dx = abs(other.x - self.x)
        dy = abs(other.y - self.y)
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

    def is_pawn_move(self, other: 'Position', player: 'Player') -> bool:
        """Check if the movement is a valid pawn move."""
        dy = other.y - self.y
        dx = abs(other.x - self.x)
        
        # Pawns move forward
        if player == Player.WHITE:
            if dy <= 0:  # Must move up
                return False
        else:
            if dy >= 0:  # Must move down
                return False

        # Normal move: one square forward
        if dx == 0 and abs(dy) == 1:
            return True
        
        # Initial two-square move
        if dx == 0 and abs(dy) == 2 and ((player == Player.WHITE and self.y == 1) or 
                                        (player == Player.BLACK and self.y == 6)):
            return True
        
        # Capture: one square diagonally forward
        if dx == 1 and abs(dy) == 1:
            return True
        
        return False
