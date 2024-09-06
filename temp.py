def search(self, board, depth, last_move=None):
    if depth == 0:  # evaluate
        return self.evaluate(board)

    moves = list(board.legal_moves)
    # random.shuffle(moves)
    if len(moves) == 0:
        # print("zero")
        if board.is_checkmate():  # checkmate is the worst outcome
            return float('-inf')
        if board.is_stalemate() or self.is_potential_threefold_repetition(board):
            return 0  # is a draw

    best_eval = float('-inf')
    for move in moves:
        board.push(move)
        # print("\nevaluating" if depth==2 else f"\tresponse to {last_move}", move)
        eval = -self.search(board, depth - 1, last_move=move)
        if eval > best_eval:
            best_eval = eval
            if depth == 4:
                self.best_move = move
        if depth == 4:
            pass
            # print("my move results:", move, eval)
        board.pop()
    return best_eval