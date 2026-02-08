
class Game:
    def __init__(self):
        self.board_state = [
        ["r","n","b","q","k","b","n","r"],  # Black back rank
        ["p"]*8,                             # Black pawns
        [None]*8,                            
        [None]*8,
        [None]*8,
        [None]*8,
        ["P"]*8,                             # White pawns
        ["R","N","B","Q","K","B","N","R"]  # White back rank
        ]
        self.is_whites_move = True
        self.K_position = (7,4)
        self.k_position = (0,4)
    
    # Gets piece at a given board sqaure
    def piece_at(self,square):
        row, col = square
        return self.board_state[row][col]
    
    # Creates a copy of the board state for actions like testing moves
    def get_board_copy(self):
        return [row[:] for row in self.board_state]
    
    # Checks if a move is legal
    def is_legal_move(self,start_sqr,end_sqr):
        # checks if move is legal without accounting for checks
        if self._is_pseudo_legal_move(start_sqr,end_sqr):
            # Gets what kings position would be after the move
            if start_sqr == self.k_position or start_sqr == self.K_position:
                king_position = end_sqr
            else:
                king_position = self.K_position if self.is_whites_move else self.k_position
            # Creates board copy and makes the move on this board then looks for checks
            moving_piece = self.piece_at(start_sqr)
            board_copy = self.get_board_copy()
            self._apply_move(start_sqr,end_sqr,moving_piece,board_copy)
            return not self._is_in_check(king_position,board_copy)
        # move was not pseudolegal so cannot be made
        else:
            return False
        
    # Updates game by making a move (that has already been checked to be legal)
    def make_move(self,start_sqr,end_sqr):
        piece = self.piece_at(start_sqr)
        # updates king positions if we have a king move
        if piece == 'k':
            self.k_position = end_sqr
        elif piece == 'K':
            self.K_position = end_sqr
        # Updates board
        self._apply_move(start_sqr,end_sqr,piece)
        # Updates move status
        self.is_whites_move = not self.is_whites_move


        
    # Helper functions
    # --------------------------------------------------------------
    # Used to help define forward and backward directions for pawns
    def _sign(self,number):
        if number > 0:
            return 1
        elif number < 0:
            return -1
        else:
            return 0
        
    # Checks if a row col combination is on the board
    def _is_square_on_board(self,row,col):
        return 0 <= row <= 7 and 0 <= col <= 7
    
    # Checks if a piece has a clear path to its target square, used for rook, queen and bishop
    def _is_path_clear(self,start_sqr,end_sqr):
        start_row, start_col = start_sqr
        end_row, end_col = end_sqr
        row_dif = end_row - start_row
        col_dif = end_col - start_col
        row_step = self._sign(row_dif)
        col_step = self._sign(col_dif)
        
        checking_square = (start_row+row_step,start_col+col_step)
        while checking_square != end_sqr:
            check_row, check_col = checking_square
            if self.piece_at(checking_square):
                return False
            else:
                checking_square = (check_row+row_step,check_col+col_step)
        return True
    
    # Checks is a move is legal but does not account for checks
    def _is_pseudo_legal_move(self, start_sqr, end_sqr):
        start_row, start_col = start_sqr
        end_row, end_col = end_sqr
        row_dif = end_row - start_row
        col_dif = end_col - start_col
        moving_piece = self.piece_at(start_sqr)
        target = self.piece_at(end_sqr)

        if start_sqr == end_sqr: # stops moves from the same square to the same square 
            return False
        elif target and moving_piece.isupper() == target.isupper(): # stops pieces taking pieces of the same colour
            return False
        else:
            # Bishop movement rules
            if moving_piece in ('b','B'):
                if abs(col_dif) == abs(row_dif):
                    return self._is_path_clear(start_sqr,end_sqr)
                else:
                    return False   
            # Queen movement rules
            elif moving_piece in ('q','Q'):
                if abs(col_dif) == abs(row_dif):
                    return self._is_path_clear(start_sqr,end_sqr)
                elif col_dif == 0 or row_dif == 0:
                    return self._is_path_clear(start_sqr,end_sqr)
                else:
                    return False
            # Rook movement rules
            elif moving_piece in ('r','R'):
                if col_dif == 0 or row_dif == 0:
                    return self._is_path_clear(start_sqr,end_sqr) 
                else:
                    return False
            # Knight movement rules
            elif moving_piece in ('n','N'):
                return (abs(row_dif) == 2 and abs(col_dif) == 1) or (abs(col_dif)==2 and abs(row_dif)==1)
            # Pawn movement rules
            elif moving_piece in ('p','P'):
                forward_unit = -1 if moving_piece == 'P' else 1
                starting_rank = 6 if moving_piece == 'P' else 1
                
                if col_dif == 0 and not target: # checks if moving vertically and not taking a piece
                    if row_dif == forward_unit:
                        return True
                    elif row_dif == 2*forward_unit:
                        return start_row == starting_rank and not self.board_state[start_row+forward_unit][start_col]
                    else:
                        return False
                return abs(col_dif) == 1 and row_dif == forward_unit and target # checks for pawn captures
            # King movement rules
            elif moving_piece in ('k','K'):
                return max(abs(row_dif), abs(col_dif)) == 1
            
    # checks if the king is in check after a move (currently unfinished)
    def _is_in_check(self,king_position,board_copy):
        # defines king position
        king_row, king_col = king_position
        
        # determines king colour
        king_piece = board_copy[king_row][king_col]
        king_is_white = king_piece.isupper()

        # defines direction that is forward for king
        forward_direction = -1 if king_is_white else 1 # row direction that is forward for king
        
        # looks for bishop, pawn and diagonal queen checks
        for row_direction in [-1, 1]:
            for col_direction in [-1, 1]:
                check_row = king_row + row_direction
                check_col = king_col + col_direction
                while True:
                    # checks if we are checking a valid square on the board
                    if self._is_square_on_board(check_row,check_col):
                        detected_piece = board_copy[check_row][check_col]
                        # checks if square non-empty
                        if detected_piece:
                            # breaks while loop if detects a piece of the same colour
                            if king_is_white == detected_piece.isupper():
                                break
                            # checks if detected opposing bish, pawn or queen is checking king
                            else:
                                if detected_piece.lower() in ('b','q'):
                                    return True
                                elif detected_piece.lower() == 'p':
                                    if forward_direction == check_row - king_row: # checks pawn is one square ahead
                                        return True
                                    else:
                                        break
                                else:
                                    break
                        # if no pieces are detected, continues to next square
                        else:
                            check_row += row_direction
                            check_col += col_direction
                    # break while loop when we reach end of board in one direction
                    else:
                        break
       
    
    # Updates a square on chosen board, updates game state board by default
    def _update_square(self,square,piece,board=None):
        row, col = square
        if not board:
            self.board_state[row][col] = piece
        else:
            board[row][col] = piece

    # Applies a move to a board without updating any flags like changing is_whites_turn, updates game board by default
    def _apply_move(self,start_sqr,end_sqr,piece,board=None):
        self._update_square(end_sqr,piece,board)
        self._update_square(start_sqr,None,board)
