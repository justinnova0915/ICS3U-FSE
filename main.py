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

def handle_newGame(action: str | None) -> bool:
    if action == "new_game":
        board.reset()
        return True
    return False

def move(action: str):
    board.move(action)
    moved = board.get_moved()
    animator.load_moved(moved)
    

running = True
while running:
    ########## ========== TIME ========== ##########
    dt = min(clock.tick(MAX_FPS) / 1000, DT_MAX)
    dt_accum += dt

    ########## ========= EVENTS ========= ##########
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    action = Input.get_action(events)
    
    ########## ========= UPDATE ========= ##########
    if state == State.GAME:
        if action in MOVE_ACTIONS:
            board.move(action)
            if board.hasWon():
                state = State.WIN
            if not board.hasLegalMove():
                state = State.LOSE

    elif state == State.WIN:
        if handle_newGame(action):
            state = State.GAME

    elif state == State.LOSE:
        if handle_newGame(action):
            state = State.GAME

    elif state == State.MENU:
        if handle_newGame(action):
            state = State.GAME

    if dt_accum >= DT_STEP:
        dt_accum -= DT_STEP
        ### ...(DT_STEP)


    ########## ========== DRAW ========== ##########
    screen.fill(BACKGROUND_COLOUR)
    renderer.draw(board, state)

    ########## ======== DISPLAY ========= ##########
    pygame.display.flip()

pygame.quit()
