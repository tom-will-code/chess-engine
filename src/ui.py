import pygame as pg

def main():
    # Initialise pygame
    pg.init()

    # Setup
    width, height = 800, 600
    screen = pg.display.set_mode((width,height))
    clock = pg.time.Clock()
    running = True

    # Start game loop
    while running:
        # Checks for events in each frame
        for event in pg.event.get():
            # Changes running to false if quit button is pressed
            if event.type == pg.QUIT:
                running = False

        # Can fill screen to cover anything from previous frame
        # pg.fill("white")
        
        # RENDER OBJECTS
        
        # Displays objects on screen
        pg.display.flip()

        # Limits fps to 60
        clock.tick(60)
    
    # Quits game once loop is exited
    pg.quit()



if __name__ == "__main__":
    main()