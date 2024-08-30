import pygame
import chess

from ChessBoard import ChessBoard

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (237, 214, 176, 255)
DARK_BROWN = (184, 135, 98, 255)
HIGHLIGHT_COLOR = (0, 255, 0)
SQUARE_SIZE = 80


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


class Game:
    def __init__(self):
        self.legal_moves = []  # keeps track of legal squares that selected piece can move to
        # self.drag = False
        pygame.init()
        pygame.display.set_caption('Chess AI')
        self.screen = pygame.display.set_mode((640, 640))
        self.chessboard = ChessBoard()
        self.clock = pygame.time.Clock()
        self.mousedown_pos = None
        self.mouseup_pos = None
        self.selected_piece = None
        self.grabbed_piece = None
        self.piece_images = load_pieces()

    def draw_board(self, screen):
        """Draw the chessboard and pieces."""
        for row in range(8):
            for col in range(8):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(screen, color,
                                 pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

                # Highlight square if it's the selected square
                if self.selected_piece and self.selected_piece[1] == chess.square(col, 7 - row):
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR,
                                     pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

                # Draw pieces
                piece = self.chessboard.board.piece_at(chess.square(col, 7 - row))
                if piece and not (self.grabbed_piece and self.grabbed_piece[1] == chess.square(col, 7 - row)):
                    piece_image = self.piece_images[piece.symbol()]
                    screen.blit(piece_image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Draw the piece being dragged at the mouse position
        if self.grabbed_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(self.piece_images[self.grabbed_piece[0].symbol()],
                        (mouse_x - SQUARE_SIZE // 2, mouse_y - SQUARE_SIZE // 2))

    def run(self):
        while True:
            self.handle_events()
            self.update_screen()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                move_made = False
                self.mousedown_pos = get_square_from_pos(pygame.mouse.get_pos())  # square from start of a move
                piece = self.chessboard.get_piece(self.mousedown_pos)
                if piece:  # if clicking on a piece
                    if self.selected_piece:  # attempting to move to another piece's location
                        move = chess.Move(self.selected_piece[1], self.mousedown_pos)
                        move_made = self.chessboard.make_move(move)
                        print("clicking a new piece")
                    if not move_made:
                        self.selected_piece = (piece, self.mousedown_pos)
                        self.grabbed_piece = (piece, self.mousedown_pos)
                        self.legal_moves = [move.to_square for move in self.chessboard.board.legal_moves if
                                            move.from_square == self.mousedown_pos]
                else:
                    if self.selected_piece:
                        print("clicking board:", self.selected_piece)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouseup_pos = get_square_from_pos(pygame.mouse.get_pos())  # square of mouse click
                if self.selected_piece:  # if a piece is selected
                    piece, old_pos = self.selected_piece
                    if old_pos != self.mouseup_pos:  # attempting move to empty square
                        print("finish move")
                        move = chess.Move(old_pos, self.mouseup_pos)
                        self.chessboard.make_move(move)
                        self.selected_piece = None  # after move no piece should be selected
                else:
                    print("clicked board:", self.selected_piece)
                    self.selected_piece = None
                self.grabbed_piece = None  # lets go grabbed piece

    def update_screen(self):
        self.screen.fill(BLACK)
        self.draw_board(self.screen)
        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
