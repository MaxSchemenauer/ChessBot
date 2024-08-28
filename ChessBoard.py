import pygame
import chess


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
