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

# Track original aspect ratio based on your initial SCREEN_SIZE constant
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = SCREEN_SIZE
TARGET_ASPECT = VIRTUAL_WIDTH / VIRTUAL_HEIGHT

SCREEN_FLAGS = pygame.RESIZABLE
realScreen = pygame.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)
screen = pygame.Surface(SCREEN_SIZE)
pygame.display.set_caption("2048")
bgImage = pygame.image.load("./assets/twitterImage-removebg-preview.png").convert_alpha()

state = State.MENU
clock = pygame.time.Clock()
MAX_FPS  = 60
DT_STEP  = 1 / MAX_FPS
DT_MAX   = 0.5
dt_accum = 0

TIMER = 2

########## ========== UTILITIES =========== ##########
def calculate_scale_rect(win_w, win_h, target_aspect):
    """Calculates the centered destination rectangle to preserve aspect ratio."""
    current_aspect = win_w / win_h
    
    if current_aspect > target_aspect:
        # Window is too wide
        new_h = win_h
        new_w = int(win_h * target_aspect)
        offset_x = (win_w - new_w) // 2
        offset_y = 0
    else:
        # Window is too tall
        new_w = win_w
        new_h = int(win_w / target_aspect)
        offset_x = 0
        offset_y = (win_h - new_h) // 2
        
    return pygame.Rect(offset_x, offset_y, new_w, new_h)

def get_logical_mouse_pos(actual_pos, scale_rect, virtual_w, virtual_h):
    """Translates real window mouse coordinates back to virtual screen coordinates."""
    # Subtract layout margins accurately
    mx = actual_pos[0] - scale_rect.x
    my = actual_pos[1] - scale_rect.y
    
    # Avoid division by zero if window is collapsed or minimized
    if scale_rect.w <= 0 or scale_rect.h <= 0:
        return 0, 0
        
    # Downscale real window inputs into the fixed virtual space
    virtual_x = int(mx * (virtual_w / scale_rect.w))
    virtual_y = int(my * (virtual_h / scale_rect.h))
    
    return virtual_x, virtual_y

# Initialize scale positioning tracking
window_width, window_height = SCREEN_SIZE
scale_rect = calculate_scale_rect(window_width, window_height, TARGET_ASPECT)

# Cache Pygame's original mouse position function before we override it
_original_get_pos = pygame.mouse.get_pos

# Globally override pygame.mouse.get_pos so other modules get the corrected space
def patched_get_pos():
    raw_pos = _original_get_pos()
    return get_logical_mouse_pos(raw_pos, scale_rect, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

pygame.mouse.get_pos = patched_get_pos

########## ========== MODULES =========== ##########
board    = Board()
animator = Animator(board.board)
renderer = Renderer(screen, board.rows, board.cols, state, patched_get_pos())

########## ========= GAME LOOP ========== ##########

def restart():
    global state
    board.reset()
    animator.startAnimation(board.board)
    board.cleanup()
    renderer.reset(screen, board.rows, board.cols, state)
    state = State.GAME

def goToMenu():
    global state
    board.reset()
    animator.startAnimation(board.board)
    board.cleanup()
    renderer.reset(screen, board.rows, board.cols, state)
    state = State.MENU

running = True
while running:

    ########## ========== TIME ========== ##########
    dt = min(clock.tick(MAX_FPS) / 1000, DT_MAX)

    ########## ========= EVENTS ========= ##########
    raw_events = pygame.event.get()
    events = []

    # Pygame Events & Mouse Coordinate Transformation
    for event in raw_events:
        if event.type == pygame.QUIT:
            running = False
            events.append(event)
            
        elif event.type == pygame.VIDEORESIZE:
            # Update window bounds and recalculate aspect viewport
            window_width, window_height = event.w, event.h
            scale_rect = calculate_scale_rect(window_width, window_height, TARGET_ASPECT)
            events.append(event)
            
        # Reconstruct mouse events with corrected virtual coordinates
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            virtual_pos = get_logical_mouse_pos(event.pos, scale_rect, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
            
            # Map attributes to dict to create a new mutated event clone
            event_dict = dict(event.__dict__)
            event_dict['pos'] = virtual_pos
            if 'rel' in event_dict and scale_rect.w > 0 and scale_rect.h > 0:
                event_dict['rel'] = (
                    int(event.rel[0] * (VIRTUAL_WIDTH / scale_rect.w)), 
                    int(event.rel[1] * (VIRTUAL_HEIGHT / scale_rect.h))
                )
            
            cloned_event = pygame.event.Event(event.type, event_dict)
            events.append(cloned_event)
        else:
            # Pass keyboard/system events straight through
            events.append(event)
    
    # Input handling (Uses the clean mapped events)
    action = Input.get_action(events)
    
    ########## ========= UPDATE ========= ##########
    if state == State.GAME:
        ######## ========= INPUT ========== ########
        if action in MOVE_ACTIONS: # Movement
            if board.tryMove(action):
                board.spawn_tile()
            animator.startAnimation(board.board)
            board.cleanup()
            # Win | Lose gamestate
            if board.hasWon():
                state = State.WIN
            if not board.hasLegalMove():
                state = State.LOSE

        if action == "newGame": # New game
            board.reset()

        ######## ========= UPDATE ========= ########

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
    renderer.draw(state, board, animator.get_animatedTiles(), restart, goToMenu, events, patched_get_pos())

    pygame.display.set_caption(f"{clock.get_fps():.0f}")

    ########## ======== DISPLAY ========= ##########
    # 1. Clear physical window backbuffer
    realScreen.fill(BACKGROUND_COLOUR)
    
    # 2. Calculate aspect-safe image size, capping maximum height to 500px cleanly
    MAX_BG_HEIGHT = 500
    real_win_width = realScreen.get_width()
    real_win_height = realScreen.get_height()
    
    scaled_bg_height = int(bgImage.get_height() * (real_win_width / bgImage.get_width()))
    
    if scaled_bg_height > MAX_BG_HEIGHT:
        scaled_bg_height = MAX_BG_HEIGHT
        scaled_bg_width = int(bgImage.get_width() * (MAX_BG_HEIGHT / bgImage.get_height()))
    else:
        scaled_bg_width = real_win_width

    # 4. Scale and blit your actual game board layer LAST (on top of the background)
    scaled_surface = pygame.transform.smoothscale(screen, (scale_rect.w, scale_rect.h))
    realScreen.blit(scaled_surface, (scale_rect.x, scale_rect.y))
    

    if state == State.MENU:
        # 3. Blit the background FIRST so it sits safely under the interface layer
        scaled_bg = pygame.transform.smoothscale(bgImage, (scaled_bg_width, scaled_bg_height))
        bg_x = (real_win_width - scaled_bg_width) // 2
        realScreen.blit(scaled_bg, (bg_x, real_win_height - scaled_bg_height))
    
    pygame.display.flip()

pygame.quit()