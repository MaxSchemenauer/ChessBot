import random
import chess

# Pawn: chess.PAWN (1)
# Knight: chess.KNIGHT (2)
# Bishop: chess.BISHOP (3)
# Rook: chess.ROOK (4)
# Queen: chess.QUEEN (5)
# King: chess.KING (6)
piece_values = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 100}


class v2_Minimax_Eval:
    def __init__(self, game):
        self.game = game
        self.position_counts = {}

    def move(self):
        board = self.game.board
        legal_moves = list(board.legal_moves)
        random.shuffle(legal_moves)
        if len(legal_moves) == 0:
            return self.game.check_game_state()

        is_white = board.turn
        best_eval = float('-inf')
        best_move = legal_moves[0]
        self.update_position_counts(board)  # update to get move opponent played

        for move in legal_moves:
            board.push(move)
            self.update_position_counts(board)  # update to get move we're testing
            eval = self.evaluate_board(board, is_white)
            self.update_position_counts(board, decrement=True)  # remove tested move
            if eval > best_eval:
                best_move = move
                best_eval = eval
            board.pop()

        board.push(best_move)
        self.update_position_counts(board)  # update with move bot played
        return self.game.check_game_state()

    def evaluate_board(self, board, is_white):
        score = 0
        if board.is_checkmate():
            return float('inf')
        if board.is_stalemate() or self.is_potential_threefold_repetition(board):
            score = 0

        for piece_type in chess.PIECE_TYPES:
            for square in board.pieces(piece_type, chess.WHITE):
                score += piece_values[piece_type]
            for square in board.pieces(piece_type, chess.BLACK):
                score -= piece_values[piece_type]
        if not is_white:
            score = -score
        return score

    def is_potential_threefold_repetition(self, board):
        fen = board.fen()
        return self.position_counts.get(fen, 0) >= 2

    def update_position_counts(self, board, decrement=False):
        fen = board.fen()
        if decrement:
            if fen in self.position_counts:
                self.position_counts[fen] -= 1
                if self.position_counts[fen] == 0:
                    del self.position_counts[fen]
        else:
            if fen in self.position_counts:
                self.position_counts[fen] += 1
            else:
                self.position_counts[fen] = 1

    def reset(self):
        self.position_counts = {}
