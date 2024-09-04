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
        if len(legal_moves) == 0:
            return self.game.check_game_state()

        if board.turn:
            best_eval = float('-inf')
        else:
            best_eval = float('inf')
        # start search
        best_move = legal_moves[0]
        for move in legal_moves:
            board.push(move)
            eval = self.evaluate_board(board)
            print("Eval", move, eval)
            board.pop()
            if board.turn and eval > best_eval:
                best_move = move
                best_eval = eval
            elif eval < best_eval:
                best_move = move
                best_eval = eval

        board.push(best_move)
        print("Bot played", best_move)
        return self.game.check_game_state()

    def evaluate_board(self, board):
        score = 0
        for piece_type in chess.PIECE_TYPES:
            for square in board.pieces(piece_type, chess.WHITE):
                score += piece_values[piece_type]
            for square in board.pieces(piece_type, chess.BLACK):
                score -= piece_values[piece_type]
        return score
