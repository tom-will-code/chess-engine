
def is_legal_move(board_state, start_sqr, end_sqr, is_whites_move):
    start_row, start_col = start_sqr
    end_row, end_col = end_sqr
    moving_piece = board_state[start_row][start_col]
    target = board_state[end_row][end_col]


    if start_sqr == end_sqr: # stops moves from the same square to the same square 
        return False
    elif target and moving_piece.isupper() == target.isupper(): # stops pieces taking pieces of the same colour
        return False
    else:
        moving_piece = moving_piece.lower()
        # Bishop movement rules
        if moving_piece == 'b':
            row_dif = abs(end_row - start_row)
            col_dif = abs(end_col - start_col)
            if col_dif == row_dif:
                return True
            else:
                return False   
        else:
            return True

    
    
