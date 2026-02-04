
def sign(number):
    if number > 0:
        return 1
    elif number < 0:
        return -1
    else:
        return 0

def is_path_clear(board_state, start_sqr, end_sqr):
    start_row, start_col = start_sqr
    end_row, end_col = end_sqr
    row_dif = end_row - start_row
    col_dif = end_col - start_col
    row_step = sign(row_dif)
    col_step = sign(col_dif)
    
    checking_square = (start_row+row_step,start_col+col_step)
    while checking_square != end_sqr:
        check_row, check_col = checking_square
        if board_state[check_row][check_col]:
            return False
        else:
            checking_square = (check_row+row_step,check_col+col_step)
    return True


def is_legal_move(board_state, start_sqr, end_sqr):
    start_row, start_col = start_sqr
    end_row, end_col = end_sqr
    row_dif = end_row - start_row
    col_dif = end_col - start_col
    moving_piece = board_state[start_row][start_col]
    target = board_state[end_row][end_col]

    if start_sqr == end_sqr: # stops moves from the same square to the same square 
        return False
    elif target and moving_piece.isupper() == target.isupper(): # stops pieces taking pieces of the same colour
        return False
    else:
        # Bishop movement rules
        if moving_piece in ('b','B'):
            if abs(col_dif) == abs(row_dif):
                return is_path_clear(board_state,start_sqr,end_sqr)
            else:
                return False   
        # Queen movement rules
        elif moving_piece in ('q','Q'):
            if abs(col_dif) == abs(row_dif):
                return is_path_clear(board_state,start_sqr,end_sqr)
            elif col_dif == 0 or row_dif == 0:
                return is_path_clear(board_state,start_sqr,end_sqr)
            else:
                return False
            

        
        else:
            return True

    
    
