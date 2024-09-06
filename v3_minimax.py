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
        self.best_eval = self.search(board, depth=4)

        if self.best_move is None:  # if no move happens to be found, use a random one
            moves = list(board.legal_moves)
            random.shuffle(moves)
            board.push(moves[0])
        else:
            board.push(self.best_move)

        print(self.best_move, self.best_eval)
        self.update_position_counts(board)  # update for this move

        return self.game.check_game_state()

    def search(self, board, depth, last_move=None):
        if depth == 0:  # evaluate
            return self.evaluate(board)

        moves = list(board.legal_moves)
        random.shuffle(moves)
        if len(moves) == 0:
            print("zero")
            if board.is_checkmate():  # checkmate is the worst outcome
                return float('-inf')
            if board.is_stalemate() or self.is_potential_threefold_repetition(board):
                return 0  # is a draw

        best_eval = float('-inf')
        for move in moves:
            board.push(move)
            #print("\nevaluating" if depth==2 else f"\tresponse to {last_move}", move)
            eval = -self.search(board, depth - 1, last_move=move)
            if eval > best_eval:
                best_eval = eval
                if depth == 4:
                    self.best_move = move
            if depth == 4:
                pass
                print("my move results:", move, eval)
            board.pop()
        return best_eval

    def evaluate(self, board):
        score = 0
        # if board.is_checkmate():  # checkmate for is the best outcome
        #     print("eval mate")
        #     return float('-inf')
        # if board.is_stalemate() or self.is_potential_threefold_repetition(board):
        #     return 0  # is a draw, regardless of other heuristics

        for piece_type in chess.PIECE_TYPES:
            for square in board.pieces(piece_type, chess.WHITE):
                score += piece_values[piece_type]
            for square in board.pieces(piece_type, chess.BLACK):
                score -= piece_values[piece_type]
        if not board.turn:  # if is blacks turn
            score = -score
        #print("\tscore", score)
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
