
import pygame

from    constants           import *
import  ui.inputHandler     as     Input
import  ui.uiObject         as     ui
from    utils.namedpair     import Size, Coord
from    utils.vector        import Vector

########## ========= INITIALIZE ========= ##########
pygame.init()

SCREEN_FLAGS = pygame.RESIZABLE
screen = pygame.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)
pygame.display.set_caption("2048")

clock = pygame.time.Clock()
MAX_FPS  = 60
DT_MAX   = 0.5

rect = ui.UIRect(
    size         = Size(100, 100),
    pos          = Vector(25, 25),
    bgColour     = (255, 150, 50),
    borderRad    = 15,
    borderWidth  = 8,
    borderColour = (255, 225, 100)
)

button = ui.UIButton(
    size        = Size(225, 75),
    pos         = Vector(SCREEN_SIZE//2),
    onClick     = lambda: print("Hello world"),
    iconSurface = ui.UITextbox(
        size         = Size(225, 75),
        pos          = Vector(0, 0),
        text         = "Button",
        font         = pygame.font.Font(FONT_FILENAME, 32),
        colour       = (100, 25, 100),
        align        = 'c',
        bgColour     = (255, 200, 255),
        borderRad    = 15,
        borderWidth  = 4,
        borderColour = (255, 150, 255)
    ).surface
)

uiManager = ui.UIManager([button])


########## ========= GAME LOOP ========== ##########
running = True
while running:
    
    ########## ========== TIME ========== ##########
    dt = min(clock.tick(MAX_FPS) / 1000, DT_MAX)

    ########## ========= EVENTS ========= ##########
    gameEvents = pygame.event.get()

    # Pygame Events
    for event in gameEvents:
        if event.type == pygame.QUIT:
            running = False
    
    # Input handling
    inputState = Input.get_inputState(gameEvents)

    ########## ========= UPDATE ========= ##########
    uiManager.update(inputState)


    ########## ========== DRAW ========== ##########
    screen.fill(BG_COLOUR)

    rect.render(dest=screen)

    button.render(dest=screen)

    ########## ======== DISPLAY ========= ##########
    pygame.display.flip()
    pygame.display.set_caption(f"{clock.get_fps():.0f}")

pygame.quit()