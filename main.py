# Introduction to Computer Science (ICS3U)
# FSE May - July 2026

########## ========== IMPORTS =========== ##########
import json

import pygame

from   constants        import *
from   game.board       import Board
from   game.state       import State
from   ui.renderer      import Renderer
from   ui.animator      import Animator
import ui.input_handler as     Input

########## ========= INITIALIZE ========= ##########
pygame.init()

SCREEN_FLAGS = pygame.RESIZABLE
screen = pygame.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)
pygame.display.set_caption("2048")

clock = pygame.time.Clock()
MAX_FPS  = 60
DT_STEP  = 1 / MAX_FPS
DT_MAX   = 0.5
dt_accum = 0

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


########## ========= GAME LOOP ========== ##########
running = True
while running:

    ########## ========== TIME ========== ##########
    dt = min(clock.tick(MAX_FPS) / 1000, DT_MAX)

    ########## ========= EVENTS ========= ##########
    events = pygame.event.get()

    # Pygame Events
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    
    # Input handling
    action = Input.get_action(events)
    
    ########## ========= UPDATE ========= ##########
    if state == State.GAME:
        if action in MOVE_ACTIONS: # Movement
            # Move board and spawn tile
            board.move(action)
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

        # New game
        if action == "new_game":
            reset()

    elif state == State.WIN:
        if action == "new_game":
            board.reset()
            renderer.reset(screen, board.rows, board.cols, state)
            state = State.GAME

    elif state == State.LOSE:
        if action == "new_game":
            board.reset()
            renderer.reset(screen, board.rows, board.cols, state)
            state = State.GAME

    elif state == State.MENU:
        if action == "new_game":
            board.reset()
            state = State.GAME
    
    ########## ========== DRAW ========== ##########
    screen.fill(BACKGROUND_COLOUR)
    animator.update(dt)
    renderer.render(state, board, animator.get_animatedTiles(), highscore, reset)

    pygame.display.set_caption(f"{clock.get_fps():.0f}")

    ########## ======== DISPLAY ========= ##########
    pygame.display.flip()

pygame.quit()