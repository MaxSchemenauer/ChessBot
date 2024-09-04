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

    def move(self):
        board = self.game.board
        legal_moves = list(board.legal_moves)
        random.shuffle(legal_moves)
        if len(legal_moves) == 0:
            return self.game.check_game_state()
        maximizing = board.turn
        # if not maximizing:
        #     # print("color black")
        best_eval = float('-inf')
        best_move = legal_moves[0]
        for move in legal_moves:
            board.push(move)
            eval = self.evaluate_board(board, maximizing)
            if not maximizing:
                eval = -eval
            # print(move, eval)
            if eval > best_eval:
                # print("best eval was", best_eval, "is now", eval)
                # print("best move is", best_move)
                best_move = move
                best_eval = eval
            board.pop()

        board.push(best_move)
        return self.game.check_game_state()

    def evaluate_board(self, board, maximizing):
        score = 0
        for piece_type in chess.PIECE_TYPES:
            for square in board.pieces(piece_type, chess.WHITE):
                score += piece_values[piece_type]
            for square in board.pieces(piece_type, chess.BLACK):
                score -= piece_values[piece_type]
            if board.is_checkmate():
                val = float('inf') if maximizing else float('-inf')
                score += val
        return score
