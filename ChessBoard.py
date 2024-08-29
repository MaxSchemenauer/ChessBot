import pygame
import chess


class ChessBoard:
    def __init__(self):
        self.board = chess.Board()  # python-chess chessboard

    def get_piece(self, pos):
        return self.board.piece_at(pos)

    def make_move(self, move):
        """Handle making a move."""
        try:
            move = chess.Move.from_uci(move.uci())
            if move in self.board.legal_moves:
                self.board.push(move)
                if self.board.is_checkmate():
                    winner = "Black" if self.board.turn else "White"
                    print(f"Checkmate! {winner} wins.")
                    return "Checkmate"
                if self.board.is_stalemate():
                    print("Stalemate")
                    return "Stalemate"
                if self.board.is_fivefold_repetition():
                    print("Five Fold Repetition")
                    return "Five Fold"
                if self.board.is_insufficient_material():
                    print("Insufficient Material")
                    return "Insufficient Material"
                return "Move made"
            else:
                print("Invalid move")
                return "Illegal move"
        except Exception as e:
            return f"Error: {e}"
