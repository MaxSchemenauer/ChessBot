import pygame
import chess
import keyboard
import time

from engines.v1_random import v1_Random
from game import Game

SCREEN_WIDTH = 640
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (237, 214, 176, 255)
DARK_BROWN = (184, 135, 98, 255)
DARK_HIGHLIGHT_COLOR = (224, 196, 76)
LIGHT_HIGHLIGHT_COLOR = (248, 236, 116)
SQUARE_SIZE = 80
MOVE_DELAY = 0
restart_button_rect = None
quit_button_rect = None


def load_pieces():
    """Load and scale images for pieces."""
    piece_images = {
        'P': pygame.transform.scale(pygame.image.load('images/white_pawn.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'N': pygame.transform.scale(pygame.image.load('images/white_knight.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'B': pygame.transform.scale(pygame.image.load('images/white_bishop.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'R': pygame.transform.scale(pygame.image.load('images/white_rook.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'Q': pygame.transform.scale(pygame.image.load('images/white_queen.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'K': pygame.transform.scale(pygame.image.load('images/white_king.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'p': pygame.transform.scale(pygame.image.load('images/black_pawn.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'n': pygame.transform.scale(pygame.image.load('images/black_knight.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'b': pygame.transform.scale(pygame.image.load('images/black_bishop.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'r': pygame.transform.scale(pygame.image.load('images/black_rook.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'q': pygame.transform.scale(pygame.image.load('images/black_queen.png'), (SQUARE_SIZE, SQUARE_SIZE)),
        'k': pygame.transform.scale(pygame.image.load('images/black_king.png'), (SQUARE_SIZE, SQUARE_SIZE))
    }
    for piece_image in piece_images.values():
        tint_color = (233, 229, 194)
        piece_image.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)
    return piece_images


class SimulationRenderer:
    def __init__(self, game=Game(), engine=v1_Random):
        self.pause = None
        self.bot1_white = False
        self.chessboard = game
        self.redo_move_stack = []
        self.game_ended = None
        pygame.init()
        pygame.display.set_caption('Chess AI')
        self.legal_moves = []  # keeps track of legal squares that selected piece can move to
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
        self.clock = pygame.time.Clock()
        self.move_from = None
        self.move_to = None
        self.piece_images = load_pieces()

    @staticmethod
    def draw_highlight(screen, square, highlight, col, row):
        """Helper function to draw highlights on the board."""
        pygame.draw.rect(screen, highlight, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def get_square_from_pos(self, pos):
        """Convert pixel position to chessboard square."""
        x, y = pos
        row = y // SQUARE_SIZE
        col = x // SQUARE_SIZE
        if self.bot1_white:
            row = 7 - row
        return chess.square(col, row)

    def draw_game_end_popup(self):
        # Define popup dimensions and colors
        global restart_button_rect, quit_button_rect
        rect_width = 300
        rect_height = 125
        rect_x = SCREEN_WIDTH / 2 - rect_width / 2
        rect_y = SCREEN_WIDTH / 2 - rect_height / 2
        popup_color = (0, 0, 0, 128)  # (R, G, B, A) with A = 128 for 50% transparency
        border_color = (255, 255, 255)
        text_color = (255, 255, 255)

        # Create a surface for the popup with an alpha channel (RGBA)
        popup_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        popup_surface.fill(popup_color)
        self.screen.blit(popup_surface, (rect_x, rect_y))
        pygame.draw.rect(self.screen, border_color, (rect_x, rect_y, rect_width, rect_height), 5)

        font = pygame.font.Font(None, 50)
        game_over_text = font.render("Game Over", True, text_color)
        self.screen.blit(game_over_text, (rect_x + rect_width / 2 - game_over_text.get_width() / 2,
                                          rect_y + rect_height / 2 - game_over_text.get_height() / 2))

    def draw_board(self, screen):
        """Draw the chessboard and pieces."""
        for row in range(8):
            for col in range(8):
                if self.bot1_white:
                    square = chess.square(col, 7 - row)
                else:
                    square = chess.square(col, row)
                if (row + col) % 2 == 0:  # light square
                    color = LIGHT_BROWN
                    highlight = LIGHT_HIGHLIGHT_COLOR
                else:
                    color = DARK_BROWN
                    highlight = DARK_HIGHLIGHT_COLOR

                # draws board
                pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE,
                                                            SQUARE_SIZE))

                # draws highlighted squares
                highlights = [
                    (self.move_to and self.move_to == square, highlight),
                    (self.move_from and self.move_from == square, highlight)]
                for condition, highlight_color in highlights:
                    if condition:
                        self.draw_highlight(screen, square, highlight_color, col, row)

                # Draw pieces
                piece = self.chessboard.get_piece(square)
                if piece:
                    piece_image = self.piece_images[piece.symbol()]
                    screen.blit(piece_image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        if self.game_ended:
            self.draw_game_end_popup()
        if self.pause:
            self.display_pause_text()

    def update_screen(self):
        self.screen.fill(BLACK)
        self.handle_events()
        self.handle_keyboard_events()
        self.update_last_move()
        self.draw_board(self.screen)
        pygame.display.flip()
        if not self.pause:
            self.delay_game()  # allows time after each move, can use keyboard controls

    @staticmethod
    def handle_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def handle_keyboard_events(self):
        """
        allows user to make bot play. hold enter to play rapidly, and space to play slowly
        pressing 'r' restarts the game and logs the result
        :return:
        """
        if not self.game_ended:  # moves stop happening when game ends
            if keyboard.is_pressed('space') and not self.pause:  # pauses game, only thing that pauses is the engine
                self.pause = True
                time.sleep(0.25)
                # resumes game is space is pressed or right arrow is pressed and no moves can be redone
                while (not keyboard.is_pressed('space') and
                       not (keyboard.is_pressed('right') and [] == self.redo_move_stack)):
                    self.update_screen()
                time.sleep(0.25)
                self.pause = False
                self.empty_redo_move_stack()

        if keyboard.is_pressed('left'):
            if self.chessboard.board.move_stack:
                self.redo_move_stack.append(self.chessboard.board.pop())
            self.move_from = None
            self.move_to = None
            time.sleep(0.25)

        if keyboard.is_pressed('right'):
            if self.redo_move_stack:
                self.chessboard.board.push(self.redo_move_stack.pop())
            self.move_from = None
            self.move_to = None
            time.sleep(0.25)

        if keyboard.is_pressed('r'):
            self.chessboard.restart()
            self.move_from = None
            self.move_to = None
            self.game_ended = False
            time.sleep(0.1)

    def update_last_move(self):
        last_move = self.chessboard.board.move_stack[-1] if self.chessboard.board.move_stack else None
        if last_move:
            self.move_from = last_move.from_square
            self.move_to = last_move.to_square

    def empty_redo_move_stack(self):
        while self.redo_move_stack:
            self.chessboard.board.push(self.redo_move_stack.pop())
            self.update_screen()  # allows for game to catch back up with moves that were undone

    def delay_game(self):
        duration = MOVE_DELAY
        start_time = time.time()
        while True:
            self.handle_events()
            elapsed_time = time.time() - start_time
            self.handle_keyboard_events()
            if elapsed_time > duration:
                break

    def display_pause_text(self):
        font = pygame.font.Font(None, 50)
        pause_text = font.render("paused", True, (255, 255, 255))
        location = (SCREEN_WIDTH / 2 - pause_text.get_width() / 2,
                    SCREEN_WIDTH / 2 - pause_text.get_height() / 2)
        self.screen.blit(pause_text, location)


def replay_game(uci_moves):
    rend = SimulationRenderer()
    i = 0
    while True:
        if i > len(uci_moves)-1:
            pass
        else:
            rend.chessboard.board.push(chess.Move.from_uci(uci_moves[i]))
            print("played", uci_moves[i])
            rend.chessboard.check_game_state()
            i += 1
        rend.update_screen()


if __name__ == "__main__":
    uci_list = ['g2g3', 'g8h6', 'f2f4', 'h8g8', 'f1h3', 'g8h8', 'h3d7', 'e8d7', 'd2d4', 'h6g8', 'd4d5', 'g8h6', 'c1d2', 'e7e6', 'd5e6', 'd7e6', 'b2b4', 'h8g8', 'b4b5', 'd8d5', 'h2h3', 'd5h1', 'b1a3', 'f8a3', 'g3g4', 'h6g4', 'h3g4', 'b7b6', 'e2e4', 'h1g1', 'e1e2', 'g1g4', 'e2e3', 'g4d1', 'a1d1', 'g8h8', 'e3f2', 'h8d8', 'f2g1', 'd8d7', 'd2e3', 'd7d1', 'g1h2', 'c8d7', 'e3b6', 'c7b6', 'c2c4', 'd1d2', 'h2g3', 'd2a2', 'c4c5', 'a3c5', 'g3f3', 'd7b5', 'f3g4', 'b8d7', 'g4g5', 'a8h8', 'g5g4', 'h8g8', 'f4f5', 'e6e7', 'g4g3', 'g8h8', 'g3g4', 'h8f8', 'g4h3', 'b5c6', 'e4e5', 'd7e5', 'h3g3', 'a2f2', 'g3h4', 'f2f5', 'h4g3', 'f8h8', 'g3h3', 'h8g8', 'h3h4', 'g8e8', 'h4g3', 'e8d8', 'g3h2', 'd8c8', 'h2g3', 'c8b8', 'g3h3', 'b8a8', 'h3h4', 'e7f8', 'h4g3', 'f8g8', 'g3h3', 'g8h8', 'h3h4', 'a8g8', 'h4h3', 'g8f8', 'h3h4', 'h8g8', 'h4g3', 'f8e8', 'g3h4', 'g8h8', 'h4h3', 'e8d8', 'h3h4', 'h8g8', 'h4g3', 'g8f8', 'g3h2', 'f8e8', 'h2g3', 'e8d7', 'g3h4', 'd8h8', 'h4g3', 'h8g8', 'g3h4', 'g8f8', 'h4g3', 'f8e8', 'g3h3', 'e8c8', 'h3h4', 'c8b8', 'h4g3', 'b8a8', 'g3h4', 'd7e8', 'h4h3', 'e8d8', 'h3g3', 'd8c8', 'g3h4', 'c8b8', 'h4g3', 'b8c7', 'g3h2', 'a8h8', 'h2g3', 'h8g8', 'g3h2', 'g8f8', 'h2h3', 'f8e8', 'h3h2', 'e8d8', 'h2h3', 'd8c8', 'h3g3', 'c8b8', 'g3h3', 'b8b7', 'h3g3', 'c7d8', 'g3h4', 'd8e8', 'h4g3', 'e8f8', 'g3h3', 'f8g8', 'h3h2', 'g8h8', 'h2h3', 'b7b8', 'h3h4', 'h8g8', 'h4g3', 'g8f8', 'g3h4', 'f8e8', 'h4g3', 'h7h6', 'g3h4', 'e8f8', 'h4g3', 'f8g8', 'g3h4', 'g8h8', 'h4g3', 'h8h7', 'g3h2', 'b8h8', 'h2g3', 'h8g8', 'g3h4', 'g8f8', 'h4g3', 'f8e8', 'g3h3', 'e8d8', 'h3h2', 'd8c8', 'h2h3', 'c8a8', 'h3g3', 'h7h8', 'g3h3', 'h8g8', 'h3h2', 'g8f8', 'h2g3', 'f8e8', 'g3h4', 'e8d8', 'h4h3', 'd8c8', 'h3h4', 'c8b8', 'h4h3', 'b8c7', 'h3h2', 'a8h8', 'h2h3', 'h8g8', 'h3h4', 'g8f8', 'h4g3', 'f8e8', 'g3h2', 'e8d8', 'h2g3', 'd8c8', 'g3h4', 'c8b8', 'h4g3', 'b8b7', 'g3h3', 'c7d8', 'h3h2', 'd8e8', 'h2g3', 'e8f8', 'g3h4', 'f8g8', 'h4g3', 'g8h8', 'g3h4', 'h8h7', 'h4g3', 'h7g6', 'g3h4', 'b7b8', 'h4g3', 'b8h8', 'g3h3', 'h8g8', 'h3g3', 'g8f8', 'g3h4', 'f8e8', 'h4g3', 'e8d8', 'g3h2', 'd8c8', 'h2g3', 'c8a8', 'g3h2', 'g6f6', 'h2g3', 'a8h8', 'g3h3', 'h8g8', 'h3h4', 'g8f8', 'h4g3', 'f8e8', 'g3h3', 'e8d8', 'h3g3', 'd8c8', 'g3h2', 'g7g6', 'h2h3', 'c8h8', 'h3h2', 'h8g8', 'h2g3', 'g8f8', 'g3h3', 'f8e8', 'h3h2', 'e8d8', 'h2g3', 'd8b8', 'g3h4', 'b8a8', 'h4h3', 'f6g7', 'h3h4', 'a8h8', 'h4g3', 'h8g8', 'g3h4', 'g8f8', 'h4h3', 'f8e8', 'h3g3', 'e8d8', 'g3h2', 'd8c8', 'h2g3', 'c8b8', 'g3h3', 'b8b7', 'h3h4', 'g7h8', 'h4g3', 'h8g8', 'g3h2', 'g8f8', 'h2h3', 'f8e8', 'h3g3', 'e8d8', 'g3h4', 'd8c8', 'h4h3', 'c8b8', 'h3g3', 'b8a8', 'g3h4', 'b7b8', 'h4g3', 'b8h8', 'g3h2', 'h8g8', 'h2g3', 'g8f8', 'g3h3', 'f8e8', 'h3h2', 'e8d8', 'h2g3', 'd8c8', 'g3h2', 'c8c7', 'h2h3', 'a8b8', 'h3h2', 'b8c8', 'h2h3', 'c8d8', 'h3h2', 'd8e8', 'h2g3', 'e8f8', 'g3h4', 'f8g8', 'h4h3', 'g8h8', 'h3g3', 'h8h7', 'g3h4', 'h7g7', 'h4g3', 'g7f6', 'g3h4', 'c7e7', 'h4h3', 'e7d7', 'h3h4', 'd7b7', 'h4h3', 'f6e7', 'h3h4', 'e7d7', 'h4g3', 'd7c7', 'g3h2', 'c7d6', 'h2h3', 'f7f6', 'h3h4', 'b7b8', 'h4h3', 'b8h8', 'h3h2', 'h8g8', 'h2h3', 'g8f8', 'h3g3', 'f8e8', 'g3h3', 'e8d8', 'h3h4', 'd8c8', 'h4h3', 'c8a8', 'h3g3', 'd6e7', 'g3h4', 'a8h8', 'h4g3', 'h8g8', 'g3h2', 'g8f8', 'h2g3', 'f8e8', 'g3h3', 'e8d8', 'h3h4', 'd8c8', 'h4h3', 'c8b8', 'h3h2', 'b8b7', 'h2g3', 'e7f8', 'g3h4', 'f8g8', 'h4g3', 'g8h8', 'g3h4', 'h8h7', 'h4g3', 'h7g7', 'g3h4', 'g7f7', 'h4h3', 'f7e8', 'h3g3', 'e8d8', 'g3h3', 'd8c8', 'h3h2', 'c8b8', 'h2h3', 'b8a8', 'h3h2', 'b7b8', 'h2h3', 'b8h8', 'h3h4', 'h8g8', 'h4h3', 'g8f8', 'h3h4', 'f8e8', 'h4h3', 'e8d8', 'h3g3', 'd8c8', 'g3h3', 'c8c7', 'h3h2', 'a8b8', 'h2h3', 'b8c8', 'h3h4', 'c8d8', 'h4h3', 'd8e8', 'h3g3', 'e8f8', 'g3h2', 'f8g8', 'h2g3', 'g8h8', 'g3h3', 'h8h7', 'h3h2', 'h7g7', 'h2g3', 'g7f7', 'g3h3', 'f7e7', 'h3h4', 'e7d7', 'h4g3', 'd7e6', 'g3h4', 'a7a6', 'h4g3', 'c7c8', 'g3h3', 'c8h8', 'h3h4', 'h8g8', 'h4h3', 'g8f8', 'h3g3', 'f8e8', 'g3h2', 'e8d8', 'h2g3', 'd8b8', 'g3h3', 'b8a8', 'h3h2', 'a8a7', 'h2h3', 'a7h7', 'h3h4', 'h7g7', 'h4h3', 'g7f7', 'h3h2', 'f7e7', 'h2g3', 'e7d7', 'g3h2', 'd7b7', 'h2h3', 'e6f7', 'h3h2', 'f7g8', 'h2g3', 'g8h8', 'g3h4', 'h8h7', 'h4h3', 'h7g7', 'h3h4', 'g7f8', 'h4g3', 'f8e8', 'g3h2', 'e8d8', 'h2h3', 'd8c8', 'h3h4', 'c8b8', 'h4g3', 'b8a8', 'g3h4', 'a8a7', 'h4g3', 'b7b8', 'g3h2', 'b8h8', 'h2g3', 'h8g8', 'g3h2', 'g8f8', 'h2h3', 'f8e8', 'h3g3', 'e8d8', 'g3h3', 'd8c8', 'h3g3', 'c8a8', 'g3h3', 'a7b8', 'h3h4', 'b8c8', 'h4g3', 'c8d8', 'g3h3', 'd8e8', 'h3h4', 'e8f8', 'h4h3', 'f8g8', 'h3h4', 'g8h8', 'h4h3', 'h8h7', 'h3g3', 'a8h8', 'g3h3', 'h8g8', 'h3h2', 'g8f8', 'h2g3', 'f8e8', 'g3h4', 'e8d8', 'h4h3', 'd8c8', 'h3h4', 'h6h5', 'h4h3', 'c8h8', 'h3g3', 'h8g8', 'g3h2', 'g8f8', 'h2h3', 'f8e8', 'h3h4', 'e8d8', 'h4g3', 'd8b8', 'g3h3', 'b8a8', 'h3g3', 'a8a7', 'g3h2', 'h7h8', 'h2h3', 'h8g8', 'h3h2', 'g8f8', 'h2g3', 'f8e8', 'g3h3', 'e8d8', 'h3g3', 'd8c8', 'g3h4', 'c8b8', 'h4g3', 'b8a8', 'g3h2', 'a8b7', 'h2h3', 'b7c7', 'h3h4', 'c7d7', 'h4h3', 'd7e7', 'h3h4', 'e7f7', 'h4g3', 'f7g7', 'g3h4', 'g7h6', 'h4g3', 'a7a8', 'g3h2', 'a8h8', 'h2h3', 'h8g8', 'h3g3', 'g8f8', 'g3h3', 'f8e8', 'h3g3', 'e8d8', 'g3h4', 'd8c8', 'h4h3', 'c8b8', 'h3h2', 'b8b7', 'h2g3', 'b7h7', 'g3h3', 'h7g7', 'h3h2', 'g7f7', 'h2h3', 'f7e7', 'h3h2', 'e7d7', 'h2g3', 'd7c7', 'g3h4', 'h6h7', 'h4g3', 'h7h8', 'g3h2', 'h8g8', 'h2g3', 'g8f8', 'g3h3', 'f8e8', 'h3h4', 'e8d8', 'h4g3', 'd8c8', 'g3h4', 'c8b8', 'h4g3', 'b8a8', 'g3h3', 'a8b7', 'h3g3', 'c7c8', 'g3h4', 'g6g5', 'h4h5', 'e5g6', 'h5g6', 'c6d7', 'g6h5', 'c8h8', 'h5g4', 'h8g8', 'g4h3', 'g8f8', 'h3g4', 'f8h8', 'g4g3', 'h8e8', 'g3h3', 'e8d8', 'h3g3', 'd8c8', 'g3h3', 'c8b8', 'h3g3', 'b8a8', 'g3g4', 'a8a7', 'g4h5', 'd7e8', 'h5h6', 'e8f7', 'h6h7', 'f7e6', 'h7h6', 'b7c8', 'h6g6', 'c8d8', 'g6h5', 'd8e8', 'h5g6', 'e8f8', 'g6h5', 'f8g8', 'h5g6', 'g8h8', 'g6h5', 'h8h7', 'h5g4', 'h7g7', 'g4h5', 'g7f7', 'h5h6', 'f7e7', 'h6h7', 'e7d7', 'h7h6', 'd7c7', 'h6g6', 'c7b8', 'g6h6', 'b8a8', 'h6h5', 'a7h7', 'h5g4', 'a8b8', 'g4g3', 'b8c8', 'g3g4', 'c8d8', 'g4g3', 'd8e8', 'g3g2', 'e8f8', 'g2g3', 'f8g8', 'g3g4', 'g8h8', 'g4g3', 'h8g7', 'g3g4', 'h7h8', 'g4g3', 'h8g8', 'g3g4', 'g8f8', 'g4h5', 'f8e8', 'h5g4', 'e8d8', 'g4h3', 'd8c8', 'h3g2', 'c8f8', 'g2h3', 'f8b8', 'h3g4', 'b8a8', 'g4g3', 'g7h8', 'g3h3', 'h8g8', 'h3g4', 'g8f8', 'g4g3', 'b6b5', 'g3h3', 'f8g8', 'h3h2', 'g8h8', 'h2g2', 'h8h7', 'g2h1', 'a8h8', 'h1h2', 'h8g8', 'h2h1', 'g8f8', 'h1g2', 'f8e8', 'g2g3', 'e8d8', 'g3h2', 'd8c8', 'h2h1', 'c8b8', 'h1h2', 'b8b7', 'h2g3', 'h7h8', 'g3h2', 'h8g8', 'h2h1', 'g8f8', 'h1h2', 'f8e8', 'h2g2', 'e8d8', 'g2g3', 'd8c8', 'g3g4', 'c8b8', 'g4g3', 'b8a8', 'g3g4', 'a8a7', 'g4g3', 'b7b8', 'g3h2', 'b8h8', 'h2g3', 'h8g8', 'g3h3', 'g8f8', 'h3h2', 'f8e8', 'h2h1', 'e8h8', 'h1g2', 'h8d8', 'g2h3', 'd8c8', 'h3g4', 'c8e8', 'g4g3', 'e8a8', 'g3h3', 'a7b8', 'h3h2', 'b8c8', 'h2h3', 'c8d8', 'h3h2', 'd8e8', 'h2h3', 'e8f7', 'h3h2', 'a8h8', 'h2g3', 'h8g8', 'g3h3', 'g8f8', 'h3g3', 'f8h8', 'g3g2', 'h8e8', 'g2h1', 'e8g8', 'h1h2', 'g8d8', 'h2h1', 'd8f8', 'h1h2', 'f8c8', 'h2h3', 'c8b8', 'h3h2', 'b8b7', 'h2g3', 'f7g7', 'g3h2', 'g7h6', 'h2g3', 'b7b8', 'g3g2', 'a6a5', 'g2h1', 'b8h8', 'h1g2', 'h8g8', 'g2h3', 'g8f8', 'h3g2', 'f8e8', 'g2h3', 'e8d8', 'h3g3', 'd8c8', 'g3h3', 'c8a8', 'h3g4', 'a8h8', 'g4h3', 'h8h7', 'h3g4', 'h7g7', 'g4g3', 'g7f7', 'g3h2', 'f7e7', 'h2h1', 'e7h7', 'h1g2', 'h7d7', 'g2h1', 'd7d8', 'h1h2', 'd8d6', 'h2h3', 'h6h7', 'h3g3', 'h7h8', 'g3g2', 'h8g8', 'g2h1', 'g8f8', 'h1g2', 'f8e8', 'g2h1', 'e8d8', 'h1h2', 'd8c8', 'h2g2', 'c8b8', 'g2h2', 'b8a8', 'h2g3', 'a8b7', 'g3g4', 'b7c8', 'g4g3', 'c8d7', 'g3g4', 'd7e8', 'g4g3', 'e8f7', 'g3h2', 'f7g7', 'h2g2', 'g7g6', 'g2h2', 'g6h5', 'h2g3', 'e6g8', 'g3g2', 'g8h7', 'g2h1', 'h7g6', 'h1g2', 'g6e8', 'g2h2', 'e8f7', 'h2g3', 'f7d5', 'g3h3', 'd6d8', 'h3h2', 'd8h8', 'h2h3', 'h8g8', 'h3g3', 'g8f8', 'g3h3', 'f8e8', 'h3g3', 'e8c8', 'g3h2', 'c8b8', 'h2h3', 'b8a8', 'h3h2', 'a8a7', 'h2g3', 'a7h7', 'g3h3', 'g5g4', 'h3h2', 'd5f7', 'h2h1', 'h7h8', 'h1g2', 'h8g8', 'g2h2', 'g8f8', 'h2g3', 'f8e8', 'g3g2', 'e8d8', 'g2g3', 'd8c8', 'g3h2', 'c8b8', 'h2h1', 'b8a8', 'h1h2', 'a8a7', 'h2g3', 'f7g8', 'g3h2', 'g8h7', 'h2h1', 'h7g6', 'h1g2', 'a7a8', 'g2g3', 'a8h8', 'g3h2', 'h8g8', 'h2h1', 'g8f8', 'h1g2', 'f8e8', 'g2h1', 'e8d8', 'h1h2', 'd8c8', 'h2h1', 'c8b8', 'h1g2', 'b8b7', 'g2g3', 'b7h7', 'g3h2', 'h7g7', 'h2g2', 'g7f7', 'g2g3', 'f7e7', 'g3h2', 'e7d7', 'h2h1', 'd7c7', 'h1h2', 'c7c6', 'h2h1', 'g6e8', 'h1h2', 'e8f7', 'h2g2', 'f7g8', 'g2g3', 'g8h7', 'g3h2', 'c6c8', 'h2g2', 'c8h8', 'g2h1', 'h8g8', 'h1g2', 'g8f8', 'g2h2', 'f8e8', 'h2g3', 'e8d8', 'g3h2', 'd8b8', 'h2g3', 'b8a8', 'g3h2', 'a8a6', 'h2h1', 'h7g8', 'h1h2', 'g8f7', 'h2g3', 'f7e8', 'g3h2', 'e8d7', 'h2h1', 'd7c8', 'h1h2', 'c8d7', 'h2g2', 'd7e6', 'g2h1', 'b5b4', 'h1h2', 'e6g8', 'h2h1', 'g8h7', 'h1h2', 'h7g6', 'h2g2', 'g6e8', 'g2h2', 'e8f7', 'h2h1', 'f7d5', 'h1h2', 'f5e5', 'h2g3', 'a6a8', 'g3f4', 'a8h8', 'f4g3', 'h8g8', 'g3h2', 'g8f8', 'h2g3', 'f8e8', 'g3f4', 'e8d8', 'f4g3', 'd8c8', 'g3h2', 'c8b8', 'h2g3', 'b8b7', 'g3h2', 'b7h7', 'h2g3', 'h7g7', 'g3h2', 'g7f7', 'h2g3', 'f7e7', 'g3h2', 'e7d7', 'h2g3', 'd7c7', 'g3f4', 'c7a7', 'f4g3', 'h5g5', 'g3h2', 'a7a8', 'h2g3', 'a8g8', 'g3h2', 'g8a8', 'h2g3', 'a8f8', 'g3h2']

    print(len(uci_list))
    MOVE_DELAY = 0.25
    replay_game(uci_list)
