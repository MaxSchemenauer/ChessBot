import chess


class Game:
    def __init__(self):
        self.board = chess.Board()  # python-chess chessboard

    def get_piece(self, pos):
        return self.board.piece_at(pos)

    def make_move(self, move):
        """
        Handle making a move by a player in renderer
        :return: -1 if move fails, 0 if move is success, 1 if game is over
        """
        try:
            if move in self.board.legal_moves:
                self.board.push(move)
                return self.check_game_state()
            elif self.is_promotion(move):
                # Convert the move to UCI, append 'q' for queen promotion, and convert back to a Move object
                move = chess.Move.from_uci(move.uci() + 'q')
                self.board.push(move)
                return self.check_game_state()
            else:
                # print("Invalid move")
                return -1
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
        """Returns 1 if game is over, else 0"""
        game_states = {
            "is_checkmate": "Checkmate!",
            "is_stalemate": "Stalemate",
            "is_fivefold_repetition": "Five Fold Repetition",
            "is_insufficient_material": "Insufficient Material",
            "is_fifty_moves": "Fifty-Move Rule Draw",
            "can_claim_threefold_repetition": "Threefold Repetition Draw"
        }
        # if self.board.is_game_over():
        for state, message in game_states.items():
            if getattr(self.board, f'{state}')():
                print(message)
                return 1
        return 0

    def restart(self):
        """Logs the winner and resets the board for a new game."""
        self.board.reset()
