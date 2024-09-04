import os

from game import Game
import time
import cProfile

from engines.v1_random import v1_Random
from simulation_renderer import SimulationRenderer
from v2_minimax_eval import v2_Minimax_Eval


class Simulate:

    def __init__(self):
        self.game = Game()
        self.renderer = None

    @staticmethod
    def log_results(bot1_name, bot2_name, data, win_count):
        col_width = max(len(bot1_name), len(bot2_name)) + 2
        header = f"{' Result':<{col_width}}| {bot1_name + ' Color':<{col_width}}\n"
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        folder = 'simulation_results'
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        path = os.path.join('simulation_results', f"{bot1_name}_vs_{bot2_name}_results.txt")
        with open(path, "a") as log_file:
            log_file.write(f"Simulation started at: {current_time}\n")
            log_file.write(f"{bot1_name} vs. {bot2_name}\n\n")
            log_file.write(header)
            for result in data:
                log_file.write(f"{result[0]:<{col_width}}|{result[1]:<{col_width}}\n")
            # Write win count summary
            log_file.write(f"\n{bot1_name}: {win_count[bot1_name]}\n")
            log_file.write(f"{bot2_name}: {win_count[bot2_name]}\n")
            log_file.write(f"Draws: {win_count['Draw']}\n")
            log_file.write('-' * (col_width * 3 + 2) + '\n')  # Add a separator line

    def start_game(self, bot1, bot2, bot1_name, bot2_name, visual=False, bot1_white=True):
        current_bot = bot1 if bot1_white else bot2  # allows for order of start to change, more variety
        next_bot = bot2 if bot1_white else bot1
        current_bot_name = bot1_name if bot1_white else bot2_name
        next_bot_name = bot2_name if bot1_white else bot1_name
        while True:
            game_ended = current_bot()
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
        bot1_name = bot1.__class__.__name__
        bot2_name = bot2.__class__.__name__
        if bot1_name == bot2_name:
            bot2_name += "(1)"
        bot1_move = bot1.move
        bot2_move = bot2.move

        if visual:  # sets up renderer to show the game
            self.renderer = SimulationRenderer(self.game)

        data = []
        win_count = {bot1_name: 0, bot2_name: 0, "Draw": 0}
        bot1_white = True
        for i in range(num_games):
            if visual:
                self.renderer.bot1_white = bot1_white
            if bot1_white:
                color = "White"
            else:
                color = "Black"
            winner = self.start_game(bot1_move, bot2_move, bot1_name, bot2_name, visual, bot1_white)
            win_count[winner] += 1
            data.append([" " + winner, " " + color])
            bot1_white = not bot1_white
        self.log_results(bot1_name, bot2_name, data, win_count)


if __name__ == "__main__":
    simulate = Simulate()
    mode = 'nvisual'
    bot_1 = v1_Random(simulate.game)
    bot_2 = v2_Minimax_Eval(simulate.game)
    visual = mode == 'visual'
    profiler = cProfile.Profile()
    profiler.enable()
    simulate.run_simulations(100, bot_1, bot_2, visual=visual)
    profiler.disable()
    profiler.print_stats(sort='time')
