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
        self.time_and_positions = []
        self.positions_evaluated = 0

    def move(self):
        """
        begins search. sets up board and gets legal moves
        """
        # profiler = cProfile.Profile()
        # profiler.enable()
        # start = time.time()
        board = self.game.board
        self.update_position_counts(board)  # update to get opponents moves
        self.positions_evaluated = 0
        self.best_move = None

        self.best_eval = self.search(board, ply_remaining=4, ply_from_root=0, alpha=float('-inf'), beta=float('inf'))

        if self.best_move is None:  # if no move happens to be found, use a random one
            print("random")
            moves = list(board.legal_moves)
            random.shuffle(moves)
            self.best_move = moves[0]
        board.push(self.best_move)

        self.update_position_counts(board)  # update for this move
        # end = time.time()
        # profiler.disable()
        # profiler.print_stats(sort='time')
        # self.time_and_positions.append((f'{self.best_move.uci()}, {self.best_eval}', round((end - start), 3), f": {self.positions_evaluated} positions evaluated"))
        # #print(self.time_and_positions[-1])
        return self.game.check_game_state()

    def search(self, board, ply_remaining, ply_from_root, alpha, beta, last_move=None):
        if ply_from_root > 0:
            if self.evaluate(board) > 0 and (self.is_potential_threefold_repetition(board) or board.is_fifty_moves() or board.is_stalemate()):
                return -1.5 # discourage draw

        moves = sorted(board.legal_moves, key=lambda move: board.is_capture(move), reverse=True)

        if ply_remaining == 0:  # evaluate
            return self.evaluate(board)
        if not moves:
            if board.is_checkmate():  # checkmate is the worst outcome
                return float('-1000000')
            else:  # stalemate, or another form of draw
                return 0

        for move in moves:
            board.push(move)
            self.positions_evaluated += 1
            eval = -self.search(board, ply_remaining - 1, ply_from_root + 1, -beta, -alpha)
            board.pop()
            # Move was *too* good, opponent will choose a different move earlier on to avoid this position. 'hard pruning'
            if eval >= beta:
                return beta
            if eval > alpha:
                alpha = eval
                if ply_from_root == 0:
                    self.best_move = move
        return alpha


    @staticmethod
    def evaluate(board):
        piece_map = board.piece_map()
        score = 0
        for square, piece in piece_map.items():
            # Add or subtract piece value depending on color
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
        eval = score if board.turn else -score
        return eval

    def is_potential_threefold_repetition(self, board):
        return board.board_fen() in self.position_counts

    def update_position_counts(self, board):
        fen = board.board_fen()
        if fen in self.position_counts:
            self.position_counts[fen] += 1
        else:
            self.position_counts[fen] = 1

    def reset(self):
        times = [time for _, time, _ in self.time_and_positions]
        print("average time per move:", sum(times) / len(times))
        self.position_counts = {}
        self.time_and_positions = []
        self.positions_evaluated = 0
