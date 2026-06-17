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
    mouseButtons_up:   dict[str, bool]
    mouseButtons_down: dict[str, bool]

def get_inputState(events: list) -> InputState:
    gameAction          = _get_action(events)
    keysPressed         = pygame.key.get_pressed()
    mousePos            = Vector(pygame.mouse.get_pos())
    mouseButtons        = _coerce_dict_mouseButtons(pygame.mouse.get_pressed())
    mouseButtons_up     = _coerce_dict_mouseButtons(pygame.mouse.get_just_released())
    mouseButtons_down   = _coerce_dict_mouseButtons(pygame.mouse.get_just_pressed())

    return InputState(gameAction, keysPressed, mousePos, mouseButtons, mouseButtons_up, mouseButtons_down)

def _get_action(events: list) -> str | None:
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_INPUTS:
                return KEY_INPUTS[event.key]
    return None

def _coerce_dict_mouseButtons(mouseButtons: tuple[bool, bool, bool] | tuple[bool, bool, bool, bool, bool]) -> dict[str, bool]:
    return {
        "left":        mouseButtons[0],
        "middle":      mouseButtons[1],
        "right":       mouseButtons[2]
    }
