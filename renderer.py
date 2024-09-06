import pygame
import chess
import keyboard
import time

from game import Game
from engines.v2_eval import v2_Eval
from v3_minimax import v3_Minimax

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


class Renderer:
    def __init__(self, piece_color, game=Game(), engine=v3_Minimax):
        if piece_color == 'w':
            self.piece_color = chess.WHITE
        else:
            self.piece_color = chess.BLACK
        self.game = game
        self.white_engine = engine(game)
        self.black_engine = engine(game)
        self.game_ended = None
        pygame.init()
        pygame.display.set_caption('Chess AI')
        self.legal_moves = []  # keeps track of legal squares that selected piece can move to
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
        self.clock = pygame.time.Clock()
        self.move_from = None
        self.move_to = None
        self.selected_piece = None
        self.grabbed_piece = None
        self.piece_images = load_pieces()

    def get_square_from_pos(self, pos):
        """Convert pixel position to chessboard square."""
        x, y = pos
        row = y // SQUARE_SIZE
        col = x // SQUARE_SIZE
        if self.piece_color == chess.WHITE:
            row = 7 - row
        return chess.square(col, row)

    def draw_highlight(self, screen, square, highlight, col, row):
        """Helper function to draw highlights on the board."""
        pygame.draw.rect(screen, highlight, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_board(self, screen):
        """Draw the chessboard and pieces."""
        for row in range(8):
            for col in range(8):
                if self.piece_color == chess.WHITE:
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
                    (self.selected_piece and self.selected_piece[1] == square, highlight),
                    (self.move_to and self.move_to == square, highlight),
                    (self.move_from and self.move_from == square, highlight)]
                for condition, highlight_color in highlights:
                    if condition:
                        self.draw_highlight(screen, square, highlight_color, col, row)

                # Draw pieces, doesn't draw dragged piece
                piece = self.game.get_piece(square)
                if piece and not (self.grabbed_piece and self.grabbed_piece[1] == square):
                    piece_image = self.piece_images[piece.symbol()]
                    screen.blit(piece_image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Draw the piece being dragged at the mouse position
        if self.grabbed_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(self.piece_images[self.grabbed_piece[0].symbol()],
                        (mouse_x - SQUARE_SIZE // 2, mouse_y - SQUARE_SIZE // 2))

        if self.game_ended:
            self.draw_game_end_popup()

    def run(self):
        while True:
            if self.game_ended:
                self.handle_game_end_events()
            else:
                # if self.game.board.turn != self.piece_color:
                #     self.engine_move()
                self.handle_events()
            self.handle_keyboard_events()
            self.update_screen()
            self.clock.tick(60)

    def update_screen(self):
        self.screen.fill(BLACK)
        self.update_last_move()
        self.draw_board(self.screen)
        pygame.display.flip()

    def update_last_move(self):
        last_move = self.game.board.move_stack[-1] if self.game.board.move_stack else None
        if last_move:
            self.move_from = last_move.from_square
            self.move_to = last_move.to_square

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                move_status = -1
                click_pos = self.get_square_from_pos(pygame.mouse.get_pos())  # square from start of a move
                piece = self.game.get_piece(click_pos)
                if piece:  # clicked on a piece
                    if self.selected_piece:  # a piece is already selected, try to move to clicked piece
                        move_status = self.handle_move(self.selected_piece[1], click_pos)
                    if move_status == -1:  # if this move failed, select the clicked piece
                        self.selected_piece = (piece, click_pos)
                        self.grabbed_piece = (piece, click_pos)
                else:  # clicked on the board
                    if self.selected_piece:  # if a piece is selected try to move that piece
                        self.handle_move(self.selected_piece[1], click_pos)
                if self.selected_piece:
                    # TODO; display these moves
                    self.legal_moves = [move.to_square for move in self.game.board.legal_moves if
                                        move.from_square == click_pos]  # update legal moves of selected piece

            elif event.type == pygame.MOUSEBUTTONUP:
                click_pos = self.get_square_from_pos(pygame.mouse.get_pos())  # square of mouse click
                if self.selected_piece:  # if a piece is selected
                    piece, old_pos = self.selected_piece
                    if old_pos != click_pos:  # drag and drop, else would be single click
                        self.handle_move(old_pos, click_pos)
                self.grabbed_piece = None  # lets go grabbed piece on mouse up

    def handle_move(self, old_pos, new_pos):
        """
        handles a move made by a player, automatically responds with current engine
        @param old_pos: moving from what square (0-63)
        @param new_pos: moving to what square (0-63)
        @return: status of the move, -1 if failed, 0 if game ended, 1 otherwise
        """
        move = chess.Move(old_pos, new_pos)
        move_status = self.game.make_move(move)
        if move_status != -1:  # after valid move no piece should be selected
            self.selected_piece = None
            self.move_from = old_pos
            self.move_to = new_pos
        if move_status == 1:  # game ended
            self.game_ended = True
        return move_status

    def engine_move(self):
        if self.game.board.turn:
            move_status = self.white_engine.move() # white moves if its whites turn
        else:
            move_status = self.black_engine.move()  # black moves if its blacks turn

        # Get the start and end squares of the last move
        last_move = self.game.board.move_stack[-1] if self.game.board.move_stack else None
        if last_move:
            self.move_from = last_move.from_square
            self.move_to = last_move.to_square
        if move_status == 1:  # game ended
            self.game_ended = True
        return move_status

    def handle_keyboard_events(self):
        """
        allows user to make bot play. hold enter to play rapidly, and space to play slowly
        pressing 'r' restarts the game and logs the result
        :return:
        """
        if not self.game_ended:  # moves stop happening when game ends
            if keyboard.is_pressed('enter'):
                move_status = self.engine_move()
                if move_status == 1:
                    self.game_ended = True
                time.sleep(0.001)  # allows for move spamming
            if keyboard.is_pressed('space'):
                move_status = self.engine_move()
                if move_status == 1:
                    self.game_ended = True
                time.sleep(0.25)  # one move at a time
        if keyboard.is_pressed('r'):
            self.game.restart()
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

        # Draw "Renderer Over" text
        font = pygame.font.Font(None, 50)
        game_over_text = font.render("Game Over", True, text_color)
        self.screen.blit(game_over_text, (rect_x + rect_width / 2 - game_over_text.get_width() / 2,
                                          rect_y + rect_height / 2 - game_over_text.get_height() / 2))


if __name__ == "__main__":
    renderer = Renderer(piece_color='w')
    mode = 'play'
    if mode == 'play':
        renderer.run()
