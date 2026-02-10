import pygame as pg
from engine import Game

def main():
    # Initialise pygame
    pg.init()

    # Setup
    # -----------------------------------------------------------------
    game = Game() # initialises game class
    board_width = 800 # Width of chess board (always do mult. of 8 so squares have int size)
    panel_width = 200 # Width of sidebar
    screen_width, screen_height = board_width + panel_width, board_width # defines screen dimmensions
    screen = pg.display.set_mode((screen_width,screen_height))
    pg.display.set_caption("BasicCarp") # sets window title
    clock = pg.time.Clock()
    running = True

    dragging_piece = None # Piece currently being dragged
    initial_piece_position = None # Location on board piece is dragged from

    # Load piece images
    w_pawn = pg.image.load("assets/pieces/white-pawn.png").convert_alpha() # convert alpha keeps the transpenerency of the pngs
    w_knight = pg.image.load("assets/pieces/white-knight.png").convert_alpha()
    w_bishop = pg.image.load("assets/pieces/white-bishop.png").convert_alpha()
    w_rook = pg.image.load("assets/pieces/white-rook.png").convert_alpha()
    w_queen = pg.image.load("assets/pieces/white-queen.png").convert_alpha()
    w_king = pg.image.load("assets/pieces/white-king.png").convert_alpha()
    b_pawn = pg.image.load("assets/pieces/black-pawn.png").convert_alpha()
    b_knight = pg.image.load("assets/pieces/black-knight.png").convert_alpha()
    b_bishop = pg.image.load("assets/pieces/black-bishop.png").convert_alpha()
    b_rook = pg.image.load("assets/pieces/black-rook.png").convert_alpha()
    b_queen = pg.image.load("assets/pieces/black-queen.png").convert_alpha()
    b_king = pg.image.load("assets/pieces/black-king.png").convert_alpha()

    # Create dictionary of piece images
    image_dict = {
        "P": w_pawn,
        "N": w_knight,
        "B": w_bishop,
        "R": w_rook,
        "Q": w_queen,
        "K": w_king,
        "p": b_pawn,
        "n": b_knight,
        "b": b_bishop,
        "r": b_rook,
        "q": b_queen,
        "k": b_king,
    }
    
    # Scale images to fit board square sizes
    square_width = board_width // 8 # // is integer division, .scale expects an int
    for key, img in image_dict.items():
        image_dict[key] = pg.transform.smoothscale(img,(square_width,square_width))
    

    # Define functions
    # ---------------------------------------------------------
    # Creates the chess board background surface
    def create_board_surface(): 
        board_surface = pg.Surface((board_width,board_width))
        light_colour = "white"
        dark_colour = "brown"

        for i in range(8):
            for j in range(8):
                if (i+j) % 2 == 0:
                    square_colour = light_colour
                else:
                    square_colour = dark_colour
                square = pg.Rect(
                    i*square_width,
                    j*square_width,
                    square_width,
                    square_width
                )
                pg.draw.rect(board_surface,square_colour,square)
        
        return board_surface
    
   # creates the side panel surface
    def create_side_panel_surface(): # creates the side panel surface
        panel_surface = pg.Surface((panel_width,board_width))
        background_colour = "gray"
        background = pg.Rect(0,0,panel_width,board_width)
        pg.draw.rect(panel_surface,background_colour,background)

        return panel_surface
    
    # Draws the board each frame according to game state from engine and ui dragging info
    def draw_pieces(): # draws pieces according to board state
        # draws board if we are dragging a piece
        if dragging_piece:
            row_intl, col_intl = initial_piece_position
            for row in range(8):
                for col in range(8):
                    piece = game.piece_at((row,col))
                    on_initial_square = row_intl == row and col_intl == col
                    # executes if there is a piece and we are not on the square that the dragged
                    # piece is from
                    if piece and not on_initial_square:
                        screen.blit(image_dict[piece],(square_width*col,square_width*row))  
            
            # Gets mouse posiion and draws dragging piece at mouse position
            mouse_x, mouse_y = pg.mouse.get_pos()
            img = image_dict[dragging_piece]
            screen.blit(
                img,
                (mouse_x - square_width // 2, # this math ensures piece is rendered with
                mouse_y - square_width // 2)  # cursor in middle of the piece
                )
        # draws board if we are not dragging a piece
        else:
            for row in range(8):
                for col in range(8):
                    piece = game.piece_at((row,col))
                    if piece: # executes if entry is not None
                        screen.blit(image_dict[piece],(square_width*col,square_width*row))

    # gets location of square in board state matrix from mouse position
    def get_current_square(position): 
        x, y = position
        if x < board_width and y < board_width:
            board_row = y // square_width # int division rounds down to give us correct indices
            board_col = x // square_width
            return board_row, board_col
        else:
            return None

    
    # Create surfaces before running game loop
    # ----------------------------------------------------------------
    board_surface = create_board_surface()
    panel_surface = create_side_panel_surface()

    # Start game loop
    # ----------------------------------------------------------------
    while running:
        # Checks for events in each frame
        for event in pg.event.get():
            # Changes running to false if quit button is pressed
            if event.type == pg.QUIT: 
                running = False
            
            # Logic for picking up a piece
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                clicked_square = get_current_square(event.pos)
                if clicked_square: # If func returns None, falsy so will not run
                    piece = game.piece_at(clicked_square) 
                    if piece: # If we have clicked an empty square, won't run
                        white_moving = piece.isupper() and game.is_whites_move 
                        black_moving = piece.islower() and not game.is_whites_move
                        correct_turn = white_moving or black_moving # true if trying to drag a piece on a correct turn
                        if correct_turn:
                            initial_piece_position = clicked_square
                            dragging_piece = piece
                        
            
            # Logic for putting down a piece
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if dragging_piece:
                    clicked_square = get_current_square(event.pos)
                    # Makes move if legal
                    if clicked_square and game.is_legal_move(initial_piece_position,clicked_square):
                        # Updates game state
                        game.make_move(initial_piece_position,clicked_square)
                        
                    # Stops dragging piece
                    dragging_piece = None
                    initial_piece_position = None
                    

        # Clear screen
        screen.fill("white")
        
        # Render objects
        screen.blit(board_surface,(0,0))
        screen.blit(panel_surface,(board_width,0))
        draw_pieces()
        
        # Displays objects on screen
        pg.display.flip()

        # Limits fps to 60
        clock.tick(60)
    
    # Quits game once loop is exited
    pg.quit()


# runs our main function
if __name__ == "__main__":
    main()