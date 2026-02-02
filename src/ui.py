import pygame as pg

def main():
    # Initialise pygame
    pg.init()

    # Setup
    board_width = 600 # Width of chess board
    panel_width = 200 # Width of sidebar
    screen_width, screen_height = board_width + panel_width, board_width
    screen = pg.display.set_mode((screen_width,screen_height))
    clock = pg.time.Clock()
    running = True

    # Define functions
    def create_board_surface():
        board_surface = pg.Surface((board_width,board_width))
        square_width = board_width / 8
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
    
    def create_side_panel_surface():
        panel_surface = pg.Surface((panel_width,board_width))
        background_colour = "gray"
        background = pg.Rect(0,0,panel_width,board_width)
        pg.draw.rect(panel_surface,background_colour,background)

        return panel_surface

    # Create surfaces
    board_surface = create_board_surface()
    panel_surface = create_side_panel_surface()

    # Start game loop
    while running:
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
        
        # Displays objects on screen
        pg.display.flip()

        # Limits fps to 60
        clock.tick(60)
    
    # Quits game once loop is exited
    pg.quit()



if __name__ == "__main__":
    main()