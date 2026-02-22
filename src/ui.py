import pygame as pg
from engine import Game
import threading


class UIstate():
    STARTING = 0
    PlAYERS_MOVE = 1
    ENGINES_MOVE = 2
    GAME_OVER = 3


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

    # Flags for UI to handle piece dragging and pawn promotion
    dragging_piece = None # Piece currently being dragged
    initial_piece_position = None # Location on board piece is dragged from
    promoting = False # True if user is being queried about what piece to promote to
    promotion_move = None # Will track what square the player is trying to promote on

    # Flags for handling engine threading. There are in lists so they are mutable
    # so threading functions can handle them
    engine_thread = [None]
    engine_thinking = [False]
    engine_result = [None]

    # Loads font for text and creates text surfaces
    font = pg.font.Font("assets/fonts/Roboto/static/Roboto-Medium.ttf",22)
    thinking_surface = font.render(
        "Engine thinking...",
        True,              # antialiasing
        (255, 255, 255)    # text color
    )
    game_over_surface = font.render(
        "Game over!",
        True,
        (255, 255, 255) 
    )

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
    
    # used to call engine for search 
    def engine_worker(game, depth):
        score, move = game.search_to_depth(game.position, depth)
        engine_result[0] = move
        engine_thinking[0] = False
    
    # starts engine thread if engine is not thinking
    def start_engine_search(game, depth=4):
        if not engine_thinking[0]:
            engine_thinking[0] = True
            engine_result[0] = None
            engine_thread[0] = threading.Thread(
                target=engine_worker,
                args=(game, depth),
                daemon=True
            )
            engine_thread[0].start()


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
        dark_grey = (64, 64, 64)
        background = pg.Rect(0,0,panel_width,board_width)
        pg.draw.rect(panel_surface,dark_grey,background)
        return panel_surface
    
    # creates background rectangle from promotion visual
    def create_promotion_background():
        surface = pg.Surface((square_width,4*square_width))
        colour = "gray"
        rectangle = pg.Rect(0,0,square_width,4*square_width)
        pg.draw.rect(surface,colour,rectangle)
        return surface
    
    # Draws the board each frame according to game state from engine and ui dragging info
    def draw_pieces(): # draws pieces according to board state
        # draws board if we are dragging a piece
        if dragging_piece:
            for row in range(8):
                for col in range(8):
                    piece = game.position.get_piece_at((row,col))
                    on_initial_square = initial_piece_position == (row,col)
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
        elif promoting:
            # draws pieces excluding promoting pawn
            init_square = promotion_move[0]
            for row in range(8):
                for col in range(8):
                    piece = game.position.get_piece_at((row,col))
                    # runs if we have a piece that is not the pawn to be promoted
                    if piece and not init_square == (row,col):
                        screen.blit(image_dict[piece],(square_width*col,square_width*row))
            
            # draws promotion graphics
            prom_row = promotion_move[1][0]
            prom_col = promotion_move[1][1]
            if prom_row == 0:
                screen.blit(create_promotion_background(),(square_width*prom_col,square_width*prom_row))
                screen.blit(image_dict["Q"],(square_width*prom_col,0))
                screen.blit(image_dict["R"],(square_width*prom_col,square_width))
                screen.blit(image_dict["B"],(square_width*prom_col,2*square_width))
                screen.blit(image_dict["N"],(square_width*prom_col,3*square_width))

            else:
                screen.blit(create_promotion_background(),(square_width*prom_col,square_width*4))
                screen.blit(image_dict["q"],(square_width*prom_col,7*square_width))
                screen.blit(image_dict["r"],(square_width*prom_col,6*square_width))
                screen.blit(image_dict["b"],(square_width*prom_col,5*square_width))
                screen.blit(image_dict["n"],(square_width*prom_col,4*square_width))
        
        # draws board if we are not dragging a piece
        else:
            # draws pieces as seen when not dragging or promoting
            for row in range(8):
                for col in range(8):
                    piece = game.position.get_piece_at((row,col))
                    # runs if we have a piece 
                    if piece:
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

    # Sets uistate as starting
    ui_state = UIstate.STARTING

    # Create surfaces before running game loop
    # ----------------------------------------------------------------
    board_surface = create_board_surface()
    panel_surface = create_side_panel_surface()
    

    # Start game loop
    # ----------------------------------------------------------------
    while running:
        if ui_state == UIstate.STARTING:
            # Checks for events in each frame
            for event in pg.event.get():
                # Changes running to false if quit button is pressed
                if event.type == pg.QUIT: 
                    running = False
            # Automatically changes state to playing for now
            ui_state = UIstate.PlAYERS_MOVE
        
        elif ui_state == UIstate.PlAYERS_MOVE:
            # Checks for events in each frame
            for event in pg.event.get():
                # Changes running to false if quit button is pressed
                if event.type == pg.QUIT: 
                    running = False
                
                # Logic for picking up a piece when not promoting
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and not promoting:
                    clicked_square = get_current_square(event.pos)
                    # checks if we have clicked a square on board
                    if clicked_square:
                        piece = game.position.get_piece_at(clicked_square) 
                        # runs if we haven't clicked an empty square
                        if piece: 
                            # can only play engine as white currently
                            correct_turn = piece.isupper()
                            # if picked up white piece, saves piece and its initial position
                            if correct_turn:
                                initial_piece_position = clicked_square
                                dragging_piece = piece
                
                # Logic for putting down a piece (can't put down when promoting as picking up a piece is blocked)
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    # gets square we have clicked on board, if not on board returns None
                    clicked_square = get_current_square(event.pos)
                    
                    # runs if a piece is being dragged
                    if dragging_piece:
                        # Runs if move is legal
                        if clicked_square and game.position.is_legal_move(initial_piece_position,clicked_square):
                            # If there is a promotion, switches out of dragging mode into promoting mode
                            if game.position.is_promotion(initial_piece_position,clicked_square):
                                # saves promotion move
                                promotion_move = (initial_piece_position,clicked_square)
                                # changes promoting flag
                                promoting = True
                            # otherwise makes the move
                            else:
                                # makes move
                                game.make_move(initial_piece_position,clicked_square)
                                # updates ui state
                                if game.is_game_over():
                                    ui_state = UIstate.GAME_OVER
                                else:
                                    ui_state = UIstate.ENGINES_MOVE
                    
                        # Stops dragging piece when non-valid square is clicked
                        dragging_piece = None
                        initial_piece_position = None

                    # runs if we are promoting a piece
                    elif promoting:
                        # unpacks promotion move
                        init_square, prom_square = promotion_move
                        prom_row, prom_col = prom_square

                        # The code below ensures the four adjacent squares in the column of the promotion square,
                        # including the promotion square, will act as selection options for promotion pieces
                        
                        # gets turn state before promotion
                        old_turn = game.position.is_whites_move
                        
                        # runs if white promotion, black no inlcuded as a player yet
                        if prom_row == 0:
                            # queens selected
                            if clicked_square == (0,prom_col):
                                game.make_move(init_square,prom_square,'q')
                            # rook selected
                            elif clicked_square == (1,prom_col):
                                game.make_move(init_square,prom_square,'r')
                            # bishop selected
                            elif clicked_square == (2,prom_col):
                                game.make_move(init_square,prom_square,'b')
                            # knight selected
                            elif clicked_square == (3,prom_col):
                                game.make_move(init_square,prom_square,'n')
                        # gets turn state after promotion
                        new_turn = game.position.is_whites_move

                        # changes ui_state if move is made
                        if old_turn != new_turn:
                            # updates ui state
                            if game.is_game_over():
                                ui_state = UIstate.GAME_OVER
                            else:
                                ui_state = UIstate.ENGINES_MOVE

                        # Stops promotion mode
                        promoting = False
                        promotion_move = None

            # Clear screen
            screen.fill("white")
            
            # Render objects
            screen.blit(board_surface,(0,0))
            screen.blit(panel_surface,(board_width,0))
            draw_pieces()
            
            # Displays objects on screen
            pg.display.flip()


        elif ui_state == UIstate.ENGINES_MOVE:
            # makes move if engine has returned a move
            if engine_result[0] is not None:
                game.make_move(*engine_result[0])
                engine_result[0] = None
                # updates ui_state
                if game.is_game_over():
                    ui_state = UIstate.GAME_OVER
                else:
                    ui_state = UIstate.PlAYERS_MOVE
            # starts engine search if not already started
            else:
                start_engine_search(game)
            
            # Checks for events in each frame
            for event in pg.event.get():
                # Changes running to false if quit button is pressed
                if event.type == pg.QUIT: 
                    running = False
            # Clear screen
            screen.fill("white")
            
            # Render objects
            screen.blit(board_surface,(0,0))
            screen.blit(panel_surface,(board_width,0))
            draw_pieces()
            # Adds thinking text
            screen.blit(thinking_surface,(board_width+panel_width//10,panel_width//10))
            
            # Displays objects on screen
            pg.display.flip()

        elif ui_state == UIstate.GAME_OVER:
            # Checks for events in each frame
            for event in pg.event.get():
                # Changes running to false if quit button is pressed
                if event.type == pg.QUIT: 
                    running = False

            # Clear screen
            screen.fill("white")
            
            # Render objects
            screen.blit(board_surface,(0,0))
            screen.blit(panel_surface,(board_width,0))
            draw_pieces()

            # Adds game over text
            screen.blit(game_over_surface,(board_width+panel_width//10,panel_width//10))
            # Displays objects on screen
            pg.display.flip()

        # Limits fps to 60
        clock.tick(60)
    
    # Quits game once loop is exited
    pg.quit()


# runs our main function
if __name__ == "__main__":
    main()