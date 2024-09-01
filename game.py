import pygame
import chess
import random


class Game:
    def __init__(self):
        self.board = chess.Board()  # python-chess chessboard

    def get_piece(self, pos):
        return self.board.piece_at(pos)

    def make_move(self, move):
        """
        Handle making a move.
        :return: -1 if move fails, 0 if move is success, 1 if game is over
        """
        try:
            if move in self.board.legal_moves:
                self.board.push(move)
                return self.check_game_state()
            elif self.is_promotion(move):
                # Convert the move to UCI, append 'q' for queen promotion, and convert back to a Move object
                move = chess.Move.from_uci(move.uci() + 'q')
                self.board.push(move)
                return self.check_game_state()
            else:
                # print("Invalid move")
                return -1
        except Exception as e:
            return f"Error: {e}"

    def is_promotion(self, move):
        # Check if the move is a pawn move
        if self.board.piece_at(move.from_square).piece_type == chess.PAWN:
            # Check if the pawn is moving to the last rank
            if (chess.square_rank(move.to_square) == 7 and self.board.turn == chess.WHITE) or \
                    (chess.square_rank(move.to_square) == 0 and self.board.turn == chess.BLACK):
                return True
        return False

    def check_game_state(self):
        """Returns 1 if game is over, else 0"""
        game_states = {
            "is_checkmate": "Checkmate! {winner} wins.",
            "is_stalemate": "Stalemate",
            "is_fivefold_repetition": "Five Fold Repetition",
            "is_insufficient_material": "Insufficient Material",
            "is_fifty_moves": "Fifty-Move Rule Draw",
            "can_claim_threefold_repetition": "Threefold Repetition Draw"
        }
        for state, message in game_states.items():
            if getattr(self.board, f'{state}')():
                if state == "checkmate":
                    winner = "Black" if self.board.turn else "White"
                    print(message.format(winner=winner))
                    return 1
                print(message)
                return 1
        return 0

    def engine_move(self):
        legal_moves = list(self.board.legal_moves)
        if len(legal_moves) == 0:
            return self.check_game_state()
        random_move = random.choice(legal_moves)
        self.board.push(random_move)
        return self.check_game_state()

    # TODO; store engines in one file, calling that engine method calls that engines move()
    def engine_move_other(self):
        legal_moves = list(self.board.legal_moves)
        if len(legal_moves) == 0:
            return self.check_game_state()
        random_move = random.choice(legal_moves)
        self.board.push(random_move)
        return self.check_game_state()

    def restart(self):
        """Logs the winner and resets the board for a new game."""
        self.board.reset()
        print("The game has been restarted.")

    def start_game(self, bot1, bot2, bot1_first=True):
        current_bot = bot1 if bot1_first else bot2
        next_bot = bot2 if bot1_first else bot1

        while True:
            game_ended = current_bot()
            if game_ended:
                winner = next_bot.__name__ if self.board.is_checkmate() else "Draw"
                self.restart()
                return winner
            current_bot, next_bot = next_bot, current_bot

    def run_simulations(self, num_games, bot1, bot2):
        data = []
        for i in range(num_games):
            winner = self.start_game(bot1, bot2)
            data.append(f"Game result: {winner}\n")

        # Join the list of strings into a single string with newline characters
        results = ''.join(data)
        # Write the results to the file
        with open("bot_vs_bot_game_results.txt", "a") as log_file:
            log_file.write(results)


if __name__ == "__main__":
    game = Game()
    game.run_simulations(50, game.engine_move, game.engine_move)

