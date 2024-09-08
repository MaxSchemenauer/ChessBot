import cProfile
import os

import chess
import chess.pgn
from game import Game
import time

from engines.v1_random import v1_Random
from engines.v2_eval import v2_Eval
from simulation_renderer import SimulationRenderer
from v3_minimax import v3_Minimax


class Simulate:

    def __init__(self):
        self.game = Game()
        self.renderer = None

    @staticmethod
    def log_results(bot1_name, bot2_name, data, win_count, uci_moves_list):
        col_width = max(len(bot1_name), len(bot2_name)) + 2
        header = f"{' Result':<{col_width}}| {'Winning Color':<{col_width}}\n"
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        folder = 'simulation_results'
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        path = os.path.join('simulation_results', f"{bot1_name}_vs_{bot2_name}_results.txt")
        with open(path, "a") as log_file:
            log_file.write(f"Simulation started at: {current_time}\n")
            log_file.write(f"{bot1_name} vs. {bot2_name}\n\n")
            log_file.write(header)
            i = 0
            for result in data:
                log_file.write(f"{result[0]:<{col_width}}|{result[1]:<{col_width}}| {uci_moves_list[i]}\n")
                i+=1
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
                # print(current_bot_name, "had last move")  # helping me detect likelihood a bot will draw
                winner = current_bot_name if self.game.board.is_checkmate() else "Draw"
                if visual:
                    self.renderer.game_ended = True
                    self.renderer.update_screen()
                    self.renderer.game_ended = False
                return winner
            # Swap bots and their names for the next turn
            current_bot, next_bot = next_bot, current_bot
            current_bot_name, next_bot_name = next_bot_name, current_bot_name
            if visual:
                self.renderer.update_screen()

    def run_simulations(self, num_games, bot1, bot2, visual=False):
        # initialize bot information
        bot1_name = bot1.__class__.__name__
        bot2_name = bot2.__class__.__name__
        if bot1_name == bot2_name:
            bot2_name += "(1)"
        bot1_move = bot1.move
        bot2_move = bot2.move
        if visual:  # sets up renderer to show the game
            self.renderer = SimulationRenderer(self.game)
        data = []
        uci_moves_list = []
        win_count = {bot1_name: 0, bot2_name: 0, "Draw": 0}
        bot1_white = True
        for i in range(num_games):
            if visual:  # update color of bot in simulation
                self.renderer.bot1_white = bot1_white
            if bot1_white:
                color = {bot1_name: "White", bot2_name: "Black", "Draw": ""}
            else:
                color = {bot1_name: "Black", bot2_name: "White", "Draw": ""}
            # play game
            winner = self.start_game(bot1_move, bot2_move, bot1_name, bot2_name, visual, bot1_white)
            # record stats, (winner, color, list of moves)
            win_count[winner] += 1
            data.append([" " + winner, " " + color[winner]])
            game = chess.pgn.Game.from_board(self.game.board)
            uci_moves = []
            for move in game.mainline_moves():
                uci_moves.append(move.uci())
            uci_moves_list.append(uci_moves)
            # reset bots and game, switch bots color
            bot1.reset()
            bot2.reset()
            self.game.restart()
            bot1_white = not bot1_white
        # finally, record all the results in a file
        self.log_results(bot1_name, bot2_name, data, win_count, uci_moves_list)


if __name__ == "__main__":
    simulate = Simulate()
    mode = 'visual'
    visual = mode == 'visual'
    bot_1 = v2_Eval(simulate.game)
    bot_2 = v3_Minimax(simulate.game)
    # profiler = cProfile.Profile()
    # profiler.enable()
    #start = time.time()
    simulate.run_simulations(1, bot_1, bot_2, visual=visual)
    # = time.time()
    # print("Simulation took", (end - start), "seconds.")
    # profiler.disable()
    # profiler.print_stats(sort='time')
