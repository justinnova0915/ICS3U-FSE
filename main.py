# Introduction to Computer Science (ICS3U)
# FSE May - June 2026

########## ========== IMPORTS =========== ##########
import  json

import  pygame

from    constants           import *
from    game.board          import Board
from    game.state          import State
from    ui.renderer         import Renderer
from    ui.animator         import Animator
import  ui.inputHandler     as     Input

import  ui.uiObject         as     ui
from    utils.vector        import Vector

########## ========= INITIALIZE ========= ##########
pygame.init()

SCREEN_FLAGS = pygame.RESIZABLE
screen = pygame.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)
pygame.display.set_caption("2048")

clock = pygame.time.Clock()
MAX_FPS  = 60
DT_MAX   = 0.5

state    = State.GAME
board    = Board()
# board._set_boardValues([
#     [0, 0, 0, 0],
#     [0, 0, 1024, 0],
#     [0, 1024, 0, 0],
#     [0, 0, 0, 0],
# ])
animator = Animator(board.board)
renderer = Renderer(screen, board.rows, board.cols, state)

def reset():
    global state, board, animator, renderer
    state    = State.GAME
    board    = Board()
    animator = Animator(board.board)
    renderer = Renderer(screen, board.rows, board.cols, state)

with open(pathJoin(ROOT_PATH, "data", "highscore.json")) as file:
    highscore = json.load(file)["highscore"]


textbox = ui.UIButton(
    size        = Size(125, 60),
    pos         = Vector(0, 0),
    onClick     =lambda: print(f"Button pressed"),
    iconSurface = ui.UITextbox(
        size         = Size(125, 60),
        pos          = Vector(0, 0),
        text         = "Hello World",
        font         = pygame.font.Font(FONT_FILENAME, 20),   
        colour       = (0, 0, 0),
        align        = 'c',
        bgColour     = (200, 200, 200),
        borderRad    = 10,
        borderWidth  = 2,
        borderColour = (0, 0, 0)
    ).surface
)


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

    match state:
    ########## ========== MENU ========== ##########
        case State.MENU:
            ########## ===== UPDATE ===== ##########
            ...
    
    ########## ========== GAME ========== ##########
        case State.GAME:
            ########## ===== UPDATE ===== ##########
            if inputState.gameAction == Input.GameActions.NEWGAME:
                reset()

            if inputState.gameAction in MOVE_ACTIONS: # Movement
                # Move board and spawn tile
                board.move(inputState.gameAction)
                if board.moved:
                    board.spawn_tile()
                # Check to update highscore
                if board.score > highscore:
                    highscore = board.score
                    # Write to highscore.json
                    with open(pathJoin(ROOT_PATH, "data", "highscore.json"), 'w') as file:
                        json.dump({"highscore" : highscore}, file, indent=4)
                # Setup for animation
                animator.startAnimation(board.board)
                # Remove extra 'merging' tiles
                board.cleanup()
                # Win | Lose gamestate
                if board.hasWon():
                    state = State.WIN
                if not board.hasLegalMove():
                    state = State.LOSE

    ########## ========== WIN =========== ##########
        case State.WIN:
            ########## ===== UPDATE ===== ##########
            if inputState.gameAction == Input.GameActions.NEWGAME:
                reset()
                state = State.GAME

    ########## ========== LOSE ========== ##########
        case State.LOSE:
            ########## ===== UPDATE ===== ##########
            if inputState.gameAction == Input.GameActions.NEWGAME:
                reset()
                renderer.reset(screen, board.rows, board.cols, state)
                state = State.GAME
    
    ########## ========== DRAW ========== ##########
    screen.fill(BG_COLOUR)
    animator.update(dt)
    renderer.render(state, board, animator.get_animatedTiles(), highscore, reset)

    textbox.render(dest=screen)

    ########## ======== DISPLAY ========= ##########
    pygame.display.flip()
    pygame.display.set_caption(f"{clock.get_fps():.0f}")

pygame.quit()