
def is_legal_move(board_state, start_sqr, end_sqr):
    start_row, start_col = start_sqr
    end_row, end_col = end_sqr
    moving_piece = board_state[start_row][start_col]
    target = board_state[end_row][end_col]


    if start_sqr == end_sqr: # stops moves from the same square to the same square 
        return False
    elif target and moving_piece.isupper() == target.isupper(): # stops pieces taking pieces of the same colour
        return False
    else:
        # Bishop movement rules
        if moving_piece in ('b','B'):
            row_dif = end_row - start_row
            col_dif = end_col - start_col
            if abs(col_dif) == abs(row_dif):
                # defines direction of step in bishop movement
                row_step = row_dif // abs(row_dif)
                col_step = col_dif // abs(col_dif)
                # checks squares in path for other pieces
                checking_square = (start_row+row_step,start_col+col_step)
                while checking_square != end_sqr:
                    check_row, check_col = checking_square
                    if board_state[check_row][check_col]:
                        return False
                    else:
                        checking_square = (check_row+row_step,check_col+col_step)
                # returns True if path is clear
                return True
            else:
                return False   
        else:
            return True

    
    
