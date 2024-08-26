import pygame
import chess

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT_COLOR = (0, 255, 0)
SQUARE_SIZE = 80


class ChessBoard:
    def __init__(self):
        self.board = chess.Board()  # python-chess chessboard
        self.selected_square = None
        self.legal_moves = []

        self.drag_start_time = None

    def get_piece(self, pos):
        return self.board.piece_at(pos)

    def make_move(self, move):
        """Handle making a move."""
        if move in self.board.legal_moves:
            self.board.push(move)
