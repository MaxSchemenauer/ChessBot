import random
import chess

# Pawn: chess.PAWN (1)
# Knight: chess.KNIGHT (2)
# Bishop: chess.BISHOP (3)
# Rook: chess.ROOK (4)
# Queen: chess.QUEEN (5)
# King: chess.KING (6)
piece_values = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 100}


class v3_Minimax:
    def __init__(self, game):
        """
        Basic Evaluation, prioritizes checkmate, correctly values draws as 0
        """
        self.game = game
        self.position_counts = {}
        self.best_move = None
        self.is_white = None

    def move(self):
        """
        begins search. sets up board and gets legal moves

        """
        board = self.game.board
        self.update_position_counts(board)  # update to get opponents moves

        self.best_move = None
        self.is_white = board.turn
        self.search(board, 2, best_eval=float('-inf'))

        if self.best_move is None:  # if no move happens to be found, use a random one
            moves = list(board.legal_moves)
            random.shuffle(moves)
            self.best_move = moves[0]

        board.push(self.best_move)
        self.update_position_counts(board)  # update for this move

        return self.game.check_game_state()

    def search(self, board, depth, best_eval):
        moves = list(board.legal_moves)
        random.shuffle(moves)
        if len(moves) == 0: # or depth == 0:
            return
        for move in moves:
            board.push(move)
            eval = self.evaluate_board(board)
            if eval > best_eval:
                self.best_move = move
                best_eval = eval
            #self.search(board, depth - 1, best_eval)
            board.pop()

    def evaluate_board(self, board):
        score = 0
        if board.is_checkmate():  # checkmate is the best outcome
            return float('inf')
        if board.is_stalemate() or self.is_potential_threefold_repetition(board):
            return 0  # is a draw, regardless of other heuristics

        for piece_type in chess.PIECE_TYPES:
            for square in board.pieces(piece_type, chess.WHITE):
                score += piece_values[piece_type]
            for square in board.pieces(piece_type, chess.BLACK):
                score -= piece_values[piece_type]
        if not self.is_white:
            score = -score
        return score

    def is_potential_threefold_repetition(self, board):
        fen = board.fen()
        return self.position_counts.get(fen, 0) >= 2

    def update_position_counts(self, board):
        fen = board.fen()
        if fen in self.position_counts:
            self.position_counts[fen] += 1
        else:
            self.position_counts[fen] = 1

    def reset(self):
        self.position_counts = {}
