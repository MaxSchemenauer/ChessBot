from game import Game
import time
import cProfile
import pstats

from v1_random import v1_Random
from visual import Visual


class Simulate:

    def __init__(self):
        self.game = Game()
        self.renderer = None

    def start_game(self, bot1, bot2, bot1_name, bot2_name, visual=False, bot1_first=True):
        current_bot = bot1 if bot1_first else bot2  # allows for order of start to change, more variety
        next_bot = bot2 if bot1_first else bot1
        current_bot_name = bot1_name
        next_bot_name = bot2_name
        while True:
            game_ended = current_bot(self.game)
            if game_ended:
                winner = current_bot_name if self.game.board.is_checkmate() else "Draw"
                if visual:
                    self.renderer.game_ended = True
                    self.renderer.update_screen()
                    self.renderer.game_ended = False
                self.game.restart()
                return winner
            # Swap bots and their names for the next turn
            current_bot, next_bot = next_bot, current_bot
            current_bot_name, next_bot_name = next_bot_name, current_bot_name
            if visual:
                self.renderer.update_screen()

    def run_simulations(self, num_games, bot1, bot2, visual=False):
        bot1_name = bot1.__name__
        bot2_name = bot2.__name__
        if bot1_name == bot2_name:
            bot2_name += "_other"
        bot1_move = bot1.move
        bot2_move = bot2.move

        if visual:  # sets up renderer to show the game
            self.renderer = Visual(self.game)

        data = []
        for i in range(num_games):
            winner = self.start_game(bot1_move, bot2_move, bot1_name, bot2_name, visual)
            data.append(f"Game result: {winner}\n")

        results = ''.join(data)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(f"{bot1_name}_vs_{bot2_name}_results.txt", "a") as log_file:
            log_file.write(f"Simulation started at: {current_time}\n")
            log_file.write(results)


if __name__ == "__main__":
    simulate = Simulate()
    mode = 'visual'
    bot_1 = v1_Random
    bot_2 = v1_Random
    visual = mode == 'visual'
    simulate.run_simulations(50, bot_1, bot_2, visual=visual)
