import pygame
import chess


class ChessBoard:
    def __init__(self):
        self.board = chess.Board()  # python-chess chessboard

    def get_piece(self, pos):
        return self.board.piece_at(pos)

    def make_move(self, move):
        """Handle making a move."""
        # TODO handle promotes
        try:
            if move in self.board.legal_moves:
                self.board.push(move)
                self.check_game_state()
            elif self.is_promotion(move):
                # Convert the move to UCI, append 'q' for queen promotion, and convert back to a Move object
                move = chess.Move.from_uci(move.uci() + 'q')
                self.board.push(move)
                self.check_game_state()
            else:
                print("Invalid move")
                return False
        except Exception as e:
            return f"Error: {e}"

    def is_promotion(self, move):
        # Check if the move is a pawn move
        if self.board.piece_at(move.from_square).piece_type == chess.PAWN:
            # Check if the pawn is moving to the last rank
            if (chess.square_rank(move.to_square) == 7 and self.board.turn == chess.WHITE) or \
                    (chess.square_rank(move.to_square) == 0 and self.board.turn == chess.BLACK):
                return True
        return False

    def check_game_state(self):
        """Check the current game state and return the appropriate message."""
        game_states = {
            "checkmate": "Checkmate! {winner} wins.",
            "stalemate": "Stalemate",
            "fivefold_repetition": "Five Fold Repetition",
            "insufficient_material": "Insufficient Material",
            "fifty_moves": "Fifty-Move Rule Draw",
            "threefold_repetition": "Threefold Repetition Draw"
        }

        for state, message in game_states.items():
            if getattr(self.board, f'is_{state}')():
                if state == "checkmate":
                    winner = "Black" if self.board.turn else "White"
                    print(message.format(winner=winner))
                    return "Checkmate"
                print(message)
                return message
        return "Move made"
