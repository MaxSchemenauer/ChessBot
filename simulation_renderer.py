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
    uci_list = ['b2b3', 'g8h6', 'g1f3', 'h8g8', 'f3g5', 'g8h8', 'g5f7', 'e8f7', 'e2e4', 'h8g8', 'c1b2', 'd8e8', 'b2g7', 'f7g7', 'b3b4', 'e8f7', 'f1e2', 'g8h8', 'h1f1', 'f7f4', 'e2f3', 'f4h2', 'f3e2', 'h2g2', 'd2d4', 'g2e4', 'c2c4', 'b8c6', 'c4c5', 'a8b8', 'd1d3', 'e4d3', 'e2d3', 'c6d4', 'd3h7', 'h8h7', 'a2a4', 'd4c2', 'e1d2', 'c2a1', 'c5c6', 'd7c6', 'f1c1', 'a1b3', 'd2e2', 'b3c1', 'e2d1', 'c1d3', 'b1c3', 'd3b4', 'c3d5', 'b4d5', 'f2f3', 'd5c3', 'd1c1', 'c3a4', 'c1c2', 'c8d7', 'f3f4', 'b8e8', 'c2d1', 'e8d8', 'd1d2', 'd8c8', 'd2e1', 'c8b8', 'e1f1', 'b8e8', 'f1g2', 'e8d8', 'g2h2', 'd8c8', 'f4f5', 'd7f5', 'h2g1', 'c8e8', 'g1h1', 'e8d8', 'h1g1', 'd8b8', 'g1f2', 'b8a8', 'f2g3', 'a8e8', 'g3f3', 'e8d8', 'f3f2', 'd8d7', 'f2e3', 'h7h8', 'e3f3', 'h8g8', 'f3f4', 'g7h8', 'f4e3', 'h8h7', 'e3f4', 'g8h8', 'f4e3', 'f8g7', 'e3f3', 'h8g8', 'f3e2', 'g8f8', 'e2e1', 'f8h8', 'e1f1', 'h8e8', 'f1g2', 'e8f8', 'g2f3', 'f8d8', 'f3e3', 'd8e8', 'e3e2', 'e8c8', 'e2f2', 'c8b8', 'f2g3', 'b8a8', 'g3f3', 'h7h8', 'f3g2', 'h8g8', 'g2f2', 'g8f8', 'f2g1', 'f8e8', 'g1f2', 'e8d8', 'f2g1', 'd8c8', 'g1g2', 'c8b8', 'g2f3', 'g7h8', 'f3f2', 'h8f6', 'f2g3', 'b8c8', 'g3f3', 'c8d8', 'f3e3', 'd8e8', 'e3e2', 'e8f8', 'e2f3', 'f8g8', 'f3f4', 'g8h8', 'f4f3', 'h8h7', 'f3e2', 'a8h8', 'e2f1', 'h8g8', 'f1e2', 'g8f8', 'e2f2', 'f8e8', 'f2e1', 'e8d8', 'e1f1', 'd8c8', 'f1e1', 'c8b8', 'e1f1', 'h7h8', 'f1g2', 'h8g8', 'g2h2', 'g8f8', 'h2g1', 'e7e6', 'g1f1', 'f8g8', 'f1f2', 'g8h8', 'f2e1', 'h8h7', 'e1e2', 'b8h8', 'e2f3', 'h8g8', 'f3f2', 'g8f8', 'f2e1', 'f8e8', 'e1f2', 'e8d8', 'f2g3', 'd8c8', 'g3f2', 'c8a8', 'f2e3', 'h7h8', 'e3f4', 'h8g8', 'f4g3', 'g8f8', 'g3g2', 'f8e8', 'g2f2', 'e8d8', 'f2f1', 'd8c8', 'f1g2', 'c8b8', 'g2f1', 'd7d8', 'f1e1', 'd8h8', 'e1f1', 'h8g8', 'f1e1', 'g8f8', 'e1f1', 'f8e8', 'f1e1', 'e8c8', 'e1f2', 'h6g8', 'f2g1', 'g8e7', 'g1h1', 'c8h8', 'h1g1', 'h8g8', 'g1f1', 'g8f8', 'f1f2', 'f8e8', 'f2e1', 'e8h8', 'e1d2', 'h8g8', 'd2c1', 'g8f8', 'c1d2', 'f8d8', 'd2e2', 'd8c8', 'e2d1', 'e7g8', 'd1c1', 'g8h6', 'c1d1', 'h6f7', 'd1e2', 'c8h8', 'e2f3', 'h8g8', 'f3e2', 'g8f8', 'e2f2', 'f8e8', 'f2e3', 'e8d8', 'e3e2', 'd8d7', 'e2f1', 'b8c8', 'f1f2', 'c8d8', 'f2f3', 'd8e8', 'f3e2', 'e8f8', 'e2f3', 'f8g8', 'f3g3', 'g8h8', 'g3h2', 'b7b6', 'h2g2', 'h8g8', 'g2h1', 'g8f8', 'h1g2', 'f8e8', 'g2h1', 'e8d8', 'h1g2', 'd8c8', 'g2h2', 'c8b8', 'h2h1', 'b8b7', 'h1h2', 'a8h8', 'h2g2', 'h8g8', 'g2f2', 'g8f8', 'f2e3', 'f8h8', 'e3f2', 'h8g8', 'f2e3', 'g8e8', 'e3f3', 'e8d8', 'f3f2', 'd8c8', 'f2e1', 'c8e8', 'e1f2', 'e8b8', 'f2e1', 'b8a8', 'e1f1', 'f7h8', 'f1f2', 'h8g6', 'f2g1', 'a8h8', 'g1g2', 'h8g8', 'g2g3', 'g8f8', 'g3f3', 'f8e8', 'f3g3', 'e8d8', 'g3h2', 'd8c8', 'h2g2', 'c8b8', 'g2h1', 'b8f8', 'h1g2', 'f8f7', 'g2g1', 'f7h7', 'g1f1', 'h7g7', 'f1e1', 'g7g8', 'e1f2', 'd7d8', 'f2f3', 'g8h8', 'f3e3', 'h8h2', 'e3f3', 'd8h8', 'f3e3', 'h8h7', 'e3f3', 'h7h6', 'f3g3', 'b7c8', 'g3f3', 'c8d8', 'f3e3', 'd8e8', 'e3f3', 'e8f8', 'f3g3', 'f8g8', 'g3f3', 'g8h8', 'f3g3', 'h8h7', 'g3f3', 'h7g7', 'f3e3', 'g7f7', 'e3f3', 'f7e7', 'f3g3', 'e7d7', 'g3f3', 'h6h3']
    print(len(uci_list))
    MOVE_DELAY = 0.25
    replay_game(uci_list)
