# class for storing all important info in a position, and methods that purely access a position
class Position:
    def __init__(self,board,is_whites_move=True,K_position=(7,4),k_position=(0,4),
                 K_cq=True,K_ck=True,k_cq=True,k_ck=True,en_passant_target=None,legal_moves=None):
        self.board = board
        self.is_whites_move = is_whites_move
        self.K_position = K_position
        self.k_position = k_position
        self.K_cq = K_cq # White king can castle queenside
        self.K_ck = K_ck # White king can castle kingside
        self.k_cq = k_cq # Black king can castle queenside
        self.k_ck = k_ck # Black king can castle kingside
        self.en_passant_target = en_passant_target # Potential square that can be moved to by en passant, None if not possible
        self.legal_moves = legal_moves # caches legal moves in a position
    
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
            # adds move if not in check
            if not new_pos._is_in_check(self.is_whites_move):
                real_moves.append(move)
 
        return real_moves
    
    # Checks if a move is legal
    def is_legal_move(self,start_sqr,end_sqr):
        # gets legal moves in position
        legal_moves = self.get_legal_moves()
        # returns true if the attempted move is in legal moves
        return (start_sqr,end_sqr) in legal_moves


    # Helper functions
    # --------------------------------------------------------------
      
    # Checks if a row, col combination is on the board
    def _is_square_on_board(self,row,col):
        return 0 <= row <= 7 and 0 <= col <= 7
    
    # checks if a square is attacked on a board
    def _is_square_attacked(self,square,by_white):
        # unpacks position
        row, col = square
        # defines direction that is forward for attacked side
        forward_direction = 1 if by_white else -1 
        # looks for checks except for knight checks
        directions = [(1,1),(-1,1),(-1,-1),(1,-1),(1,0),(-1,0),(0,1),(0,-1)]
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
                    # continues while loop if detects a piece of the same colour
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
    def _is_in_check(self,white):
        king_position = self.K_position if white else self.k_position
        return self._is_square_attacked(king_position, not white)
    
    # Modifies a square on position's board
    def _update_square(self,square,piece):
        row, col = square
        self.board[row][col] = piece

    # gets pawn moves
    def _pawn_moves(self,square):
        # unpacks square
        row,col = square
        # gets our piece
        piece = self.get_piece_at(square)
        # gets our piece colour
        piece_white = piece.isupper()
        # defines forward direction
        forward_direction = -1 if piece_white else 1
        # initialises move list
        moves = []
        # runs if one square forward is empty
        if not self.get_piece_at((row+forward_direction,col)):
            moves.append((square,(row+forward_direction,col)))
            # checks for two square moves
            home_row = 6 if piece_white else 1
            # runs if on home row and target square is empty
            if row == home_row and not self.get_piece_at((row+2*forward_direction,col)):
                moves.append((square,(row+2*forward_direction,col)))
        # checks diagonal moves
        for diagonal in (1,-1):
            check_row = row + forward_direction
            check_col = col + diagonal
            # runs if square on board
            if self._is_square_on_board(check_row,check_col):
                detected_piece = self.get_piece_at((check_row,check_col))
                # runs if we have a diagonal capture or en passant
                if (detected_piece and detected_piece.isupper() != piece_white) or self.en_passant_target == (check_row,check_col):
                    moves.append((square,(check_row,check_col)))
        return moves


    # gets knight moves
    def _knight_moves(self,square):
        # unpacks square
        row,col = square
        # gets our piece
        piece = self.get_piece_at(square)
        # gets our piece colour
        piece_white = piece.isupper()
        # defines knight directions
        directions = [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
        # initialises moves list
        moves = []
        for direction in directions:
            row_direction, col_direction = direction
            check_row = row + row_direction
            check_col = col + col_direction
            # checks if we are checking a valid square on the board
            if self._is_square_on_board(check_row,check_col):
                detected_piece = self.get_piece_at((check_row,check_col))
                # runs if we are on an empty square or enemy piece
                if not (detected_piece and piece_white == detected_piece.isupper()):
                    moves.append((square,(check_row,check_col)))              
        return moves


    # gets bishop moves
    def _bishop_moves(self,square):
        # unpacks our start square
        row, col = square
        # gets our piece
        piece = self.get_piece_at(square)
        # gets our piece colour
        piece_white = piece.isupper()
        # defines initial directions for bishops
        directions = [(1,1),(-1,1),(-1,-1),(1,-1)]
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
                        if piece_white == detected_piece.isupper():
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
        return moves

    # gets rook moves 
    def _rook_moves(self,square):
        # unpacks our start square
        row, col = square
        # gets our piece
        piece = self.get_piece_at(square)
        # gets our piece colour
        piece_white = piece.isupper()
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
                        if piece_white == detected_piece.isupper():
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
        return moves

    # gets king moves
    def _king_moves(self,square):
        # unpacks square
        row,col = square
        # gets our piece
        piece = self.get_piece_at(square)
        # gets our piece colour
        piece_white = piece.isupper()
        # defines king directions
        directions = [(1,1),(-1,1),(-1,-1),(1,-1),(1,0),(-1,0),(0,1),(0,-1)]
        # initialises moves list
        moves = []
        # handles normal king moves
        for direction in directions:
            row_direction, col_direction = direction
            check_row = row + row_direction
            check_col = col + col_direction
            # checks if we are checking a valid square on the board
            if self._is_square_on_board(check_row,check_col):
                detected_piece = self.get_piece_at((check_row,check_col))
                # runs if we are on an empty square or enemy piece
                if not (detected_piece and piece_white == detected_piece.isupper()):
                    moves.append((square,(check_row,check_col)))              
        
        # handles castling
        home_row = 7 if piece_white else 0
        enemy_white = not piece_white
        
        # runs if has kingside castling rights
        if (self.K_ck if piece_white else self.k_ck):
            # runs if squares between king and rook are empty (kingside)
            if not self.get_piece_at((home_row,5)) and not self.get_piece_at((home_row,6)):
                # runs if king not in check or castling through check
                if not self._is_square_attacked((home_row,4),enemy_white) and not self._is_square_attacked((home_row,5),enemy_white) and not self._is_square_attacked((home_row,6),enemy_white):
                    moves.append((square,(home_row,6)))
        # runs if has queenside castling rights
        if (self.K_cq if piece_white else self.k_cq):
            # runs if squares between king and rook are empty (queenside)
            if not self.get_piece_at((home_row,3)) and not self.get_piece_at((home_row,2)) and not self.get_piece_at((home_row,1)):
                # runs if king not in check or castling through check
                if not self._is_square_attacked((home_row,4),enemy_white) and not self._is_square_attacked((home_row,3),enemy_white) and not self._is_square_attacked((home_row,2),enemy_white):
                    moves.append((square,(home_row,2)))
        
        return moves

    # gets queen moves
    def _queen_moves(self,square):
        # unpacks our start square
        row, col = square
        # gets our piece
        piece = self.get_piece_at(square)
        # gets our piece colour
        piece_white = piece.isupper()
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
                        if piece_white == detected_piece.isupper():
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
        return moves

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
        self.position = Position(initial_board_state)
        
        # Adds list of past moves
        self.move_history = []
    
    # modifies the game position
    def make_move(self,start_sqr,end_sqr,promoting_piece='q'):
        piece = self.position.get_piece_at(start_sqr)
        # Updates move history
        self.move_history.append((start_sqr,end_sqr,piece))
        # Updates game position
        self.position = self.position.after_move(start_sqr,end_sqr,promoting_piece)
    
