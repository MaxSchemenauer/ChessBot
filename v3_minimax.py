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
        #print("\nstarting search")
        start = time.time()
        board = self.game.board
        self.update_position_counts(board)  # update to get opponents moves
        self.positions_evaluated = 0
        self.best_move = None

        self.best_eval = self.search(board, ply_remaining=4, ply_from_root=0, alpha=float('-inf'), beta=float('inf'))

        if self.best_move is None:  # if no move happens to be found, use a random one
            moves = list(board.legal_moves)
            random.shuffle(moves)
            board.push(moves[0])
        else:
            board.push(self.best_move)

        self.update_position_counts(board)  # update for this move
        end = time.time()
        self.time_and_positions.append((f'{self.best_move.uci()}, {self.best_eval}', round((end - start), 3), f": {self.positions_evaluated} positions evaluated"))
        print(self.time_and_positions[-1])
        return self.game.check_game_state()

    def search(self, board, ply_remaining, ply_from_root, alpha, beta):
        moves = board.legal_moves
        if not moves:
            if board.is_checkmate():  # checkmate is the worst outcome
                self.positions_evaluated += 1  # early eval
                return float('-inf')
            else:  # stalemate, or another form of draw
                return 0
        if ply_from_root > 0:
            if self.is_potential_threefold_repetition(board):
                self.positions_evaluated += 1  # early eval
                return -66
        if ply_remaining == 0:  # evaluate
            self.positions_evaluated += 1  # early eval
            return self.evaluate(board)

        best_eval = float('-inf')
        for move in moves:
            board.push(move)
            eval = -self.search(board, ply_remaining - 1, ply_from_root + 1, -beta, -alpha)
            board.pop()
            if eval > best_eval:
                best_eval = eval
                if ply_remaining == 4:
                    self.best_move = move  # assigns best move at top level
            if ply_remaining == 4:
                print(move, eval)
            alpha = max(alpha, eval)
            if alpha >= beta:
                break  # Alpha-beta pruning

        return best_eval

    @staticmethod
    def evaluate(board):
        score = 0
        piece_map = board.piece_map()

        for square, piece in piece_map.items():
            # Add or subtract piece value depending on color
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
        return score if board.turn else -score

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
