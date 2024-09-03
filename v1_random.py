import random


class v1_Random:
    def __init__(self, game):
        self.game = game

    def move(self):
        # find legal moves
        legal_moves = list(self.game.board.legal_moves)
        if len(legal_moves) == 0:
            return self.game.check_game_state()

        # find move
        random_move = random.choice(legal_moves)
        self.game.board.push(random_move)

        # return game state
        return self.game.check_game_state()
