if event.type == pygame.MOUSEBUTTONDOWN:
    move_made = False
    self.mousedown_pos = get_square_from_pos(pygame.mouse.get_pos())  # square from start of a move
    piece = self.chessboard.get_piece(self.mousedown_pos)
    if piece:  # if clicking on a piece
        if self.selected_piece:  # a piece is already selected, try to move to clicked piece
            move = chess.Move(self.selected_piece[1], self.mousedown_pos)
            move_made = self.chessboard.make_move(move)
        if move_made == -1:  # if this move failed, select the clicked piece
            self.selected_piece = (piece, self.mousedown_pos)
            self.grabbed_piece = (piece, self.mousedown_pos)
            self.legal_moves = [move.to_square for move in self.chessboard.board.legal_moves if
                                move.from_square == self.mousedown_pos]  # update legal moves for selected piece for display
    else:  # clicked on the board, try to move there
        if self.selected_piece:
            move = chess.Move(self.selected_piece[1], self.mousedown_pos)
        if move == -1:
            self.selected_piece = self.chessboard.get_piece(self.mousedown_pos)



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
                if state == "is_checkmate":
                    winner = "Black" if self.board.turn else "White"
                    print(message.format(winner=winner))
                    return 1
                print(message)
                return 1
        return 0