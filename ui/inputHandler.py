from    dataclasses     import dataclass

import  pygame

from utils.vector import Vector


class GameActions():
    LEFT    = "left"
    RIGHT   = "right"
    UP      = "up"
    DOWN    = "down"
    NEWGAME = "newGame"

KEY_INPUTS = {
    pygame.K_LEFT   : GameActions.LEFT,
    pygame.K_a      : GameActions.LEFT,
    pygame.K_RIGHT  : GameActions.RIGHT,
    pygame.K_d      : GameActions.RIGHT,
    pygame.K_UP     : GameActions.UP,
    pygame.K_w      : GameActions.UP,
    pygame.K_DOWN   : GameActions.DOWN,
    pygame.K_s      : GameActions.DOWN,

    pygame.K_r      : GameActions.NEWGAME,
}

@dataclass
class InputState:
    gameAction:        str | None
    keysPressed:       pygame.key.ScancodeWrapper
    mousePos:          Vector
    mouseButtons:      dict[str, bool]
    mouseButtons_down: dict[str, bool]
    mouseButtons_up:   dict[str, bool]

def get_inputState(events: list) -> InputState:
    # Game-specific input
    gameAction  = _get_action(events)
    # Keys
    keysPressed = pygame.key.get_pressed()
    # Mouse
    mousePos      = Vector(pygame.mouse.get_pos())
    mouseButtons  = _coerce_dict_mouseButtons(pygame.mouse.get_pressed())
        # Extract just_pressed and just_released from the event queue
    mouseButtons_down, mouseButtons_up = _get_mouseButtonState(events)
    mouseButtons_down = _coerce_dict_mouseButtons(mouseButtons_down)
    mouseButtons_up   = _coerce_dict_mouseButtons(mouseButtons_up)
    
    return InputState(
        gameAction, 
        keysPressed, 
        mousePos, 
        mouseButtons, 
        mouseButtons_down,
        mouseButtons_up, 
    )

def _get_action(events: list) -> str | None:
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_INPUTS:
                return KEY_INPUTS[event.key]
    return None

def _get_mouseButtonState(events: list) -> tuple[tuple[bool, bool, bool], tuple[bool, bool, bool]]:
    ''' Returns mouse button down & up '''
    down_buttons = [False, False, False]
    up_buttons   = [False, False, False]
    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # -1 since mouse events use 1-indexed buttons (1=Left, 2=Middle, 3=Right)
            if 1 <= event.button <= 3:
                down_buttons[event.button - 1] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if 1 <= event.button <= 3:
                up_buttons[event.button - 1] = True
                
    return tuple(down_buttons), tuple(up_buttons)

def _coerce_dict_mouseButtons(mouseButtons: tuple[bool, bool, bool] | list[bool]) -> dict[str, bool]:
    return {
        "left":   mouseButtons[0],
        "middle": mouseButtons[1],
        "right":  mouseButtons[2]
    }
