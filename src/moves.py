
def sign(number):
    if number > 0:
        return 1
    elif number < 0:
        return -1
    else:
        return 0

def is_square_on_board(row,col):
    return 0 <= row <= 7 and 0 <= col <= 7

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


def is_psuedo_legal_move(board_state, start_sqr, end_sqr):
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
        # Rook movement rules
        elif moving_piece in ('r','R'):
            if col_dif == 0 or row_dif == 0:
                return is_path_clear(board_state,start_sqr,end_sqr) 
            else:
                return False
        # Knight movement rules
        elif moving_piece in ('n','N'):
            return (abs(row_dif) == 2 and abs(col_dif) == 1) or (abs(col_dif)==2 and abs(row_dif)==1)
        # Pawn movement rules
        elif moving_piece in ('p','P'):
            forward_unit = -1 if moving_piece == 'P' else 1
            starting_rank = 6 if moving_piece == 'P' else 1
            
            if col_dif == 0 and not target:
                if row_dif == forward_unit:
                   return True
                elif row_dif == 2*forward_unit:
                   return start_row == starting_rank and not board_state[start_row+forward_unit][start_col]
                else:
                    return False
            return abs(col_dif) == 1 and row_dif == forward_unit and target
        # King movement rules
        elif moving_piece in ('k','K'):
            return max(abs(row_dif), abs(col_dif)) == 1
        
def is_in_check(board_state,start_sqr,end_sqr):
    start_row, start_col = start_sqr
    end_row, end_col = end_sqr
    moving_piece = board_state[start_row][start_col]
    
    # looks for checks if king has moved
    if moving_piece in ('k','K'):
        # board_copy = board_state <---- not this because lists are mutable objects
        board_copy = [row[:] for row in board_state] #CHANGE CODE SO BOARD NOT CHANGED AT ALL
        board_copy[start_row][start_col] = None
        board_copy[end_row][end_col] = moving_piece
        king_is_white = moving_piece.isupper()
        forward_direction = -1 if king_is_white else 1 # row direction that is forward for king
        
        # looks for bishop, pawn and queen checks
        for row_direction in [-1, 1]:
            for col_direction in [-1, 1]:
                check_row = end_row + row_direction # king has moved to end square
                check_col = end_col + col_direction
                keep_checking = True
                while keep_checking:
                    if is_square_on_board(check_row,check_col):
                        detected_piece = board_copy[check_row][check_col]
                        if detected_piece:
                            if king_is_white == detected_piece.isupper():
                                break
                            else:
                                if detected_piece.lower() in ('b','q'):
                                    return True
                                elif detected_piece.lower() == 'p':
                                    if forward_direction == check_row - end_row:
                                        return True
                                    else:
                                        break
                                else:
                                    break

                        else:
                            check_row += row_direction
                            check_col += col_direction
                    else:
                        break
    # Looks for checks if king hasn't moved
    else:
        return False # returns false for now




def is_legal_move(board_state,start_sqr,end_sqr):
    if is_psuedo_legal_move(board_state,start_sqr,end_sqr):
        return not is_in_check(board_state,start_sqr,end_sqr)
    else:
        return False


    
    
