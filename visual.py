import pygame
import chess
import keyboard
import time

from v1_random import v1_Random
from game import Game

SCREEN_WIDTH = 640
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (237, 214, 176, 255)
DARK_BROWN = (184, 135, 98, 255)
DARK_HIGHLIGHT_COLOR = (224, 196, 76)
LIGHT_HIGHLIGHT_COLOR = (248, 236, 116)
SQUARE_SIZE = 80
restart_button_rect = None
quit_button_rect = None


def get_square_from_pos(pos):
    """Convert pixel position to chessboard square."""
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return chess.square(col, 7 - row)


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


class Visual:
    def __init__(self, game=Game(), engine=v1_Random):
        self.pause = None
        self.chessboard = game
        self.engine = engine
        self.game_ended = None
        pygame.init()
        pygame.display.set_caption('Chess AI')
        self.legal_moves = []  # keeps track of legal squares that selected piece can move to
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
        self.clock = pygame.time.Clock()
        self.move_from = None
        self.move_to = None
        self.grabbed_piece = None
        self.piece_images = load_pieces()

    def draw_highlight(self, screen, square, highlight, col, row):
        """Helper function to draw highlights on the board."""
        pygame.draw.rect(screen, highlight, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_board(self, screen):
        """Draw the chessboard and pieces."""
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
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

                # Draw pieces, doesn't draw dragged piece
                piece = self.chessboard.get_piece(chess.square(col, 7 - row))
                if piece:
                    piece_image = self.piece_images[piece.symbol()]
                    screen.blit(piece_image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        if self.game_ended:
            self.draw_game_end_popup()

    def update_screen(self):
        self.screen.fill(BLACK)
        self.draw_board(self.screen)
        pygame.display.flip()

    def handle_events(self):
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
            if keyboard.is_pressed('space'):
                self.pause = True
        if keyboard.is_pressed('r'):
            self.chessboard.restart()
            self.move_from = None
            self.move_to = None
            self.game_ended = False
            time.sleep(0.1)  # one move at a time

    @staticmethod
    def handle_game_end_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

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