import chess


class Piece:
    def __init__(self, color, position):
        self.color = color
        self.position = position  # Expected as a chess.Square (e.g., chess.E2)
        self.has_moved = False

    def move(self, board, new_position):
        """Attempt to move the piece to a new position on the chessboard."""
        move = chess.Move(self.position, new_position)
        if move in board.legal_moves:
            board.push(move)
            self.position = new_position
            self.has_moved = True
        else:
            raise ValueError(f"Move {move} is not legal.")

    def get_legal_moves(self, board):
        """Return a list of legal moves for this piece."""
        legal_moves = [move for move in board.legal_moves if move.from_square == self.position]
        return legal_moves

    def __str__(self):
        """Return a string representation of the piece (for debugging)."""
        piece_type = self.__class__.__name__
        return f"{self.color.capitalize()} {piece_type} at {chess.square_name(self.position)}"


# Example specific piece classes
class Pawn(Piece):
    def get_legal_moves(self, board):
        """Return a list of legal moves specific to pawns."""
        return super().get_legal_moves(board)


class Knight(Piece):
    def get_legal_moves(self, board):
        """Return a list of legal moves specific to knights."""
        return super().get_legal_moves(board)


class Bishop(Piece):
    def get_legal_moves(self, board):
        """Return a list of legal moves specific to bishops."""
        return super().get_legal_moves(board)


class Rook(Piece):
    def get_legal_moves(self, board):
        """Return a list of legal moves specific to rooks."""
        return super().get_legal_moves(board)


class Queen(Piece):
    def get_legal_moves(self, board):
        """Return a list of legal moves specific to queens."""
        return super().get_legal_moves(board)


class King(Piece):
    def get_legal_moves(self, board):
        """Return a list of legal moves specific to kings."""
        return super().get_legal_moves(board)
