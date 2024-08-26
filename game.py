import pygame
import chess

from ChessBoard import ChessBoard

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT_COLOR = (0, 255, 0)
SQUARE_SIZE = 80


def get_square_from_pos(pos):
    """Convert pixel position to chessboard square."""
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return chess.square(col, row)


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
    return piece_images


class Game:
    def __init__(self):
        self.draggedpiece = None
        self.drag = False
        pygame.init()
        pygame.display.set_caption('Chess AI')
        self.screen = pygame.display.set_mode((640, 640))
        self.chessboard = ChessBoard()
        self.selected_square = None
        self.clock = pygame.time.Clock()
        self.start_pos = None
        self.end_pos = None
        self.selected_piece = None
        self.piece_images = load_pieces()

    def draw_board(self, screen):
        """Draw the chessboard and pieces."""
        for row in range(8):
            for col in range(8):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(screen, color,
                                 pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

                # Highlight square if it's the selected square
                if self.selected_square and self.selected_square == chess.square(col, row):
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR,
                                     pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

                # Draw pieces
                piece = self.chessboard.board.piece_at(chess.square(col, row))
                if piece: #and (self.draggedpiece is None or piece != self.draggedpiece):
                    screen.blit(self.piece_images[piece.symbol()], (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Draw the piece being dragged at the mouse position
        if self.drag and self.draggedpiece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(self.piece_images[self.draggedpiece.symbol()],
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
                pos = pygame.mouse.get_pos()
                self.start_pos = get_square_from_pos(pos)
                piece = self.chessboard.get_piece(self.start_pos)
                if piece:
                    self.drag = True
                    self.draggedpiece = piece
                    self.selected_piece = (piece, self.start_pos)
                    self.chessboard.legal_moves = [move.to_square for move in self.chessboard.board.legal_moves if
                                                   move.from_square == self.start_pos]

            elif event.type == pygame.MOUSEBUTTONUP:
                self.drag = False
                pos = pygame.mouse.get_pos()
                self.end_pos = get_square_from_pos(pos)  # Calculate the square where the piece should be dropped

                if self.selected_piece:
                    piece, old_pos = self.selected_piece
                    move = chess.Move(old_pos, self.end_pos)

                    if move in self.chessboard.board.legal_moves:
                        self.chessboard.make_move(move)

                self.draggedpiece = None
                self.selected_piece = None

    def handle_click_to_move(self):
        if self.start_pos and self.end_pos:
            move = chess.Move(self.start_pos, self.end_pos)
            if move in self.chessboard.board.legal_moves:
                self.chessboard.make_move(move)
            self.start_pos = None
            self.end_pos = None

    def update_screen(self):
        self.screen.fill(BLACK)
        self.draw_board(self.screen)
        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
