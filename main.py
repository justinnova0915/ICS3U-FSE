<<<<<<< HEAD
import pygame
import math

width,height=800,600
screen=pygame.display.set_mode((width,height))

clock=pygame.time.Clock()

running=True

while running:
    for evt in pygame.event.get():
        if evt.type==pygame.QUIT:
            running=False
                       
    mx,my=pygame.mouse.get_pos()
    mb=pygame.mouse.get_pressed()
    
    clock.tick(60)
    pygame.display.flip()
            
quit()
=======
# Introduction to Computer Science (ICS3U)
# FSE May - July 2026

########## ========== IMPORTS =========== ##########
import json

import pygame

from   constants        import *
from   game.board       import Board
from   game.state       import State
from   ui.renderer      import Renderer
import ui.input_handler as     Input


import game.logic       as logic

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
renderer = Renderer(screen, board.rows, board.cols)

########## ========= GAME LOOP ========== ##########

state = State.GAME

def handle_newGame(action: str | None) -> bool:
    if action == "new_game":
        board.reset()
        return True
    return False

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
            if board.win:
                state = State.WIN
            if board.lose:
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

    if dt_accum >= TIMER:
        dt_accum %= TIMER


    ########## ========== DRAW ========== ##########
    screen.fill(BACKGROUND_COLOUR)
    renderer.draw(board, state)

    ########## ======== DISPLAY ========= ##########
    pygame.display.flip()

pygame.quit()
>>>>>>> e483a6b7e9926e955f2cfa2dc9b4b7593646de09
