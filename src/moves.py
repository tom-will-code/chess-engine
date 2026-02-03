
def is_legal_move(board_state, start_sqr, end_sqr, is_whites_move):
    start_row, start_col = start_sqr
    end_row, end_col = end_sqr
    moving_piece = board_state[start_row][start_col]
    target = board_state[end_row][end_col]
    correct_turn = (moving_piece.isupper() and is_whites_move) or (moving_piece.islower() and not is_whites_move)


    if correct_turn:
        if start_sqr == end_sqr: # stops moves from the same square to the same square 
            return False
        elif not target: # runs if target square is empty
            return True
        elif moving_piece.isupper() == target.isupper(): # stops pieces taking pieces of the same colour
            return False
        else:
            return True
    else:
        return False
    
    
    