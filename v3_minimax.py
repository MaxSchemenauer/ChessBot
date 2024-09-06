import cProfile
import random
import chess
import time

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
        self.best_move = None
        self.best_eval = None
        self.game = game
        self.position_counts = {}

    def move(self):
        """
        begins search. sets up board and gets legal moves
        """
        board = self.game.board
        self.update_position_counts(board)  # update to get opponents moves

        self.best_move = None
        # TODO; check time on eval mate vs search mate
        start = time.time()
        print("starting search")
        # profiler = cProfile.Profile()
        # profiler.enable()
        self.best_eval = self.search(board, depth=4, alpha=float('-inf'), beta=float('inf'))
        end = time.time()
        print("move took", end - start, "seconds")
        # profiler.disable()
        # profiler.print_stats(sort='time')

        if self.best_move is None:  # if no move happens to be found, use a random one
            moves = list(board.legal_moves)
            random.shuffle(moves)
            board.push(moves[0])
        else:
            board.push(self.best_move)

        print(self.best_move, self.best_eval)
        self.update_position_counts(board)  # update for this move

        return self.game.check_game_state()

    def search(self, board, depth, alpha, beta):
        if depth == 0:  # evaluate
            return self.evaluate(board)

        moves = board.legal_moves

        if not moves:
            if board.is_checkmate():  # checkmate is the worst outcome
                return float('-inf')
        # if board.is_stalemate() or self.is_potential_threefold_repetition(board):
        #     return -100  # is a draw

        best_eval = float('-inf')
        for move in moves:
            board.push(move)
            eval = -self.search(board, depth - 1, -beta, -alpha)
            board.pop()
            if eval > best_eval:
                best_eval = eval
                if depth == 4:
                    self.best_move = move
            alpha = max(alpha, eval)
            if alpha >= beta:
                break  # Alpha-beta pruning

        return best_eval

    def evaluate(self, board):
        score = 0
        # if board.is_checkmate():  # checkmate for is the best outcome
        #     print("eval mate")
        #     return float('-inf')
        # if board.is_stalemate() or self.is_potential_threefold_repetition(board):
        #     return 0  # is a draw, regardless of other heuristics
        score = 0
        piece_map = board.piece_map()

        if board.is_stalemate() or self.is_potential_threefold_repetition(board):
            print("threefold detected")
            return -1  # is a draw

        for square, piece in piece_map.items():
            # Add or subtract piece value depending on color
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value

        return score if board.turn else -score

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
