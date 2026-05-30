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

SCREEN_SIZE  = Size(900, 1000)
SCREEN_FLAGS = pygame.RESIZABLE
screen = pygame.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)
pygame.display.set_caption("2048")

clock = pygame.time.Clock()
MAX_FPS  = 60
DT_STEP  = 1 / MAX_FPS
DT_MAX   = 0.5
dt_accum = 0

TIMER = 2

########## ========== MODULES =========== ##########
board    = Board()
animator = Animator()
renderer = Renderer(screen, board.rows, board.cols)

########## ========= GAME LOOP ========== ##########

state = State.GAME

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
        # Movement
        if action in MOVE_ACTIONS:
            board.move(action)
            # Win | Lose gamestate
            if board.hasWon():
                state = State.WIN
            if not board.hasLegalMove():
                state = State.LOSE
        
        if action == "newGame":
            board.reset()

    elif state == State.WIN:
        if action == "new_game":
            board.reset()
            state = State.GAME

    elif state == State.LOSE:
        if action == "new_game":
            board.reset()
            state = State.GAME

    elif state == State.MENU:
        if action == "new_game":
            board.reset()
            state = State.GAME
    
    ########## ========== DRAW ========== ##########
    screen.fill(BACKGROUND_COLOUR)
    renderer.draw(board, state)

    ########## ======== DISPLAY ========= ##########
    pygame.display.flip()

pygame.quit()