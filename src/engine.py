# class for storing all important info in a position, and methods that purely access a position
class Position:
    def __init__(self,board,is_whites_move,K_position,k_position,
                 K_cq,K_ck,k_cq,k_ck,en_passant_target):
        self.board = board
        self.is_whites_move = is_whites_move
        self.K_position = K_position
        self.k_position = k_position
        self.K_cq = K_cq # White king can castle queenside
        self.K_ck = K_ck # White king can castle kingside
        self.k_cq = k_cq # Black king can castle queenside
        self.k_ck = k_ck # Black king can castle kingside
        self.en_passant_target = en_passant_target # Potential square that can be moved to by en passant, None if not possible
    
    # Gets piece at a given board sqaure
    def get_piece_at(self,square):
        row, col = square
        return self.board[row][col]
    
    # Gets a copy of the board
    def get_board_copy(self):
        return [row[:] for row in self.board]
    
    # Returns a copy of the current position
    def get_position_copy(self):
        board_copy = self.get_board_copy()
        return Position(board_copy, self.is_whites_move,
                self.K_position, self.k_position,
                self.K_cq, self.K_ck, self.k_cq, self.k_ck,self.en_passant_target)
    
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
            move_made = self.after_move(start_sqr,end_sqr)
            return not move_made._is_in_check(king_position)
        # move was not pseudolegal so cannot be made
        else:
            return False
    
    # Returns new position with move applied (presumed legal)
    def after_move(self,start_sqr,end_sqr,promoting_piece='q'):
        # creates a copy of the position we can modify
        new_position = self.get_position_copy()
        # gets our pieces that will be involved in the move
        piece = self.get_piece_at(start_sqr)
        taken_square = self.get_piece_at(end_sqr)

        # runs if moving piece is a pawn
        if piece.lower() == 'p':
            start_row, start_col = start_sqr
            end_row, end_col = end_sqr
            # if we have a two square pawn move, updates en_passant_target
            if abs(start_row-end_row) == 2:
                forward_dir = 1 if piece == 'p' else -1
                new_position.en_passant_target = (start_row+forward_dir,start_col)
            # makes en passant target None
            else:
                new_position.en_passant_target = None
                # Removes take en passant pawn from board, note that it uses old en_passant target as new one 
                # has already been updated
                if end_sqr == self.en_passant_target:
                    new_position._update_square((start_row,end_col),None)
                # handles promotion by black
                elif end_row == 7:
                    piece = promoting_piece.lower()
                # handles promotion by white
                elif end_row == 0:
                    piece = promoting_piece.upper()

        # runs when we don't have a pawn move
        else: 
            # updates en passant target
            new_position.en_passant_target = None
            # updates castling rights if we have a suitable rook move
            if piece == 'r':
                if self.k_ck and start_sqr == (0,7):
                    new_position.k_ck = False
                elif self.k_cq and start_sqr == (0,0):
                    new_position.k_cq = False
            elif piece == 'R':
                if self.K_ck and start_sqr == (7,7):
                    new_position.K_ck = False
                elif self.K_cq and start_sqr == (7,0):
                    new_position.K_cq = False

            # runs if we have a king move, handles castling
            elif piece.lower() == 'k':
                start_row, start_col = start_sqr
                end_col = end_sqr[1]
                # if king castles queenside updates rook position
                if start_col - end_col == 2:
                    rook = new_position.get_piece_at((start_row,0))
                    new_position._update_square((start_row,0),None)
                    new_position._update_square((start_row,end_col+1),rook)
                # if king castles kingside updates rook position
                elif start_col - end_col == -2:
                    rook = new_position.get_piece_at((start_row,7))
                    new_position._update_square((start_row,7),None)
                    new_position._update_square((start_row,end_col-1),rook)

                # updates castling flags
                # runs if white king move
                if piece == 'k':
                    new_position.k_position = end_sqr
                    new_position.k_ck = False
                    new_position.k_cq = False
                # runs if left king move
                else:
                    new_position.K_position = end_sqr
                    new_position.K_ck = False
                    new_position.K_cq = False
  
        
        # updates castling rights if we have a rook capture
        if taken_square and taken_square.lower() == 'r': # if taken_piece stops crash when we have an empty square
            if self.k_ck and end_sqr == (0,7):
                new_position.k_ck = False
            elif self.k_cq and end_sqr == (0,0):
                new_position.k_cq = False
            elif self.K_ck and end_sqr == (7,7):
                new_position.K_ck = False
            elif self.K_cq and end_sqr == (7,0):
                new_position.K_cq = False


        # updates moving piece position
        new_position._update_square(end_sqr,piece)
        new_position._update_square(start_sqr,None)
        
        # Updates move status
        new_position.is_whites_move = not self.is_whites_move
        return new_position
    
    # Returns true if a given move is a promotion
    def is_promotion(self,start_sqr,end_sqr):
        end_row = end_sqr[0]
        piece = self.get_piece_at(start_sqr)
        return end_row in (0,7) and piece.lower() == 'p'

    
    # gets legal moves in a position
    def get_legal_moves(self):
        pseudo_moves = self._get_pseudo_legal_moves()
        real_moves = []
        for move in pseudo_moves:
            new_pos = self.after_move(*move)
            # gets king position of moving sides king after move made
            king_position = new_pos.K_position if self.is_whites_move else new_pos.k_position
            # doesn't add move if it results in check
            if new_pos._is_in_check(king_position):
                continue
            # adds move if not in check
            else:
                real_moves.append(move)
        return real_moves

            

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
            if self.get_piece_at(checking_square):
                return False
            # otherwise increments to next checking square
            else:
                checking_square = (check_row+row_step,check_col+col_step)
        # returns true if no pieces in the way have been detected in the loop
        return True
    
    # checks if a square is attacked on a board
    def _is_square_attacked(self,square,by_white):
        # unpacks position
        row, col = square
        
        # defines direction that is forward for attacked side
        forward_direction = 1 if by_white else -1 
        
        # looks for checks except for knight checks
        directions = [(1,1),(-1,1),(-1,-1),(1,-1),(1,0),(-1,0),(0,1),(0,-1)]
        for direction in directions:
            row_direction = direction[0]
            col_direction = direction[1]
            
            # checks out all valid square in the given directions
            check_row = row + row_direction
            check_col = col + col_direction
            while True:
                # checks if we are checking a valid square on the board
                if self._is_square_on_board(check_row,check_col):
                    detected_piece = self.get_piece_at((check_row,check_col))
                    # checks if square non-empty
                    if detected_piece:
                        # breaks while loop if detects a piece of the same colour
                        if by_white != detected_piece.isupper():
                            break
                        # runs if we find a piece of attacking colour
                        else:
                            # runs if we are on a rook direction
                            if min(abs(row_direction),abs(col_direction)) == 0:
                                # checks for rook or queen attack
                                if detected_piece.lower() in ('r','q'):
                                    return True
                                # checks for king attack
                                elif detected_piece.lower() == 'k':
                                    if abs(check_row-row) == 1 or abs(check_col-col) == 1:
                                        return True
                                    else:
                                        break
                                else:
                                    break
                            # runs if we are on a bishop direction
                            else:
                                # checks for bishop or queen attack
                                if detected_piece.lower() in ('b','q'):
                                    return True
                                # checks for king attack
                                elif detected_piece.lower() == 'k':
                                    if abs(check_row-row) == 1:
                                        return True
                                    else:
                                        break
                                # checks for pawn check
                                elif detected_piece.lower() == 'p':
                                    if forward_direction == check_row - row: # checks pawn is one square ahead
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
        # looks for knight attacks
        knight_directions = [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
        for direction in knight_directions:
            row_direction, col_direction = direction
            check_row = row + row_direction
            check_col = col + col_direction
            # checks if we are checking a valid square on the board
            if self._is_square_on_board(check_row,check_col):
                detected_piece = self.get_piece_at((check_row,check_col))
                # checks if square non-empty
                if detected_piece:
                    # breaks while loop if detects a piece of the same colour
                    if by_white != detected_piece.isupper():
                        continue
                    else:
                        # checks if there is a knight on square
                        if detected_piece.lower() == 'n':
                            return True
                        # if not a knight continues
                        else:
                            continue
        # returns false if no attacks detected
        return False

    # checks if the king is in check when given king position and board
    def _is_in_check(self,king_position):
        by_white = self.get_piece_at(king_position).islower()
        return self._is_square_attacked(king_position,by_white)
    
    # Checks is a move is legal but does not account for checks, assumes that we have a piece on square
    def _is_pseudo_legal_move(self, start_sqr, end_sqr):
        # unpacks inputs
        start_row, start_col = start_sqr
        end_row, end_col = end_sqr
        row_dif = end_row - start_row
        col_dif = end_col - start_col
        # gets the piece that is moving and what is on the target square
        moving_piece = self.get_piece_at(start_sqr)
        target = self.get_piece_at(end_sqr)

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
                        return start_row == starting_rank and not self.get_piece_at((start_row+forward_unit,start_col))
                    # otherwise not allowed
                    else:
                        return False
                # runs for diagonal moves
                elif abs(col_dif) == 1 and row_dif == forward_unit:
                    # allows capture if there is a piece on the square or if it is an en passant target
                    return target or end_sqr == self.en_passant_target
                else:
                    return False

            # King movement rules
            else:
                # runs for a normal one square king move
                if max(abs(row_dif), abs(col_dif)) == 1:
                    return True
                # runs for black king castling
                # NB: castling logic does not check if will castle into check as this is handled by is_in_check later
                elif moving_piece == 'k':
                    # checks if target square is castling one and king has castling rights (kingside)
                    if end_sqr == (0,6) and self.k_ck:
                        # checks if path is clear for castling
                        if not self.get_piece_at((0,6)) and not self.get_piece_at((0,5)):
                            # returns true if king not in check and not castling through check
                            return not self._is_square_attacked((0,4),True) and not self._is_square_attacked((0,5),True)
                        else:
                            return False
                    # checks if target square is castling one and king has castling rights (queenside)
                    elif end_sqr == (0,2) and self.k_cq:
                        # checks if path is clear for castling
                        if not self.get_piece_at((0,1)) and not self.get_piece_at((0,2)) and not self.get_piece_at((0,3)):
                            # returns true if king not in check and not castling through check
                            return not self._is_square_attacked((0,4),True) and not self._is_square_attacked((0,3),True)
                        else:
                            return False
                    else:
                        return False
                # runs for white king castling
                else:
                    # checks if target square is castling one and king has castling rights (kingside)
                    if end_sqr == (7,6) and self.K_ck:
                        # checks if path is clear for castling
                        if not self.get_piece_at((7,6)) and not self.get_piece_at((7,5)):
                            # returns true if king not in check and not castling through check
                            return not self._is_square_attacked((7,4),False) and not self._is_square_attacked((7,5),False)
                        else:
                            return False
                    # checks if target square is castling one and king has castling rights (queenside)
                    elif end_sqr == (7,2) and self.K_cq:
                        # checks if path is clear for castling
                        if not self.get_piece_at((7,1)) and not self.get_piece_at((7,2)) and not self.get_piece_at((7,3)):
                            # returns true if king not in check and not castling through check
                            return not self._is_square_attacked((7,4),False) and not self._is_square_attacked((7,3),False)
                        else:
                            return False
                    else:
                        return False

    # Modifies a square on position's board
    def _update_square(self,square,piece):
        row, col = square
        self.board[row][col] = piece

    # gets pawn moves
    def _pawn_moves(self,square):
        pass

    # gets knight moves
    def _knight_moves(self,square):
        pass

    # gets bishop moves
    def _bishop_moves(self,square):
        pass

    # gets rook moves 
    def _rook_moves(self,square):
        # unpacks our start square
        row, col = square
        # defines directions for rooks moves
        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        # initialises move list
        moves = []
        for direction in directions:
            row_direction, col_direction = direction
            # checks out all valid square in the given directions
            check_row = row + row_direction
            check_col = col + col_direction
            while True:
                # checks if we are checking a valid square on the board
                if self._is_square_on_board(check_row,check_col):
                    detected_piece = self.get_piece_at((check_row,check_col))
                    # checks if square non-empty
                    if detected_piece:
                        # breaks while loop if detects a piece of the same colour
                        if self.is_whites_move == detected_piece.isupper():
                            break
                        # runs if we find a piece of opposite colour
                        else:
                            moves.append((square,(check_row,check_col)))
                            break
                    # if no pieces are detected, continues to next square
                    else:
                        moves.append((square,(check_row,check_col)))
                        check_row += row_direction
                        check_col += col_direction
                # break while loop when we reach end of board in one direction
                else:
                    break

    # gets king moves
    def _king_moves(self,square):
        pass

    # gets queen moves
    def _queen_moves(self,square):
        # unpacks our start square
        row, col = square
        # defines initial directions for queens
        directions = [(1,1),(-1,1),(-1,-1),(1,-1),(1,0),(-1,0),(0,1),(0,-1)]
        # initialises move list
        moves = []
        for direction in directions:
            row_direction, col_direction = direction
            # checks out all valid square in the given directions
            check_row = row + row_direction
            check_col = col + col_direction
            while True:
                # checks if we are checking a valid square on the board
                if self._is_square_on_board(check_row,check_col):
                    detected_piece = self.get_piece_at((check_row,check_col))
                    # checks if square non-empty
                    if detected_piece:
                        # breaks while loop if detects a piece of the same colour
                        if self.is_whites_move == detected_piece.isupper():
                            break
                        # runs if we find a piece of opposite colour
                        else:
                            moves.append((square,(check_row,check_col)))
                            break
                    # if no pieces are detected, continues to next square
                    else:
                        moves.append((square,(check_row,check_col)))
                        check_row += row_direction
                        check_col += col_direction
                # break while loop when we reach end of board in one direction
                else:
                    break

    # gets pseudo-legal moves for a piece in a particular position
    # assumes piece is correct colour to move
    def _get_pieces_pseudo_legal_moves(self,square,piece):
        if piece.lower() == 'p':
            return self._pawn_moves(square)
        elif piece.lower() == 'n':
            return self._knight_moves(square)
        elif piece.lower() == 'b':
            return self._bishop_moves(square)
        elif piece.lower() == 'r':
            return self._rook_moves(square)
        elif piece.lower() == 'k':
            return self._king_moves(square)
        elif piece.lower() == 'q':
            return self._queen_moves(square)

    # gets legal moves in a given position
    def _get_pseudo_legal_moves(self):
        moves = []
        # loops over board
        for row in range(8):
            for col in range(8):
                # gets board entry at square
                piece = self.get_piece_at((row,col))
                # runs if no piece detected
                if not piece:
                    continue
                # runs if detects an opposition piece
                elif self.is_whites_move != piece.isupper():
                    continue
                # runs if we find a piece with the correct colour
                else:
                    new_moves = self._get_pieces_pseudo_legal_moves((row,col),piece)
                    # adds unpacked list
                    moves.extend(new_moves)
        # returns pseudo legal moves
        return moves



# class for managing evolution of game
class Game:
    def __init__(self):
       # sets board state as usual chess starting position 
        initial_board_state = [
        ["r","n","b","q","k","b","n","r"],  # Black back rank
        ["p"]*8,                             # Black pawns
        [None]*8,                            
        [None]*8,
        [None]*8,
        [None]*8,
        ["P"]*8,                             # White pawns
        ["R","N","B","Q","K","B","N","R"]  # White back rank
        ]
        # sets up board state for standard chess starting position
        self.position = Position(initial_board_state,True,(7,4),(0,4),
                                 True,True,True,True,None)
        
        # Adds list of past moves
        self.move_history = []
    
    # modifies the game position
    def make_move(self,start_sqr,end_sqr,promoting_piece='q'):
        piece = self.position.get_piece_at(start_sqr)
        # Updates move history
        self.move_history.append((start_sqr,end_sqr,piece))
        # Updates game position
        self.position = self.position.after_move(start_sqr,end_sqr,promoting_piece)
    
