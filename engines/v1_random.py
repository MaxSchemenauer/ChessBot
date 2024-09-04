import random


class v1_Random:
    def __init__(self, game):
        self.game = game

    def move(self):
        board = self.game.board
        # find legal moves
        legal_moves = list(board.legal_moves)
        if len(legal_moves) == 0:
            return self.game.check_game_state()

        # find move
        random_move = random.choice(legal_moves)
        board.push(random_move)

        # return game state
        return self.game.check_game_state()

    def reset(self):
        pass