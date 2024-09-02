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
MOVE_DELAY = 0.5
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
