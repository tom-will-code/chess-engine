
class Game:
    def __init__(self):
       # sets board state as usual chess starting position 
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
        # Adds flags for various important game variables, like whether a player can
        # castle or who's turn to move it is
        # King positions are stored for check detection
        self.is_whites_move = True
        self.K_position = (7,4)
        self.k_position = (0,4)
        self.K_can_castle_kingside = True
        self.K_can_castle_queenside = True
        self.k_can_castle_kingside = True
        self.k_can_castle_queenside = True
    
    # Gets piece at a given board sqaure, the default board is the games state board
    def piece_at(self,square,board=None):
        row, col = square
        # Updates board_state as default
        if board is None:
            return self.board_state[row][col]
        # Updates passed board otherwise
        else:
            return board[row][col]
    
    # Creates a copy of the board state for actions like testing moves
    def get_board_copy(self):
        return [row[:] for row in self.board_state]
    
    # Checks if a move is legal
    def is_legal_move(self,start_sqr,end_sqr):
        # checks if move is legal without accounting for checks
        if self._is_pseudo_legal_move(start_sqr,end_sqr):
            # Gets what kings position would be after the move
            if start_sqr == self.k_position or start_sqr == self.K_position: # runs if we have a king move
                king_position = end_sqr
            else:
                king_position = self.K_position if self.is_whites_move else self.k_position # runs if we have a non-king move
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
        # updates king positions and castling rights if we have a king move
        if piece == 'k':
            self.k_position = end_sqr
            self.k_can_castle_kingside = False
            self.k_can_castle_queenside = False
        elif piece == 'K':
            self.K_position = end_sqr
            self.K_can_castle_kingside = False
            self.K_can_castle_queenside = False
        # updates castling rights if we have a suitable rook move
        elif piece == 'r':
            if self.k_can_castle_kingside and start_sqr == (0,7):
                self.k_can_castle_kingside = False
            elif self.k_can_castle_queenside and start_sqr == (0,0):
                self.k_can_castle_queenside = False
        elif piece == 'R':
            if self.K_can_castle_kingside and start_sqr == (7,7):
                self.K_can_castle_kingside = False
            elif self.K_can_castle_queenside and start_sqr == (7,0):
                self.K_can_castle_queenside = False
        
        # updates castling rights if we have a rook capture
        taken_piece = self.piece_at(end_sqr)
        if taken_piece and taken_piece.lower() == 'r': # if taken_piece stops crash when we have an empty square
            if self.k_can_castle_kingside and end_sqr == (0,7):
                self.k_can_castle_kingside = False
            elif self.k_can_castle_queenside and end_sqr == (0,0):
                self.k_can_castle_queenside = False
            elif self.K_can_castle_kingside and end_sqr == (7,7):
                self.K_can_castle_kingside = False
            elif self.K_can_castle_queenside and end_sqr == (7,0):
                self.K_can_castle_queenside = False

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
        # gets correct step in row and column direction to check paths
        start_row, start_col = start_sqr
        end_row, end_col = end_sqr
        row_dif = end_row - start_row
        col_dif = end_col - start_col
        row_step = self._sign(row_dif)
        col_step = self._sign(col_dif)
        
        # Loops over approriate squares and checks that the path is not blocked
        checking_square = (start_row+row_step,start_col+col_step)
        while checking_square != end_sqr:
            check_row, check_col = checking_square
            # returns false if a non empty square is detected
            if self.piece_at(checking_square):
                return False
            # otherwise increments to next checking square
            else:
                checking_square = (check_row+row_step,check_col+col_step)
        # returns true if no pieces in the way have been detected in the loop
        return True
    
    # Checks is a move is legal but does not account for checks
    def _is_pseudo_legal_move(self, start_sqr, end_sqr):
        # unpacks inputs
        start_row, start_col = start_sqr
        end_row, end_col = end_sqr
        row_dif = end_row - start_row
        col_dif = end_col - start_col
        # gets the piece that is moving and what is on the target square
        moving_piece = self.piece_at(start_sqr)
        target = self.piece_at(end_sqr)

        # stops moves from the same square to the same square
        if start_sqr == end_sqr:  
            return False
        # stops pieces taking pieces of the same colour
        elif target and moving_piece.isupper() == target.isupper(): 
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
                # checks diagonal moves
                if abs(col_dif) == abs(row_dif):
                    return self._is_path_clear(start_sqr,end_sqr)
                # checks rook like moves
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
                
                # checks if moving vertically and not taking a piece
                if col_dif == 0 and not target: 
                    # allows one square forward moves
                    if row_dif == forward_unit:
                        return True
                    # allows 2 square first move
                    elif row_dif == 2*forward_unit:
                        return start_row == starting_rank and not self.board_state[start_row+forward_unit][start_col]
                    # otherwise not allowed
                    else:
                        return False
                # allows diagonal captures
                return abs(col_dif) == 1 and row_dif == forward_unit and target
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
        
        # looks for checks except for knight checks
        directions = [(1,1),(-1,1),(-1,-1),(1,-1),(1,0),(-1,0),(0,1),(0,-1)]
        for direction in directions:
            row_direction = direction[0]
            col_direction = direction[1]
            
            # checks out all valid square in the given directions
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
                        else:
                            # runs if we are on a rook direction
                            if min(abs(row_direction),abs(col_direction)) == 0:
                                # checks for rook or queen check
                                if detected_piece.lower() in ('r','q'):
                                    return True
                                # checks for "king check", implements the you can't move near a king rule
                                elif detected_piece.lower() == 'k':
                                    if abs(check_row-king_row) == 1 or abs(check_col-king_col) == 1:
                                        return True
                                    else:
                                        break
                                else:
                                    break
                            # runs if we are on a bishop direction
                            else:
                                # checks for bishop or queen check
                                if detected_piece.lower() in ('b','q'):
                                    return True
                                # checks for "king check"
                                elif detected_piece.lower() == 'k':
                                    if abs(check_row-king_row) == 1:
                                        return True
                                    else:
                                        break
                                # checks for pawn check
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
        # looks for knight checks
        knight_directions = [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
        for direction in knight_directions:
            row_direction, col_direction = direction
            check_row = king_row + row_direction
            check_col = king_col + col_direction
            # checks if we are checking a valid square on the board
            if self._is_square_on_board(check_row,check_col):
                detected_piece = board_copy[check_row][check_col]
                # checks if square non-empty
                if detected_piece:
                    # breaks while loop if detects a piece of the same colour
                    if king_is_white == detected_piece.isupper():
                        continue
                    else:
                        # checks if there is a knight on square
                        if detected_piece.lower() == 'n':
                            return True
                        # if not a knight continues
                        else:
                            continue
        # returns true if no checks detected
        return False
    

    # Updates a square on chosen board, updates game state board by default
    def _update_square(self,square,piece,board=None):
        row, col = square
        # Updates game board by default
        if board is None:
            self.board_state[row][col] = piece
        # Updates passed board otheriwse
        else:
            board[row][col] = piece

    # Applies a move to a board without updating any flags like changing is_whites_turn, updates game board by default
    def _apply_move(self,start_sqr,end_sqr,piece,board=None):
        # runs if we have a king move, handles castling
        if piece.lower() == 'k':
            start_row, start_col = start_sqr
            end_col = end_sqr[1]
            # if king castles queenside updates rook position
            if start_col - end_col == 2:
                rook = self.piece_at((start_row,0),board)
                self._update_square((start_row,0),None,board)
                self._update_square((start_row,end_col+1),rook,board)
            # if king castles kingside updates rook position
            elif start_col - end_col == -2:
                rook = self.piece_at((start_row,7),board)
                self._update_square((start_row,7),None,board)
                self._update_square((start_row,end_col-1),rook,board)
        # updates moving piece position
        self._update_square(end_sqr,piece,board)
        self._update_square(start_sqr,None,board)
