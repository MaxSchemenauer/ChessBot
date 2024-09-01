import random


class v1_Random:
    """
    game has methods:

    """
    @staticmethod
    def move(game):
        # find legal moves
        legal_moves = list(game.board.legal_moves)
        if len(legal_moves) == 0:
            return game.check_game_state()

        # find move
        random_move = random.choice(legal_moves)
        game.board.push(random_move)

        # return game state
        return game.check_game_state()
